from datetime import datetime, timezone
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Flowable,
)


class DrawingFlowable(Flowable):
    def __init__(self, drawing, width, height):
        super().__init__()
        self.drawing = drawing
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)


def box(d, x, y, w, h, title, subtitle=None, fill=colors.whitesmoke):
    d.add(Rect(x, y, w, h, fillColor=fill, strokeColor=colors.black, strokeWidth=1))
    d.add(String(x + 8, y + h - 18, title, fontName="Helvetica-Bold", fontSize=10))
    if subtitle:
        d.add(String(x + 8, y + h - 34, subtitle, fontName="Helvetica", fontSize=9))


def arrow(d, x1, y1, x2, y2):
    d.add(Line(x1, y1, x2, y2, strokeColor=colors.black, strokeWidth=1))


def architecture_drawing():
    w, h = 540, 260
    d = Drawing(w, h)

    box(d, 20, 180, 160, 60, "Clients", "Web / Mobile / Admin UI", fill=colors.lightgrey)
    box(d, 220, 180, 300, 60, "FastAPI Backend", "app/main.py (routers)", fill=colors.aliceblue)

    box(d, 220, 100, 90, 60, "Routers", "ggt/routers", fill=colors.beige)
    box(d, 325, 100, 90, 60, "Workflows", "workflow_models", fill=colors.beige)
    box(d, 430, 100, 90, 60, "Processes", "process_models (bp_*)", fill=colors.beige)

    box(d, 220, 20, 140, 60, "Data Models", "MySQL CRUD/queries", fill=colors.honeydew)
    box(d, 380, 20, 140, 60, "Adapters", "AWS/Stripe/Twilio/etc.", fill=colors.honeydew)

    box(d, 20, 20, 160, 60, "Modal Compute", "ggt/modal_app.py", fill=colors.lavender)

    arrow(d, 180, 210, 220, 210)
    arrow(d, 370, 180, 265, 160)
    arrow(d, 370, 180, 370, 160)
    arrow(d, 370, 180, 475, 160)

    arrow(d, 265, 100, 290, 80)
    arrow(d, 370, 100, 370, 80)
    arrow(d, 475, 100, 450, 80)

    arrow(d, 220, 50, 180, 50)
    arrow(d, 180, 50, 220, 50)

    d.add(String(32, 160, "Async/remote jobs", fontName="Helvetica", fontSize=8))
    arrow(d, 180, 50, 220, 80)

    return d, w, h


def tech_stack_table():
    rows = [
        ["Layer", "Technology / Notes"],
        ["API", "Python + FastAPI (ASGI), Uvicorn; routers under app/ggt/routers"],
        ["Business logic", "workflow_models → process_models (bp_*) → data_models"],
        ["Database", "MySQL (mysql-connector-python)"],
        ["Auth", "Auth0 JWT validation (jose/jwt) + optional API key header for vendors"],
        ["Messaging/Tasks", "In-process BackgroundTasks plus Modal compute offload"],
        ["Cloud", "AWS (Secrets Manager, S3, SNS/SQS/Pinpoint, DynamoDB), GCP Storage"],
        ["Payments", "Stripe"],
        ["Comms", "Twilio (SMS/voice), SendGrid (email templates)"],
        ["Docs/Run", "Docker images for ASGI and Lambda; runbook under docs/runbook.md"],
    ]
    t = Table(rows, colWidths=[1.4 * inch, 5.6 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ]
        )
    )
    return t


def build_pdf(out_path: Path):
    styles = getSampleStyleSheet()
    title = styles["Title"]
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]

    doc = SimpleDocTemplate(str(out_path), pagesize=letter, title="GGT Project Explanation")
    story = []

    story.append(Paragraph("GGT Project Explanation", title))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            body,
        )
    )
    story.append(Spacer(1, 18))

    story.append(Paragraph("1. Overview", h1))
    story.append(
        Paragraph(
            "This repository is a Python FastAPI backend that exposes multiple role-based APIs (patient, portal/admin, providers, contact center, billing, reporting, vendors). It integrates with MySQL and several external services (AWS, Auth0, Twilio, SendGrid, Stripe, GCP Storage). Heavy or long-running compute can be offloaded to Modal using a dedicated Modal app.",
            body,
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Architecture Visualization", h1))
    d, w, h = architecture_drawing()
    story.append(DrawingFlowable(d, w, h))
    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Frontend / Client Layer", h1))
    story.append(
        Paragraph(
            "This repo primarily contains the backend service. Frontend clients are assumed to be separate applications (web/mobile/admin UI) that call the REST endpoints. The backend organizes routes by role and prefixes (e.g., /api for patient, /api/portal for admin).",
            body,
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("4. Backend Details", h1))
    story.append(Paragraph("4.1 Entry points", h2))
    story.append(
        Paragraph(
            "FastAPI app wiring lives in app/main.py; routers are included from app/ggt/routers. AWS Lambda is supported via Mangum, and Modal compute is provided via app/ggt/modal_app.py.",
            body,
        )
    )
    story.append(Spacer(1, 8))
    story.append(Paragraph("4.2 Layering", h2))
    story.append(
        Paragraph(
            "Routers → workflow_models → process_models (bp_*) → data_models. Adapters in ggt/lib/adapters isolate external dependencies such as AWS services and vendor APIs.",
            body,
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("5. Web Tech Stack & Technologies", h1))
    story.append(tech_stack_table())
    story.append(Spacer(1, 12))

    story.append(Paragraph("6. Deployment & Runtime Options", h1))
    story.append(
        Paragraph(
            "The service can run as a normal ASGI web service (local Uvicorn, Docker gunicorn/uvicorn image) or as an AWS Lambda container. Modal compute can run background job functions and expose an HTTP endpoint for triggering those jobs remotely.",
            body,
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Operational endpoints: /healthz and /readyz. /readyz can optionally perform a MySQL connectivity check when enabled via environment variable.",
            body,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("7. Modal Integration (Compute Backend)", h1))
    story.append(
        Paragraph(
            "Modal compute is integrated through a Modal app that wraps selected heavy workloads (queue processors, lab integration, schedule generation). The API service can trigger Modal either by calling the deployed Modal HTTP endpoint (when MODAL_WEB_BASE_URL is set) or by SDK lookup.",
            body,
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Key environment variables: MODAL_APP_NAME, MODAL_SECRET_NAME, MODAL_WEB_BASE_URL, READYZ_CHECK_DB, STRICT_CONFIG.",
            body,
        )
    )

    story.append(Spacer(1, 18))
    story.append(Paragraph("8. Quick Run Commands (Reference)", h1))
    story.append(
        Paragraph(
            "For step-by-step commands and troubleshooting, see docs/runbook.md in the repository. Typical local dev run: cd app && ./run.sh. Docker run: docker build -t ggt-api . && docker run --rm -p 8000:80 ggt-api.",
            body,
        )
    )

    doc.build(story)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "project-explanation.pdf"
    build_pdf(out)
    print(out)
