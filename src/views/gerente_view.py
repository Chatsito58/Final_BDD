import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox
from PyQt5.uic import loadUi
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
)

class GerenteView(QMainWindow):
    def __init__(self, user_data, db_manager, auth_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.on_logout = on_logout
        self._emp_sel = None

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'gerente_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_empleados_tab()
        self._setup_vehiculos_tab()
        self._setup_clientes_tab()
        self._setup_reportes_tab()
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
            user_email = self.user_data.get("usuario")
            auth_result = self.auth_manager.cambiar_contrasena(user_email, actual_pass, nueva_pass)

            if auth_result is True:
                QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente.")
                self.actual_pass_edit.clear()
                self.nueva_pass_edit.clear()
                self.confirmar_pass_edit.clear()
            else:
                QMessageBox.warning(self, "Error", auth_result)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar la contraseña: {e}")

    def _setup_reportes_tab(self):
        self.generar_reporte_sucursal_button.clicked.connect(self._generar_reporte_ingresos_sucursal)
        self.generar_reporte_vendedor_button.clicked.connect(self._generar_reporte_ingresos_vendedor)
        self.generar_reporte_vehiculos_alquilados_button.clicked.connect(self._generar_reporte_vehiculos_mas_alquilados)
        self.generar_reporte_abonos_button.clicked.connect(self._generar_reporte_abonos_realizados)

        # Asumiendo que tienes un QTextEdit llamado 'reporte_output_textedit' en tu UI
        # Si no lo tienes, necesitarás añadirlo en gerente_view.ui
        self.reporte_output_textedit.setReadOnly(True)

    def _generar_reporte_ingresos_sucursal(self):
        # Lógica para obtener ingresos por sucursal
        query = """
            SELECT
                s.nombre AS Sucursal,
                SUM(a.valor) AS Total_Ingresos
            FROM Alquiler a
            JOIN Sucursal s ON a.id_sucursal = s.id_sucursal
            GROUP BY s.nombre
            ORDER BY Total_Ingresos DESC
        """
        rows, headers = self.db_manager.execute_query_with_headers(query)
        self._display_report("Reporte de Ingresos por Sucursal", rows, headers)

    def _generar_reporte_ingresos_vendedor(self):
        # Lógica para obtener ingresos por vendedor
        query = """
            SELECT
                e.nombre AS Vendedor,
                SUM(a.valor) AS Total_Ingresos
            FROM Alquiler a
            JOIN Empleado e ON a.id_empleado = e.id_empleado
            GROUP BY e.nombre
            ORDER BY Total_Ingresos DESC
        """
        rows, headers = self.db_manager.execute_query_with_headers(query)
        self._display_report("Reporte de Ingresos por Vendedor", rows, headers)

    def _generar_reporte_vehiculos_mas_alquilados(self):
        # Lógica para obtener vehículos más alquilados
        query = """
            SELECT
                v.modelo AS Modelo,
                v.placa AS Placa,
                COUNT(a.id_vehiculo) AS Veces_Alquilado
            FROM Alquiler a
            JOIN Vehiculo v ON a.id_vehiculo = v.placa
            GROUP BY v.modelo, v.placa
            ORDER BY Veces_Alquilado DESC
            LIMIT 10
        """
        rows, headers = self.db_manager.execute_query_with_headers(query)
        self._display_report("Reporte de Vehículos Más Alquilados", rows, headers)

    def _generar_reporte_abonos_realizados(self):
        # Lógica para obtener abonos realizados
        query = """
            SELECT
                ar.fecha_hora AS Fecha_Hora,
                ar.valor AS Monto,
                mp.descripcion AS Metodo_Pago,
                ra.id_reserva AS ID_Reserva
            FROM Abono_reserva ar
            JOIN Medio_pago mp ON ar.id_medio_pago = mp.id_medio_pago
            JOIN Reserva_alquiler ra ON ar.id_reserva = ra.id_reserva
            ORDER BY ar.fecha_hora DESC
        """
        rows, headers = self.db_manager.execute_query_with_headers(query)
        self._display_report("Reporte de Abonos Realizados", rows, headers)

    def _display_report(self, title, rows, headers):
        report_text = f"### {title}\n\n"
        if not rows:
            report_text += "No hay datos disponibles para este reporte.\n"
        else:
            # Formatear encabezados
            header_line = " | ".join(headers)
            report_text += header_line + "\n"
            report_text += "-" * len(header_line) + "\n"
            
            # Formatear filas
            for row in rows:
                row_str = []
                for item in row:
                    if isinstance(item, (int, float)):
                        row_str.append(f"{item:, .0f}") # Formato numérico
                    else:
                        row_str.append(str(item))
                report_text += " | ".join(row_str) + "\n"
        
        self.reporte_output_textedit.setText(report_text)

    def _setup_clientes_tab(self):
        self.nuevo_cliente_button.clicked.connect(self._nuevo_cliente)
        self.guardar_cliente_button.clicked.connect(self._guardar_cliente)
        self.eliminar_cliente_button.clicked.connect(self._eliminar_cliente)
        self.clientes_list.itemSelectionChanged.connect(self._seleccionar_cliente)
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
        self.direccion_cliente_edit.clear()
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
        self.guardar_vehiculo_button.clicked.connect(self._guardar_vehiculo)
        self._cargar_catalogos_vehiculos()

    def _cargar_catalogos_vehiculos(self):
        # Cargar marcas
        marcas = self.db_manager.execute_query("SELECT id_marca, nombre_marca FROM Marca_vehiculo")
        self.marca_vehiculo_map = {m[1]: m[0] for m in (marcas or [])}
        self.marca_vehiculo_combo.clear()
        self.marca_vehiculo_combo.addItems(list(self.marca_vehiculo_map.keys()))

        # Cargar colores
        colores = self.db_manager.execute_query("SELECT id_color, nombre_color FROM Color_vehiculo")
        self.color_vehiculo_map = {c[1]: c[0] for c in (colores or [])}
        self.color_vehiculo_combo.clear()
        self.color_vehiculo_combo.addItems(list(self.color_vehiculo_map.keys()))

        # Cargar tipos de vehículo
        tipos = self.db_manager.execute_query("SELECT id_tipo, descripcion FROM Tipo_vehiculo")
        self.tipo_vehiculo_map = {t[1]: t[0] for t in (tipos or [])}
        self.tipo_vehiculo_combo.clear()
        self.tipo_vehiculo_combo.addItems(list(self.tipo_vehiculo_map.keys()))

        # Cargar transmisiones
        transmisiones = self.db_manager.execute_query("SELECT id_transmision, descripcion FROM Transmision_vehiculo")
        self.transmision_vehiculo_map = {t[1]: t[0] for t in (transmisiones or [])}
        self.transmision_vehiculo_combo.clear()
        self.transmision_vehiculo_combo.addItems(list(self.transmision_vehiculo_map.keys()))

        # Cargar blindajes
        blindajes = self.db_manager.execute_query("SELECT id_blindaje, descripcion FROM Blindaje_vehiculo")
        self.blindaje_vehiculo_map = {b[1]: b[0] for b in (blindajes or [])}
        self.blindaje_vehiculo_combo.clear()
        self.blindaje_vehiculo_combo.addItems(list(self.blindaje_vehiculo_map.keys()))

        # Cargar seguros
        seguros = self.db_manager.execute_query("SELECT id_seguro, descripcion FROM Seguro_vehiculo WHERE estado = 'Activo'")
        self.seguro_vehiculo_map = {s[1]: s[0] for s in (seguros or [])}
        self.seguro_vehiculo_combo.clear()
        self.seguro_vehiculo_combo.addItems(list(self.seguro_vehiculo_map.keys()))

        # Cargar proveedores
        proveedores = self.db_manager.execute_query("SELECT id_proveedor, nombre FROM Proveedor_vehiculo")
        self.proveedor_vehiculo_map = {p[1]: p[0] for p in (proveedores or [])}
        self.proveedor_vehiculo_combo.clear()
        self.proveedor_vehiculo_combo.addItems(list(self.proveedor_vehiculo_map.keys()))

    def _guardar_vehiculo(self):
        placa = self.placa_vehiculo_edit.text().strip()
        chasis = self.chasis_vehiculo_edit.text().strip()
        modelo = self.modelo_vehiculo_edit.text().strip()
        kilometraje_str = self.kilometraje_vehiculo_edit.text().strip()

        marca_desc = self.marca_vehiculo_combo.currentText()
        color_desc = self.color_vehiculo_combo.currentText()
        tipo_desc = self.tipo_vehiculo_combo.currentText()
        transmision_desc = self.transmision_vehiculo_combo.currentText()
        blindaje_desc = self.blindaje_vehiculo_combo.currentText()
        seguro_desc = self.seguro_vehiculo_combo.currentText()
        proveedor_desc = self.proveedor_vehiculo_combo.currentText()

        if not all([placa, modelo, marca_desc, color_desc, tipo_desc, transmision_desc, blindaje_desc, seguro_desc, proveedor_desc]):
            QMessageBox.warning(self, "Aviso", "Todos los campos son obligatorios.")
            return

        try:
            kilometraje = int(kilometraje_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Kilometraje inválido. Ingrese un número entero.")
            return

        id_marca = self.marca_vehiculo_map.get(marca_desc)
        id_color = self.color_vehiculo_map.get(color_desc)
        id_tipo_vehiculo = self.tipo_vehiculo_map.get(tipo_desc)
        id_transmision = self.transmision_vehiculo_map.get(transmision_desc)
        id_blindaje = self.blindaje_vehiculo_map.get(blindaje_desc)
        id_seguro_vehiculo = self.seguro_vehiculo_map.get(seguro_desc)
        id_proveedor = self.proveedor_vehiculo_map.get(proveedor_desc)
        id_sucursal = self.user_data.get("id_sucursal") # Asumiendo que el gerente solo puede agregar vehículos a su sucursal

        try:
            query = "INSERT INTO Vehiculo (placa, n_chasis, modelo, kilometraje, id_marca, id_color, id_tipo_vehiculo, id_transmision, id_blindaje, id_seguro_vehiculo, id_estado_vehiculo, id_proveedor, id_sucursal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (placa, chasis, modelo, kilometraje, id_marca, id_color, id_tipo_vehiculo, id_transmision, id_blindaje, id_seguro_vehiculo, 1, id_proveedor, id_sucursal)
            self.db_manager.insert(query, params)
            QMessageBox.information(self, "Éxito", "Vehículo guardado correctamente.")
            # Limpiar formulario
            self.placa_vehiculo_edit.clear()
            self.chasis_vehiculo_edit.clear()
            self.modelo_vehiculo_edit.clear()
            self.kilometraje_vehiculo_edit.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar el vehículo: {e}")

    def _setup_ui(self):
        # Conectar botones
        self.logout_button.clicked.connect(self.logout)

        # Actualizar estado de la conexión
        self.update_connection_status()

    def _setup_empleados_tab(self):
        # Conectar señales y slots
        self.nuevo_empleado_button.clicked.connect(self._nuevo_empleado)
        self.guardar_empleado_button.clicked.connect(self._guardar_empleado)
        self.empleados_list.itemSelectionChanged.connect(self._seleccionar_empleado)

        # Cargar datos iniciales
        cargos = cargos_permitidos_para_gerente()
        self.cargo_empleado_combo.addItems(cargos)
        self._cargar_empleados()

    def _cargar_empleados(self):
        self.empleados_list.clear()
        rows = self.db_manager.execute_query(
            "SELECT id_empleado, nombre, cargo, documento, telefono, correo FROM Empleado "
            "WHERE LOWER(cargo) NOT IN ('gerente','administrador')"
        )
        if rows:
            for r in rows:
                id_e, nombre, cargo, doc, tel, cor = r
                self.empleados_list.addItem(f"{id_e} | {nombre} | {cargo} | {doc} | {tel} | {cor}")

    def _seleccionar_empleado(self):
        selected_items = self.empleados_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        self._emp_sel = int(selected_item.text().split("|")[0].strip())
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, correo, cargo FROM Empleado WHERE id_empleado = %s",
            (self._emp_sel,),
        )
        if row:
            doc, nom, tel, cor, cargo = row[0]
            self.doc_empleado_edit.setText(doc or "")
            self.nombre_empleado_edit.setText(nom or "")
            self.telefono_empleado_edit.setText(tel or "")
            self.correo_empleado_edit.setText(cor or "")
            self.cargo_empleado_combo.setCurrentText(cargo or cargos_permitidos_para_gerente()[0])

    def _nuevo_empleado(self):
        self._emp_sel = None
        self.doc_empleado_edit.clear()
        self.nombre_empleado_edit.clear()
        self.telefono_empleado_edit.clear()
        self.correo_empleado_edit.clear()
        self.cargo_empleado_combo.setCurrentIndex(0)

    def _guardar_empleado(self):
        doc = self.doc_empleado_edit.text().strip()
        nom = self.nombre_empleado_edit.text().strip()
        tel = self.telefono_empleado_edit.text().strip()
        cor = self.correo_empleado_edit.text().strip()
        cargo = self.cargo_empleado_combo.currentText().strip()

        if not doc or not nom or not cor or not cargo:
            QMessageBox.warning(self, "Aviso", "Documento, nombre, correo y cargo son obligatorios")
            return

        if cargo.lower() == "gerente" and not puede_gestionar_gerentes(self.user_data.get("rol")):
            QMessageBox.warning(self, "Aviso", "No tiene permiso para gestionar empleados con cargo 'gerente'")
            return

        if not verificar_permiso_creacion_empleado(cargo, self.user_data.get("rol")):
            QMessageBox.warning(self, "Aviso", "No tiene permiso para crear/editar este empleado")
            return

        try:
            if self._emp_sel:
                q = f"UPDATE Empleado SET documento=%s, nombre=%s, telefono=%s, correo=%s, cargo=%s WHERE id_empleado=%s"
                params = (doc, nom, tel, cor, cargo, self._emp_sel)
            else:
                q = f"INSERT INTO Empleado (documento, nombre, telefono, correo, cargo) VALUES (%s, %s, %s, %s, %s)"
                params = (doc, nom, tel, cor, cargo)
            
            self.db_manager.execute_query(q, params, fetch=False)
            QMessageBox.information(self, "Éxito", "Empleado guardado correctamente")
            self._nuevo_empleado()
            self._cargar_empleados()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

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