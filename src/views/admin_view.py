import os
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.uic import loadUi

class AdminView(QMainWindow):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout

        # Cargar la interfaz de usuario desde el archivo .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'admin_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()

    def _setup_ui(self):
        # Configurar mensaje de bienvenida
        self.welcome_label.setText(f"Bienvenido administrador, {self.user_data.get('usuario', '')}")

        # Conectar botones
        self.logout_button.clicked.connect(self.logout)

        # Actualizar estado de la conexión
        self.update_connection_status()

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