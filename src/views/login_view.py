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
            
            self.auth_manager = auth_manager
            self.user_data = None
            
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
            
            logger.info("LoginView inicializada correctamente")
            
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
            QMessageBox.critical(
                self,
                "Error de base de datos",
                "Ocurri\u00f3 un problema al conectar con la base de datos."
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
            registro = RegistroCTk(self.auth_manager.db)
            registro.mainloop()
        except Exception as e:
            logger.error(f"Error abriendo registro: {e}")
            QMessageBox.critical(self, "Error", f"Error al abrir registro: {e}")
