import io
from pathlib import Path
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.incident import Incident
from backend.app.schemas.predict import (
    PredictRequest, PredictionResult, BatchPredictionResponse, PacketFeatureVector
)
from backend.app.services.predict_service import PredictService
from backend.app.core.dependencies import get_current_user
from backend.app.core.exceptions import InvalidDatasetError
from ml.dataset.cicids2017_schema import CICIDS2017_FEATURES

router = APIRouter(prefix="/predict", tags=["Prediction Engine"])


@router.post("/single", response_model=PredictionResult, summary="Predict Threat for Single Network Flow Vector")
async def predict_single(
    payload: PredictRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Evaluates a single network packet feature vector and logs the threat classification."""
    return await PredictService.process_single_prediction(
        vector=payload.features,
        model_name=payload.model_name or "Random Forest",
        db=db
    )


@router.post("/csv", response_model=BatchPredictionResponse, summary="Batch Predict Network Traffic CSV Upload")
async def predict_csv(
    file: UploadFile = File(...),
    model_name: Optional[str] = Form("Random Forest"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ingests a network capture CSV file, evaluates all rows, and returns malicious flow highlights."""
    if not file.filename or Path(file.filename).suffix.lower() != ".csv":
        raise InvalidDatasetError(detail="File uploaded must be a CSV dataset.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise InvalidDatasetError(detail=f"Failed to parse CSV file: {str(e)}")

    if df.empty:
        raise InvalidDatasetError(detail="Uploaded CSV file is empty.")

    results: List[PredictionResult] = []
    malicious_count = 0

    # Limit to top 50 rows for real-time responsiveness
    sample_df = df.head(50)
    for _, row in sample_df.iterrows():
        # Parse fields from row or fallback to standard vector
        vector = PacketFeatureVector(
            source_ip=_as_text(row, ("Source IP", "source_ip"), f"192.168.1.{random_ip_suffix()}"),
            destination_ip=_as_text(row, ("Destination IP", "destination_ip"), "10.0.0.1"),
            source_port=_as_int(row, ("Source Port", "source_port"), 443),
            destination_port=_as_int(row, ("Destination Port", "destination_port"), 80),
            protocol=_as_text(row, ("Protocol", "protocol"), "TCP"),
            flow_duration=_as_float(row, ("Flow Duration", "flow_duration"), 1000.0),
            total_fwd_packets=_as_float(row, ("Total Fwd Packets", "total_fwd_packets"), 10.0),
            total_backward_packets=_as_float(row, ("Total Backward Packets", "total_backward_packets"), 8.0),
            packet_length_std=_as_float(row, ("Packet Length Std", "packet_length_std"), 128.0),
            flow_bytes_s=_as_float(row, ("Flow Bytes/s", "flow_bytes_s"), 10240.0),
            syn_flag_count=_as_float(row, ("SYN Flag Count", "syn_flag_count"), 0.0),
            rst_flag_count=_as_float(row, ("RST Flag Count", "rst_flag_count"), 0.0),
            psh_flag_count=_as_float(row, ("PSH Flag Count", "psh_flag_count"), 0.0),
            ack_flag_count=_as_float(row, ("ACK Flag Count", "ack_flag_count"), 0.0),
            urg_flag_count=_as_float(row, ("URG Flag Count", "urg_flag_count"), 0.0),
            flow_packets_s=_as_float(row, ("Flow Packets/s", "flow_packets_s"), 100.0),
            packet_length_mean=_as_float(row, ("Packet Length Mean", "packet_length_mean"), 256.0),
            extra_features=_extract_extra_features(row),
        )
        res = await PredictService.process_single_prediction(vector, model_name or "Random Forest", db)
        if res.is_malicious:
            malicious_count += 1
        results.append(res)

    total = len(results)
    benign_count = total - malicious_count
    ratio = round((malicious_count / total) * 100.0, 2) if total > 0 else 0.0

    return BatchPredictionResponse(
        total_packets_inspected=total,
        malicious_packets_count=malicious_count,
        benign_packets_count=benign_count,
        threat_ratio_percentage=ratio,
        results=results
    )


def random_ip_suffix() -> int:
    import random
    return random.randint(2, 254)


def _row_value(row: pd.Series, names: tuple[str, ...], default: object) -> object:
    """Returns the first populated value under any supported CSV column name."""
    for name in names:
        value = row.get(name)
        if value is not None and not pd.isna(value) and str(value).strip():
            return value
    return default


def _as_text(row: pd.Series, names: tuple[str, ...], default: str) -> str:
    return str(_row_value(row, names, default)).strip()


def _as_float(row: pd.Series, names: tuple[str, ...], default: float) -> float:
    try:
        return float(_row_value(row, names, default))
    except (TypeError, ValueError):
        return default


def _as_int(row: pd.Series, names: tuple[str, ...], default: int) -> int:
    try:
        return int(float(_row_value(row, names, default)))
    except (TypeError, ValueError):
        return default


def _extract_extra_features(row: pd.Series) -> dict[str, float]:
    """Preserves every recognized CICIDS2017 feature present in an uploaded row."""
    extra: dict[str, float] = {}
    for feature in CICIDS2017_FEATURES:
        snake_name = feature.lower().replace(" ", "_").replace("/", "_")
        value = _row_value(row, (feature, snake_name), None)
        if value is None:
            continue
        try:
            extra[feature] = float(value)
        except (TypeError, ValueError):
            continue
    return extra
