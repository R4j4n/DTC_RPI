from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

_BUTTON_STYLE = (
    "QPushButton { background-color: #3a3a3a; color: white; font-size: 14px; padding: 8px; }"
    "QPushButton:hover { background-color: #505050; }"
)


class ControlPanel(QWidget):
    """Always-on-top control surface meant to sit in the dead/cracked
    column of the screen, never overlapping the video output window."""

    select_video_clicked = pyqtSignal()
    schedule_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setStyleSheet("background-color: #1c1c1c;")

        title = QLabel("Controls")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        self.status_label = QLabel("No video selected")
        self.status_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        self.status_label.setWordWrap(True)

        select_btn = QPushButton("Select Video")
        schedule_btn = QPushButton("Schedule Settings")
        quit_btn = QPushButton("Quit")
        for btn in (select_btn, schedule_btn, quit_btn):
            btn.setMinimumHeight(48)
            btn.setStyleSheet(_BUTTON_STYLE)

        select_btn.clicked.connect(self.select_video_clicked.emit)
        schedule_btn.clicked.connect(self.schedule_clicked.emit)
        quit_btn.clicked.connect(self.quit_clicked.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(select_btn)
        layout.addWidget(schedule_btn)
        layout.addWidget(quit_btn)
        layout.addStretch()
        layout.addWidget(self.status_label)

    def set_status(self, text: str):
        self.status_label.setText(text)
