from fastapi import APIRouter

from app.api.schemas.request import RiskAnalysisRequest
from app.api.schemas.response import RiskAnalysisResponse
from app.domain.services.analyze_strategy import analyze_strategy

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/analyze", response_model=RiskAnalysisResponse)
def analyze_risk(request: RiskAnalysisRequest) -> RiskAnalysisResponse:
    return analyze_strategy(request)
