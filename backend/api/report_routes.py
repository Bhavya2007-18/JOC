from fastapi import APIRouter
from fastapi.responses import JSONResponse

from intelligence.report_engine import ReportEngine
from main import monitor

router = APIRouter(prefix="/report", tags=["report"])

@router.get("/")
def get_session_report():
    engine = ReportEngine(monitor)
    report_data = engine.generate_session_report()
    return JSONResponse(content=report_data)

@router.get("/export")
def export_session_report():
    engine = ReportEngine(monitor)
    report_data = engine.generate_session_report()
    return JSONResponse(
        content=report_data,
        headers={"Content-Disposition": f"attachment; filename=joc_session_report_{int(report_data['timestamp'])}.json"}
    )
