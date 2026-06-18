import subprocess
import sys
import time

from ffmpeg_processor import SAFE_HEIGHT, SAFE_WIDTH

WIDTH, HEIGHT = SAFE_WIDTH, SAFE_HEIGHT
POLL_SECONDS = 1


def launch_chrome(url: str | None):
    args = [
        "open", "-na", "Google Chrome", "--args",
        "--new-window",
        "--window-position=0,0",
        f"--window-size={WIDTH},{HEIGHT}",
    ]
    if url:
        args.append(url)
    subprocess.run(args, check=True)


def _set_bounds(left, top, right, bottom):
    script = (
        f'tell application "Google Chrome" to set bounds of window 1 '
        f"to {{{left}, {top}, {right}, {bottom}}}"
    )
    subprocess.run(["osascript", "-e", script], capture_output=True)


def _get_bounds():
    result = subprocess.run(
        ["osascript", "-e", 'tell application "Google Chrome" to get bounds of window 1'],
        capture_output=True, text=True,
    )
    return [int(p.strip()) for p in result.stdout.strip().split(",")]


def determine_target_bounds():
    # A normal titled window can't have its top edge above the menu bar -
    # macOS clamps it. Request the ideal top-left rect, then read back what
    # was actually applied; that becomes the enforced target, so the real
    # menu bar height never needs to be hardcoded per machine.
    _set_bounds(0, 0, WIDTH, HEIGHT)
    time.sleep(0.3)
    return _get_bounds()


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else None
    launch_chrome(url)
    time.sleep(2)
    target = determine_target_bounds()
    while True:
        _set_bounds(*target)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
