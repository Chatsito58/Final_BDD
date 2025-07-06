import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox
from PyQt5.uic import loadUi

class EmpleadoCajaView(QMainWindow):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._reserva_efectivo_sel = None

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'empleado_caja_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_pagos_tab()

    def _setup_ui(self):
        # Conectar botones
        self.logout_button.clicked.connect(self.logout)

        # Actualizar estado de la conexión
        self.update_connection_status()

    def _setup_pagos_tab(self):
        # Conectar señales y slots
        self.aprobar_pago_button.clicked.connect(self._aprobar_pago_efectivo)
        self.reservas_list.itemSelectionChanged.connect(self._seleccionar_reserva_efectivo)

        # Cargar datos iniciales
        self._cargar_reservas_pendientes_efectivo()

    def _cargar_reservas_pendientes_efectivo(self):
        self.reservas_list.clear()
        query = (
            "SELECT ra.id_reserva, c.nombre, v.placa, ra.saldo_pendiente, a.fecha_hora_salida "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            f"WHERE ra.saldo_pendiente > 0 AND a.id_sucursal = %s"
        )
        reservas = self.db_manager.execute_query(query, (self.user_data.get("id_sucursal"),)) or []
        for rid, nombre, placa, saldo, fecha in reservas:
            self.reservas_list.addItem(f"{rid} | {nombre} | {placa} | Saldo: ${saldo:,.0f}")

    def _seleccionar_reserva_efectivo(self):
        selected_items = self.reservas_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        self._reserva_efectivo_sel = int(selected_item.text().split("|")[0].strip())

    def _aprobar_pago_efectivo(self):
        if not self._reserva_efectivo_sel:
            QMessageBox.warning(self, "Aviso", "Seleccione una reserva")
            return

        monto = self.monto_edit.text().strip()
        if not monto:
            QMessageBox.warning(self, "Error", "Ingrese el monto recibido")
            return

        self._procesar_pago_efectivo(self._reserva_efectivo_sel, monto)

    def _procesar_pago_efectivo(self, id_reserva, monto):
        try:
            monto_f = float(monto)
        except ValueError:
            QMessageBox.critical(self, "Error", "Monto inválido")
            return

        if monto_f <= 0:
            QMessageBox.critical(self, "Error", "El monto debe ser mayor a 0")
            return

        val_q = (
            "SELECT ra.saldo_pendiente, a.id_sucursal "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"WHERE ra.id_reserva = %s"
        )
        row = self.db_manager.execute_query(val_q, (id_reserva,))
        if not row:
            QMessageBox.critical(self, "Error", "Reserva no encontrada")
            return

        saldo = float(row[0][0])
        sucursal_reserva = row[0][1]

        if sucursal_reserva != self.user_data.get("id_sucursal"):
            QMessageBox.critical(self, "Error", "No puedes procesar reservas de otra sucursal")
            return

        if monto_f < saldo:
            QMessageBox.critical(self, "Error", f"El monto no cubre el saldo pendiente (${saldo:,.0f})")
            return

        # Registrar el abono en efectivo
        insert_q = f"INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) VALUES (%s, CURRENT_TIMESTAMP, %s, 1)"
        self.db_manager.execute_query(insert_q, (monto_f, id_reserva), fetch=False)

        # Actualizar saldo pendiente de la reserva
        nuevo_saldo = max(0, saldo - monto_f)
        update_q = f"UPDATE Reserva_alquiler SET saldo_pendiente = %s"
        params = [nuevo_saldo]
        if nuevo_saldo <= 0:
            update_q += ", id_estado_reserva = 2"
        update_q += f" WHERE id_reserva = %s"
        params.append(id_reserva)
        self.db_manager.execute_query(update_q, tuple(params), fetch=False)

        QMessageBox.information(self, "Pago registrado", f"Pago de ${monto_f:,.0f} registrado")

        self.monto_edit.clear()
        self._cargar_reservas_pendientes_efectivo()

    def update_connection_status(self):
        status1 = "Online" if self.db_manager.is_remote1_active() else "Offline"
        status2 = "Online" if self.db_manager.is_remote2_active() else "Offline"
        self.status_label1.setText(f"BD Remota 1: {status1}")
        self.status_label2.setText(f"BD Remota 2: {status2}")

    def logout(self):
        self.close()
        self.on_logout()

    def show(self):
        super().show()