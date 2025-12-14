import json
import logging
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

device_names_router = APIRouter()

DEVICE_NAMES_FILE = Path("device_names.json")


class DeviceNameUpdate(BaseModel):
    host: str
    custom_name: str


def load_device_names() -> Dict:
    """Load device names from JSON file"""
    try:
        if DEVICE_NAMES_FILE.exists():
            with open(DEVICE_NAMES_FILE, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading device names: {e}")
        return {}


def save_device_names(device_names: Dict) -> None:
    """Save device names to JSON file"""
    try:
        with open(DEVICE_NAMES_FILE, "w") as f:
            json.dump(device_names, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving device names: {e}")
        raise HTTPException(status_code=500, detail="Failed to save device names")


@device_names_router.get("")
async def get_device_names():
    """Get all custom device names"""
    try:
        device_names = load_device_names()
        return device_names
    except Exception as e:
        logger.error(f"Error getting device names: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@device_names_router.post("")
async def update_device_name(device_name_update: DeviceNameUpdate):
    """Update or create a custom name for a device"""
    try:
        device_names = load_device_names()

        device_names[device_name_update.host] = device_name_update.custom_name

        save_device_names(device_names)
        return {"host": device_name_update.host, "custom_name": device_name_update.custom_name}
    except Exception as e:
        logger.error(f"Error updating device name: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@device_names_router.delete("/{host}")
async def delete_device_name(host: str):
    """Delete a custom device name (reset to default)"""
    try:
        device_names = load_device_names()

        if host in device_names:
            del device_names[host]
            save_device_names(device_names)
            return {"message": "Device name reset successfully"}
        else:
            raise HTTPException(status_code=404, detail="Device name not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting device name: {e}")
        raise HTTPException(status_code=500, detail=str(e))
