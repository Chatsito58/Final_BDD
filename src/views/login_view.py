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


class LoginView(QDialog):

    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        logger.info("Inicializando LoginView...")

        self.auth_manager = auth_manager
        self.user_data = None
        self._status_label1 = None
        self._status_label2 = None
        self._stop_status = False
        self._modern_stylesheet = """
            QDialog, QWidget {
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
        """

        try:
            # Cargar la interfaz con ruta absoluta
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ui_path = os.path.join(current_dir, "../../ui/login.ui")
            logger.info(f"Cargando UI desde: {ui_path}")
            loadUi(ui_path, self)
            self.setStyleSheet(self._modern_stylesheet)

            # Obtener referencias a los widgets
            # Los nombres se corresponden con los definidos en el archivo .ui
            self.emailLineEdit = self.findChild(QLineEdit, "emailLineEdit")
            self.passwordLineEdit = self.findChild(QLineEdit, "passwordLineEdit")
            self.btn_login = self.findChild(QPushButton, "btn_login")
            self.btn_register = self.findChild(QPushButton, "btn_register")

            if not all([self.emailLineEdit, self.passwordLineEdit, self.btn_login]):
                logger.error("No se pudieron encontrar todos los widgets necesarios")
                raise Exception("Widgets no encontrados")

            # Conectar eventos
            self.btn_login.clicked.connect(self.attempt_login)
            self.btn_register.clicked.connect(self._open_registration_dialog)

            # Configurar la ventana
            self.setWindowTitle("Inicio de Sesión - Sistema de Alquiler de Vehículos")
            self.setModal(True)

            # Agregar labels de estado de conexión (remoto1/remoto2) arriba del todo
            self._status_label1 = QLabel(self)
            self._status_label1.setAlignment(Qt.AlignCenter)
            self._status_label1.setStyleSheet("font-size: 15px; margin-bottom: 2px;")
            self._status_label2 = QLabel(self)
            self._status_label2.setAlignment(Qt.AlignCenter)
            self._status_label2.setStyleSheet("font-size: 15px; margin-bottom: 10px;")
            # Insertar en orden inverso para que label1 quede arriba
            self.layout().insertWidget(0, self._status_label2)
            self.layout().insertWidget(0, self._status_label1)
            self._update_status_labels()
            self._start_status_updater()
            self.showMaximized()

            # Centrar y modernizar campos y botones
            for widget in [
                self.emailLineEdit,
                self.passwordLineEdit,
                self.btn_login,
                self.btn_register,
            ]:
                if widget:
                    widget.setMinimumWidth(320)
                    widget.setMaximumWidth(400)
            for label in self.findChildren(QLabel):
                label.setAlignment(Qt.AlignCenter)
            self.layout().setAlignment(Qt.AlignCenter)

            logger.info("LoginView inicializada correctamente")

            # Registrar callback de desconexión para mostrar alerta inmediata
            try:
                db = getattr(self.auth_manager, "db", None)
                if db is not None and hasattr(db, "set_on_disconnect_callback"):

                    def mostrar_alerta_desconexion():
                        from PyQt5.QtWidgets import QMessageBox

                        QMessageBox.critical(
                            self,
                            "Desconexión detectada",
                            "Ocurrió una desconexión del servidor principal y ahora estás en modo offline. Puedes seguir trabajando y los cambios se sincronizarán automáticamente cuando vuelva la conexión.",
                        )

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
            logger.info("Verificando si el correo existe...")
            correo_existe = self.auth_manager.verificar_correo_existe(correo)

            if not correo_existe:
                logger.info(f"Correo {correo} no está registrado")
                reply = QMessageBox.question(
                    self,
                    "Usuario no registrado",
                    f"El correo '{correo}' no está registrado en el sistema.\n\n¿Deseas registrarte como nuevo cliente?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )

            logger.info("Correo existe, intentando autenticar usuario...")
            user_data = self.auth_manager.login(correo, contrasena)
            logger.info(f"Resultado de autenticación: {user_data}")
        except Exception as e:
            logger.error(f"Error en login: {e}")
            db = getattr(self.auth_manager, "db", None)
            if db is not None and not getattr(db, "offline", False):
                QMessageBox.critical(
                    self,
                    "Error de base de datos",
                    "Ocurrió un problema al conectar con la base de datos.",
                )
            return

        if user_data:
            self.user_data = user_data
            logger.info(f"Login exitoso para usuario: {user_data['usuario']}")
            self.accept()
        else:
            logger.warning("Contraseña incorrecta")
            QMessageBox.warning(self, "Error", "Contraseña incorrecta")

    def _open_registration_dialog(self):
        from src.views.registro_view import RegistroDialog

        reg_dialog = RegistroDialog(
            self.auth_manager.db, on_registration_success=self._on_registration_success
        )
        reg_dialog.exec_()

    def _on_registration_success(self, registered_email):
        self.emailLineEdit.setText(registered_email)
        self.passwordLineEdit.clear()
        self.emailLineEdit.setFocus()

    def _update_status_labels(self):
        db = getattr(self.auth_manager, "db", None)
        if db is None:
            return
        if hasattr(db, "ping_remotes"):
            try:
                db.ping_remotes()
            except Exception as exc:
                logger.error(f"Error pinging remotes: {exc}")
        r1 = getattr(
            db, "is_remote1_active", lambda: getattr(db, "remote1_active", False)
        )()
        r2 = getattr(
            db, "is_remote2_active", lambda: getattr(db, "remote2_active", False)
        )()
        emoji1 = "🟢" if r1 else "🔴"
        emoji2 = "🟢" if r2 else "🔴"
        estado1 = "ONLINE" if r1 else "OFFLINE"
        estado2 = "ONLINE" if r2 else "OFFLINE"
        if self._status_label1:
            color1 = "#00FF00" if r1 else "#FF5555"
            self._status_label1.setText(f"{emoji1} Remote1: {estado1}")
            self._status_label1.setStyleSheet(
                f"color: {color1}; font-size: 15px; margin-bottom: 2px;"
            )
        if self._status_label2:
            color2 = "#00FF00" if r2 else "#FF5555"
            self._status_label2.setText(f"{emoji2} Remote2: {estado2}")
            self._status_label2.setStyleSheet(
                f"color: {color2}; font-size: 15px; margin-bottom: 10px;"
            )

    def _start_status_updater(self):
        import threading, time

        def updater():
            while not self._stop_status:
                self._update_status_labels()
                time.sleep(2)

        t = threading.Thread(target=updater, daemon=True)
        t.start()

    def closeEvent(self, event):
        self._stop_status = True
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        # Reaplicar el estilo moderno cada vez que se muestre la ventana
        self.setStyleSheet(self._modern_stylesheet)
