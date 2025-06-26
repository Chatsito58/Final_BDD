import os
from PyQt5.QtWidgets import QDialog, QMessageBox, QPushButton, QLineEdit, QLabel
from PyQt5.uic import loadUi

class LoginView(QDialog):
    Accepted = 1
    
    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        
        # Cargar la interfaz con ruta absoluta
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, '../../ui/login.ui')
        loadUi(ui_path, self)
        
        # Obtener referencias a los widgets
        # Los nombres se corresponden con los definidos en el archivo .ui
        self.usernameLineEdit = self.findChild(QLineEdit, 'usernameLineEdit')
        self.passwordLineEdit = self.findChild(QLineEdit, 'passwordLineEdit')
        self.btn_login = self.findChild(QPushButton, 'btn_login')
        self.lbl_registro = self.findChild(QLabel, 'lbl_registro')
        
        self.auth_manager = auth_manager
        self.user_data = None
        
        # Conectar eventos
        self.btn_login.clicked.connect(self.attempt_login)
        if hasattr(self, 'lbl_registro') and self.lbl_registro:
            self.lbl_registro.linkActivated.connect(self.open_registration)
        
    def attempt_login(self):
        usuario = self.usernameLineEdit.text().strip()
        contrasena = self.passwordLineEdit.text().strip()
        
        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
            
        user_data = self.auth_manager.login(usuario, contrasena)
        
        if user_data:
            self.user_data = user_data
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas")
    
    def open_registration(self):
        print("Funcionalidad de registro a implementar")
        QMessageBox.information(self, "Registro", "Funcionalidad de registro en desarrollo")
