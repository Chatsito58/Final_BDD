import os
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.uic import loadUi

class EmpleadoMantenimientoView(QMainWindow):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'empleado_mantenimiento_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_vehiculos_tab()
        self._setup_reportar_tab()
        self._setup_historial_tab()
        self._setup_perfil_tab()
        self._setup_cambiar_contrasena_tab()

    # --- Pestaña Mi Perfil ---
    def _setup_perfil_tab(self):
        self.guardar_perfil_button.clicked.connect(self._guardar_perfil)
        self._cargar_datos_perfil()

    def _cargar_datos_perfil(self):
        id_empleado = self.user_data.get("id_empleado")
        query = "SELECT nombre, telefono, direccion, correo FROM Empleado WHERE id_empleado = %s"
        datos = self.db_manager.execute_query(query, (id_empleado,))
        if datos:
            nombre, telefono, direccion, correo = datos[0]
            self.nombre_perfil_edit.setText(nombre or "")
            self.telefono_perfil_edit.setText(telefono or "")
            self.direccion_perfil_edit.setText(direccion or "")
            self.correo_perfil_edit.setText(correo or "")

    def _guardar_perfil(self):
        nombre = self.nombre_perfil_edit.text().strip()
        telefono = self.telefono_perfil_edit.text().strip()
        direccion = self.direccion_perfil_edit.text().strip()
        correo = self.correo_perfil_edit.text().strip()
        id_empleado = self.user_data.get("id_empleado")

        if not nombre or not correo:
            QMessageBox.warning(self, "Aviso", "Nombre y correo son obligatorios.")
            return

        try:
            query = "UPDATE Empleado SET nombre = %s, telefono = %s, direccion = %s, correo = %s WHERE id_empleado = %s"
            self.db_manager.update(query, (nombre, telefono, direccion, correo, id_empleado))
            QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente.")
            self.user_data["usuario"] = nombre
            self._setup_ui()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar el perfil: {e}")

    # --- Pestaña Cambiar Contraseña ---
    def _setup_cambiar_contrasena_tab(self):
        self.cambiar_pass_button.clicked.connect(self._cambiar_contrasena)

    def _cambiar_contrasena(self):
        actual_pass = self.actual_pass_edit.text()
        nueva_pass = self.nueva_pass_edit.text()
        confirmar_pass = self.confirmar_pass_edit.text()

        if not actual_pass or not nueva_pass or not confirmar_pass:
            QMessageBox.warning(self, "Aviso", "Todos los campos son obligatorios.")
            return

        if nueva_pass != confirmar_pass:
            QMessageBox.warning(self, "Error", "La nueva contraseña y la confirmación no coinciden.")
            return

        try:
            user_id = self.user_data.get("id_usuario") 
            if not user_id:
                QMessageBox.critical(self, "Error", "No se pudo obtener el ID de usuario para cambiar la contraseña.")
                return

            query_hash = "SELECT contrasena_hash FROM Usuario WHERE id_usuario = %s"
            stored_hash = self.db_manager.execute_query(query_hash, (user_id,))

            if not stored_hash or stored_hash[0][0] != hashlib.sha256(actual_pass.encode()).hexdigest():
                QMessageBox.warning(self, "Error", "Contraseña actual incorrecta.")
                return

            new_hash = hashlib.sha256(nueva_pass.encode()).hexdigest()
            update_pass_query = "UPDATE Usuario SET contrasena_hash = %s WHERE id_usuario = %s"
            self.db_manager.update(update_pass_query, (new_hash, user_id))

            QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente.")
            self.actual_pass_edit.clear()
            self.nueva_pass_edit.clear()
            self.confirmar_pass_edit.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar la contraseña: {e}")

    def _setup_historial_tab(self):
        self.historial_list.itemSelectionChanged.connect(self._on_historial_selection_changed)
        self._cargar_historial_mantenimiento()

    def _on_historial_selection_changed(self):
        # Implementar lógica si es necesario al seleccionar un elemento del historial
        pass

    def _cargar_historial_mantenimiento(self):
        self.historial_list.clear()
        id_sucursal = self.user_data.get("id_sucursal")
        query = (
            "SELECT m.id_vehiculo, m.descripcion, m.fecha_hora, m.valor, tm.descripcion as tipo_mantenimiento, t.nombre as taller_nombre "
            "FROM Mantenimiento_vehiculo m "
            "JOIN Vehiculo v ON m.id_vehiculo = v.placa "
            "LEFT JOIN Tipo_mantenimiento tm ON m.id_tipo = tm.id_tipo "
            "LEFT JOIN Taller_mantenimiento t ON m.id_taller = t.id_taller "
            "WHERE v.id_sucursal = %s "
            "ORDER BY m.fecha_hora DESC"
        )
        historial = self.db_manager.execute_query(query, (id_sucursal,)) or []

        if not historial:
            self.historial_list.addItem("No hay registros de mantenimiento para esta sucursal.")
            return

        for h in historial:
            placa, descripcion, fecha_hora, valor, tipo_mantenimiento, taller_nombre = h
            item_text = f"Vehículo: {placa} | Tipo: {tipo_mantenimiento or 'N/A'} | Taller: {taller_nombre or 'N/A'}\n"
            item_text += f"  Fecha: {fecha_hora} | Costo: ${valor:,.0f} | Descripción: {descripcion}"
            self.historial_list.addItem(item_text)

    def _setup_reportar_tab(self):
        self.guardar_mantenimiento_button.clicked.connect(self._guardar_mantenimiento)
        self._cargar_tipos_mantenimiento()
        self._cargar_talleres()

    def _cargar_tipos_mantenimiento(self):
        self.tipo_mantenimiento_combo.clear()
        tipos = self.db_manager.execute_query("SELECT id_tipo, descripcion FROM Tipo_mantenimiento") or []
        self.tipos_mantenimiento_map = {t[1]: t[0] for t in tipos}
        self.tipo_mantenimiento_combo.addItems(list(self.tipos_mantenimiento_map.keys()))

    def _cargar_talleres(self):
        self.taller_combo.clear()
        talleres = self.db_manager.execute_query("SELECT id_taller, nombre FROM Taller_mantenimiento") or []
        self.talleres_map = {t[1]: t[0] for t in talleres}
        self.taller_combo.addItems(list(self.talleres_map.keys()))

    def _guardar_mantenimiento(self):
        placa = self.placa_edit.text().strip()
        tipo_mantenimiento_desc = self.tipo_mantenimiento_combo.currentText()
        taller_nombre = self.taller_combo.currentText()
        costo_str = self.costo_edit.text().strip()
        descripcion = self.descripcion_edit.toPlainText().strip()

        if not placa or not tipo_mantenimiento_desc or not taller_nombre or not costo_str or not descripcion:
            QMessageBox.warning(self, "Aviso", "Todos los campos son obligatorios.")
            return

        try:
            costo = float(costo_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Costo inválido. Ingrese un número.")
            return

        id_tipo = self.tipos_mantenimiento_map.get(tipo_mantenimiento_desc)
        id_taller = self.talleres_map.get(taller_nombre)

        if id_tipo is None or id_taller is None:
            QMessageBox.critical(self, "Error", "Tipo de mantenimiento o taller no válido.")
            return

        try:
            # Insertar el registro de mantenimiento
            query_mantenimiento = "INSERT INTO Mantenimiento_vehiculo (descripcion, fecha_hora, valor, id_tipo, id_taller, id_vehiculo) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s)"
            self.db_manager.insert(query_mantenimiento, (descripcion, costo, id_tipo, id_taller, placa))

            # Actualizar el estado del vehículo a 'En Mantenimiento' (estado 3)
            query_update_vehiculo = "UPDATE Vehiculo SET id_estado_vehiculo = 3 WHERE placa = %s"
            self.db_manager.update(query_update_vehiculo, (placa,))

            QMessageBox.information(self, "Éxito", "Mantenimiento registrado y vehículo actualizado a 'En Mantenimiento'.")
            self.placa_edit.clear()
            self.costo_edit.clear()
            self.descripcion_edit.clear()
            self._cargar_vehiculos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar el mantenimiento: {e}")

    def _setup_ui(self):
        # Conectar botones
        self.logout_button.clicked.connect(self.logout)

        # Actualizar estado de la conexión
        self.update_connection_status()

    def _setup_vehiculos_tab(self):
        self._cargar_vehiculos()

    def _cargar_vehiculos(self):
        self.vehiculos_list.clear()
        id_sucursal = self.user_data.get("id_sucursal")
        query = (
            "SELECT v.placa, v.modelo, m.nombre_marca, t.descripcion "
            "FROM Vehiculo v "
            "JOIN Marca_vehiculo m ON v.id_marca = m.id_marca "
            "JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo "
        )
        params = ()
        if id_sucursal is not None:
            query += f"WHERE v.id_sucursal = %s"
            params = (id_sucursal,)
        vehiculos = self.db_manager.execute_query(query, params)

        if not vehiculos:
            self.vehiculos_list.addItem("Sin vehículos asignados")
            return

        for v in vehiculos:
            placa, modelo, marca, tipo = v
            self.vehiculos_list.addItem(f"{marca} {modelo} | Placa: {placa} | {tipo}")

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