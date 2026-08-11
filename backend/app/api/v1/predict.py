from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.predict import PredictionRequest, PredictionResponse
from backend.app.services.predict_service import predict_service
from backend.app.core.dependencies import require_role

router = APIRouter(prefix="/predict", tags=["Prediction & Threat Detection Engine"])


class RemediationRequest(BaseModel):
    target_ip: str
    action: str


@router.post("/single", response_model=PredictionResponse, summary="Predict Single Packet Flow Vector")
async def predict_single_packet(
    payload: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Evaluates a single 78-feature network flow vector using loaded ML model classifier and real SHAP XAI."""
    result = await predict_service.predict_single_flow(
        db=db,
        features=payload.features,
        model_name=payload.model_name
    )

    audit = AuditLog(
        user_id=current_user.id,
        action="PACKET_INSPECTION_SINGLE",
        resource="PREDICT",
        status="SUCCESS",
        details={
            "attack_type": result.attack_type,
            "is_malicious": result.is_malicious,
            "model_used": result.model_used
        }
    )
    db.add(audit)
    await db.commit()

    return result


@router.post("/csv", summary="Ingest & Classify Bulk PCAP/CSV Packet Capture File")
async def predict_csv_file(
    file: UploadFile = File(...),
    model_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Processes uploaded CSV file containing network packet flow attributes."""
    content = await file.read()
    results = await predict_service.predict_csv_batch(
        db=db,
        file_content=content,
        model_name=model_name
    )

    audit = AuditLog(
        user_id=current_user.id,
        action="PACKET_INSPECTION_CSV",
        resource="PREDICT",
        status="SUCCESS",
        details={
            "filename": file.filename,
            "total_records": results["total_records"],
            "malicious_count": results["malicious_count"]
        }
    )
    db.add(audit)
    await db.commit()

    return results


@router.post("/remediate", summary="Dispatch Automated Threat Remediation Action")
async def dispatch_remediation(
    payload: RemediationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Executes automated containment action (Perimeter Drop Rule / VLAN Quarantine) on target malicious IP."""
    audit = AuditLog(
        user_id=current_user.id,
        action=f"REMEDIATION_{payload.action.upper()}",
        resource="SECURITY_OPS",
        status="SUCCESS",
        details={
            "target_ip": payload.target_ip,
            "action": payload.action,
            "mode": "SIMULATION MODE"
        }
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "SUCCESS",
        "remediation_mode": "SIMULATION MODE",
        "target_ip": payload.target_ip,
        "action": payload.action,
        "message": f"[SIMULATION MODE] Automated Playbook [{payload.action.upper()}] dispatched for target IP {payload.target_ip}."
    }
