import json
import os
from typing import Dict

from fastapi import APIRouter, HTTPException, Response
from src.file_utils import atomic_write_json, safe_read_json

# Create router with prefix and tags
router_cec = APIRouter(tags=["HDMI Controls"])

# Constants
HDMI_DEVICES_FILE = "hdmi_devices.json"
CURRENT_INPUT_FILE = "current_input.json"

# Store the controller reference
_cec_controller = None


def initialize_router_cec_controller(controller):
    """Initialize the router with a CEC controller instance"""
    global _cec_controller
    _cec_controller = controller


def load_current_input():
    try:
        data = safe_read_json(CURRENT_INPUT_FILE, default={})
        return data.get("current_input", 0)
    except Exception:
        return 0


def save_current_input(device_number):
    atomic_write_json(CURRENT_INPUT_FILE, {"current_input": device_number})


@router_cec.get("/check_json")
async def check_json() -> bool:
    """Check if hdmi_devices.json exists"""
    return os.path.exists(HDMI_DEVICES_FILE)


@router_cec.post("/set_hdmi_map")
async def set_hdmi_map(hdmi_map: Dict[str, str]):
    """Save HDMI device mapping and update current input"""
    try:
        # Save the HDMI map atomically
        atomic_write_json(HDMI_DEVICES_FILE, hdmi_map)

        # Find the key for "raspberry pi" and update current_input.json
        raspberry_pi_port = None
        for port, device in hdmi_map.items():
            if device.lower() == "raspberry pi":
                raspberry_pi_port = port
                break

        # Switch TV to that HDMI
        if raspberry_pi_port:
            _cec_controller.switch_input(device_number=int(raspberry_pi_port))

        # Load current input with safe defaults
        current_input = safe_read_json(CURRENT_INPUT_FILE, default={"current_input": "1"})

        # Update current_input if raspberry pi is found
        if raspberry_pi_port:
            current_input["current_input"] = raspberry_pi_port

        # Save the updated current_input atomically
        atomic_write_json(CURRENT_INPUT_FILE, current_input)

        return Response(content="HDMI mapped Successfully", status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving HDMI map: {str(e)}")


@router_cec.get("/fetch_hdmi_map")
async def fetch_hdmi_map():
    """Read and return the HDMI device mapping"""
    try:
        if not os.path.exists(HDMI_DEVICES_FILE):
            raise HTTPException(status_code=404, detail="HDMI devices file not found")

        hdmi_map = safe_read_json(HDMI_DEVICES_FILE, default={})
        if not hdmi_map:
            raise HTTPException(status_code=404, detail="HDMI devices file is empty or corrupted")

        return hdmi_map

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading HDMI map: {str(e)}")


@router_cec.get("/current")
async def get_current_input():
    current_input = load_current_input()
    return {"current_input": current_input}


@router_cec.post("/switch/{device_number}")
async def switch_input(device_number: int):
    try:
        success = _cec_controller.switch_input(device_number)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to switch input")
        save_current_input(device_number)
        return {"message": f"Successfully switched to input {device_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Can't switch HDMI. . . ")


@router_cec.post("/reset")
async def reset_files():
    """Delete both hdmi_devices.json and current_input.json files"""
    deleted_files = []

    try:
        # Delete hdmi_devices.json if it exists
        if os.path.exists(HDMI_DEVICES_FILE):
            os.remove(HDMI_DEVICES_FILE)
            deleted_files.append(HDMI_DEVICES_FILE)

        # Delete current_input.json if it exists
        if os.path.exists(CURRENT_INPUT_FILE):
            os.remove(CURRENT_INPUT_FILE)
            deleted_files.append(CURRENT_INPUT_FILE)

        if deleted_files:
            return {"message": f"Successfully deleted: {', '.join(deleted_files)}"}
        else:
            return {"message": "No files found to delete"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting files: {str(e)}")
