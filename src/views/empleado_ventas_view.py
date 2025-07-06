import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox
from PyQt5.uic import loadUi

class EmpleadoVentasView(QMainWindow):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._cliente_sel = None

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'empleado_ventas_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_clientes_tab()

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