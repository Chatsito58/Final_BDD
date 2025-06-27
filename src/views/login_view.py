import os
import logging
from PyQt5.QtWidgets import (
    QDialog,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QLabel,
)
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

try:
    from .registro_ctk import RegistroCTk
except Exception as e:
    logger.error(f"Error importando RegistroCTk: {e}")
    RegistroCTk = None

class LoginView(QDialog):
    
    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        logger.info("Inicializando LoginView...")
        
        self.auth_manager = auth_manager
        self.user_data = None
        self._status_label = None
        self._stop_status = False
        
        try:
            # Cargar la interfaz con ruta absoluta
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ui_path = os.path.join(current_dir, '../../ui/login.ui')
            logger.info(f"Cargando UI desde: {ui_path}")
            loadUi(ui_path, self)
            
            # Obtener referencias a los widgets
            # Los nombres se corresponden con los definidos en el archivo .ui
            self.emailLineEdit = self.findChild(QLineEdit, 'emailLineEdit')
            self.passwordLineEdit = self.findChild(QLineEdit, 'passwordLineEdit')
            self.btn_login = self.findChild(QPushButton, 'btn_login')
            self.btn_register = self.findChild(QPushButton, 'btn_register')
            
            if not all([self.emailLineEdit, self.passwordLineEdit, self.btn_login]):
                logger.error("No se pudieron encontrar todos los widgets necesarios")
                raise Exception("Widgets no encontrados")
            
            # Conectar eventos
            self.btn_login.clicked.connect(self.attempt_login)
            if self.btn_register:
                self.btn_register.clicked.connect(self.open_registration)
            
            # Configurar la ventana
            self.setWindowTitle("Login - Sistema de Alquiler")
            self.setModal(True)
            
            # === ESTILO MODERNO Y FONDO OSCURO ===
            self.setStyleSheet('''
                QDialog {
                    background-color: #18191A;
                }
                QLabel {
                    color: #F5F6FA;
                    font-size: 15px;
                }
                QLineEdit {
                    background: #242526;
                    color: #F5F6FA;
                    border: 1px solid #3A3B3C;
                    border-radius: 8px;
                    padding: 6px 10px;
                    font-size: 15px;
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
            ''')
            
            # Agregar label de estado
            self._status_label = QLabel(self)
            self._status_label.setText("")
            self._status_label.setAlignment(Qt.AlignCenter)
            self._status_label.setStyleSheet("font-size: 15px; margin-bottom: 10px;")
            self.layout().insertWidget(0, self._status_label)
            self._update_status_label()
            self._start_status_updater()
            self.showMaximized()
            
            # Centrar y modernizar campos y botones
            for widget in [self.emailLineEdit, self.passwordLineEdit, self.btn_login, self.btn_register]:
                if widget:
                    widget.setMinimumWidth(320)
                    widget.setMaximumWidth(400)
                    widget.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 8px; margin: 10px auto;")
            for label in self.findChildren(QLabel):
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("color: #F5F6FA; font-size: 15px; margin: 0 auto;")
            self.layout().setAlignment(Qt.AlignCenter)
            
            logger.info("LoginView inicializada correctamente")
            
            # Registrar callback de desconexión para mostrar alerta inmediata
            try:
                db = getattr(self.auth_manager, 'db', None)
                if db is not None and hasattr(db, 'set_on_disconnect_callback'):
                    def mostrar_alerta_desconexion():
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.critical(self, "Desconexión detectada", "Ocurrió una desconexión del servidor principal y ahora estás en modo offline. Puedes seguir trabajando y los cambios se sincronizarán automáticamente cuando vuelva la conexión.")
                    db.set_on_disconnect_callback(mostrar_alerta_desconexion)
            except Exception as e:
                logger.error(f"No se pudo registrar el callback de desconexión: {e}")
            
        except Exception as e:
            logger.error(f"Error inicializando LoginView: {e}")
            raise
        
    def attempt_login(self):
        logger.info("Intento de login iniciado")
        correo = self.emailLineEdit.text().strip()
        contrasena = self.passwordLineEdit.text().strip()

        logger.info(f"Credenciales ingresadas - Email: {correo}")

        if not correo or not contrasena:
            logger.warning("Campos vacíos en el login")
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return

        try:
            logger.info("Intentando autenticar usuario...")
            user_data = self.auth_manager.login(correo, contrasena)
            logger.info(f"Resultado de autenticación: {user_data}")
        except Exception as e:
            logger.error(f"Error en login: {e}")
            # Si la app ya está en modo offline, no mostrar otro mensaje (ya lo muestra el callback global)
            db = getattr(self.auth_manager, 'db', None)
            if db is not None and not getattr(db, 'offline', False):
                QMessageBox.critical(
                    self,
                    "Error de base de datos",
                    "Ocurrió un problema al conectar con la base de datos."
                )
            return

        if user_data:
            self.user_data = user_data
            logger.info(f"Login exitoso para usuario: {user_data['usuario']}")
            self.accept()
        else:
            logger.warning("Credenciales incorrectas")
            QMessageBox.warning(self, "Error", "Credenciales incorrectas")
    
    def open_registration(self):
        if RegistroCTk is None:
            QMessageBox.warning(self, "Error", "Módulo de registro no disponible")
            return
        try:
            self._stop_status = True
            self.hide()
            def volver_a_login():
                self.show()
                self._stop_status = False
                self._start_status_updater()
            registro = RegistroCTk(self.auth_manager.db, on_back=volver_a_login)
            registro.mainloop()
            self.show()
            self._stop_status = False
            self._start_status_updater()
        except Exception as e:
            logger.error(f"Error abriendo registro: {e}")
            QMessageBox.critical(self, "Error", f"Error al abrir registro: {e}")

    def _update_status_label(self):
        online = not getattr(self.auth_manager.db, 'offline', False)
        emoji = "🟢" if online else "🔴"
        estado = "ONLINE" if online else "OFFLINE"
        if self._status_label:
            self._status_label.setText(f"{emoji} Estado: {estado}")
            color = "#00FF00" if online else "#FF5555"
            self._status_label.setStyleSheet(f"color: {color}; font-size: 15px; margin-bottom: 10px;")

    def _start_status_updater(self):
        import threading, time
        def updater():
            while not self._stop_status:
                self._update_status_label()
                time.sleep(2)
        t = threading.Thread(target=updater, daemon=True)
        t.start()

    def closeEvent(self, event):
        self._stop_status = True
        super().closeEvent(event)
