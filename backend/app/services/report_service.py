import os
import uuid
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.incident import Incident
from backend.app.schemas.report import ReportResponse


class ReportService:
    """Service generating downloadable executive PDF, Excel, and CSV threat reports."""

    @classmethod
    async def generate_report(
        cls,
        format_type: str,
        db: AsyncSession
    ) -> ReportResponse:
        """Generates downloadable report file in specified format (pdf, excel, csv)."""
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        query = select(Incident).order_by(Incident.timestamp.desc()).limit(100)
        result = await db.execute(query)
        incidents = result.scalars().all()

        records = [
            {
                "ID": inc.id,
                "Timestamp": inc.timestamp.isoformat(),
                "Source IP": inc.source_ip,
                "Destination IP": inc.destination_ip,
                "Protocol": inc.protocol,
                "Attack Type": inc.attack_type,
                "Is Malicious": inc.is_malicious,
                "Severity": inc.severity,
                "Confidence Score": inc.confidence_score,
                "Model Used": inc.model_name
            }
            for inc in incidents
        ]
        df = pd.DataFrame(records)

        report_id = str(uuid.uuid4())[:8]
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        normalized_format = format_type.lower()
        if normalized_format == "csv":
            file_name = f"sentinelai_threat_report_{timestamp_str}_{report_id}.csv"
            file_path = reports_dir / file_name
            df.to_csv(file_path, index=False)
        elif normalized_format == "excel":
            file_name = f"sentinelai_threat_report_{timestamp_str}_{report_id}.xlsx"
            file_path = reports_dir / file_name
            df.to_excel(file_path, index=False, engine="openpyxl")
        elif normalized_format == "pdf":
            file_name = f"sentinelai_threat_report_{timestamp_str}_{report_id}.pdf"
            file_path = reports_dir / file_name
            cls._generate_pdf_report(file_path, records)
        else:
            raise ValueError(f"Unsupported report format: {format_type}")

        download_url = f"/api/v1/reports/download/{file_name}"
        return ReportResponse(
            report_id=report_id,
            file_name=file_name,
            format=normalized_format,
            download_url=download_url,
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_records_exported=len(records)
        )

    @staticmethod
    def _generate_pdf_report(file_path: Path, records: list) -> None:
        """Generates PDF executive report layout using ReportLab."""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(file_path), pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor("#00F0FF"),
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=20
        )

        elements.append(Paragraph("SentinelAI Threat Intelligence & Incident Report", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | Executive Summary", subtitle_style))
        elements.append(Spacer(1, 10))

        # Table data setup
        table_data = [["Timestamp", "Source IP", "Attack Type", "Severity", "Confidence"]]
        for r in records[:15]:  # Top 15 in PDF table
            table_data.append([
                r["Timestamp"][:19],
                r["Source IP"],
                r["Attack Type"],
                r["Severity"],
                f"{r['Confidence Score'] * 100:.1f}%"
            ])

        t = Table(table_data, colWidths=[120, 90, 110, 70, 70])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00F0FF")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        elements.append(t)
        doc.build(elements)
