from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel

class SettingsPage(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        layout = QVBoxLayout()
        self.btn_export = QPushButton("Export Donors to CSV")
        self.status = QLabel("")
        layout.addWidget(self.btn_export)
        layout.addWidget(self.status)
        layout.addStretch()
        self.setLayout(layout)

        self.btn_export.clicked.connect(self.export_csv)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save donors CSV", "donors.csv", "CSV Files (*.csv)")
        if not path:
            return
        file = self.api.export_donors_csv(path)
        self.status.setText(f"Exported to {file}")
