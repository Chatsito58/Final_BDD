from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

class LoginView(QtWidgets.QWidget):
    """Widget that handles user login."""

    authenticated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve().parent / 'ui' / 'login.ui'
        uic.loadUi(ui_path, self)

        # Access widgets defined in the .ui file
        self.user_input = self.findChild(QtWidgets.QLineEdit, 'usernameLineEdit')
        self.pass_input = self.findChild(QtWidgets.QLineEdit, 'passwordLineEdit')
        self.error_label = self.findChild(QtWidgets.QLabel, 'errorLabel')
        self.login_button = self.findChild(QtWidgets.QPushButton, 'loginButton')

        if self.login_button:
            self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        """Validate credentials and emit authenticated signal."""
        username = self.user_input.text() if self.user_input else ''
        password = self.pass_input.text() if self.pass_input else ''

        if not username or not password:
            if self.error_label:
                self.error_label.setText('Usuario y contraseña son obligatorios.')
            return

        if self.error_label:
            self.error_label.clear()

        # Here would normally be authentication logic with backend
        # For now we assume success when fields are not empty
        self.authenticated.emit(username)
