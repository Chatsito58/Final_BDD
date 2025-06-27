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
        self._sync_timer.timeout.connect(self._sync_and_update_status)
        self._sync_timer.start(5 * 60 * 1000)
        self._update_status_bar()

        # Timer para actualizar el estado de conexión cada 2 segundos
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status_bar)
        self._status_timer.start(2000)

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

        # Registrar callback de desconexión para mostrar alerta inmediata en toda la app
        try:
            if hasattr(self._db_manager, 'set_on_disconnect_callback'):
                def mostrar_alerta_desconexion():
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.critical(self, "Desconexión detectada", "Ocurrió una desconexión del servidor principal y ahora estás en modo offline. Puedes seguir trabajando y los cambios se sincronizarán automáticamente cuando vuelva la conexión.")
                self._db_manager.set_on_disconnect_callback(mostrar_alerta_desconexion)
            if hasattr(self._db_manager, 'set_on_reconnect_callback'):
                def mostrar_alerta_reconexion():
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Reconexión exitosa", "Tu conexión con el servidor principal regresó, ahora se sincronizarán los cambios hechos en modo offline.")
                self._db_manager.set_on_reconnect_callback(mostrar_alerta_reconexion)
        except Exception as e:
            print(f"[SYNC][ERROR] No se pudo registrar el callback de desconexión en MainView: {e}")

        self._apply_role_visibility(role)

    def _apply_role_visibility(self, role: str):
        """Show or hide menus depending on the user role."""
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(role.lower() == 'admin')

    def logout(self):
        """Emit logout signal and close the window."""
        self.logged_out.emit()
        self.close()

    def _update_status_bar(self):
        estado = "ONLINE" if not self._db_manager.offline else "OFFLINE"
        if self.statusBar():
            self.statusBar().showMessage(f"Usuario: {self._username} | Rol: {self._role} | Estado: {estado}")

    def _sync_and_update_status(self):
        self._db_manager.sync_pending_reservations()
        self._update_status_bar()
