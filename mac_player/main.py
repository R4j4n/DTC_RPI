import sys
from datetime import datetime, time as dtime
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStyle,
    QSystemTrayIcon,
)

import config
from control_panel import ControlPanel
from ffmpeg_processor import ProcessWorker, SAFE_WIDTH, TARGET_WIDTH
from schedule_dialog import ScheduleDialog
from vlc_player import VLCPlayer

WEEKDAY_GROUP = {0, 1, 2, 3}  # Mon-Thu
WEEKEND_GROUP = {4, 5, 6}     # Fri-Sun


def _parse_time(value: str) -> dtime:
    h, m = value.split(":")
    return dtime(int(h), int(m))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = config.load()
        self.worker = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        screen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geom)

        self.video_frame = QFrame(self)
        self.video_frame.setGeometry(0, 0, screen_geom.width(), screen_geom.height())
        self.video_frame.setAutoFillBackground(True)
        palette = self.video_frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("black"))
        self.video_frame.setPalette(palette)

        self._build_tray()
        self.showFullScreen()

        # Attach libVLC only after the native NSView exists on screen.
        self.player = VLCPlayer(self.video_frame)

        # Separate top-level window, not a child widget: VLC's video output
        # is a native NSView that paints over normal Qt sibling widgets
        # regardless of stacking order, so overlapping it would hide these
        # controls. A distinct always-on-top window avoids that entirely.
        # Safe-zone boundary is calibrated against TARGET_WIDTH/HEIGHT, but
        # the real screen geometry may differ (different point scaling,
        # wrong screen picked, etc). Scale the boundary proportionally
        # against the actual screen rect so the panel can never sit outside it.
        safe_ratio = SAFE_WIDTH / TARGET_WIDTH
        panel_x = screen_geom.x() + round(screen_geom.width() * safe_ratio)
        panel_width = screen_geom.width() - round(screen_geom.width() * safe_ratio)

        self.control_panel = ControlPanel()
        self.control_panel.select_video_clicked.connect(self.select_video)
        self.control_panel.schedule_clicked.connect(self.open_schedule_dialog)
        self.control_panel.quit_clicked.connect(QApplication.quit)
        self.control_panel.setGeometry(
            panel_x,
            screen_geom.y(),
            panel_width,
            screen_geom.height(),
        )
        self.control_panel.show()
        self.control_panel.raise_()

        self.scheduler_timer = QTimer(self)
        self.scheduler_timer.timeout.connect(self.evaluate_schedule)
        self.scheduler_timer.start(15_000)
        self.evaluate_schedule(force=True)

        video_path = self.cfg.get("video_path")
        processed_path = self.cfg.get("processed_path")
        if video_path and (not processed_path or not Path(processed_path).exists()):
            self._process_and_store(video_path)
        elif video_path:
            self.control_panel.set_status(f"Loaded: {Path(video_path).name}")

    def _build_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

        menu = QMenu()
        select_action = QAction("Select Video...", self)
        select_action.triggered.connect(self.select_video)
        menu.addAction(select_action)

        schedule_action = QAction("Schedule Settings...", self)
        schedule_action.triggered.connect(self.open_schedule_dialog)
        menu.addAction(schedule_action)

        menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.setToolTip("DTC Mac Player")
        self.tray.show()

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.mov *.mkv *.avi *.m4v)"
        )
        if not path:
            return
        self.cfg["video_path"] = path
        self.cfg["processed_path"] = None
        config.save(self.cfg)
        self._process_and_store(path)

    def _process_and_store(self, path: str):
        self.tray.setToolTip("DTC Mac Player - processing video...")
        self.control_panel.set_status(f"Processing: {Path(path).name}...")
        self.worker = ProcessWorker(path)
        self.worker.finished_ok.connect(self._on_processed)
        self.worker.failed.connect(self._on_process_failed)
        self.worker.start()

    def _on_processed(self, dest_path: str):
        self.cfg["processed_path"] = dest_path
        config.save(self.cfg)
        self.tray.setToolTip("DTC Mac Player")
        self.control_panel.set_status(f"Loaded: {Path(self.cfg['video_path']).name}")
        self.evaluate_schedule(force=True)

    def _on_process_failed(self, message: str):
        self.tray.setToolTip("DTC Mac Player")
        self.control_panel.set_status("Processing failed - see dialog")
        QMessageBox.warning(self, "Processing failed", message)

    def open_schedule_dialog(self):
        dlg = ScheduleDialog(self.cfg, self)
        if dlg.exec():
            self.cfg.update(dlg.result_config())
            config.save(self.cfg)
            self.evaluate_schedule(force=True)

    def _should_play_now(self) -> bool:
        processed_path = self.cfg.get("processed_path")
        if not processed_path or not Path(processed_path).exists():
            return False
        if not self.cfg.get("schedule_enabled", True):
            return True
        now = datetime.now()
        if now.weekday() in WEEKDAY_GROUP:
            start, end = self.cfg["weekday_start"], self.cfg["weekday_end"]
        else:
            start, end = self.cfg["weekend_start"], self.cfg["weekend_end"]
        return _parse_time(start) <= now.time() <= _parse_time(end)

    def evaluate_schedule(self, force: bool = False):
        should_play = self._should_play_now()
        is_playing = self.player.is_playing()
        if should_play and (force or not is_playing):
            self.player.play(self.cfg["processed_path"])
        elif not should_play and (force or is_playing):
            self.player.stop_blank()

        if self.cfg.get("video_path"):
            name = Path(self.cfg["video_path"]).name
            state = "Playing" if should_play else "Blank (outside schedule)"
            self.control_panel.set_status(f"{name}\n{state}")


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()  # noqa: F841 - keeps window alive
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
