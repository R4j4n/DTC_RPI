"""
Wristband Schedule Manager for Trampoline Park
Manages the rotating color schedule for jump times
"""
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WristbandSlot:
    """Represents a single wristband time slot"""
    time: time
    color: str
    hex_color: str


class WristbandScheduleManager:
    """Manages the trampoline park wristband rotation schedule"""

    # Define the schedule with actual hex colors for each wristband
    SCHEDULE = [
        {"time": "10:30", "color": "pink", "hex": "#FF69B4"},
        {"time": "10:45", "color": "yellow", "hex": "#FFD700"},
        {"time": "11:00", "color": "orange", "hex": "#FF8C00"},
        {"time": "11:15", "color": "green", "hex": "#26f434"},
        {"time": "11:30", "color": "aqua", "hex": "#00FFFF"},
        {"time": "11:45", "color": "silver", "hex": "#C0C0C0"},
        {"time": "12:00", "color": "brown", "hex": "#8B4513"},
        {"time": "12:15", "color": "blue", "hex": "#1E90FF"},
        {"time": "12:30", "color": "red", "hex": "#ff1152"},
        {"time": "12:45", "color": "pink", "hex": "#FF69B4"},
        {"time": "13:00", "color": "yellow", "hex": "#FFD700"},
        {"time": "13:15", "color": "orange", "hex": "#FF8C00"},
        {"time": "13:30", "color": "green", "hex": "#26f434"},
        {"time": "13:45", "color": "aqua", "hex": "#00FFFF"},
        {"time": "14:00", "color": "silver", "hex": "#C0C0C0"},
        {"time": "14:15", "color": "brown", "hex": "#8B4513"},
        {"time": "14:30", "color": "blue", "hex": "#1E90FF"},
        {"time": "14:45", "color": "red", "hex": "#ff1152"},
        {"time": "15:00", "color": "pink", "hex": "#FF69B4"},
        {"time": "15:15", "color": "yellow", "hex": "#FFD700"},
        {"time": "15:30", "color": "orange", "hex": "#FF8C00"},
        {"time": "15:45", "color": "green", "hex": "#26f434"},
        {"time": "16:00", "color": "aqua", "hex": "#00FFFF"},
        {"time": "16:15", "color": "silver", "hex": "#C0C0C0"},
        {"time": "16:30", "color": "brown", "hex": "#8B4513"},
        {"time": "16:45", "color": "blue", "hex": "#1E90FF"},
        {"time": "17:00", "color": "red", "hex": "#ff1152"},
        {"time": "17:15", "color": "pink", "hex": "#FF69B4"},
        {"time": "17:30", "color": "yellow", "hex": "#FFD700"},
        {"time": "17:45", "color": "orange", "hex": "#FF8C00"},
        {"time": "18:00", "color": "green", "hex": "#26f434"},
        {"time": "18:15", "color": "aqua", "hex": "#00FFFF"},
        {"time": "18:30", "color": "silver", "hex": "#C0C0C0"},
        {"time": "18:45", "color": "brown", "hex": "#8B4513"},
        {"time": "19:00", "color": "blue", "hex": "#1E90FF"},
        {"time": "19:15", "color": "red", "hex": "#ff1152"},
        {"time": "19:30", "color": "pink", "hex": "#FF69B4"},
        {"time": "19:45", "color": "yellow", "hex": "#FFD700"},
        {"time": "20:00", "color": "orange", "hex": "#FF8C00"},
        {"time": "20:15", "color": "green", "hex": "#26f434"},
        {"time": "20:30", "color": "aqua", "hex": "#00FFFF"},
        {"time": "20:45", "color": "silver", "hex": "#C0C0C0"},
        {"time": "21:00", "color": "brown", "hex": "#8B4513"},
        {"time": "21:15", "color": "blue", "hex": "#1E90FF"},
        {"time": "21:30", "color": "red", "hex": "#ff1152"},
        {"time": "21:45", "color": "pink", "hex": "#FF69B4"},
        {"time": "22:00", "color": "yellow", "hex": "#FFD700"},
    ]

    def __init__(self):
        """Initialize the schedule manager"""
        self.slots = self._parse_schedule()
        logger.info(f"Wristband schedule initialized with {len(self.slots)} time slots")

    def _parse_schedule(self) -> List[WristbandSlot]:
        """Parse the schedule into WristbandSlot objects"""
        slots = []
        for entry in self.SCHEDULE:
            time_obj = datetime.strptime(entry["time"], "%H:%M").time()
            slot = WristbandSlot(
                time=time_obj,
                color=entry["color"],
                hex_color=entry["hex"]
            )
            slots.append(slot)
        return slots

    def get_current_slot(self, current_time: Optional[datetime] = None) -> Optional[WristbandSlot]:
        """
        Get the current active wristband slot
        Returns the slot that is currently active based on the time
        """
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()

        # Find the most recent slot that has passed
        active_slot = None
        for slot in self.slots:
            if slot.time <= current_time_only:
                active_slot = slot
            else:
                break

        # If no slot has started yet today, return None or the last slot from previous day
        if active_slot is None and len(self.slots) > 0:
            # Before first slot of the day
            return None

        return active_slot

    def get_previous_slots(self, count: int = 3, current_time: Optional[datetime] = None) -> List[WristbandSlot]:
        """
        Get the previous N wristband slots (excluding current)
        """
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()

        # Find current slot index
        current_index = None
        for i, slot in enumerate(self.slots):
            if slot.time <= current_time_only:
                current_index = i
            else:
                break

        if current_index is None or current_index == 0:
            return []

        # Get previous slots
        start_index = max(0, current_index - count)
        return self.slots[start_index:current_index]

    def get_upcoming_slots(self, count: int = 3, current_time: Optional[datetime] = None) -> List[Dict]:
        """
        Get the next N upcoming wristband slots with countdown
        Returns slots with time remaining until each slot starts
        """
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()

        # Find next slots
        upcoming = []
        for slot in self.slots:
            if slot.time > current_time_only:
                # Calculate time until slot
                slot_datetime = datetime.combine(current_time.date(), slot.time)
                time_until = slot_datetime - current_time

                upcoming.append({
                    "time": slot.time.strftime("%H:%M"),
                    "color": slot.color,
                    "hex_color": slot.hex_color,
                    "seconds_until": int(time_until.total_seconds()),
                    "countdown": self._format_countdown(time_until)
                })

                if len(upcoming) >= count:
                    break

        return upcoming

    def _format_countdown(self, time_delta: timedelta) -> str:
        """Format time delta as MM:SS"""
        total_seconds = int(time_delta.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_schedule_status(self, current_time: Optional[datetime] = None) -> Dict:
        """
        Get comprehensive schedule status including current, previous, and upcoming slots
        """
        if current_time is None:
            current_time = datetime.now()

        current = self.get_current_slot(current_time)
        previous = self.get_previous_slots(3, current_time)
        upcoming = self.get_upcoming_slots(3, current_time)

        # Calculate time remaining in current slot
        current_slot_info = None
        if current:
            # Find next slot to calculate time remaining
            current_time_only = current_time.time()
            next_slot_time = None
            for slot in self.slots:
                if slot.time > current_time_only:
                    next_slot_time = slot.time
                    break

            if next_slot_time:
                next_slot_datetime = datetime.combine(current_time.date(), next_slot_time)
                time_remaining = next_slot_datetime - current_time

                current_slot_info = {
                    "time": current.time.strftime("%H:%M"),
                    "color": current.color,
                    "hex_color": current.hex_color,
                    "seconds_remaining": int(time_remaining.total_seconds()),
                    "countdown": self._format_countdown(time_remaining)
                }

        return {
            "current_time": current_time.strftime("%H:%M:%S"),
            "current_slot": current_slot_info,
            "previous_slots": [
                {
                    "time": slot.time.strftime("%H:%M"),
                    "color": slot.color,
                    "hex_color": slot.hex_color
                }
                for slot in previous
            ],
            "upcoming_slots": upcoming
        }

    def get_full_schedule(self) -> List[Dict]:
        """Get the complete schedule for display/configuration purposes"""
        return [
            {
                "time": slot.time.strftime("%H:%M"),
                "color": slot.color,
                "hex_color": slot.hex_color
            }
            for slot in self.slots
        ]


# Create global schedule manager instance
wristband_schedule_manager = WristbandScheduleManager()
