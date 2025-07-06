import os
import hashlib
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from datetime import datetime

class EmpleadoCajaView(QMainWindow):
    def __init__(self, user_data, db_manager, auth_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.on_logout = on_logout
        self._reserva_efectivo_sel = None
        self._transacciones_dia = []

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'empleado_caja_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_pagos_tab()
        self._setup_caja_dia_tab()
        self._setup_perfil_tabs()

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

    def _seleccionar_reserva_efectivo(self):
        selected_items = self.reservas_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        self._reserva_efectivo_sel = int(selected_item.text().split("|")[0].strip())

    def _aprobar_pago_efectivo(self, monto):
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
        self.db_manager.insert(insert_q, (monto_f, id_reserva), fetch=False)

        # Actualizar saldo pendiente de la reserva
        nuevo_saldo = max(0, saldo - monto_f)
        update_q = f"UPDATE Reserva_alquiler SET saldo_pendiente = %s"
        params = [nuevo_saldo]
        if nuevo_saldo <= 0:
            update_q += ", id_estado_reserva = 2"
        update_q += f" WHERE id_reserva = %s"
        params.append(id_reserva)
        self.db_manager.update(update_q, tuple(params), fetch=False)

        QMessageBox.information(self, "Pago registrado", f"Pago de ${monto_f:,.0f} registrado")

        self.monto_edit.clear()
        self._cargar_reservas_pendientes_efectivo()
        self._transacciones_dia = self._cargar_transacciones_dia()
        self._actualizar_caja_dia()

    def _setup_caja_dia_tab(self):
        self.cerrar_caja_button.clicked.connect(self._cerrar_caja)
        self._transacciones_dia = self._cargar_transacciones_dia()
        self._actualizar_caja_dia()

    def _cargar_transacciones_dia(self):
        date_fn = "CURDATE()" if not self.db_manager.offline else "date('now')"
        query = (
            "SELECT ab.valor, c.nombre, ab.fecha_hora "
            "FROM Abono_reserva ab "
            "JOIN Reserva_alquiler ra ON ab.id_reserva = ra.id_reserva "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            f"WHERE DATE(ab.fecha_hora) = {date_fn} "
            "AND ab.id_medio_pago = 1 "
            f"AND a.id_sucursal = %s"
        )
        return (
            self.db_manager.execute_query(
                query, (self.user_data.get("id_sucursal"),)
            )
            or []
        )

    def _actualizar_caja_dia(self):
        transacciones = getattr(self, "_transacciones_dia", [])
        total = sum(float(t[0]) for t in transacciones)
        count = len(transacciones)
        promedio = total / count if count else 0

        self.total_caja_label.setText(f"Total efectivo del día: ${total:,.0f}")
        self.transacciones_count_label.setText(f"Transacciones: {count}")
        self.promedio_caja_label.setText(f"Promedio: ${promedio:,.0f}")

        self.transacciones_list.clear()
        for valor, cliente, fecha in transacciones:
            hora = str(fecha)[11:16] if fecha else ""
            self.transacciones_list.addItem(f"{hora} | {cliente} | ${float(valor):,.0f}")

    def _cerrar_caja(self):
        reply = QMessageBox.question(self, 'Confirmar Cierre', 
                                     "¿Está seguro que desea cerrar la caja del día? Esto borrará el registro actual.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        
        self._transacciones_dia = []
        self._actualizar_caja_dia()
        QMessageBox.information(self, "Caja Cerrada", "La caja del día ha sido cerrada y el registro limpiado.")

    def update_connection_status(self):
        status1 = "Online" if self.db_manager.is_remote1_active() else "Offline"
        status2 = "Online" if self.db_manager.is_remote2_active() else "Offline"
        self.status_label1.setText(f"BD Remota 1: {status1}")
        self.status_label2.setText(f"BD Remota 2: {status2}")

    # --- Pestañas de Perfil ---
    def _setup_perfil_tabs(self):
        self.update_profile_button.clicked.connect(self._update_personal_info)
        self.update_password_button.clicked.connect(self._update_password)
        self._cargar_datos_perfil()
        self._cargar_tipos_documento()

    def _cargar_datos_perfil(self):
        id_usuario = self.user_data.get("id_usuario")
        id_empleado = self.user_data.get("id_empleado")

        # Cargar datos del usuario (email)
        query_usuario = "SELECT usuario FROM Usuario WHERE id_usuario = %s"
        usuario_data = self.db_manager.execute_query(query_usuario, (id_usuario,))
        if usuario_data:
            self.email_lineEdit.setText(usuario_data[0][0] or "")

        # Cargar datos del empleado (nombre, documento, telefono, direccion, id_tipo_documento)
        query_empleado = "SELECT documento, nombre, telefono, direccion, id_tipo_documento FROM Empleado WHERE id_empleado = %s"
        empleado_data = self.db_manager.execute_query(query_empleado, (id_empleado,))
        if empleado_data:
            documento, nombre, telefono, direccion, id_tipo_documento = empleado_data[0]
            self.documento_lineEdit.setText(documento or "")
            self.nombre_lineEdit.setText(nombre or "")
            self.telefono_lineEdit.setText(telefono or "")
            self.direccion_lineEdit.setText(direccion or "")
            
            # Set the correct type document in the combo box
            if hasattr(self, 'tipos_documento_map') and id_tipo_documento is not None:
                for desc, id_tipo in self.tipos_documento_map.items():
                    if id_tipo == id_tipo_documento:
                        self.tipo_documento_combo.setCurrentText(desc)
                        break

    def _cargar_tipos_documento(self):
        self.tipo_documento_combo.clear()
        tipos = self.db_manager.execute_query("SELECT id_tipo_documento, descripcion FROM Tipo_documento") or []
        self.tipos_documento_map = {t[1]: t[0] for t in tipos}
        self.tipo_documento_combo.addItems(list(self.tipos_documento_map.keys()))

    def _update_personal_info(self):
        new_nombre = self.nombre_lineEdit.text().strip()
        new_email = self.email_lineEdit.text().strip()
        new_documento = self.documento_lineEdit.text().strip()
        new_telefono = self.telefono_lineEdit.text().strip()
        new_direccion = self.direccion_lineEdit.text().strip()
        selected_tipo_documento_desc = self.tipo_documento_combo.currentText()

        id_usuario = self.user_data.get("id_usuario")
        id_empleado = self.user_data.get("id_empleado")

        if not all([new_nombre, new_email, new_documento, selected_tipo_documento_desc]):
            QMessageBox.warning(self, "Aviso", "Nombre, Email, Documento y Tipo de Documento son obligatorios.")
            return

        id_tipo_documento = self.tipos_documento_map.get(selected_tipo_documento_desc)
        if id_tipo_documento is None:
            QMessageBox.critical(self, "Error", "Tipo de documento no válido.")
            return

        try:
            # Update Employee data
            query_update_empleado = "UPDATE Empleado SET documento = %s, nombre = %s, telefono = %s, direccion = %s, id_tipo_documento = %s WHERE id_empleado = %s"
            self.db_manager.update(query_update_empleado, (new_documento, new_nombre, new_telefono, new_direccion, id_tipo_documento, id_empleado))

            # Update User email
            query_update_usuario_email = "UPDATE Usuario SET usuario = %s WHERE id_usuario = %s"
            self.db_manager.update(query_update_usuario_email, (new_email, id_usuario))

            QMessageBox.information(self, "Éxito", "Información personal actualizada correctamente.")
            self.user_data["usuario"] = new_email # Update user_data in session
            self.user_data["nombre"] = new_nombre # Update user_data in session

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar la información personal: {e}")

    def _update_password(self):
        current_password = self.current_password_lineEdit.text()
        new_password = self.new_password_lineEdit.text()
        confirm_password = self.confirm_password_lineEdit.text()

        id_usuario = self.user_data.get("id_usuario")

        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Aviso", "Todos los campos de contraseña son obligatorios.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "La nueva contraseña y la confirmación no coinciden.")
            return

        try:
            user_email = self.user_data.get("usuario")
            auth_result = self.auth_manager.cambiar_contrasena(user_email, current_password, new_password)
            
            if auth_result is True:
                QMessageBox.information(self, "Éxito", "Contraseña actualizada correctamente.")
                
                # Clear password fields after successful update
                self.current_password_lineEdit.clear()
                self.new_password_lineEdit.clear()
                self.confirm_password_lineEdit.clear()
            else:
                QMessageBox.warning(self, "Error", auth_result)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar la contraseña: {e}")

    def logout(self):
        self.close()
        self.on_logout()

    def show(self):
        super().show()
