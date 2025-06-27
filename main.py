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
        'port': 3306,
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
        # Crear y mostrar vista de login
        login_view = LoginView(self.auth_manager)
        logger.info("Vista de login creada")
        
        if login_view.exec_() == QDialog.Accepted:
            user_data = login_view.user_data
            logger.info(f"Login exitoso para usuario: {user_data}")
            print(f"¡Login exitoso! Bienvenido {user_data['usuario']}")
            logger.info("Creando vista principal...")
            try:
                main_view = MainView(user_data['usuario'], user_data['rol'])
                logger.info("Vista principal creada, mostrando...")
                main_view.show()
                logger.info("Aplicación iniciada correctamente")
                sys.exit(app.exec_())
            except Exception as e:
                logger.error(f"Error al crear o mostrar la vista principal: {e}")
                QMessageBox.critical(None, "Error crítico", f"Ocurrió un error al mostrar la ventana principal:\n{e}")
                sys.exit(1)
        else:
            logger.info("Login cancelado por el usuario")
            sys.exit()

if __name__ == "__main__":
    logger.info("=== Iniciando aplicación de alquiler ===")
    app = AlquilerApp()
    app.run()
