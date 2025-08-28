from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import json, os

class AnalyticsPage(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.view = QWebEngineView()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.refresh()

    def _load_html(self, data):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", "html", "analytics.html")
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace("__DATA__", json.dumps(data))
        self.view.setHtml(html)

    def refresh(self):
        data = self.api.analytics_summary(days=30)
        self._load_html(data)
