from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QTimer

from ..db_manager import DBManager


class MainView(QtWidgets.QMainWindow):
    """Main application window handling role based menus and logout."""

    logged_out = pyqtSignal()

    def __init__(self, username: str, role: str, parent=None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve().parents[2] / 'ui' / 'main_window.ui'
        uic.loadUi(ui_path, self)

        self._username = username
        self._role = role
        self._db_manager = DBManager()

        self._sync_timer = QTimer(self)
        self._sync_timer.timeout.connect(self._db_manager.sync_pending_reservations)
        self._sync_timer.start(5 * 60 * 1000)

        # Setup status bar information
        if self.statusBar():
            self.statusBar().showMessage(f"Usuario: {username} | Rol: {role}")

        # Access menus
        self.menu_reservas = self.findChild(QtWidgets.QMenu, 'menuReservas')
        self.menu_clientes = self.findChild(QtWidgets.QMenu, 'menuClientes')
        self.menu_vehiculos = self.findChild(QtWidgets.QMenu, 'menuVehiculos')
        self.menu_admin = self.findChild(QtWidgets.QMenu, 'menuAdministracion')

        # Add logout action under Administración
        self.logout_action = QtWidgets.QAction('Cerrar sesión', self)
        if self.menu_admin:
            self.menu_admin.addAction(self.logout_action)
        else:
            self.menuBar().addAction(self.logout_action)
        self.logout_action.triggered.connect(self.logout)

        self._apply_role_visibility(role)

    def _apply_role_visibility(self, role: str):
        """Show or hide menus depending on the user role."""
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(role.lower() == 'admin')

    def logout(self):
        """Emit logout signal and close the window."""
        self.logged_out.emit()
        self.close()
