from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi


class LoginView(QDialog):
    # Definir una constante Accepted
    Accepted = 1

    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        loadUi('ui/login.ui', self)
        self.auth_manager = auth_manager
        self.user_data = None

        # Conectar eventos
        self.btn_login.clicked.connect(self.attempt_login)
        self.lbl_registro.linkActivated.connect(self.open_registration)

    def attempt_login(self):
        usuario = self.txt_usuario.text().strip()
        contrasena = self.txt_contrasena.text().strip()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return

        user_data = self.auth_manager.login(usuario, contrasena)

        if user_data:
            self.user_data = user_data
            self.accept()  # Cierra el di\u00e1logo con resultado Accepted
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas")

    def open_registration(self):
        # TODO: Implementar apertura de vista de registro
        print("Funcionalidad de registro a implementar")
        QMessageBox.information(self, "Registro", "Funcionalidad de registro en desarrollo")
