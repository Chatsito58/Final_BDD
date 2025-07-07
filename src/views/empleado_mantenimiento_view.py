import os
import hashlib
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView, QWidget, QVBoxLayout, QComboBox, QTableWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate

class EmpleadoMantenimientoView(QMainWindow):
    def __init__(self, user_data, db_manager, auth_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.on_logout = on_logout

        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'empleado_mantenimiento_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_vehiculos_tab()
        self._setup_mantenimiento_tab()
        self._setup_mis_mantenimientos_tab()
        self._setup_historial_mantenimientos_tab()
        self._setup_perfil_tabs()

    def _setup_ui(self):
        self.logout_button.clicked.connect(self.logout)
        self.update_connection_status()

        # Mover las pestañas de perfil al nivel superior
        self.tabWidget.addTab(self.perfil_tab, "Información Personal")
        self.tabWidget.addTab(self.cambiar_contrasena_tab, "Cambiar Contraseña")

    def update_connection_status(self):
        status1 = "Online" if self.db_manager.is_remote1_active() else "Offline"
        status2 = "Online" if self.db_manager.is_remote2_active() else "Offline"
        self.status_label1.setText(f"BD Remota 1: {status1}")
        self.status_label2.setText(f"BD Remota 2: {status2}")

    # --- Pestaña Vehículos Disponibles ---
    def _setup_vehiculos_tab(self):
        print(f"[DEBUG] Setting up vehiculos tab. User data: {self.user_data}")
        self._cargar_vehiculos_disponibles()

    def _cargar_vehiculos_disponibles(self):
        self.vehiculos_table.setRowCount(0) # Clear existing rows
        id_sucursal = self.user_data.get("id_sucursal")
        print(f"[DEBUG] _cargar_vehiculos_disponibles called. id_sucursal: {id_sucursal}")
        
        # Query para obtener vehículos que NO están alquilados hoy y no están en mantenimiento
        query = """
            SELECT 
                v.placa AS Placa, 
                mv.nombre_marca AS Marca, 
                v.modelo AS Modelo, 
                ev.descripcion AS Estado, 
                tv.combustible AS Combustible, 
                bv.descripcion AS Blindaje, 
                cv.descripcion AS Cilindraje
            FROM Vehiculo v
            JOIN Marca_vehiculo mv ON v.id_marca = mv.id_marca
            JOIN Estado_vehiculo ev ON v.id_estado_vehiculo = ev.id_estado
            JOIN Tipo_vehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo
            JOIN Blindaje_vehiculo bv ON v.id_blindaje = bv.id_blindaje
            JOIN Cilindraje_vehiculo cv ON v.id_cilindraje = cv.id_cilindraje
            WHERE v.id_sucursal = %s
            AND v.id_estado_vehiculo NOT IN (2, 3) -- Excluir 'Alquilado' (2) y 'En Mantenimiento' (3)
        """
        
        print(f"[DEBUG] Query for available vehicles: {query} with sucursal_id: {id_sucursal}")
        vehiculos, headers = self.db_manager.execute_query_with_headers(query, (id_sucursal,))
        print(f"[DEBUG] Result of available vehicles query: {vehiculos}")

        if vehiculos:
            self.vehiculos_table.setColumnCount(len(headers))
            self.vehiculos_table.setHorizontalHeaderLabels(headers)
            self.vehiculos_table.setRowCount(len(vehiculos))
            for row_idx, vehiculo in enumerate(vehiculos):
                for col_idx, data in enumerate(vehiculo):
                    self.vehiculos_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
            self.vehiculos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.vehiculos_table.horizontalHeader().setStretchLastSection(True)
        else:
            # Optionally display a message if no vehicles are available
            print("[DEBUG] No available vehicles found.")

    # --- Pestaña Registrar Mantenimiento ---
    def _setup_mantenimiento_tab(self):
        print(f"[DEBUG] Setting up mantenimiento tab. User data: {self.user_data}")
        self.fecha_fin_mantenimiento_dateEdit.setDate(QDate.currentDate().addDays(7)) # Default to 7 days from now
        self.registrar_mantenimiento_button.clicked.connect(self._registrar_mantenimiento)
        self._cargar_vehiculos_para_mantenimiento_combo()
        self._cargar_tipos_mantenimiento()
        self._cargar_talleres()

    def _setup_mis_mantenimientos_tab(self):
        print(f"[DEBUG] Setting up mis mantenimientos tab. User data: {self.user_data}")
        # Crear la nueva pestaña
        self.mis_mantenimientos_tab = QWidget()
        self.tabWidget.insertTab(2, self.mis_mantenimientos_tab, "Mis Mantenimientos")

        # Crear el layout y la tabla
        layout = QVBoxLayout(self.mis_mantenimientos_tab)
        self.mis_mantenimientos_table = QTableWidget()
        layout.addWidget(self.mis_mantenimientos_table)

        # Cargar los datos
        self._cargar_mis_mantenimientos()

    def _setup_historial_mantenimientos_tab(self):
        print(f"[DEBUG] Setting up historial mantenimientos tab. User data: {self.user_data}")
        # Crear la nueva pestaña
        self.historial_mantenimientos_tab = QWidget()
        self.tabWidget.insertTab(3, self.historial_mantenimientos_tab, "Historial de Mantenimientos")

        # Crear el layout, el combo box y la tabla
        layout = QVBoxLayout(self.historial_mantenimientos_tab)
        self.historial_vehiculo_combo = QComboBox()
        self.historial_mantenimientos_table = QTableWidget()
        layout.addWidget(self.historial_vehiculo_combo)
        layout.addWidget(self.historial_mantenimientos_table)

        # Conectar el combo box a la función de carga
        self.historial_vehiculo_combo.currentIndexChanged.connect(self._cargar_historial_mantenimientos)

        # Cargar los datos
        self._cargar_vehiculos_para_historial_combo()

    def _cargar_vehiculos_para_mantenimiento_combo(self):
        self.vehiculo_mantenimiento_combo.clear()
        id_sucursal = self.user_data.get("id_sucursal")
        print(f"[DEBUG] _cargar_vehiculos_para_mantenimiento_combo called. id_sucursal: {id_sucursal}")
        
        # Obtener todos los vehículos de la sucursal que no estén en mantenimiento
        query = """
            SELECT v.placa, mv.nombre_marca, v.modelo, v.placa
            FROM Vehiculo v
            JOIN Marca_vehiculo mv ON v.id_marca = mv.id_marca
            WHERE v.id_sucursal = %s
            AND v.id_estado_vehiculo != 3 -- Asumiendo 3 es 'En Mantenimiento'
        """
        print(f"[DEBUG] Query for vehicles for maintenance combo: {query} with sucursal_id: {id_sucursal}")
        vehiculos = self.db_manager.execute_query(query, (id_sucursal,))
        print(f"[DEBUG] Result of vehicles for maintenance combo query: {vehiculos}")
        
        self.vehiculos_mantenimiento_map = {}
        if vehiculos:
            for placa, marca, modelo, _ in vehiculos:
                display_text = f"{marca} {modelo} (Placa: {placa})"
                self.vehiculo_mantenimiento_combo.addItem(display_text, placa)
                self.vehiculos_mantenimiento_map[display_text] = placa
        else:
            print("[DEBUG] No vehicles found for maintenance combo.")

    def _cargar_tipos_mantenimiento(self):
        print("[DEBUG] _cargar_tipos_mantenimiento called.")
        self.tipo_mantenimiento_combo.clear()
        tipos = self.db_manager.execute_query("SELECT id_tipo, descripcion FROM Tipo_mantenimiento") or []
        print(f"[DEBUG] Result of tipos mantenimiento query: {tipos}")
        self.tipos_mantenimiento_map = {t[1]: t[0] for t in tipos}
        self.tipo_mantenimiento_combo.addItems(list(self.tipos_mantenimiento_map.keys()))

    def _cargar_talleres(self):
        print("[DEBUG] _cargar_talleres called.")
        self.taller_mantenimiento_combo.clear()
        talleres = self.db_manager.execute_query("SELECT id_taller, nombre FROM Taller_mantenimiento") or []
        print(f"[DEBUG] Result of talleres query: {talleres}")
        self.talleres_mantenimiento_map = {t[1]: t[0] for t in talleres}
        self.taller_mantenimiento_combo.addItems(list(self.talleres_mantenimiento_map.keys()))

    def _cargar_mis_mantenimientos(self):
        self.mis_mantenimientos_table.setRowCount(0)
        id_empleado = self.user_data.get("id_empleado")
        print(f"[DEBUG] _cargar_mis_mantenimientos called. id_empleado: {id_empleado}")
        rows, headers = self.db_manager.get_mantenimientos_empleado(id_empleado)
        print(f"[DEBUG] Result of mis mantenimientos query: Rows: {rows}, Headers: {headers}")
        if rows:
            self.mis_mantenimientos_table.setRowCount(len(rows))
            self.mis_mantenimientos_table.setColumnCount(len(headers))
            self.mis_mantenimientos_table.setHorizontalHeaderLabels(headers)
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    self.mis_mantenimientos_table.setItem(i, j, QTableWidgetItem(str(col)))
            self.mis_mantenimientos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _cargar_vehiculos_para_historial_combo(self):
        self.historial_vehiculo_combo.clear()
        print("[DEBUG] _cargar_vehiculos_para_historial_combo called.")
        vehiculos, _ = self.db_manager.get_all_vehiculos()
        print(f"[DEBUG] Result of get_all_vehiculos for historial combo: {vehiculos}")
        if vehiculos:
            for v in vehiculos:
                self.historial_vehiculo_combo.addItem(f"{v[1]} {v[2]} (Placa: {v[0]})", v[0])
        else:
            self.historial_vehiculo_combo.addItem("No hay vehículos disponibles", None)
            print("[DEBUG] No vehicles found for historial combo.")

    def _cargar_historial_mantenimientos(self):
        self.historial_mantenimientos_table.setRowCount(0)
        placa = self.historial_vehiculo_combo.currentData()
        print(f"[DEBUG] _cargar_historial_mantenimientos called. Placa: {placa}")
        if placa:
            rows, headers = self.db_manager.get_historial_mantenimientos_vehiculo(placa)
            print(f"[DEBUG] Result of historial mantenimientos query: Rows: {rows}, Headers: {headers}")
            if rows:
                self.historial_mantenimientos_table.setRowCount(len(rows))
                self.historial_mantenimientos_table.setColumnCount(len(headers))
                self.historial_mantenimientos_table.setHorizontalHeaderLabels(headers)
                for i, row in enumerate(rows):
                    for j, col in enumerate(row):
                        self.historial_mantenimientos_table.setItem(i, j, QTableWidgetItem(str(col)))
                self.historial_mantenimientos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            else:
                QMessageBox.information(self, "Historial de Mantenimientos", f"No hay mantenimientos registrados para el vehículo con placa {placa}.")
        else:
            QMessageBox.information(self, "Historial de Mantenimientos", "Seleccione un vehículo para ver su historial.")

    def _registrar_mantenimiento(self):
        selected_vehiculo_placa = self.vehiculo_mantenimiento_combo.currentData()
        fecha_fin = self.fecha_fin_mantenimiento_dateEdit.date().toString("yyyy-MM-dd")
        descripcion = self.descripcion_mantenimiento_textEdit.toPlainText().strip()
        valor_str = self.valor_mantenimiento_lineEdit.text().strip()
        tipo_mantenimiento_desc = self.tipo_mantenimiento_combo.currentText()
        taller_nombre = self.taller_mantenimiento_combo.currentText()

        print(f"[DEBUG] _registrar_mantenimiento called with: Placa={selected_vehiculo_placa}, Fecha_fin={fecha_fin}, Descripcion={descripcion}, Valor_str={valor_str}, Tipo={tipo_mantenimiento_desc}, Taller={taller_nombre}")

        if not selected_vehiculo_placa or not descripcion or not valor_str or not tipo_mantenimiento_desc or not taller_nombre:
            QMessageBox.warning(self, "Aviso", "Todos los campos de mantenimiento son obligatorios.")
            return

        try:
            valor = float(valor_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Valor de mantenimiento inválido. Ingrese un número.")
            return

        id_tipo_mantenimiento = self.tipos_mantenimiento_map.get(tipo_mantenimiento_desc)
        id_taller_mantenimiento = self.talleres_mantenimiento_map.get(taller_nombre)

        print(f"[DEBUG] Mapped IDs: id_tipo_mantenimiento={id_tipo_mantenimiento}, id_taller_mantenimiento={id_taller_mantenimiento}")

        if id_tipo_mantenimiento is None or id_taller_mantenimiento is None:
            QMessageBox.critical(self, "Error", "Tipo de mantenimiento o taller no válido.")
            return

        try:
            # Insertar el registro de mantenimiento en la tabla Mantenimiento
            query_insert_mantenimiento = """
                INSERT INTO Mantenimiento (placa, descripcion, fecha, fecha_fin)
                VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
            """
            print(f"[DEBUG] Inserting into Mantenimiento: Query={query_insert_mantenimiento}, Params={(selected_vehiculo_placa, descripcion, fecha_fin)}")
            self.db_manager.execute_query(query_insert_mantenimiento, 
                                   (selected_vehiculo_placa, descripcion, fecha_fin), fetch=False)

            # Insertar el registro de mantenimiento en la tabla Mantenimiento_vehiculo
            query_insert_mantenimiento_vehiculo = """
                INSERT INTO Mantenimiento_vehiculo (id_vehiculo, descripcion, fecha_hora, valor, id_tipo, id_taller)
                VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
            """
            print(f"[DEBUG] Inserting into Mantenimiento_vehiculo: Query={query_insert_mantenimiento_vehiculo}, Params={(selected_vehiculo_placa, descripcion, valor, id_tipo_mantenimiento, id_taller_mantenimiento)}")
            self.db_manager.execute_query(query_insert_mantenimiento_vehiculo, 
                                   (selected_vehiculo_placa, descripcion, valor, id_tipo_mantenimiento, id_taller_mantenimiento), fetch=False)

            # Actualizar el estado del vehículo a 'En Mantenimiento' (id_estado_vehiculo = 3)
            query_update_vehiculo_estado = "UPDATE Vehiculo SET id_estado_vehiculo = 3 WHERE placa = %s"
            print(f"[DEBUG] Updating Vehiculo status: Query={query_update_vehiculo_estado}, Params={(selected_vehiculo_placa,)}")
            self.db_manager.execute_query(query_update_vehiculo_estado, (selected_vehiculo_placa,), fetch=False)

            QMessageBox.information(self, "Éxito", "Mantenimiento registrado y vehículo puesto en estado de mantenimiento.")
            self._cargar_vehiculos_disponibles() # Refresh the available vehicles list
            self._cargar_vehiculos_para_mantenimiento_combo() # Refresh the combo box
            self.descripcion_mantenimiento_textEdit.clear()
            self.valor_mantenimiento_lineEdit.clear()
        except Exception as e:
            print(f"[DEBUG] Error during maintenance registration: {e}")
            QMessageBox.critical(self, "Error", f"Error al registrar mantenimiento: {e}")

    # --- Pestañas de Perfil ---
    def _setup_perfil_tabs(self):
        print(f"[DEBUG] Setting up perfil tabs. User data: {self.user_data}")
        # Las pestañas de perfil ya no se insertan aquí, se mueven en _setup_ui
        self.update_profile_button.clicked.connect(self._update_personal_info)
        self.update_password_button.clicked.connect(self._update_password)
        self._cargar_datos_perfil()
        self._cargar_tipos_documento()

    def _cargar_datos_perfil(self):
        id_usuario = self.user_data.get("id_usuario")
        id_empleado = self.user_data.get("id_empleado")
        print(f"[DEBUG] _cargar_datos_perfil called. id_usuario: {id_usuario}, id_empleado: {id_empleado}")

        # Cargar datos del usuario (email)
        query_usuario = "SELECT usuario FROM Usuario WHERE id_usuario = %s"
        usuario_data = self.db_manager.execute_query(query_usuario, (id_usuario,))
        print(f"[DEBUG] Result of usuario query: {usuario_data}")
        if usuario_data:
            self.email_lineEdit.setText(usuario_data[0][0] or "")

        # Cargar datos del empleado (nombre, documento, telefono, direccion, id_tipo_documento)
        query_empleado = "SELECT documento, nombre, telefono, direccion, id_tipo_documento FROM Empleado WHERE id_empleado = %s"
        empleado_data = self.db_manager.execute_query(query_empleado, (id_empleado,))
        print(f"[DEBUG] Result of empleado query: {empleado_data}")
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
        print("[DEBUG] _cargar_tipos_documento called.")
        self.tipo_documento_combo.clear()
        tipos = self.db_manager.execute_query("SELECT id_tipo_documento, descripcion FROM Tipo_documento") or []
        print(f"[DEBUG] Result of tipos documento query: {tipos}")
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

        print(f"[DEBUG] _update_personal_info called with: Nombre={new_nombre}, Email={new_email}, Documento={new_documento}, Telefono={new_telefono}, Direccion={new_direccion}, Tipo_Documento={selected_tipo_documento_desc}, id_usuario={id_usuario}, id_empleado={id_empleado}")

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
            print(f"[DEBUG] Updating Empleado: Query={query_update_empleado}, Params={(new_documento, new_nombre, new_telefono, new_direccion, id_tipo_documento, id_empleado)}")
            self.db_manager.update(query_update_empleado, (new_documento, new_nombre, new_telefono, new_direccion, id_tipo_documento, id_empleado))

            # Update User email
            query_update_usuario_email = "UPDATE Usuario SET usuario = %s WHERE id_usuario = %s"
            print(f"[DEBUG] Updating Usuario email: Query={query_update_usuario_email}, Params={(new_email, id_usuario)}")
            self.db_manager.update(query_update_usuario_email, (new_email, id_usuario))

            QMessageBox.information(self, "Éxito", "Información personal actualizada correctamente.")
            self.user_data["usuario"] = new_email # Update user_data in session
            self.user_data["nombre"] = new_nombre # Update user_data in session

        except Exception as e:
            print(f"[DEBUG] Error during personal info update: {e}")
            QMessageBox.critical(self, "Error", f"Error al actualizar la información personal: {e}")

    def _update_password(self):
        current_password = self.current_password_lineEdit.text()
        new_password = self.new_password_lineEdit.text()
        confirm_password = self.confirm_password_lineEdit.text()

        id_usuario = self.user_data.get("id_usuario")

        print(f"[DEBUG] _update_password called for id_usuario: {id_usuario}")

        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Aviso", "Todos los campos de contraseña son obligatorios.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "La nueva contraseña y la confirmación no coinciden.")
            return

        try:
            # Verify current password
            query_hash = "SELECT contrasena FROM Usuario WHERE id_usuario = %s"
            print(f"[DEBUG] Verifying current password: Query={query_hash}, Params={(id_usuario,)}")
            stored_hash_result = self.db_manager.execute_query(query_hash, (id_usuario,))
            print(f"[DEBUG] Stored hash result: {stored_hash_result}")
            
            if not stored_hash_result or not stored_hash_result[0][0]:
                QMessageBox.critical(self, "Error", "No se pudo verificar la contraseña actual. Intente de nuevo.")
                return
            
            stored_hash = stored_hash_result[0][0]
            input_hash = hashlib.sha256(current_password.encode()).hexdigest()
            
            print(f"Stored hash: {stored_hash}")
            print(f"Input hash: {input_hash}")

            if stored_hash != input_hash:
                QMessageBox.warning(self, "Error", "Contraseña actual incorrecta.")
                return

            # Update password
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            query_update_password = "UPDATE Usuario SET contrasena = %s WHERE id_usuario = %s"
            print(f"[DEBUG] Updating password: Query={query_update_password}, Params={(new_hash, id_usuario)}")
            self.db_manager.update(query_update_password, (new_hash, id_usuario))

            QMessageBox.information(self, "Éxito", "Contraseña actualizada correctamente.")
            
            # Clear password fields after successful update
            self.current_password_lineEdit.clear()
            self.new_password_lineEdit.clear()
            self.confirm_password_lineEdit.clear()

        except Exception as e:
            print(f"[DEBUG] Error during password update: {e}")
            QMessageBox.critical(self, "Error", f"Error al cambiar la contraseña: {e}")

    def logout(self):
        self.close()
        self.on_logout()

    def show(self):
        super().show()