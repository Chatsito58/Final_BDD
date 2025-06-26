import sys
from PyQt5.QtWidgets import QApplication
from src.db import DBManager
from src.auth import AuthManager
from src.views.login_view import LoginView
from src.views.main_view import MainView


class AlquilerApp:
    def __init__(self):
        # Inicializar gestores
        self.db_manager = DBManager()
        self.auth_manager = AuthManager(self.db_manager)

    def run(self):
        app = QApplication(sys.argv)

        # Crear y mostrar vista de login
        login_view = LoginView(self.auth_manager)

        if login_view.exec_() == LoginView.Accepted:
            user_data = login_view.user_data
            print(f"\u00a1Login exitoso! Bienvenido {user_data['usuario']}")
            print(f"Rol: {user_data['rol']}")
            print(f"ID Cliente: {user_data.get('id_cliente', 'N/A')}")
            print(f"ID Empleado: {user_data.get('id_empleado', 'N/A')}")

            # Mostrar la ventana principal
            main_view = MainView(user_data['usuario'], user_data['rol'])
            main_view.show()
            sys.exit(app.exec_())
        else:
            print("Aplicaci\u00f3n cerrada")
            sys.exit()


if __name__ == "__main__":
    app = AlquilerApp()
    app.run()
