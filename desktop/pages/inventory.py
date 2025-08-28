from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QSpinBox, QLabel, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
REASONS = ["donation", "issue", "discard", "adjust"]
LOW_STOCK_THRESHOLD = 5


class InventoryPage(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api

        # === Stock table ===
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Blood Group", "Units"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)

        # === Controls ===
        controls = QFrame()
        cl = QHBoxLayout(controls)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)

        self.bg = QComboBox()
        self.bg.addItems(BLOOD_GROUPS)
        self.bg.setToolTip("Blood group")

        self.delta = QSpinBox()
        self.delta.setRange(-100, 100)
        self.delta.setValue(1)
        self.delta.setToolTip("Change in units (+ add / - remove)")

        self.reason = QComboBox()
        self.reason.addItems(REASONS)
        self.reason.setCurrentText("donation")
        self.reason.setToolTip("Reason")

        self.btn_apply = QPushButton("Apply Change")
        self.btn_refresh = QPushButton("Refresh")

        # Quick actions
        self.btn_quick_add = QPushButton("Receive +1 (Donation)")
        self.btn_quick_issue = QPushButton("Issue −1")
        self.btn_quick_discard = QPushButton("Discard −1")

        cl.addWidget(QLabel("Group"))
        cl.addWidget(self.bg)
        cl.addWidget(QLabel("Δ Units"))
        cl.addWidget(self.delta)
        cl.addWidget(QLabel("Reason"))
        cl.addWidget(self.reason)
        cl.addWidget(self.btn_apply)
        cl.addStretch(1)
        cl.addWidget(self.btn_quick_add)
        cl.addWidget(self.btn_quick_issue)
        cl.addWidget(self.btn_quick_discard)
        cl.addWidget(self.btn_refresh)

        # === Root layout ===
        root = QVBoxLayout()
        root.addWidget(controls)
        root.addWidget(self.table)
        self.setLayout(root)

        # Events
        self.btn_apply.clicked.connect(self.apply_change)
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_quick_add.clicked.connect(self.quick_add)
        self.btn_quick_issue.clicked.connect(self.quick_issue)
        self.btn_quick_discard.clicked.connect(self.quick_discard)
        self.table.itemSelectionChanged.connect(self._sync_bg_with_selection)

        self.refresh()

    # ---------- UI helpers ----------

    def _sync_bg_with_selection(self):
        """When a row is selected, sync dropdown blood group to that row."""
        rows = self.table.selectionModel().selectedRows()
        if rows:
            r = rows[0].row()
            group = self.table.item(r, 0).text()
            if group in BLOOD_GROUPS:
                self.bg.setCurrentText(group)

    def _highlight_rows(self):
        """
        Highlight low stock rows using setBackground with QBrush/QColor.
        No use of setBackgroundRole (which doesn't exist on QTableWidgetItem).
        """
        light_row = QBrush(QColor("#fff1f2"))   # very light red
        accent    = QBrush(QColor("#fee2e2"))   # units cell accent
        clear     = QBrush()                    # reset to default / alternating

        for r in range(self.table.rowCount()):
            # Defensive parse of units
            try:
                units = int(self.table.item(r, 1).text())
            except (TypeError, ValueError):
                units = 0

            if units < LOW_STOCK_THRESHOLD:
                # Soft tint entire row
                for c in range(self.table.columnCount()):
                    self.table.item(r, c).setBackground(light_row)
                # Stronger tint just for Units cell
                self.table.item(r, 1).setBackground(accent)
            else:
                # Clear any prior custom backgrounds to restore default/alternating colors
                for c in range(self.table.columnCount()):
                    self.table.item(r, c).setBackground(clear)

    # ---------- Data ops ----------

    def refresh(self):
        stock = self.api.get_stock()
        # Keep the table ordered by standard groups
        order = {bg: i for i, bg in enumerate(BLOOD_GROUPS)}
        stock.sort(key=lambda s: order.get(s["blood_group"], 999))

        self.table.setRowCount(0)
        for s in stock:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(s["blood_group"]))
            self.table.setItem(r, 1, QTableWidgetItem(str(s["units"])))

        self.table.resizeColumnsToContents()
        self._highlight_rows()

    def _apply(self, bg: str, delta: int, reason: str):
        try:
            self.api.adjust_stock(bg, delta, reason)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------- Actions ----------

    def apply_change(self):
        bg = self.bg.currentText()
        delta = int(self.delta.value())
        reason = self.reason.currentText()

        if reason not in REASONS:
            QMessageBox.warning(self, "Invalid reason", "Please pick a valid reason.")
            return
        if delta == 0:
            QMessageBox.information(self, "No change", "Delta must be non-zero.")
            return

        self._apply(bg, delta, reason)

    def quick_add(self):
        group = self._selected_or_dropdown_group()
        self._apply(group, +1, "donation")

    def quick_issue(self):
        group = self._selected_or_dropdown_group()
        self._apply(group, -1, "issue")

    def quick_discard(self):
        group = self._selected_or_dropdown_group()
        self._apply(group, -1, "discard")

    def _selected_or_dropdown_group(self) -> str:
        rows = self.table.selectionModel().selectedRows()
        if rows:
            return self.table.item(rows[0].row(), 0).text()
        return self.bg.currentText()
