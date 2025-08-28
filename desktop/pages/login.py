from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from ..api import ApiClient

class LoginPage(QWidget):
    def __init__(self, api: ApiClient, on_success):
        super().__init__()
        self.api = api
        self.on_success = on_success

        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("Hospital Blood Desk")
        title.setStyleSheet("font-size: 28px; font-weight: 800;")
        subtitle = QLabel("Manage donors & stock securely. Login below.")
        subtitle.setStyleSheet("color: #475569;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")

        self.btn = QPushButton("Login")
        self.btn.clicked.connect(self._login)

        layout.addWidget(title, 0, Qt.AlignHCenter)
        layout.addWidget(subtitle, 0, Qt.AlignHCenter)
        layout.addSpacing(8)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def _login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        try:
            user = self.api.login(u, p)
            self.on_success(user)
        except Exception as e:
            QMessageBox.critical(self, "Login failed", str(e))
