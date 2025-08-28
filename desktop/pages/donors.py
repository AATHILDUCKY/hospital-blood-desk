from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QDialog, QLabel, QTextEdit, QSpinBox, QDateEdit, QMessageBox
from PyQt5.QtCore import Qt, QDate
from datetime import date

BLOOD_GROUPS = ["O+","O-","A+","A-","B+","B-","AB+","AB-"]

class DonorDialog(QDialog):
    def __init__(self, api, donor=None, parent=None):
        super().__init__(parent)
        self.api = api
        self.donor = donor
        self.setWindowTitle("Donor Profile")
        self.resize(420, 520)

        layout = QVBoxLayout()

        self.name = QLineEdit(); self.name.setPlaceholderText("Full name")
        self.nic = QLineEdit(); self.nic.setPlaceholderText("NIC/ID (optional)")
        self.phone = QLineEdit(); self.phone.setPlaceholderText("Phone")
        self.email = QLineEdit(); self.email.setPlaceholderText("Email")
        self.address = QLineEdit(); self.address.setPlaceholderText("Address")
        self.area = QLineEdit(); self.area.setPlaceholderText("Area")
        self.bg = QComboBox(); self.bg.addItems(BLOOD_GROUPS)
        self.age = QSpinBox(); self.age.setRange(16, 80); self.age.setValue(25)
        self.last = QDateEdit(); self.last.setCalendarPopup(True); self.last.setDate(QDate.currentDate()); self.last.setDisplayFormat("yyyy-MM-dd")
        self.notes = QTextEdit(); self.notes.setPlaceholderText("Notes")
        self.save = QPushButton("Save")

        for w in [self.name, self.nic, self.phone, self.email, self.address, self.area, self.bg, self.age, self.last, self.notes, self.save]:
            layout.addWidget(w)

        if donor:
            self.name.setText(donor.get("name",""))
            self.nic.setText(donor.get("nic","") or "")
            self.phone.setText(donor.get("phone","") or "")
            self.email.setText(donor.get("email","") or "")
            self.address.setText(donor.get("address","") or "")
            self.area.setText(donor.get("area","") or "")
            self.bg.setCurrentText(donor.get("blood_group","O+"))
            if donor.get("age"): self.age.setValue(int(donor["age"]))
            if donor.get("last_donation_date"):
                y,m,d = map(int, donor["last_donation_date"].split("-"))
                self.last.setDate(QDate(y,m,d))
            self.notes.setText(donor.get("notes","") or "")
        self.save.clicked.connect(self._save)
        self.setLayout(layout)

    def _save(self):
        payload = {
            "name": self.name.text().strip(),
            "nic": self.nic.text().strip() or None,
            "phone": self.phone.text().strip() or None,
            "email": self.email.text().strip() or None,
            "address": self.address.text().strip() or None,
            "area": self.area.text().strip() or None,
            "blood_group": self.bg.currentText(),
            "age": int(self.age.value()),
            "last_donation_date": self.last.date().toString("yyyy-MM-dd"),
            "notes": self.notes.toPlainText().strip() or None,
            "active": True,
        }
        try:
            if self.donor:
                self.api.update_donor(self.donor["id"], payload)
            else:
                self.api.create_donor(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class DonorsPage(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID","Name","Blood Group","Area","Phone","Last Donation"])
        self.table.cellDoubleClicked.connect(self.open_profile)

        self.search = QLineEdit(); self.search.setPlaceholderText("Search name/phone/email/area")
        self.bg = QComboBox(); self.bg.addItem("Any"); self.bg.addItems(BLOOD_GROUPS)
        self.btn_filter = QPushButton("Filter")
        self.btn_new = QPushButton("Add Donor")

        hl = QHBoxLayout()
        hl.addWidget(self.search); hl.addWidget(self.bg); hl.addWidget(self.btn_filter); hl.addStretch(); hl.addWidget(self.btn_new)

        layout = QVBoxLayout()
        layout.addLayout(hl)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.btn_filter.clicked.connect(self.apply_filter)
        self.btn_new.clicked.connect(self.add_new)

        self.refresh()

    def populate(self, donors):
        self.table.setRowCount(0)
        for d in donors:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(d["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(d["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(d["blood_group"]))
            self.table.setItem(r, 3, QTableWidgetItem(d.get("area","") or ""))
            self.table.setItem(r, 4, QTableWidgetItem(d.get("phone","") or ""))
            self.table.setItem(r, 5, QTableWidgetItem(d.get("last_donation_date","") or ""))
        self.table.resizeColumnsToContents()

    def refresh(self):
        donors = self.api.list_donors()
        self.populate(donors)

    def apply_filter(self):
        params = {}
        if self.search.text().strip():
            params["q"] = self.search.text().strip()
        if self.bg.currentText() != "Any":
            params["blood_group"] = self.bg.currentText()
        donors = self.api.search_donors(params)
        self.populate(donors)

    def add_new(self):
        dlg = DonorDialog(self.api, None, self)
        if dlg.exec_():
            self.refresh()

    def open_profile(self, row, col):
        donor_id = int(self.table.item(row, 0).text())
        donor = self.api.get_donor(donor_id)
        dlg = DonorDialog(self.api, donor, self)
        if dlg.exec_():
            self.refresh()
