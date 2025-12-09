import json
import os
import subprocess
import threading
import time
from datetime import datetime
from typing import Optional

import schedule

from src.routers.tv_controller import DaySchedule, WeeklySchedule

SCHEDULE_FILE = "schedule.json"

from src.hdmi_controllers import CECController
from src.routers.inputs_switch import load_current_input
from src.video_manager import video_manager
from src.file_utils import atomic_write_json, safe_read_json


class TVController:
    def __init__(self):
        self.current_schedule = self.load_schedule() or WeeklySchedule()
        print(self.current_schedule)
        self.start_scheduler()
        self.apply_schedule()

    def turn_on_tv(self):
        switch_handler = CECController()
        current_device = load_current_input()
        print(f"Turning on TV at {datetime.now()}")

        # Turn on TV using subprocess instead of os.system
        try:
            result = subprocess.run(
                ["bash", "-c", 'echo "on 0" | cec-client -s -d 1'],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"TV turn on command result: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("TV turn on command timed out")
            result = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="Timeout")
        except Exception as e:
            print(f"Error turning on TV: {e}")
            result = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=str(e))

        # Wait a moment for TV to be ready
        time.sleep(3)

        # Try to switch input using the improved method
        if current_device == 0:
            print("No HDMI device mapping set.")
        else:
            try:
                success = switch_handler.switch_input_simple(device_number=current_device)
                if success:
                    print(f"Successfully switched to HDMI {current_device}")
                else:
                    print(f"Failed to switch to HDMI {current_device}")
            except Exception as e:
                print(f"Exception switching to HDMI {current_device}: {e}")

        # Play the last played content
        video_manager.load_last_played()
        return result.returncode

    def turn_off_tv(self):
        print(f"Turning off TV at {datetime.now()}")

        # Stop the item which is being currently played
        try:
            video_manager.stop()
        except Exception as e:
            print(f"Error stopping video: {e}")

        # Turn off TV using subprocess instead of os.system
        try:
            result = subprocess.run(
                ["bash", "-c", 'echo "standby 0" | cec-client -s -d 1'],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"TV turn off command result: {result.returncode}")
            return result.returncode
        except subprocess.TimeoutExpired:
            print("TV turn off command timed out")
            return 1
        except Exception as e:
            print(f"Error turning off TV: {e}")
            return 1

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds

    def start_scheduler(self):
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()

    def should_run_today(self, day_tag: str) -> bool:
        current_day = datetime.now().strftime("%A").lower()
        return current_day == day_tag

    def schedule_day(self, day: str, times: DaySchedule):
        if times and (times.turn_on_time or times.turn_off_time):
            # Clear existing schedules for this day
            schedule.clear(day)

            if times.turn_on_time:
                # Fix lambda variable capture bug by using default argument
                schedule.every().day.at(times.turn_on_time).do(
                    lambda day_tag=day: self.turn_on_tv() if self.should_run_today(day_tag) else None
                ).tag(day)

            if times.turn_off_time:
                # Fix lambda variable capture bug by using default argument
                schedule.every().day.at(times.turn_off_time).do(
                    lambda day_tag=day: self.turn_off_tv() if self.should_run_today(day_tag) else None
                ).tag(day)

    def apply_schedule(self):
        schedule_dict = self.current_schedule.model_dump()
        for day, times in schedule_dict.items():
            if times:
                self.schedule_day(day, DaySchedule(**times))

    def save_schedule(self):
        atomic_write_json(SCHEDULE_FILE, self.current_schedule.model_dump())

    def load_schedule(self) -> Optional[WeeklySchedule]:
        try:
            schedule_data = safe_read_json(SCHEDULE_FILE, default=None)
            if schedule_data:
                return WeeklySchedule(**schedule_data)
        except Exception as e:
            print(f"Error loading schedule: {e}")
        return None

    def get_tv_status(self) -> bool:
        """
        Query the TV power status using cec-client.
        Returns True if TV is on, False if TV is off/standby.
        """
        try:
            result = subprocess.run(
                ["bash", "-c", 'echo "pow 0" | cec-client -s -d 1'],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout.lower()
            if "power status: on" in output:
                return True
            elif "power status: standby" in output:
                return False
            else:
                print(f"Unexpected power status response: {result.stdout}")
                return False
        except subprocess.TimeoutExpired:
            print("TV status query timed out")
            return False
        except Exception as e:
            print(f"Error getting TV status: {e}")
            return False
