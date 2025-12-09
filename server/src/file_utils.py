"""
File utilities for atomic file operations and safe JSON handling.
Prevents corruption of persistent data files.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


def atomic_write_json(file_path: str | Path, data: Dict[str, Any]) -> None:
    """
    Atomically write JSON data to a file to prevent corruption.

    Uses a temporary file and atomic rename to ensure the file is never
    partially written or corrupted if the process is interrupted.

    Args:
        file_path: Path to the JSON file
        data: Dictionary to write as JSON

    Raises:
        OSError: If file operations fail
        TypeError: If data is not JSON serializable
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in the same directory to ensure same filesystem
    temp_fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=f".{file_path.name}.",
        suffix=".tmp"
    )

    try:
        # Write JSON to temporary file
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk

        # Atomic rename (POSIX guarantees atomicity)
        os.replace(temp_path, file_path)

    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def safe_read_json(file_path: str | Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Safely read JSON file with fallback to default value.

    Args:
        file_path: Path to the JSON file
        default: Default value if file doesn't exist or is corrupted

    Returns:
        Parsed JSON data or default value
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return default if default is not None else {}

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        # Log error but return default instead of crashing
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to read JSON from {file_path}: {e}")

        # Backup corrupted file
        backup_path = file_path.with_suffix(f"{file_path.suffix}.corrupted")
        try:
            file_path.rename(backup_path)
            logger.info(f"Moved corrupted file to {backup_path}")
        except OSError:
            pass

        return default if default is not None else {}
