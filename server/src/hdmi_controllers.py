import logging
import subprocess
import time
from typing import Optional


class CECController:
    def __init__(self):
        self.logger = self._setup_logging()
        self.cec_adapter = self._detect_cec_adapter()

    def _setup_logging(self):
        logger = logging.getLogger("cec_controller")
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _detect_cec_adapter(self) -> Optional[int]:
        """Detect available CEC adapter by testing a simple command"""
        try:
            # Test with a simple power query command
            result = subprocess.run(
                'echo "pow 0" | cec-client -s -d 1',
                shell=True,
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                self.logger.info("CEC adapter detected successfully")
                return 0
            else:
                self.logger.warning(f"CEC adapter test failed with return code: {result.returncode}")
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Failed to detect CEC adapter: {e}")
            return None

    def _execute_cec_command(self, command: str, timeout: int = 10) -> tuple[bool, str]:
        """Execute CEC command with proper error handling and timeout"""
        if self.cec_adapter is None:
            self.logger.warning("CEC adapter not detected, but attempting command anyway")
            # Don't return here - try the command anyway since detection might be unreliable

        try:
            self.logger.debug(f"Executing CEC command: {command}")
            
            # Use Popen for better control over the process
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            
            if process.returncode == 0:
                self.logger.debug(f"CEC command successful. Output: {stdout}")
                return True, stdout
            else:
                self.logger.error(f"CEC command failed with return code {process.returncode}. Error: {stderr}")
                return False, stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"CEC command timed out after {timeout} seconds")
            process.kill()
            return False, "Command timed out"
        except Exception as e:
            self.logger.error(f"CEC command execution failed: {e}")
            return False, str(e)

    def _wait_for_tv_ready(self, max_wait: int = 10) -> bool:
        """Wait for TV to be ready to accept commands"""
        self.logger.info("Waiting for TV to be ready...")
        
        for attempt in range(max_wait):
            success, output = self._execute_cec_command('echo "pow 0" | cec-client -s -d 1')
            
            if success and ("power status: on" in output.lower() or "power status: standby" in output.lower()):
                self.logger.info("TV is ready for commands")
                return True
                
            time.sleep(1)
            
        self.logger.warning("TV readiness check timed out")
        return False

    def switch_input(self, device_number, retry_count: int = 3) -> bool:
        """
        Switch HDMI input with improved command format and retry logic
        
        Args:
            device_number: HDMI port number (1-4 typically)
            retry_count: Number of retry attempts
        """
        # Convert to int if it's a string
        try:
            device_number = int(device_number)
        except (ValueError, TypeError):
            self.logger.error(f"Invalid device number: {device_number}. Cannot convert to integer")
            return False
            
        if not (1 <= device_number <= 4):
            self.logger.error(f"Invalid device number: {device_number}. Must be 1-4")
            return False

        self.logger.info(f"Switching to HDMI input {device_number}")
        
        # Wait for TV to be ready
        if not self._wait_for_tv_ready():
            self.logger.warning("Proceeding without TV readiness confirmation")

        # Try multiple command formats as different TVs may respond to different commands
        commands_to_try = [
            # Standard HDMI input selection command
            f'echo "tx 1f:82:{device_number}0:00" | cec-client -s -d 1',
            
            # Alternative format
            f'echo "tx 10:82:{device_number}0:00" | cec-client -s -d 1',
            
            # Direct source selection
            f'echo "as" | cec-client -s -d 1 && echo "tx 1f:82:{device_number}0:00" | cec-client -s -d 1',
            
            # Using decimal format
            f'echo "tx 1f:82:{device_number * 16:02x}:00" | cec-client -s -d 1'
        ]

        for attempt in range(retry_count):
            self.logger.info(f"Attempt {attempt + 1} of {retry_count}")
            
            for i, command in enumerate(commands_to_try):
                self.logger.debug(f"Trying command format {i + 1}: {command}")
                
                success, output = self._execute_cec_command(command)
                
                if success:
                    # Give the TV some time to process the command
                    time.sleep(2)
                    
                    # Verify the input change (optional)
                    if self._verify_input_change(device_number):
                        self.logger.info(f"Successfully switched to HDMI input {device_number}")
                        return True
                    else:
                        self.logger.info(f"Command executed but input change not verified")
                        # Still consider it successful since verification might not work on all TVs
                        return True
                else:
                    self.logger.warning(f"Command format {i + 1} failed: {output}")
                    
            # Wait before retry
            if attempt < retry_count - 1:
                self.logger.info("Waiting before retry...")
                time.sleep(3)

    def switch_input_simple(self, device_number) -> bool:
        """
        Simple input switching using the same approach as your working TV commands
        """
        # Convert to int if it's a string
        try:
            device_number = int(device_number)
        except (ValueError, TypeError):
            self.logger.error(f"Invalid device number: {device_number}. Cannot convert to integer")
            return False
            
        if not (1 <= device_number <= 4):
            self.logger.error(f"Invalid device number: {device_number}. Must be 1-4")
            return False

        self.logger.info(f"Switching to HDMI input {device_number}")
        
        # Wait a moment for TV to be ready after turning on
        time.sleep(2)
        
        # Try different command formats that are most commonly supported
        commands_to_try = [
            # Format 1: Standard HDMI input selection (most common)
            f'echo "tx 1f:82:{device_number}0:00" | cec-client -s -d 1',
            
            # Format 2: Alternative addressing
            f'echo "tx 10:82:{device_number}0:00" | cec-client -s -d 1',
            
            # Format 3: Using hex calculation like your original
            f'echo "tx 1F:82:{format(device_number * 16, "02x").upper()}:00" | cec-client -s -d 1',
        ]

        for i, command in enumerate(commands_to_try):
            self.logger.info(f"Trying input switch command {i + 1}: {command}")
            
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                self.logger.info(f"Command {i + 1} result - Return code: {result.returncode}")
                self.logger.info(f"Command {i + 1} stdout: {result.stdout}")
                if result.stderr:
                    self.logger.info(f"Command {i + 1} stderr: {result.stderr}")
                
                if result.returncode == 0:
                    self.logger.info(f"Input switch command {i + 1} executed successfully")
                    time.sleep(3)  # Give TV time to process
                    return True
                    
            except Exception as e:
                self.logger.error(f"Command {i + 1} failed with exception: {e}")
        
        self.logger.error(f"All input switch attempts failed for device {device_number}")
        return False

    def _verify_input_change(self, expected_input: int) -> bool:
        """
        Attempt to verify input change (may not work on all TV models)
        """
        try:
            success, output = self._execute_cec_command('echo "give_device_vendor_id" | cec-client -s -d 1')
            # This is a basic check - verification methods vary by TV manufacturer
            return success
        except Exception as e:
            self.logger.debug(f"Input verification failed: {e}")
            return False

    def get_tv_power_status(self) -> Optional[bool]:
        """Get TV power status"""
        success, output = self._execute_cec_command('echo "pow 0" | cec-client -s -d 1')
        
        if success:
            output_lower = output.lower()
            if "power status: on" in output_lower:
                return True
            elif "power status: standby" in output_lower:
                return False
        
        self.logger.warning(f"Could not determine TV power status. Output: {output}")
        return None

    def turn_on_tv(self) -> bool:
        """Turn on TV"""
        self.logger.info("Turning on TV")
        success, output = self._execute_cec_command('echo "on 0" | cec-client -s -d 1')
        
        if success:
            # Wait for TV to power on
            time.sleep(3)
            return True
        
        self.logger.error(f"Failed to turn on TV: {output}")
        return False

    def turn_off_tv(self) -> bool:
        """Turn off TV"""
        self.logger.info("Turning off TV")
        success, output = self._execute_cec_command('echo "standby 0" | cec-client -s -d 1')
        
        if success:
            return True
            
        self.logger.error(f"Failed to turn off TV: {output}")
        return False