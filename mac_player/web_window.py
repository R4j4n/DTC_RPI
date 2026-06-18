import sys

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from ffmpeg_processor import SAFE_HEIGHT, SAFE_WIDTH

URL = "https://www.google.com"


class QuitPanel(QWidget):
    """Separate top-level always-on-top window, not a child widget of the
    web view's window: QWebEngineView's Chromium compositor uses a native
    surface that can paint over sibling Qt widgets regardless of stacking
    order, same issue as VLC's video output in the main player app."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setStyleSheet("background-color: #1c1c1c;")

        quit_btn = QPushButton("Quit")
        quit_btn.setMinimumHeight(48)
        quit_btn.setStyleSheet(
            "QPushButton { background-color: #3a3a3a; color: white; font-size: 14px; padding: 8px; }"
            "QPushButton:hover { background-color: #505050; }"
        )
        quit_btn.clicked.connect(QApplication.quit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.addWidget(quit_btn)
        layout.addStretch()


class WebWindow(QMainWindow):
    """Same frameless/always-on-top/safe-zone pattern as the video player's
    MainWindow, but showing an embedded Chromium view instead of VLC. Being
    frameless means there are no close/minimize buttons to begin with -
    nothing to lock down, unlike a real Chrome window."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        screen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geom)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("black"))
        self.setPalette(palette)

        # Exact pixel size on the real 1920x1080 target - not proportionally
        # scaled, so it is always precisely SAFE_WIDTH x SAFE_HEIGHT there.
        web_width = SAFE_WIDTH
        web_height = SAFE_HEIGHT

        self.web_view = QWebEngineView(self)
        self.web_view.setGeometry(0, 0, web_width, web_height)
        self.web_view.setUrl(QUrl(URL))

        # show(), not showFullScreen(): native fullscreen on macOS opens a
        # new Space. The window is already frameless and sized to the full
        # screen geometry, so a plain show() looks identical without that.
        self.show()

        self.quit_panel = QuitPanel()
        self.quit_panel.setGeometry(
            screen_geom.x() + web_width,
            screen_geom.y(),
            screen_geom.width() - web_width,
            screen_geom.height(),
        )
        self.quit_panel.show()
        self.quit_panel.raise_()


def main():
    QApplication.setApplicationName("DTC Chrome Kiosk")
    QApplication.setOrganizationName("DTC")  # keeps QtWebEngine's persistent
    # storage (cookies/login session) at a stable path across launches.
    app = QApplication(sys.argv)
    window = WebWindow()  # noqa: F841 - keeps window alive
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
