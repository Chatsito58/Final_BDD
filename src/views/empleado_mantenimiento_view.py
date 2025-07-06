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