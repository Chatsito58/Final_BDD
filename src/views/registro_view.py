from pathlib import Path
from PyQt5 import QtWidgets, uic
from ..triple_db_manager import TripleDBManager


class RegistroView(QtWidgets.QDialog):
    """Formulario simple para registrar clientes."""

    def __init__(self, db_manager: TripleDBManager, parent=None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve().parents[2] / 'ui' / 'registro.ui'
        uic.loadUi(ui_path, self)

        self.db_manager = db_manager

        # Widgets
        self.documento_edit = self.findChild(QtWidgets.QLineEdit, 'documentoLineEdit')
        self.nombre_edit = self.findChild(QtWidgets.QLineEdit, 'nombreLineEdit')
        self.telefono_edit = self.findChild(QtWidgets.QLineEdit, 'telefonoLineEdit')
        self.correo_edit = self.findChild(QtWidgets.QLineEdit, 'correoLineEdit')
        self.registrar_btn = self.findChild(QtWidgets.QPushButton, 'btn_registrar')

        if self.registrar_btn:
            self.registrar_btn.clicked.connect(self.registrar_cliente)

    def registrar_cliente(self):
        """Insertar un nuevo cliente después de validar los datos."""
        documento = self.documento_edit.text().strip()
        nombre = self.nombre_edit.text().strip()
        telefono = self.telefono_edit.text().strip()
        correo = self.correo_edit.text().strip()

        if not documento or not nombre or not correo:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Complete todos los campos requeridos')
            return

        # Detectar motor activo y ajustar placeholder
        is_sqlite = hasattr(self.db_manager, 'offline') and self.db_manager.offline
        if is_sqlite:
            count_q = 'SELECT COUNT(*) FROM Cliente WHERE correo = ?'
            params = (correo,)
        else:
            count_q = 'SELECT COUNT(*) FROM Cliente WHERE correo = %s'
            params = (correo,)
        result = self.db_manager.execute_query(count_q, params)
        if result and result[0][0] > 0:
            QtWidgets.QMessageBox.warning(self, 'Error', 'El correo ya está registrado')
            return

        if is_sqlite:
            insert_q = (
                'INSERT INTO Cliente (documento, nombre, telefono, correo) '
                'VALUES (?, ?, ?, ?)'
            )
        else:
            insert_q = (
                'INSERT INTO Cliente (documento, nombre, telefono, correo) '
                'VALUES (%s, %s, %s, %s)'
            )
        params = (documento, nombre, telefono, correo)
        try:
            self.db_manager.execute_query(insert_q, params, fetch=False)
            QtWidgets.QMessageBox.information(self, 'Éxito', 'Registro completado')
            self.accept()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, 'Error', f'No se pudo registrar: {exc}')

