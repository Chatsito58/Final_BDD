import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from PyQt5.QtWidgets import QApplication, QDialog
from src.db_manager import DBManager
from src.auth import AuthManager
from src.views.login_view import LoginView
from src.views.main_view import MainView

# Configuración centralizada de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)

class AlquilerApp:
    def __init__(self):
        # Inicializar gestores
        self.db_manager = DBManager()
        self.auth_manager = AuthManager(self.db_manager)

    def run(self):
        app = QApplication(sys.argv)
        # Crear y mostrar vista de login
        login_view = LoginView(self.auth_manager)
        if login_view.exec_() == QDialog.Accepted:
            user_data = login_view.user_data
            # Mensaje de bienvenida útil
            print(f"¡Login exitoso! Bienvenido {user_data['usuario']}")
            # Mostrar la ventana principal
            main_view = MainView(user_data['usuario'], user_data['rol'])
            main_view.show()
            sys.exit(app.exec_())
        else:
            sys.exit()

if __name__ == "__main__":
    app = AlquilerApp()
    app.run()
