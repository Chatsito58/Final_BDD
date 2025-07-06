import os
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.uic import loadUi

class ClienteView(QMainWindow):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'client_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_reservas_tab()

    def _setup_ui(self):
        # Conectar botones
        self.logout_button.clicked.connect(self.logout)

        # Actualizar estado de la conexión
        self.update_connection_status()

    def _setup_reservas_tab(self):
        self._cargar_reservas_cliente()

    def _cargar_reservas_cliente(self):
        self.reservas_list.clear()
        id_cliente = self.user_data.get("id_cliente")
        query = (
            "SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, a.valor, ra.saldo_pendiente, ra.abono, es.descripcion "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            "LEFT JOIN Estado_reserva es ON ra.id_estado_reserva = es.id_estado "
            "WHERE a.id_cliente = %s "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        params = (id_cliente,)
        reservas = self.db_manager.execute_query(query, params)

        if not reservas:
            self.reservas_list.addItem("No tienes reservas registradas")
            return

        for r in reservas:
            id_reserva, salida, entrada, id_vehiculo, modelo, placa, valor, saldo, abono, estado = r
            self.reservas_list.addItem(f"Reserva {id_reserva}: {modelo} ({placa}) - Salida: {salida} - Estado: {estado}")

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