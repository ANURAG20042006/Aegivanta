from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.report import ReportGenerationRequest, ReportResponse
from backend.app.services.report_service import ReportService
from backend.app.core.dependencies import get_current_user
from backend.app.core.exceptions import NotFoundError

router = APIRouter(prefix="/reports", tags=["Reports & Export"])


@router.post("/generate", response_model=ReportResponse, summary="Generate Executive Threat Intelligence Report")
async def generate_report(
    payload: ReportGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates PDF, Excel, or CSV threat intelligence report for executive download."""
    return await ReportService.generate_report(format_type=payload.format, db=db)


@router.get("/download/{file_name}", summary="Download Generated Threat Report File")
async def download_report(
    file_name: str,
    current_user: User = Depends(get_current_user)
):
    """Downloads a generated PDF, Excel, or CSV report file."""
    if Path(file_name).name != file_name:
        raise NotFoundError(resource_name="Report File", resource_id=file_name)

    file_path = Path("reports") / file_name
    if not file_path.exists() or not file_path.is_file():
        raise NotFoundError(resource_name="Report File", resource_id=file_name)
    return FileResponse(path=file_path, filename=file_name, media_type="application/octet-stream")
