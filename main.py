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

# ---------------------------------------------------------------------------
# Connection logging setup
# ---------------------------------------------------------------------------
def setup_connection_logging():
    """Configure logging for remote connection status changes."""
    conn_logger = logging.getLogger("connection_changes")
    conn_logger.setLevel(logging.INFO)
    if not any(isinstance(h, logging.FileHandler) for h in conn_logger.handlers):
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler = logging.FileHandler("connection.log")
        handler.setFormatter(formatter)
        conn_logger.addHandler(handler)
    return conn_logger

# --- PRUEBA DE CONEXIÓN ANTES DE IMPORTAR PyQt5 ---
offline_mode = False
try:
    import mysql.connector
    load_dotenv()
    config = {
        'host': os.getenv('DB_REMOTE_HOST'),
        'user': os.getenv('DB_REMOTE_USER'),
        'password': os.getenv('DB_REMOTE_PASSWORD'),
        'database': os.getenv('DB_REMOTE_NAME'),
        'port': os.getenv('DB_REMOTE_PORT'),
        'connection_timeout': 4,
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
    offline_mode = True
    print(f"[TEST-CONN-MAIN] Error de conexión directa: {e}")
    logger.error(f"[TEST-CONN-MAIN] Error de conexión directa: {e}")
    print("[TEST-CONN-MAIN] Se continuará en modo offline")

# --- IMPORTS PyQt5 y módulos dependientes ---
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from src.triple_db_manager import TripleDBManager
from src.backup_manager import BackupManager
from src.auth import AuthManager
from src.views.login_view import LoginView
from src.views.client_view import ClienteView
from src.views.admin_view import AdminView
from src.views.gerente_view import GerenteView
from src.views.empleado_ventas_view import EmpleadoVentasView
from src.views.empleado_caja_view import EmpleadoCajaView
from src.views.empleado_mantenimiento_view import EmpleadoMantenimientoView
from src.styles import MODERN_QSS


class AlquilerApp:
    def __init__(self):
        logger.info("Inicializando AlquilerApp...")
        # Setup backup manager and create startup backup
        self.backup_manager = BackupManager(os.getenv("LOCAL_DB_PATH", "local.db"))
        try:
            self.backup_manager.backup_on_startup()
        except Exception as exc:
            logger.error("Error running startup backup: %s", exc)

        # Inicializar gestores
        setup_connection_logging()
        self.db_manager = TripleDBManager()
        self.db_manager.ping_remotes()
        self.offline = offline_mode or self.db_manager.offline
        if self.offline:
            logger.warning("Trabajando en modo offline")
        if hasattr(self.db_manager, "start_worker"):
            # Iniciar hilo de sincronización en segundo plano si está disponible
            self.db_manager.start_worker()
        if hasattr(self.db_manager, "update_maintenance_states"):
            try:
                self.db_manager.update_maintenance_states()
            except Exception as exc:
                logger.error("Error updating maintenance states: %s", exc)
        self.auth_manager = AuthManager(self.db_manager)
        logger.info("Gestores inicializados correctamente")

    def _cleanup(self):
        """Stop background services before exiting."""
        if hasattr(self, "backup_manager"):
            try:
                self.backup_manager.backup_on_shutdown()
            except Exception as exc:  # pragma: no cover - cleanup errors
                logger.error("Error during shutdown backup: %s", exc)
        if hasattr(self.db_manager, "stop_worker"):
            try:
                self.db_manager.stop_worker()
            except Exception as exc:  # pragma: no cover - cleanup errors
                logger.error("Error stopping worker: %s", exc)

    def run(self):
        logger.info("Iniciando aplicación...")
        app = QApplication(sys.argv)
        app.setStyleSheet(MODERN_QSS)
        if self.offline:
            QMessageBox.warning(
                None,
                "Modo offline",
                "No se pudo conectar con el servidor. La aplicación funcionará en modo offline.",
            )
        # Crear y mostrar vista de login
        def show_login():
            login_view = LoginView(self.auth_manager)
            logger.info("Vista de login creada")
            result = login_view.exec_()
            if result == QDialog.Accepted:
                user_data = login_view.user_data
                logger.info(f"Login exitoso para usuario: {user_data}")
                print(f"¡Login exitoso! Bienvenido {user_data['usuario']}")
                self.show_role_view(user_data, show_login, self.db_manager, self.auth_manager)
            else:
                logger.info("Login cancelado por el usuario - cerrando aplicación")
                # Cerrar completamente la aplicación cuando se rechaza el login
                self._cleanup()
                app.quit()
                sys.exit(0)
        try:
            show_login()
        finally:
            self._cleanup()

    def show_role_view(self, user_data, on_logout, db_manager, auth_manager):
        rol = (user_data.get('rol') or '').lower()
        tipo_empleado = (user_data.get('tipo_empleado') or '').lower() if user_data.get('tipo_empleado') else None
        def handle_logout():
            # For CTk (Tkinter based) windows we can call the callback directly
            # since they do not share the Qt event loop. Using QTimer.singleShot
            # here delays the re-display of the login dialog after closing the
            # admin window. When running a Qt based view this still allows the
            # callback to be executed safely in the Qt event loop.
            on_logout()
        if rol == 'admin':
            logger.debug("Opening AdminView for %s", user_data.get('usuario'))
            try:
                self.win = AdminView(user_data, db_manager, handle_logout)
                self.win.show()
            except Exception:
                logger.exception("Failed to open %s view", rol)
                QMessageBox.critical(None, "Error", str(sys.exc_info()[1]))
        elif rol == 'gerente':
            logger.debug("Opening GerenteView for %s", user_data.get('usuario'))
            try:
                self.win = GerenteView(user_data, db_manager, handle_logout)
                self.win.show()
            except Exception:
                logger.exception("Failed to open %s view", rol)
                QMessageBox.critical(None, "Error", str(sys.exc_info()[1]))
        elif rol == 'empleado':
            if not tipo_empleado and user_data.get('id_empleado'):
                query = "SELECT cargo FROM Empleado WHERE id_empleado = %s"
                params = (user_data['id_empleado'],)
                result = db_manager.execute_query(query, params)
                tipo_empleado = result[0][0].lower() if result and len(result) > 0 else ""
            if tipo_empleado == 'ventas':
                logger.debug("Opening EmpleadoVentasView for %s", user_data.get('usuario'))
                self.win = EmpleadoVentasView(user_data, db_manager, handle_logout)
                self.win.show()
            elif tipo_empleado == 'mantenimiento':
                logger.debug("Opening EmpleadoMantenimientoView for %s", user_data.get('usuario'))
                self.win = EmpleadoMantenimientoView(user_data, db_manager, handle_logout)
                self.win.show()
            elif tipo_empleado == 'caja':
                logger.debug("Opening EmpleadoCajaView for %s", user_data.get('usuario'))
                self.win = EmpleadoCajaView(user_data, db_manager, handle_logout)
                self.win.show()
            else:
                QMessageBox.warning(None, "Error", "Tipo de empleado desconocido")
                handle_logout()
                return
        else:
            from src.views.client_view import ClienteView
            logger.debug("Opening ClienteView for %s", user_data.get('usuario'))
            try:
                self.win = ClienteView(user_data, db_manager, on_logout)
                self.win.show()
            except Exception:
                logger.exception("Failed to open %s view", rol or 'cliente')
                QMessageBox.critical(None, "Error", str(sys.exc_info()[1]))

if __name__ == "__main__":
    logger.info("=== Iniciando aplicación de alquiler ===")
    app = AlquilerApp()
    app.run()
