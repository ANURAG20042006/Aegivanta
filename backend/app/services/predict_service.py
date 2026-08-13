import io
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.models.incident import Incident
from backend.app.models.model_registry import ModelRegistry
from backend.app.schemas.predict import PacketFeatureVector, PredictionResult
from ml.dataset.cicids2017_schema import ATTACK_CLASSES
from ml.schema.feature_schema import DEFAULT_FEATURE_SCHEMA, validate_input_vector, validate_artifact_compatibility
from ml.explainability.real_explainer import RealModelExplainer
from ml.monitoring.drift_detector import AccumulatedWindowDriftDetector


class PredictService:
    """
    Production-Quality Business Service Executing Packet Threat Classification
    via Loaded ML Artifacts, Feature Schema Validation, Real SHAP XAI, and Incident Logging.
    """

    _model_artifacts: Dict[str, Any] = {}
    _preprocessor_artifact: Any = None
    _explainers: Dict[str, RealModelExplainer] = {}
    _drift_detector: AccumulatedWindowDriftDetector = AccumulatedWindowDriftDetector(window_size=50)

    _artifact_filenames = {
        "Random Forest": "random_forest.joblib",
        "XGBoost": "xgboost.joblib",
        "LightGBM": "lightgbm.joblib",
        "CatBoost": "catboost.joblib",
        "Decision Tree": "decision_tree.joblib",
        "Logistic Regression": "logistic_regression.joblib",
        "SVM": "svm.joblib",
        "KNN": "knn.joblib",
        "Naive Bayes": "naive_bayes.joblib",
        "1D-CNN": "1d-cnn.joblib",
        "LSTM": "lstm.joblib",
        "Autoencoder": "autoencoder.joblib",
    }

    @classmethod
    def _load_artifacts(cls, model_name: str) -> Tuple[Any, Any]:
        """
        Loads model and preprocessor artifacts fail-closed.
        Raises HTTPException(503) if artifacts are missing or unreadable.
        """
        artifact_dir = Path(settings.MODEL_ARTIFACTS_DIR)
        if not artifact_dir.is_absolute():
            artifact_dir = Path(__file__).resolve().parents[3] / artifact_dir

        filename = cls._artifact_filenames.get(model_name, "best_model.joblib")
        if model_name not in cls._model_artifacts or cls._model_artifacts[model_name] is None:
            model_path = artifact_dir / filename
            if not model_path.exists():
                model_path = artifact_dir / "best_model.joblib"

            if not model_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Model artifact '{filename}' missing from '{artifact_dir}'. Run training pipeline."
                )

            try:
                cls._model_artifacts[model_name] = joblib.load(model_path)
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Model artifact '{model_path}' is corrupted or unreadable: {exc}"
                )

        if cls._preprocessor_artifact is None:
            preprocessor_path = artifact_dir / "preprocessor.joblib"
            if not preprocessor_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Preprocessor artifact 'preprocessor.joblib' missing from '{artifact_dir}'."
                )

            try:
                cls._preprocessor_artifact = joblib.load(preprocessor_path)

                baseline_path = artifact_dir / "baseline_X_train.joblib"
                if baseline_path.exists():
                    baseline_matrix = joblib.load(baseline_path)
                    feature_names = getattr(cls._preprocessor_artifact, "selected_feature_names", [])
                    cls._drift_detector.update_baseline(
                        baseline_matrix=baseline_matrix,
                        feature_names=feature_names,
                        reference_version=getattr(cls._preprocessor_artifact, "version", "schema-v1.0")
                    )
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Preprocessor artifact '{preprocessor_path}' is corrupted or unreadable: {exc}"
                )

        return cls._model_artifacts[model_name], cls._preprocessor_artifact

    @classmethod
    def get_explainer(cls, model_name: str, model: Any, feature_names: List[str]) -> RealModelExplainer:
        if model_name not in cls._explainers:
            cls._explainers[model_name] = RealModelExplainer(model, feature_names)
        return cls._explainers[model_name]

    @classmethod
    def infer_packet_threat(
        cls,
        vector: PacketFeatureVector,
        model_name: str = "Random Forest"
    ) -> Tuple[str, Optional[float], bool, str, Optional[Dict[str, float]], Dict[str, Any]]:
        """
        Executes actual machine learning model inference using loaded preprocessor & model artifacts.
        Fails closed on missing or corrupted artifacts. No hardcoded attack rules.
        """
        model, preprocessor = cls._load_artifacts(model_name)
        raw_dict = vector.model_dump()

        # Step 3: Validate Feature Schema Contract (Fail-closed -> HTTP 400)
        is_valid, schema_errors = validate_input_vector(raw_dict, DEFAULT_FEATURE_SCHEMA)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Feature schema validation failed: {schema_errors}"
            )

        # Step 4: Model/Artifact Integrity & Compatibility Check
        artifact_dir = Path(settings.MODEL_ARTIFACTS_DIR)
        if not artifact_dir.is_absolute():
            artifact_dir = Path(__file__).resolve().parents[3] / artifact_dir

        meta_path = artifact_dir / "metadata.json"
        if not meta_path.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Model metadata artifact 'metadata.json' missing from '{artifact_dir}'."
            )

        try:
            import json
            with meta_path.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Model metadata file 'metadata.json' is corrupted: {exc}"
            )

        compat_ok, compat_errors = validate_artifact_compatibility(metadata)
        if not compat_ok:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Artifact compatibility validation failed: {compat_errors}"
            )

        # Verify preprocessor output feature count matches model input feature count
        selected_feats = len(getattr(preprocessor, "selected_feature_names", []))
        inner_model = getattr(model, "model", model)
        n_features_in = getattr(inner_model, "n_features_in_", None)
        if n_features_in is not None and selected_feats > 0 and n_features_in != selected_feats:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"MODEL_PREPROCESSOR_SCHEMA_MISMATCH: Preprocessor produces {selected_feats} features but model expects {n_features_in}."
            )

        try:
            # Transform vector via fitted preprocessor
            processed_matrix = preprocessor.transform_raw_sample(raw_dict)
            cls._drift_detector.add_observation(processed_matrix)

            # Actual Model Prediction
            confidence_score = None
            probs_arr = None

            if hasattr(model, "predict_proba"):
                try:
                    probs_arr = model.predict_proba(processed_matrix)
                    if probs_arr is not None and len(probs_arr) > 0:
                        probs_arr = probs_arr[0]
                        class_idx = int(np.argmax(probs_arr))
                        confidence_score = float(np.max(probs_arr))
                    else:
                        preds_arr = model.predict(processed_matrix)
                        class_idx = int(preds_arr[0])
                except Exception:
                    preds_arr = model.predict(processed_matrix)
                    class_idx = int(preds_arr[0])
            else:
                preds_arr = model.predict(processed_matrix)
                class_idx = int(preds_arr[0])

            # Map predicted index to Attack Class Name
            classes = getattr(preprocessor, "label_encoder", None)
            if classes and hasattr(classes, "classes_") and class_idx < len(classes.classes_):
                attack_type = str(classes.classes_[class_idx])
            elif class_idx < len(ATTACK_CLASSES):
                attack_type = ATTACK_CLASSES[class_idx]
            else:
                attack_type = "BENIGN"

            is_malicious = (attack_type != "BENIGN")

            # Map Probability Dictionary if supported by model architecture
            probabilities = None
            if probs_arr is not None and hasattr(preprocessor, "label_encoder") and hasattr(preprocessor.label_encoder, "classes_"):
                probabilities = {}
                for idx, name in enumerate(preprocessor.label_encoder.classes_):
                    if idx < len(probs_arr):
                        probabilities[str(name)] = round(float(probs_arr[idx]), 4)

            # Map Severity based on threat state and real model confidence
            if not is_malicious:
                severity = "Low"
            elif confidence_score is not None and confidence_score > 0.95:
                severity = "Critical"
            elif confidence_score is not None and confidence_score > 0.90:
                severity = "High"
            else:
                severity = "Medium"

            # Compute Real SHAP Feature Explanation
            model_ver = metadata.get("model_version", f"{model_name.lower().replace(' ', '_')}-v1.0")
            feature_names = getattr(preprocessor, "selected_feature_names", [])
            explainer = cls.get_explainer(model_name, getattr(model, "model", model), feature_names)

            shap_explanation = explainer.explain_instance(
                processed_vector=processed_matrix,
                model_version=model_ver,
                prediction=attack_type,
                confidence=confidence_score,
                top_n=5
            )

            conf_out = round(confidence_score, 4) if confidence_score is not None else None
            return attack_type, conf_out, is_malicious, severity, probabilities, shap_explanation

        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Error executing model inference for %s: %s", model_name, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model inference failed for '{model_name}': {str(exc)}"
            )

    async def predict_single_flow(
        self,
        db: AsyncSession,
        features: Any,
        model_name: Optional[str] = "Random Forest"
    ) -> PredictionResult:
        if isinstance(features, dict):
            vector = PacketFeatureVector(**features)
        elif isinstance(features, PacketFeatureVector):
            vector = features
        else:
            vector = PacketFeatureVector()

        model_name = model_name or "Random Forest"
        attack_type, confidence_score, is_malicious, severity, probs, shap = self.infer_packet_threat(
            vector, model_name
        )

        incident = Incident(
            source_ip=vector.source_ip,
            destination_ip=vector.destination_ip,
            source_port=vector.source_port,
            destination_port=vector.destination_port,
            protocol=vector.protocol,
            packet_length=int(vector.packet_length_mean),
            flow_duration=vector.flow_duration,
            attack_type=attack_type,
            confidence_score=confidence_score,
            is_malicious=is_malicious,
            severity=severity,
            model_name=model_name,
            timestamp=datetime.now(timezone.utc),
            feature_payload=vector.model_dump()
        )
        db.add(incident)
        await db.commit()
        await db.refresh(incident)

        return PredictionResult(
            incident_id=incident.id,
            source_ip=incident.source_ip,
            destination_ip=incident.destination_ip,
            source_port=incident.source_port,
            destination_port=incident.destination_port,
            protocol=incident.protocol,
            attack_type=incident.attack_type,
            confidence_score=incident.confidence_score,
            confidence_available=(incident.confidence_score is not None),
            is_malicious=incident.is_malicious,
            severity=incident.severity,
            model_used=incident.model_name,
            timestamp=incident.timestamp,
            attack_probabilities=probs,
            shap_explanation=shap
        )

    async def predict_csv_batch(
        self,
        db: AsyncSession,
        file_content: bytes,
        model_name: Optional[str] = "Random Forest"
    ) -> Dict[str, Any]:
        df = pd.read_csv(io.BytesIO(file_content))
        total_records = len(df)
        predictions: List[PredictionResult] = []
        malicious_count = 0

        for i, row in df.head(50).iterrows():
            row_dict = row.to_dict()
            vector = PacketFeatureVector(
                source_ip=str(row_dict.get("source_ip", f"192.168.1.{100 + i}")),
                destination_ip=str(row_dict.get("destination_ip", "10.0.0.1")),
                source_port=int(row_dict.get("source_port", 443)),
                destination_port=int(row_dict.get("destination_port", 80)),
                protocol=str(row_dict.get("protocol", "TCP")),
                flow_duration=float(row_dict.get("flow_duration", 120500.0)),
                flow_packets_s=float(row_dict.get("flow_packets_s", 150.0)),
                packet_length_mean=float(row_dict.get("packet_length_mean", 512.0)),
                syn_flag_count=float(row_dict.get("syn_flag_count", 0.0))
            )
            res = await self.predict_single_flow(db, vector, model_name)
            if res.is_malicious:
                malicious_count += 1
            predictions.append(res)

        return {
            "total_records": total_records,
            "malicious_count": malicious_count,
            "predictions": [p.model_dump() for p in predictions]
        }


predict_service = PredictService()
