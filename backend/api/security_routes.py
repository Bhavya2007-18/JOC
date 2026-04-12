from fastapi import APIRouter
from security.security_engine import analyze_security

router = APIRouter()


@router.get("/security/analyze")
def analyze():
    return analyze_security()
