import sys
import os
import logging
from dotenv import load_dotenv

# Configuración centralizada de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# --- PRUEBA DE CONEXIÓN ANTES DE IMPORTAR PyQt5 ---
try:
    import mysql.connector
    load_dotenv()
    config = {
        'host': os.getenv('DB_REMOTE_HOST'),
        'user': os.getenv('DB_REMOTE_USER'),
        'password': os.getenv('DB_REMOTE_PASSWORD'),
        'database': os.getenv('DB_REMOTE_NAME'),
        'port': os.getenv('DB_REMOTE_PORT'),
        'connection_timeout': 10,
    }
    print("[TEST-CONN-MAIN] Intentando conectar antes de importar PyQt5...")
    conn = mysql.connector.connect(**config)
    print("[TEST-CONN-MAIN] Conexión directa exitosa!")
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"[TEST-CONN-MAIN] Resultado SELECT 1: {result}")
    cursor.close()
    conn.close()
    print("[TEST-CONN-MAIN] Conexión cerrada correctamente.")
except Exception as e:
    print(f"[TEST-CONN-MAIN] Error de conexión directa: {e}")
    logger.error(f"[TEST-CONN-MAIN] Error de conexión directa: {e}")
    sys.exit(1)

# --- IMPORTS PyQt5 y módulos dependientes ---
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from src.db_manager import DBManager
from src.auth import AuthManager
from src.views.login_view import LoginView
from src.views.main_view import MainView
from src.views.ctk_views import (
    ClienteView, GerenteView, AdminView, EmpleadoView,
    EmpleadoVentasView, EmpleadoMantenimientoView, EmpleadoCajaView
)

MODERN_QSS = """
QMainWindow, QWidget {
    background-color: #18191A;
    color: #F5F6FA;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
}
QMenuBar, QMenu {
    background-color: #242526;
    color: #F5F6FA;
}
QMenuBar::item:selected, QMenu::item:selected {
    background: #3A86FF;
    color: white;
}
QTabWidget::pane {
    border: 1px solid #3A3B3C;
    border-radius: 8px;
    background: #18191A;
}
QTabBar::tab {
    background: #242526;
    color: #F5F6FA;
    border-radius: 8px;
    padding: 8px 20px;
    margin: 2px;
}
QTabBar::tab:selected {
    background: #3A86FF;
    color: white;
}
QPushButton {
    background-color: #3A86FF;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 0px;
    font-size: 15px;
}
QPushButton:hover {
    background-color: #265DAB;
}
QLineEdit, QComboBox, QSpinBox {
    background: #242526;
    color: #F5F6FA;
    border: 1px solid #3A3B3C;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 15px;
}
QStatusBar {
    background: #242526;
    color: #F5F6FA;
    border-top: 1px solid #3A3B3C;
}
"""

class AlquilerApp:
    def __init__(self):
        logger.info("Inicializando AlquilerApp...")
        # Inicializar gestores
        self.db_manager = DBManager()
        self.auth_manager = AuthManager(self.db_manager)
        logger.info("Gestores inicializados correctamente")

    def run(self):
        logger.info("Iniciando aplicación...")
        app = QApplication(sys.argv)
        app.setStyleSheet(MODERN_QSS)
        # Crear y mostrar vista de login
        def show_login():
            login_view = LoginView(self.auth_manager)
            logger.info("Vista de login creada")
            if login_view.exec_() == QDialog.Accepted:
                user_data = login_view.user_data
                logger.info(f"Login exitoso para usuario: {user_data}")
                print(f"¡Login exitoso! Bienvenido {user_data['usuario']}")
                self.show_role_view(user_data, show_login, self.db_manager, self.auth_manager)
            else:
                logger.info("Login cancelado por el usuario")
                sys.exit()
        show_login()

    def show_role_view(self, user_data, on_logout, db_manager, auth_manager):
        from PyQt5.QtCore import QTimer
        rol = (user_data.get('rol') or '').lower()
        tipo_empleado = (user_data.get('tipo_empleado') or '').lower() if user_data.get('tipo_empleado') else None
        username = user_data.get('usuario')
        app = QApplication.instance()
        def handle_logout():
            QTimer.singleShot(0, on_logout)
        view_kwargs = dict(db_manager=db_manager, auth_manager=auth_manager, app=app)
        if rol == 'admin':
            from src.views.main_view import AdminViewQt
            win = AdminViewQt(username, **view_kwargs)
            win.logged_out.connect(handle_logout)
            win.show()
            win.exec_() if hasattr(win, 'exec_') else app.exec_()
        elif rol == 'gerente':
            from src.views.main_view import GerenteViewQt
            win = GerenteViewQt(username, **view_kwargs)
            win.logged_out.connect(handle_logout)
            win.show()
            win.exec_() if hasattr(win, 'exec_') else app.exec_()
        elif rol == 'empleado':
            if not tipo_empleado and user_data.get('id_empleado'):
                query = "SELECT cargo FROM Empleado WHERE id_empleado = %s"
                params = (user_data['id_empleado'],)
                result = db_manager.execute_query(query, params)
                tipo_empleado = result[0][0].lower() if result else ""
            if tipo_empleado == 'ventas':
                from src.views.main_view import EmpleadoVentasViewQt
                win = EmpleadoVentasViewQt(username, **view_kwargs)
            elif tipo_empleado == 'mantenimiento':
                from src.views.main_view import EmpleadoMantenimientoViewQt
                win = EmpleadoMantenimientoViewQt(username, **view_kwargs)
            elif tipo_empleado == 'caja':
                from src.views.main_view import EmpleadoCajaViewQt
                win = EmpleadoCajaViewQt(username, **view_kwargs)
            else:
                from src.views.main_view import EmpleadoViewQt
                win = EmpleadoViewQt(username, **view_kwargs)
            win.logged_out.connect(handle_logout)
            win.show()
            win.exec_() if hasattr(win, 'exec_') else app.exec_()
        else:
            from src.views.ctk_views import ClienteView
            import threading
            
            def run_cliente_view():
                cliente_view = ClienteView(user_data, db_manager, on_logout)
                # Usar after() para manejar el logout de manera segura
                def safe_logout():
                    cliente_view._stop_status = True
                    cliente_view.withdraw()
                    # Usar QTimer para volver al login de manera segura
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(0, on_logout)
                cliente_view.on_logout = safe_logout
                cliente_view.mainloop()
            
            # Ejecutar la vista de cliente en un hilo separado
            cliente_thread = threading.Thread(target=run_cliente_view, daemon=True)
            cliente_thread.start()

if __name__ == "__main__":
    logger.info("=== Iniciando aplicación de alquiler ===")
    app = AlquilerApp()
    app.run()
