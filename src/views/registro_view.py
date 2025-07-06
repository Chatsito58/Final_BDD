import os
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
import hashlib

class RegistroDialog(QDialog):
    def __init__(self, db_manager, on_registration_success=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.on_registration_success = on_registration_success

        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'registro_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()

    def _setup_ui(self):
        self.registrar_button.clicked.connect(self._registrar_cliente)
        self.cancelar_button.clicked.connect(self.reject)

    def _registrar_cliente(self):
        documento = self.documento_edit.text().strip()
        nombre = self.nombre_edit.text().strip()
        telefono = self.telefono_edit.text().strip()
        direccion = self.direccion_edit.text().strip()
        correo = self.correo_edit.text().strip()

        if not all([documento, nombre, correo]):
            QMessageBox.warning(self, "Aviso", "Documento, nombre y correo son obligatorios.")
            return

        try:
            # Insertar en Cliente
            cliente_query = "INSERT INTO Cliente (documento, nombre, telefono, direccion, correo) VALUES (%s, %s, %s, %s, %s)"
            id_cliente = self.db_manager.insert(cliente_query, (documento, nombre, telefono, direccion, correo))

            if not id_cliente:
                QMessageBox.critical(self, "Error", "No se pudo registrar el cliente.")
                return

            # Insertar en Usuario (contraseña inicial es el documento hasheado)
            contrasena_hash = hashlib.sha256(documento.encode()).hexdigest()
            usuario_query = "INSERT INTO Usuario (nombre_usuario, contrasena_hash, id_rol, id_cliente) VALUES (%s, %s, %s, %s)"
            self.db_manager.insert(usuario_query, (correo, contrasena_hash, 6, id_cliente)) # Rol 6 para cliente

            QMessageBox.information(self, "Registro Exitoso", 
                                    f"¡Bienvenido {nombre}! Su cuenta ha sido creada.\nSu contraseña inicial es su número de documento: {documento}.\nPor favor, cámbiela al iniciar sesión por primera vez.")
            
            if self.on_registration_success:
                self.on_registration_success(correo)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar el cliente: {e}")