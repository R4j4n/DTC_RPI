"""
API Router for Wristband Schedule
Provides endpoints for accessing trampoline park wristband rotation schedule
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.wristband_schedule import wristband_schedule_manager
import logging

logger = logging.getLogger(__name__)

wristband_router = APIRouter()


@wristband_router.get("/schedule/status")
async def get_schedule_status():
    """
    Get current wristband schedule status
    Returns current slot, previous 3 slots, and upcoming 3 slots with countdowns
    """
    try:
        status = wristband_schedule_manager.get_schedule_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting schedule status: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@wristband_router.get("/schedule/full")
async def get_full_schedule():
    """
    Get the complete wristband schedule for the day
    """
    try:
        schedule = wristband_schedule_manager.get_full_schedule()
        return JSONResponse(content={"schedule": schedule})
    except Exception as e:
        logger.error(f"Error getting full schedule: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@wristband_router.get("/schedule/current")
async def get_current_slot():
    """
    Get only the current active wristband slot
    """
    try:
        current = wristband_schedule_manager.get_current_slot()
        if current:
            return JSONResponse(content={
                "time": current.time.strftime("%H:%M"),
                "color": current.color,
                "hex_color": current.hex_color
            })
        else:
            return JSONResponse(content={"message": "No active slot at this time"})
    except Exception as e:
        logger.error(f"Error getting current slot: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@wristband_router.get("/schedule/upcoming")
async def get_upcoming_slots():
    """
    Get upcoming wristband slots with countdowns
    """
    try:
        upcoming = wristband_schedule_manager.get_upcoming_slots(count=3)
        return JSONResponse(content={"upcoming_slots": upcoming})
    except Exception as e:
        logger.error(f"Error getting upcoming slots: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
