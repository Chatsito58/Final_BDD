from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QTimer
import logging

from ..db_manager import DBManager
from ..auth import AuthManager
from ..styles import MODERN_QSS

class MainView(QtWidgets.QMainWindow):
    """Main application window handling role based menus and logout."""

    logged_out = pyqtSignal()

    def __init__(self, username: str, role: str, parent=None, db_manager=None, auth_manager=None, app=None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve().parents[2] / 'ui' / 'main_window.ui'
        uic.loadUi(ui_path, self)

        # Aplicar QSS si se pasa QApplication
        if app is not None:
            app.setStyleSheet(MODERN_QSS)

        self._username = username
        self._role = role
        self._db_manager = db_manager if db_manager is not None else DBManager()
        self._auth_manager = auth_manager if auth_manager is not None else AuthManager(self._db_manager)

        self._sync_timer = QTimer(self)
        self._sync_timer.timeout.connect(self._sync_and_update_status)
        self._sync_timer.start(5 * 60 * 1000)
        self._update_status_bar()

        # Timer para actualizar el estado de conexión cada 2 segundos
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status_bar)
        self._status_timer.start(2000)

        # Intentar reconexión periódica si está offline
        self._reconnect_timer = QTimer(self)
        self._reconnect_timer.timeout.connect(self._attempt_reconnect)
        self._reconnect_timer.start(5000)

        # Setup status bar information
        if self.statusBar():
            self.statusBar().showMessage(f"Usuario: {username} | Rol: {role}")

        # Access menus
        self.menu_reservas = self.findChild(QtWidgets.QMenu, 'menuReservas')
        self.menu_clientes = self.findChild(QtWidgets.QMenu, 'menuClientes')
        self.menu_vehiculos = self.findChild(QtWidgets.QMenu, 'menuVehiculos')
        self.menu_admin = self.findChild(QtWidgets.QMenu, 'menuAdministracion')

        # Add logout action under Administración (siempre visible)
        self.logout_action = QtWidgets.QAction('Cerrar sesión', self)
        self.menuBar().addAction(self.logout_action)
        self.logout_action.triggered.connect(self.logout)
        if self.menu_admin and self.menu_admin.actions() and self.logout_action not in self.menu_admin.actions():
            self.menu_admin.addAction(self.logout_action)

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

        # --- Depuración: mostrar pestañas disponibles ---
        if self.tabWidget:
            for i in range(self.tabWidget.count()):
                _ = self.tabWidget.tabText(i)

        # --- Agregar botón 'Cerrar sesión' en la pestaña principal ---
        tab_principal = self.findChild(QtWidgets.QWidget, 'tabPrincipal')
        if tab_principal is not None:
            layout_principal = tab_principal.layout()
            if layout_principal is not None:
                from PyQt5.QtWidgets import QPushButton
                self.btn_logout_tab = QPushButton('Cerrar sesión')
                self.btn_logout_tab.setStyleSheet('background-color: #3A86FF; color: white; border-radius: 8px; padding: 8px 0px; font-size: 15px;')
                self.btn_logout_tab.clicked.connect(self.logout)
                layout_principal.addWidget(self.btn_logout_tab)

        # --- Agregar widgets de la pestaña Cambiar contraseña ---
        from PyQt5.QtWidgets import QVBoxLayout
        self.tabCambiarContrasena = self.findChild(QtWidgets.QWidget, 'tabCambiarContrasena')
        if self.tabCambiarContrasena is not None:
            self.verticalLayoutTabCambiarContrasena = self.tabCambiarContrasena.layout()
            if self.verticalLayoutTabCambiarContrasena is None:
                self.verticalLayoutTabCambiarContrasena = QVBoxLayout(self.tabCambiarContrasena)
        else:
            self.verticalLayoutTabCambiarContrasena = None
        
        if self.tabCambiarContrasena and self.verticalLayoutTabCambiarContrasena:
            try:
                # Limpiar el layout antes de agregar widgets (evita duplicados)
                while self.verticalLayoutTabCambiarContrasena.count():
                    item = self.verticalLayoutTabCambiarContrasena.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                from PyQt5.QtWidgets import QLineEdit, QPushButton, QLabel
                self.label_actual = QLabel('Contraseña actual:')
                self.input_actual = QLineEdit()
                self.input_actual.setEchoMode(QLineEdit.Password)
                self.label_nueva = QLabel('Nueva contraseña:')
                self.input_nueva = QLineEdit()
                self.input_nueva.setEchoMode(QLineEdit.Password)
                self.label_confirmar = QLabel('Confirmar nueva contraseña:')
                self.input_confirmar = QLineEdit()
                self.input_confirmar.setEchoMode(QLineEdit.Password)
                self.btn_cambiar = QPushButton('Cambiar')
                self.btn_cambiar.clicked.connect(self._cambiar_contrasena)
                for w in [self.label_actual, self.input_actual, self.label_nueva, self.input_nueva, self.label_confirmar, self.input_confirmar, self.btn_cambiar]:
                    self.verticalLayoutTabCambiarContrasena.addWidget(w)
                # Forzar actualización y repintado
                self.tabCambiarContrasena.update()
                self.tabCambiarContrasena.repaint()
                self.verticalLayoutTabCambiarContrasena.update()
                self.verticalLayoutTabCambiarContrasena.invalidate()
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                import traceback
                tb = traceback.format_exc()
                QMessageBox.critical(self, "Error de UI", f"Error al inicializar la pestaña de cambio de contraseña:\n{e}\n{tb}")
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error de UI", "No se pudo inicializar la pestaña de cambio de contraseña. Por favor revisa el archivo main_window.ui y los nombres de los layouts.")

    def _apply_role_visibility(self, role: str):
        """Show or hide menus depending on the user role."""
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(role.lower() == 'admin')

    def logout(self):
        """Emit logout signal and close the window."""
        self.logged_out.emit()
        self.close()
        self.deleteLater()

    def _update_status_bar(self):
        estado = "ONLINE" if not self._db_manager.offline else "OFFLINE"
        if self.statusBar():
            self.statusBar().showMessage(f"Usuario: {self._username} | Rol: {self._role} | Estado: {estado}")

    def _sync_and_update_status(self):
        self._db_manager.sync_pending_reservations()
        self._update_status_bar()

    def _attempt_reconnect(self):
        """Intentar reconectar y actualizar el estado si tiene éxito."""
        if self._db_manager.offline and self._db_manager.try_reconnect():
            self._update_status_bar()

    def _cambiar_contrasena(self):
        from PyQt5.QtWidgets import QMessageBox
        logger = logging.getLogger(__name__)
        actual = self.input_actual.text()
        nueva = self.input_nueva.text()
        confirmar = self.input_confirmar.text()
        
        logger.info(f"[DEBUG] _cambiar_contrasena llamado para usuario: {self._username}")
        logger.info(f"[DEBUG] actual: {actual}, nueva: {nueva}, confirmar: {confirmar}")
        if not actual or not nueva or not confirmar:
            
            logger.warning("[DEBUG] Faltan campos en el cambio de contraseña")
            QMessageBox.warning(self, 'Error', 'Complete todos los campos')
            return
        if nueva != confirmar:
            
            logger.warning("[DEBUG] Nueva y confirmación no coinciden")
            QMessageBox.warning(self, 'Error', 'La nueva contraseña y la confirmación no coinciden')
            return
        
        logger.info(f"[DEBUG] Llamando a self._auth_manager.cambiar_contrasena({self._username}, actual, nueva)")
        resultado = self._auth_manager.cambiar_contrasena(self._username, actual, nueva)
        
        logger.info(f"[DEBUG] Resultado de cambiar_contrasena: {resultado}")
        if resultado is True:
            QMessageBox.information(self, 'Éxito', 'Contraseña cambiada correctamente')
            self.input_actual.clear()
            self.input_nueva.clear()
            self.input_confirmar.clear()
        else:
            QMessageBox.warning(self, 'Error', str(resultado))

class AdminViewQt(MainView):
    def __init__(self, username, parent=None, db_manager=None, auth_manager=None, app=None):
        super().__init__(username, 'admin', parent, db_manager=db_manager, auth_manager=auth_manager, app=app)
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(True)

class GerenteViewQt(MainView):
    def __init__(self, username, parent=None, db_manager=None, auth_manager=None, app=None):
        super().__init__(username, 'gerente', parent, db_manager=db_manager, auth_manager=auth_manager, app=app)
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(False)

class EmpleadoViewQt(MainView):
    def __init__(self, username, parent=None, db_manager=None, auth_manager=None, app=None):
        super().__init__(username, 'empleado', parent, db_manager=db_manager, auth_manager=auth_manager, app=app)
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(False)

class EmpleadoVentasViewQt(MainView):
    def __init__(self, username, parent=None, db_manager=None, auth_manager=None, app=None):
        super().__init__(username, 'empleado_ventas', parent, db_manager=db_manager, auth_manager=auth_manager, app=app)
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(False)

class EmpleadoCajaViewQt(MainView):
    def __init__(self, username, parent=None, db_manager=None, auth_manager=None, app=None):
        super().__init__(username, 'empleado_caja', parent, db_manager=db_manager, auth_manager=auth_manager, app=app)
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(False)

class EmpleadoMantenimientoViewQt(MainView):
    def __init__(self, username, parent=None, db_manager=None, auth_manager=None, app=None):
        super().__init__(username, 'empleado_mantenimiento', parent, db_manager=db_manager, auth_manager=auth_manager, app=app)
        if self.menu_admin:
            self.menu_admin.menuAction().setVisible(False)
