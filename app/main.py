import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import logging

from .models import BirthInfo, ChartResponse, EmailRequest
from .services.astrology import AstrologyService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Astrological Service",
    description="A modern API for generating astrological charts and horoscopes",
    version="1.0.0"
)

# Initialize services
astrology_service = AstrologyService()

# Only initialize email service if credentials are provided
email_service = None
try:
    from .services.email import EmailService
    email_service = EmailService()
    logger.info("Email service initialized successfully")
except (ValueError, ImportError) as e:
    logger.warning(f"Email service not available: {str(e)}")

# Skip PDF service initialization for now due to system dependencies
pdf_service = None
logger.warning("PDF service disabled - system dependencies missing")

@app.post("/chart", response_model=ChartResponse)
async def generate_chart(birth_info: BirthInfo, background_tasks: BackgroundTasks):
    """Generate an astrological chart based on birth information."""
    try:
        logger.info(f"Generating chart for birth date: {birth_info.birth_date}")
        # Calculate chart
        chart_data = astrology_service.calculate_chart(
            birth_info.birth_date,
            birth_info.birth_time,
            birth_info.birth_place_zip,
            birth_info.email  # Pass email to the astrology service
        )
        
        # Generate interpretation
        interpretation = astrology_service.interpret_chart(chart_data)
        chart_data['interpretation'] = interpretation
        
        # Add user info if provided
        if birth_info.name:
            chart_data['name'] = birth_info.name
        if birth_info.email:
            chart_data['email'] = birth_info.email
            
        # Send email if requested and email service is configured
        if birth_info.email and email_service:
            try:
                background_tasks.add_task(
                    email_service.send_chart_email,
                    birth_info.email,
                    "Your Astrological Chart",
                    chart_data
                )
                logger.info(f"Email queued for {birth_info.email}")
            except Exception as e:
                # Log the error but don't fail the request
                logger.error(f"Failed to send email: {str(e)}")
        
        return ChartResponse(
            sun_sign=chart_data['planets']['sun']['sign'],
            moon_sign=chart_data['planets']['moon']['sign'],
            ascendant=chart_data['angles']['ascendant']['sign'],
            houses=chart_data['houses'],
            planets=chart_data['planets'],
            interpretation=interpretation
        )
        
    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/webhook")
async def webhook_handler(birth_info: BirthInfo, background_tasks: BackgroundTasks):
    """Webhook endpoint for external services to request chart generation"""
    try:
        logger.info(f"Webhook request received for {birth_info.email}")
        # Generate chart data
        chart_data = astrology_service.calculate_chart(
            birth_info.birth_date,
            birth_info.birth_time,
            birth_info.birth_place_zip,
            birth_info.email  # Pass email to the astrology service
        )
        
        # Generate interpretation
        interpretation = astrology_service.interpret_chart(chart_data)
        chart_data['interpretation'] = interpretation
        
        # Add user info
        if birth_info.name:
            chart_data['name'] = birth_info.name
        if birth_info.email:
            chart_data['email'] = birth_info.email
        
        # Send email if email is provided and email service is configured
        if birth_info.email and email_service:
            try:
                background_tasks.add_task(
                    email_service.send_chart_email,
                    birth_info.email,
                    "Your Astrological Chart",
                    chart_data
                )
                logger.info(f"Email queued for {birth_info.email} via webhook")
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
        
        return JSONResponse(content={
            "success": True,
            "chart": {
                "sun_sign": chart_data['planets']['sun']['sign'],
                "moon_sign": chart_data['planets']['moon']['sign'],
                "ascendant": chart_data['angles']['ascendant']['sign'],
                "interpretation": interpretation
            }
        })
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )

@app.post("/chart/pdf/{chart_id}")
async def generate_pdf(chart_id: str):
    """Generate a PDF report for a specific chart."""
    try:
        # PDF service is disabled for now
        return JSONResponse(
            status_code=501,  # Not Implemented
            content={"error": "PDF generation is currently unavailable due to missing system dependencies"}
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chart/email")
async def send_chart_email(email_request: EmailRequest, background_tasks: BackgroundTasks):
    """Send a chart report via email."""
    try:
        # In a real application, you would fetch the chart data from a database
        # For now, we'll return a 501 Not Implemented
        return JSONResponse(
            status_code=501,  # Not Implemented
            content={"error": "Email sending from stored charts is not implemented yet"}
        )
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
