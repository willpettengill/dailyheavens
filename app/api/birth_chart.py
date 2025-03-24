from fastapi import APIRouter, HTTPException
from app.models.birth_chart import BirthChartRequest, BirthChartResponse
from app.services.birth_chart import BirthChartService

router = APIRouter()
birth_chart_service = BirthChartService()

@router.post("/birthchart", response_model=BirthChartResponse)
async def calculate_birth_chart(request: BirthChartRequest):
    try:
        chart = birth_chart_service.calculate_birth_chart(
            date_of_birth=request.date_of_birth,
            latitude=request.location.latitude,
            longitude=request.location.longitude
        )
        return BirthChartResponse(
            status="success",
            data=chart,
            location=request.location
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 