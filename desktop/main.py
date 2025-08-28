import os, sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QStackedWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from .api import ApiClient
from .pages.login import LoginPage
from .pages.dashboard import DashboardPage
from .pages.donors import DonorsPage
from .pages.inventory import InventoryPage
from .pages.analytics import AnalyticsPage
from .pages.settings import SettingsPage

def load_styles(app):
    qss_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = ApiClient()
        self.setWindowTitle("Hospital Blood Desk")
        self.resize(1100, 700)

        self.stack = QStackedWidget()
        self.login = LoginPage(self.api, self._on_login_success)
        self.stack.addWidget(self.login)
        self.setCentralWidget(self.stack)

    def _on_login_success(self, user):
        # Build main app UI
        shell = QWidget()
        root = QHBoxLayout()
        shell.setLayout(root)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItem("Dashboard")
        self.sidebar.addItem("Donors")
        self.sidebar.addItem("Inventory")
        self.sidebar.addItem("Analytics")
        self.sidebar.addItem("Settings")
        self.sidebar.setMaximumWidth(180)
        self.sidebar.currentRowChanged.connect(self.stack_pages)

        # Pages
        self.pages = QStackedWidget()
        self.page_dashboard = DashboardPage(self.api)
        self.page_donors = DonorsPage(self.api)
        self.page_inventory = InventoryPage(self.api)
        self.page_analytics = AnalyticsPage(self.api)
        self.page_settings = SettingsPage(self.api)

        for p in [self.page_dashboard, self.page_donors, self.page_inventory, self.page_analytics, self.page_settings]:
            self.pages.addWidget(p)

        root.addWidget(self.sidebar)
        root.addWidget(self.pages, 1)

        self.stack.addWidget(shell)
        self.stack.setCurrentWidget(shell)
        self.sidebar.setCurrentRow(0)

    def stack_pages(self, index):
        self.pages.setCurrentIndex(index)
        # Refresh page data when switching
        try:
            page = self.pages.currentWidget()
            if hasattr(page, "refresh"):
                page.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Refresh failed", str(e))

def main():
    app = QApplication(sys.argv)
    load_styles(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
