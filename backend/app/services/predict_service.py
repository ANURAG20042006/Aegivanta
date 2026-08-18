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

    # Classical sklearn/boosting models -> joblib
    # PyTorch deep learning models     -> .pt  (torch.save artifact)
    _artifact_filenames = {
        "Random Forest":      "random_forest.joblib",
        "XGBoost":            "xgboost.joblib",
        "LightGBM":           "lightgbm.joblib",
        "CatBoost":           "catboost.joblib",
        "Decision Tree":      "decision_tree.joblib",
        "Logistic Regression": "logistic_regression.joblib",
        "SVM":                "svm.joblib",
        "KNN":                "knn.joblib",
        "Naive Bayes":        "naive_bayes.joblib",
        "1D-CNN":             "cnn_1d.pt",
        "LSTM":               "lstm.pt",
        "Autoencoder":        "autoencoder.pt",
    }
    # Models whose artifacts are stored as PyTorch .pt files
    _pytorch_model_names = {"1D-CNN", "LSTM", "Autoencoder"}

    @classmethod
    def _load_artifacts(cls, model_name: str) -> Tuple[Any, Any]:
        """
        Loads model and preprocessor artifacts fail-closed.
        Raises HTTPException(503) if artifacts are missing or unreadable.
        """
        from ml.schema.artifact_mapping import resolve_model_artifact_path, PYTORCH_MODEL_NAMES

        artifact_dir = Path(settings.MODEL_ARTIFACTS_DIR)
        if not artifact_dir.is_absolute():
            artifact_dir = Path(__file__).resolve().parents[3] / artifact_dir

        if model_name not in cls._model_artifacts or cls._model_artifacts[model_name] is None:
            model_path, art_type, _, exists = resolve_model_artifact_path(model_name, artifact_dir)

            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Model artifact for '{model_name}' missing from '{artifact_dir}'. Run training pipeline."
                )

            try:
                if model_name in cls._pytorch_model_names:
                    # PyTorch artifact: reconstruct network from stored architecture metadata
                    from ml.models.deep_learning import _load_pytorch_artifact, CNN1DModel, LSTMModel, AutoencoderModel
                    _model_map = {"1D-CNN": CNN1DModel, "LSTM": LSTMModel, "Autoencoder": AutoencoderModel}
                    wrapper = _model_map[model_name]()
                    wrapper.load(str(model_path))
                    cls._model_artifacts[model_name] = wrapper
                else:
                    cls._model_artifacts[model_name] = joblib.load(model_path)
            except HTTPException:
                raise
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
        if (not n_features_in or n_features_in == 0) and hasattr(inner_model, "feature_names_") and inner_model.feature_names_:
            n_features_in = len(inner_model.feature_names_)
        elif (not n_features_in or n_features_in == 0) and hasattr(inner_model, "_input_dim") and inner_model._input_dim:
            n_features_in = inner_model._input_dim

        if n_features_in and n_features_in > 0 and selected_feats > 0 and n_features_in != selected_feats:
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid feature payload: expected dictionary or PacketFeatureVector."
            )

        model_name = model_name or "Random Forest"
        attack_type, confidence_score, is_malicious, severity, probs, shap = self.infer_packet_threat(
            vector, model_name
        )

        from backend.app.models.protected_asset import ProtectedAsset
        from backend.app.models.alert import Alert
        now_utc = datetime.now(timezone.utc)
        target_incident_id = None

        if settings.SOC_PHASE1_ENABLED:
            from backend.app.models.protected_asset import ProtectedAsset
            from backend.app.models.alert import Alert
            from backend.app.models.security_event import SecurityEvent
            from backend.app.models.incident_timeline import IncidentTimelineEvent
            from backend.app.services.risk_engine import RiskScoringEngine
            from backend.app.services.correlation_engine import IncidentCorrelationEngine
            from backend.app.api.v1.websockets import manager
            from sqlalchemy import or_, and_

            # 1. Resolve Target Protected Asset deterministically (active only)
            asset = None
            if vector.destination_ip:
                asset_stmt = select(ProtectedAsset).where(
                    and_(
                        ProtectedAsset.status != "inactive",
                        or_(
                            ProtectedAsset.ip_address == vector.destination_ip,
                            ProtectedAsset.hostname == vector.destination_ip
                        )
                    )
                ).limit(1)
                asset_res = await db.execute(asset_stmt)
                asset = asset_res.scalar_one_or_none()

            asset_crit = asset.criticality if asset else "medium"

            # 2. Calculate dynamic operational risk score
            risk_score = RiskScoringEngine.calculate_risk_score(
                severity=severity,
                confidence=confidence_score,
                criticality=asset_crit,
                alert_count=1
            )

            if is_malicious:
                # 3. Create First-Class Security Alert
                alert = Alert(
                    asset_id=asset.id if asset else None,
                    title=f"Detected {severity} {attack_type} Attack",
                    description=f"Automated threat detection by {model_name} classified incoming packet flow as {attack_type}.",
                    severity=severity.lower(),
                    confidence=confidence_score,
                    risk_score=risk_score,
                    source=f"ML_ENGINE:{model_name}",
                    source_ip=vector.source_ip,
                    destination_ip=vector.destination_ip,
                    source_port=vector.source_port,
                    destination_port=vector.destination_port,
                    protocol=vector.protocol,
                    attack_type=attack_type,
                    status="new",
                    explanation=shap,
                    timestamp=now_utc
                )
                db.add(alert)
                await db.flush()

                # 4. Correlate Alert into Incident & Append Chronological Timeline Event
                incident, timeline_evt = await IncidentCorrelationEngine.process_alert(db, alert, asset)
                target_incident_id = incident.id

                # 5. Record Security Event Ledger
                sec_event = SecurityEvent(
                    asset_id=asset.id if asset else None,
                    source_ip=vector.source_ip,
                    destination_ip=vector.destination_ip,
                    source_port=vector.source_port,
                    destination_port=vector.destination_port,
                    protocol=vector.protocol,
                    event_type="ALERT_TRIGGERED",
                    severity=severity.lower(),
                    model_prediction=attack_type,
                    confidence=confidence_score,
                    risk_score=risk_score,
                    status="ACTIONABLE",
                    metadata_payload={"alert_id": alert.alert_id, "incident_id": incident.id, "attack_type": attack_type}
                )

                # Phase 2 Enrichment: Threat Intel IOC Enrichment & Behavioral Anomaly Detection
                try:
                    from backend.app.services.threat_intel_service import ThreatIntelService
                    ioc_res = await ThreatIntelService.enrich_telemetry(vector.source_ip, vector.destination_ip, None, db)
                    if ioc_res.get("is_match"):
                        sec_event.metadata_payload["ioc_enrichment"] = ioc_res
                except Exception as tie:
                    logger.debug("Threat intel enrichment skipped: %s", tie)

                try:
                    if asset and vector.flow_packets_s:
                        from backend.app.services.anomaly_service import AnomalyService
                        await AnomalyService.detect_anomaly(asset.id, "packet_rate", float(vector.flow_packets_s), db)
                except Exception as ane:
                    logger.debug("Anomaly detection check skipped: %s", ane)

                try:
                    from backend.app.services.investigation_service import InvestigationService
                    await InvestigationService.analyze_incident(incident.id, db)
                except Exception as ive:
                    logger.debug("Automated investigation update skipped: %s", ive)

                db.add(sec_event)

                # Commit transaction first to ensure persistence
                await db.commit()

                # 6. Publish real-time event to WebSocket subscribers AFTER commit
                try:
                    await manager.broadcast_event("ALERT_TRIGGERED", {
                        "alert_id": alert.alert_id,
                        "incident_id": incident.id,
                        "incident_code": incident.incident_code,
                        "attack_type": attack_type,
                        "severity": incident.severity,
                        "confidence": confidence_score,
                        "risk_score": incident.risk_score,
                        "source_ip": vector.source_ip,
                        "destination_ip": vector.destination_ip,
                        "asset_name": asset.name if asset else None,
                        "timestamp": now_utc.isoformat()
                    })
                except Exception as ws_err:
                    logger.warning("WebSocket broadcast skipped: %s", ws_err)

            else:
                # Benign Flow: Record Incident for telemetry tracking and baseline stats
                incident = Incident(
                    asset_id=asset.id if asset else None,
                    source_ip=vector.source_ip,
                    destination_ip=vector.destination_ip,
                    source_port=vector.source_port,
                    destination_port=vector.destination_port,
                    protocol=vector.protocol,
                    packet_length=int(vector.packet_length_mean),
                    flow_duration=vector.flow_duration,
                    attack_type=attack_type,
                    confidence_score=confidence_score,
                    is_malicious=False,
                    severity=severity,
                    model_name=model_name,
                    timestamp=now_utc,
                    first_seen=now_utc,
                    last_seen=now_utc,
                    feature_payload=vector.model_dump()
                )
                db.add(incident)
                await db.flush()
                target_incident_id = incident.id

                # Record root timeline event
                timeline_evt = IncidentTimelineEvent(
                    incident_id=incident.id,
                    timestamp=now_utc,
                    event_type="DETECTION",
                    title=f"Telemetry Inspected: {attack_type}",
                    description=f"Flow from {vector.source_ip} to {vector.destination_ip} evaluated as {attack_type} by {model_name}.",
                    actor="ML_ENGINE",
                    metadata_payload={"model": model_name, "is_malicious": False}
                )
                db.add(timeline_evt)

                sec_event = SecurityEvent(
                    asset_id=asset.id if asset else None,
                    source_ip=vector.source_ip,
                    destination_ip=vector.destination_ip,
                    source_port=vector.source_port,
                    destination_port=vector.destination_port,
                    protocol=vector.protocol,
                    event_type="FLOW_INSPECTED_BENIGN",
                    severity="info",
                    model_prediction=attack_type,
                    confidence=confidence_score,
                    risk_score=0.0,
                    status="PROCESSED"
                )
                db.add(sec_event)
                await db.commit()

        else:
            # Baseline Fallback Path (When SOC Phase 1 is disabled)
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
                timestamp=now_utc,
                first_seen=now_utc,
                last_seen=now_utc,
                feature_payload=vector.model_dump()
            )
            db.add(incident)
            await db.flush()
            target_incident_id = incident.id

        await db.commit()

        return PredictionResult(
            incident_id=target_incident_id,
            source_ip=vector.source_ip,
            destination_ip=vector.destination_ip,
            source_port=vector.source_port,
            destination_port=vector.destination_port,
            protocol=vector.protocol,
            attack_type=attack_type,
            confidence_score=confidence_score,
            confidence_available=(confidence_score is not None),
            is_malicious=is_malicious,
            severity=severity,
            model_used=model_name,
            timestamp=now_utc,
            attack_probabilities=probs,
            shap_explanation=shap
        )

    async def predict_csv_batch(
        self,
        db: AsyncSession,
        file_content: bytes,
        model_name: Optional[str] = "Random Forest"
    ) -> Dict[str, Any]:
        try:
            df = pd.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to parse CSV file: {e}"
            )

        total_records = len(df)
        if total_records == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded CSV file is empty."
            )

        # Standardize column headers (lowercase, strip, replace spaces/dots with underscores)
        normalized_columns = {}
        for col in df.columns:
            clean_col = str(col).strip().lower().replace(" ", "_").replace(".", "_").replace("/", "_per_")
            normalized_columns[col] = clean_col
        df = df.rename(columns=normalized_columns)

        predictions: List[PredictionResult] = []
        malicious_count = 0

        # Process up to 200 rows per batch
        MAX_CSV_BATCH = 200
        records_to_process = df.head(MAX_CSV_BATCH)

        for i, row in records_to_process.iterrows():
            row_dict = row.dropna().to_dict()
            try:
                vector = PacketFeatureVector(**row_dict)
            except Exception as val_err:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"CSV row #{i + 1} validation failed: {val_err}"
                )
            res = await self.predict_single_flow(db, vector, model_name)
            if res.is_malicious:
                malicious_count += 1
            predictions.append(res)

        return {
            "total_records": total_records,
            "processed_records": len(predictions),
            "malicious_count": malicious_count,
            "predictions": [p.model_dump() for p in predictions]
        }


predict_service = PredictService()
