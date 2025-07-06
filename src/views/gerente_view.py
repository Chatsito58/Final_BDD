import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox
from PyQt5.uic import loadUi
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
)

class GerenteView(QMainWindow):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._emp_sel = None

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'gerente_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_empleados_tab()

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