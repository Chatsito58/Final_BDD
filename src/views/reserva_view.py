from pathlib import Path
from PyQt5 import QtWidgets, uic
from mysql.connector import Error

from ..db_manager import DBManager


class ReservaView(QtWidgets.QWidget):
    """Widget to manage reservations for a single client."""

    def __init__(self, client_id: int, parent=None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve().parents[2] / 'ui' / 'reserva_view.ui'
        uic.loadUi(ui_path, self)

        self.client_id = client_id
        self.db_manager = DBManager()

        # Widgets
        self.vehicle_combo = self.findChild(QtWidgets.QComboBox, 'vehicleComboBox')
        self.start_date = self.findChild(QtWidgets.QDateEdit, 'startDateEdit')
        self.end_date = self.findChild(QtWidgets.QDateEdit, 'endDateEdit')
        self.insurance_checkbox = self.findChild(QtWidgets.QCheckBox, 'insuranceCheckBox')
        self.table = self.findChild(QtWidgets.QTableWidget, 'reservationsTable')
        self.new_btn = self.findChild(QtWidgets.QPushButton, 'nuevaReservaButton')
        self.cancel_btn = self.findChild(QtWidgets.QPushButton, 'cancelReservaButton')

        if self.new_btn:
            self.new_btn.clicked.connect(self.create_reservation)
        if self.cancel_btn:
            self.cancel_btn.clicked.connect(self.cancel_reservation)

        self.load_vehicles()
        self.load_reservations()

    def load_vehicles(self):
        """Load available vehicles into the combo box."""
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT placa FROM Vehiculo")
            vehicles = cursor.fetchall()
            self.vehicle_combo.clear()
            for placa, in vehicles:
                self.vehicle_combo.addItem(placa)
            cursor.close()
        except Error as exc:
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error al cargar veh\u00edculos: {exc}')

    def load_reservations(self):
        """Populate the table with reservations for the current client."""
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_alquiler, id_vehiculo, fecha_hora_salida, fecha_hora_entrada "
                "FROM Alquiler WHERE id_cliente = %s",
                (self.client_id,),
            )
            records = cursor.fetchall()
            cursor.close()

            self.table.setRowCount(0)
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(['ID', 'Veh\u00edculo', 'Inicio', 'Fin'])

            for row_idx, row in enumerate(records):
                self.table.insertRow(row_idx)
                for col_idx, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
        except Error as exc:
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error al cargar reservas: {exc}')

    def create_reservation(self):
        """Insert a new reservation in the database."""
        vehicle = self.vehicle_combo.currentText()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        seguro = 1 if self.insurance_checkbox.isChecked() else None

        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            query = (
                "INSERT INTO Alquiler "
                "(fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_seguro, id_estado) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(query, (start, end, vehicle, self.client_id, seguro, 1))
            conn.commit()
            cursor.close()
            self.load_reservations()
        except Error as exc:
            if conn.is_connected():
                conn.rollback()
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error al crear reserva: {exc}')

    def cancel_reservation(self):
        """Remove the selected reservation."""
        row = self.table.currentRow()
        if row == -1:
            return
        reserva_id = self.table.item(row, 0).text()
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Alquiler WHERE id_alquiler = %s AND id_cliente = %s",
                (reserva_id, self.client_id),
            )
            conn.commit()
            cursor.close()
            self.load_reservations()
        except Error as exc:
            if conn.is_connected():
                conn.rollback()
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error al cancelar reserva: {exc}')
