import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.uic import loadUi

class EmpleadoVentasView(QMainWindow):
    def __init__(self, user_data, db_manager, auth_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.on_logout = on_logout
        self._cliente_sel = None
        self._selected_reserva_id = None

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'empleado_ventas_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_clientes_tab()
        self._setup_reservas_tab()
        self._setup_vehiculos_tab()
        self._setup_perfil_tab()
        self._setup_cambiar_contrasena_tab()

    def _setup_ui(self):
        # Conectar botones
        self.logout_button.clicked.connect(self.logout)

        # Actualizar estado de la conexión
        self.update_connection_status()

    def _setup_clientes_tab(self):
        # Conectar señales y slots
        self.nuevo_cliente_button.clicked.connect(self._nuevo_cliente)
        self.guardar_cliente_button.clicked.connect(self._guardar_cliente)
        self.clientes_list.itemSelectionChanged.connect(self._seleccionar_cliente)

        # Cargar datos iniciales
        self._cargar_clientes()

    def _cargar_clientes(self):
        self.clientes_list.clear()
        rows = self.db_manager.execute_query(
            "SELECT id_cliente, nombre, correo FROM Cliente"
        )
        if rows:
            for c in rows:
                self.clientes_list.addItem(f"{c[0]} | {c[1]} | {c[2]}")

    def _seleccionar_cliente(self):
        selected_items = self.clientes_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        self._cliente_sel = int(selected_item.text().split("|")[0].strip())
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = %s",
            (self._cliente_sel,),
        )
        if row:
            doc, nom, tel, dir_, cor = row[0]
            self.doc_cliente_edit.setText(doc or "")
            self.nombre_cliente_edit.setText(nom or "")
            self.telefono_cliente_edit.setText(tel or "")
            self.direccion_cliente_edit.setText(dir_ or "")
            self.correo_cliente_edit.setText(cor or "")

    def _nuevo_cliente(self):
        self._cliente_sel = None
        self.doc_cliente_edit.clear()
        self.nombre_cliente_edit.clear()
        self.telefono_cliente_edit.clear()
        self.correo_cliente_edit.clear()

    def _guardar_cliente(self):
        doc = self.doc_cliente_edit.text().strip()
        nom = self.nombre_cliente_edit.text().strip()
        tel = self.telefono_cliente_edit.text().strip()
        dir_ = self.direccion_cliente_edit.text().strip()
        cor = self.correo_cliente_edit.text().strip()

        if not doc or not nom or not cor:
            QMessageBox.warning(self, "Aviso", "Documento, nombre y correo son obligatorios")
            return

        try:
            if self._cliente_sel:
                q = f"UPDATE Cliente SET documento=%s, nombre=%s, telefono=%s, direccion=%s, correo=%s WHERE id_cliente=%s"
                params = (doc, nom, tel, dir_, cor, self._cliente_sel)
            else:
                q = f"INSERT INTO Cliente (documento, nombre, telefono, direccion, correo) VALUES (%s, %s, %s, %s, %s)"
                params = (doc, nom, tel, dir_, cor)
            
            self.db_manager.execute_query(q, params, fetch=False)
            QMessageBox.information(self, "Éxito", "Cliente guardado correctamente")
            self._nuevo_cliente()
            self._cargar_clientes()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _eliminar_cliente(self):
        if not self._cliente_sel:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente para eliminar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Eliminación', 
                                     "¿Está seguro que desea eliminar este cliente y todos sus datos asociados (reservas, abonos, etc.)?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            # Eliminar datos asociados (reservas, abonos, etc.)
            # Esto es un ejemplo, la lógica real debe ser más robusta y considerar las relaciones de la BD
            self.db_manager.delete("DELETE FROM Abono_reserva WHERE id_reserva IN (SELECT id_reserva FROM Reserva_alquiler WHERE id_alquiler IN (SELECT id_alquiler FROM Alquiler WHERE id_cliente = %s))", (self._cliente_sel,))
            self.db_manager.delete("DELETE FROM Reserva_alquiler WHERE id_alquiler IN (SELECT id_alquiler FROM Alquiler WHERE id_cliente = %s)", (self._cliente_sel,))
            self.db_manager.delete("DELETE FROM Alquiler WHERE id_cliente = %s", (self._cliente_sel,))
            self.db_manager.delete("DELETE FROM Usuario WHERE id_cliente = %s", (self._cliente_sel,))
            self.db_manager.delete("DELETE FROM Cliente WHERE id_cliente = %s", (self._cliente_sel,))

            QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente.")
            self._nuevo_cliente()
            self._cargar_clientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar el cliente: {e}")

    def _setup_vehiculos_tab(self):
        self._cargar_vehiculos()

    def _cargar_vehiculos(self):
        self.vehiculos_table.setRowCount(0)
        rows, headers = self.db_manager.get_all_vehiculos()
        if rows:
            self.vehiculos_table.setRowCount(len(rows))
            self.vehiculos_table.setColumnCount(len(headers))
            self.vehiculos_table.setHorizontalHeaderLabels(headers)
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    self.vehiculos_table.setItem(i, j, QTableWidgetItem(str(col)))
            self.vehiculos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _setup_reservas_tab(self):
        self.aprobar_reserva_button.clicked.connect(self._aprobar_reserva)
        self.reservas_pendientes_list.itemSelectionChanged.connect(self._on_reserva_pendiente_selection_changed)
        self._cargar_reservas_pendientes()

    def _on_reserva_pendiente_selection_changed(self):
        selected_items = self.reservas_pendientes_list.selectedItems()
        if selected_items:
            item_text = selected_items[0].text()
            self._selected_reserva_id = int(item_text.split(":")[0].replace("Reserva ", "").strip())
        else:
            self._selected_reserva_id = None

    def _cargar_reservas_pendientes(self):
        self.reservas_pendientes_list.clear()
        query = (
            "SELECT ra.id_reserva, c.nombre, v.placa, a.fecha_hora_salida, a.valor "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            "WHERE ra.id_estado_reserva = 1 AND a.id_sucursal = %s"
        )
        reservas = self.db_manager.execute_query(query, (self.user_data.get("id_sucursal"),)) or []

        if not reservas:
            self.reservas_pendientes_list.addItem("No hay reservas pendientes de aprobación.")
            return

        for r in reservas:
            id_reserva, cliente_nombre, placa, fecha_salida, valor = r
            self.reservas_pendientes_list.addItem(f"Reserva {id_reserva}: {cliente_nombre} - {placa} - Salida: {fecha_salida} - Valor: ${valor:,.0f}")

    def _aprobar_reserva(self):
        if not self._selected_reserva_id:
            QMessageBox.warning(self, "Aviso", "Seleccione una reserva para aprobar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Aprobación', 
                                     "¿Está seguro que desea aprobar esta reserva?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            update_reserva_query = "UPDATE Reserva_alquiler SET id_estado_reserva = 2 WHERE id_reserva = %s"
            self.db_manager.update(update_reserva_query, (self._selected_reserva_id,))

            QMessageBox.information(self, "Éxito", "Reserva aprobada correctamente.")
            self._cargar_reservas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo aprobar la reserva: {e}")

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
