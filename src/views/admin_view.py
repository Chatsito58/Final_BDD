import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.uic import loadUi
import hashlib

class AdminView(QMainWindow):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._gerente_sel = None
        self._sede_sel = None

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'admin_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_gerentes_tab()
        self._setup_sedes_tab()
        self._setup_monitoreo_tab()
        self._setup_sql_libre_tab()
        self._setup_cambiar_contrasena_tab()

    def _setup_ui(self):
        # Configurar mensaje de bienvenida
        self.welcome_label.setText(f"Bienvenido administrador, {self.user_data.get('usuario', '')}")

        # Conectar botones
        self.logout_button.clicked.connect(self.logout)

        # Actualizar estado de la conexión
        self.update_connection_status()

    def _setup_gerentes_tab(self):
        self.nuevo_gerente_button.clicked.connect(self._nuevo_gerente)
        self.guardar_gerente_button.clicked.connect(self._guardar_gerente)
        self.eliminar_gerente_button.clicked.connect(self._eliminar_gerente)
        self.gerentes_list.itemSelectionChanged.connect(self._seleccionar_gerente)
        self._cargar_sucursales_combo()
        self._cargar_gerentes()

    def _cargar_sucursales_combo(self):
        self.sucursal_gerente_combo.clear()
        sucursales = self.db_manager.execute_query("SELECT id_sucursal, nombre FROM Sucursal") or []
        self.sucursales_map = {s[1]: s[0] for s in sucursales}
        self.sucursal_gerente_combo.addItems(list(self.sucursales_map.keys()))

    def _cargar_gerentes(self):
        self.gerentes_list.clear()
        rows = self.db_manager.execute_query(
            "SELECT id_empleado, nombre, correo, id_sucursal FROM Empleado WHERE cargo = 'Gerente'"
        )
        if rows:
            for r in rows:
                id_e, nombre, correo, id_sucursal = r
                sucursal_nombre = next((name for name, id_s in self.sucursales_map.items() if id_s == id_sucursal), "Desconocida")
                self.gerentes_list.addItem(f"{id_e} | {nombre} | {correo} | {sucursal_nombre}")

    def _seleccionar_gerente(self):
        selected_items = self.gerentes_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        self._gerente_sel = int(selected_item.text().split("|")[0].strip())
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, correo, id_sucursal FROM Empleado WHERE id_empleado = %s",
            (self._gerente_sel,),
        )
        if row:
            doc, nom, tel, cor, id_sucursal = row[0]
            self.doc_gerente_edit.setText(doc or "")
            self.nombre_gerente_edit.setText(nom or "")
            self.telefono_gerente_edit.setText(tel or "")
            self.correo_gerente_edit.setText(cor or "")
            sucursal_nombre = next((name for name, id_s in self.sucursales_map.items() if id_s == id_sucursal), "")
            self.sucursal_gerente_combo.setCurrentText(sucursal_nombre)

    def _nuevo_gerente(self):
        self._gerente_sel = None
        self.doc_gerente_edit.clear()
        self.nombre_gerente_edit.clear()
        self.telefono_gerente_edit.clear()
        self.correo_gerente_edit.clear()
        self.sucursal_gerente_combo.setCurrentIndex(0)

    def _guardar_gerente(self):
        doc = self.doc_gerente_edit.text().strip()
        nom = self.nombre_gerente_edit.text().strip()
        tel = self.telefono_gerente_edit.text().strip()
        cor = self.correo_gerente_edit.text().strip()
        sucursal_nombre = self.sucursal_gerente_combo.currentText()
        id_sucursal = self.sucursales_map.get(sucursal_nombre)

        if not all([doc, nom, cor, sucursal_nombre]):
            QMessageBox.warning(self, "Aviso", "Documento, nombre, correo y sucursal son obligatorios.")
            return

        try:
            if self._gerente_sel:
                q = "UPDATE Empleado SET documento=%s, nombre=%s, telefono=%s, correo=%s, id_sucursal=%s WHERE id_empleado=%s"
                params = (doc, nom, tel, cor, id_sucursal, self._gerente_sel)
            else:
                q = "INSERT INTO Empleado (documento, nombre, telefono, correo, cargo, id_sucursal, id_tipo_documento, id_tipo_empleado) VALUES (%s, %s, %s, %s, 'Gerente', %s, 1, 2)"
                params = (doc, nom, tel, cor, id_sucursal)
            
            self.db_manager.execute_query(q, params, fetch=False)
            QMessageBox.information(self, "Éxito", "Gerente guardado correctamente.")
            self._nuevo_gerente()
            self._cargar_gerentes()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Error al guardar el gerente: {exc}")

    def _eliminar_gerente(self):
        if not self._gerente_sel:
            QMessageBox.warning(self, "Aviso", "Seleccione un gerente para eliminar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Eliminación', 
                                     "¿Está seguro que desea eliminar este gerente?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            self.db_manager.delete("DELETE FROM Empleado WHERE id_empleado = %s", (self._gerente_sel,))
            QMessageBox.information(self, "Éxito", "Gerente eliminado correctamente.")
            self._nuevo_gerente()
            self._cargar_gerentes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar el gerente: {e}")

    def _setup_sedes_tab(self):
        self.nuevo_sede_button.clicked.connect(self._nuevo_sede)
        self.guardar_sede_button.clicked.connect(self._guardar_sede)
        self.eliminar_sede_button.clicked.connect(self._eliminar_sede)
        self.sedes_list.itemSelectionChanged.connect(self._seleccionar_sede)
        self._cargar_sedes()

    def _cargar_sedes(self):
        self.sedes_list.clear()
        rows = self.db_manager.execute_query("SELECT id_sucursal, nombre, direccion, telefono FROM Sucursal") or []
        if rows:
            for r in rows:
                self.sedes_list.addItem(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")

    def _seleccionar_sede(self):
        selected_items = self.sedes_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        self._sede_sel = int(selected_item.text().split("|")[0].strip())
        row = self.db_manager.execute_query(
            f"SELECT nombre, direccion, telefono, gerente, id_codigo_postal FROM Sucursal WHERE id_sucursal = %s",
            (self._sede_sel,),
        )
        if row:
            nombre, direccion, telefono, gerente, id_codigo_postal = row[0]
            self.nombre_sede_edit.setText(nombre or "")
            self.direccion_sede_edit.setText(direccion or "")
            self.telefono_sede_edit.setText(telefono or "")
            self.gerente_sede_edit.setText(gerente or "")
            self.codigo_postal_sede_edit.setText(str(id_codigo_postal) or "")

    def _nuevo_sede(self):
        self._sede_sel = None
        self.nombre_sede_edit.clear()
        self.direccion_sede_edit.clear()
        self.telefono_sede_edit.clear()
        self.gerente_sede_edit.clear()
        self.codigo_postal_sede_edit.clear()

    def _guardar_sede(self):
        nombre = self.nombre_sede_edit.text().strip()
        direccion = self.direccion_sede_edit.text().strip()
        telefono = self.telefono_sede_edit.text().strip()
        gerente = self.gerente_sede_edit.text().strip()
        codigo_postal_str = self.codigo_postal_sede_edit.text().strip()

        if not all([nombre, direccion, telefono, gerente, codigo_postal_str]):
            QMessageBox.warning(self, "Aviso", "Todos los campos son obligatorios.")
            return

        try:
            codigo_postal = int(codigo_postal_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Código Postal inválido. Ingrese un número entero.")
            return

        try:
            if self._sede_sel:
                self.db_manager.update_sucursal(self._sede_sel, nombre, direccion, telefono, gerente, codigo_postal)
            else:
                self.db_manager.create_sucursal(nombre, direccion, telefono, gerente, codigo_postal)
            
            QMessageBox.information(self, "Éxito", "Sede guardada correctamente.")
            self._nuevo_sede()
            self._cargar_sedes()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Error al guardar la sede: {exc}")

    def _eliminar_sede(self):
        if not self._sede_sel:
            QMessageBox.warning(self, "Aviso", "Seleccione una sede para eliminar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Eliminación', 
                                     "¿Está seguro que desea eliminar esta sede?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            self.db_manager.delete_sucursal(self._sede_sel)
            QMessageBox.information(self, "Éxito", "Sede eliminada correctamente.")
            self._nuevo_sede()
            self._cargar_sedes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar la sede: {e}")

    def _setup_monitoreo_tab(self):
        self.forzar_sincronizacion_button.clicked.connect(self._forzar_sincronizacion)
        self._actualizar_estado_monitoreo()

    def _actualizar_estado_monitoreo(self):
        status1 = "Online" if self.db_manager.is_remote1_active() else "Offline"
        status2 = "Online" if self.db_manager.is_remote2_active() else "Offline"
        self.status_remota1_label.setText(f"BD Remota 1: {status1}")
        self.status_remota2_label.setText(f"BD Remota 2: {status2}")

        pending_ops = self.db_manager.fetch_retry_queue()
        self.operaciones_pendientes_label.setText(f"Operaciones Pendientes: {len(pending_ops)}")

    def _forzar_sincronizacion(self):
        try:
            self.db_manager.retry_pending()
            QMessageBox.information(self, "Sincronización", "Sincronización forzada completada.")
            self._actualizar_estado_monitoreo()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al forzar sincronización: {e}")

    def _setup_sql_libre_tab(self):
        self.ejecutar_sql_button.clicked.connect(self._ejecutar_sql_libre)

    def _ejecutar_sql_libre(self):
        query = self.sql_query_text.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Aviso", "Ingrese una consulta SQL.")
            return

        try:
            # Limpiar tabla de resultados
            self.sql_results_table.clear()
            self.sql_results_table.setRowCount(0)
            self.sql_results_table.setColumnCount(0)

            # Ejecutar la consulta
            if query.lower().startswith("select"):
                rows, headers = self.db_manager.execute_query_with_headers(query)
                
                self.sql_results_table.setRowCount(0) # Clear existing rows
                self.sql_results_table.setColumnCount(0) # Clear existing columns

                if headers:
                    self.sql_results_table.setColumnCount(len(headers))
                    self.sql_results_table.setHorizontalHeaderLabels(headers)
                    # Auto-resize columns to content and stretch last section
                    self.sql_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                    self.sql_results_table.horizontalHeader().setStretchLastSection(True)
                
                if rows:
                    self.sql_results_table.setRowCount(len(rows))
                    for i, row_data in enumerate(rows):
                        for j, item in enumerate(row_data):
                            self.sql_results_table.setItem(i, j, QTableWidgetItem(str(item)))
                else:
                    QMessageBox.information(self, "Resultado", "Consulta SELECT ejecutada, no se encontraron resultados.")
                    # Clear headers if no rows to ensure a clean state
                    self.sql_results_table.setColumnCount(0)
            else:
                # Para INSERT, UPDATE, DELETE, etc.
                self.db_manager.execute_query(query, fetch=False)
                QMessageBox.information(self, "Éxito", "Consulta SQL ejecutada correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al ejecutar SQL: {e}")

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