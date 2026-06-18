from PyQt6.QtCore import QTime
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QTimeEdit,
    QVBoxLayout,
)


class ScheduleDialog(QDialog):
    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Schedule Settings")

        self.enabled_box = QCheckBox("Enable schedule (uncheck to loop 24/7)")
        self.enabled_box.setChecked(cfg["schedule_enabled"])

        self.weekday_start = self._time_edit(cfg["weekday_start"])
        self.weekday_end = self._time_edit(cfg["weekday_end"])
        self.weekend_start = self._time_edit(cfg["weekend_start"])
        self.weekend_end = self._time_edit(cfg["weekend_end"])

        form = QFormLayout()
        form.addRow("Mon-Thu start", self.weekday_start)
        form.addRow("Mon-Thu stop", self.weekday_end)
        form.addRow("Fri-Sun start", self.weekend_start)
        form.addRow("Fri-Sun stop", self.weekend_end)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.enabled_box)
        layout.addLayout(form)
        layout.addWidget(buttons)

    @staticmethod
    def _time_edit(value: str) -> QTimeEdit:
        edit = QTimeEdit(QTime.fromString(value, "HH:mm"))
        edit.setDisplayFormat("HH:mm")
        return edit

    def result_config(self) -> dict:
        return {
            "schedule_enabled": self.enabled_box.isChecked(),
            "weekday_start": self.weekday_start.time().toString("HH:mm"),
            "weekday_end": self.weekday_end.time().toString("HH:mm"),
            "weekend_start": self.weekend_start.time().toString("HH:mm"),
            "weekend_end": self.weekend_end.time().toString("HH:mm"),
        }
