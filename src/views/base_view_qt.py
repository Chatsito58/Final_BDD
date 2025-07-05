from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit
)
from PyQt5.QtCore import QTimer

from ..styles import MODERN_QSS


class BaseQtView(QWidget):
    """Vista base para interfaces Qt con pestañas y barra de estado."""

    def __init__(self, user_data, db_manager, on_logout=None):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._status_label1 = None
        self._status_label2 = None
        self._stop_status = False
        self.setStyleSheet(MODERN_QSS)
        self.resize(600, 400)
        self._build_ui()
        self._update_status_labels()
        self._start_status_updater()
        QTimer.singleShot(100, self.showMaximized)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        # Barra superior
        topbar = QHBoxLayout()
        self._status_label1 = QLabel("")
        self._status_label2 = QLabel("")
        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.clicked.connect(self.logout)
        topbar.addWidget(self._status_label1)
        topbar.addWidget(self._status_label2)
        topbar.addStretch()
        topbar.addWidget(btn_logout)
        layout.addLayout(topbar)

        # Pestañas
        self.tabview = QTabWidget()
        layout.addWidget(self.tabview)

        # Tab: Mis reservas
        self.tab_reservas = QWidget()
        self.tabview.addTab(self.tab_reservas, "Mis reservas")
        if hasattr(self, "_build_tab_mis_reservas"):
            self._build_tab_mis_reservas(self.tab_reservas)

        # Tab: Crear reserva
        self.tab_crear = QWidget()
        self.tabview.addTab(self.tab_crear, "Crear reserva")
        if hasattr(self, "_build_tab_crear_reserva"):
            self._build_tab_crear_reserva(self.tab_crear)

        # Tab: Vehículos disponibles
        self.tab_vehiculos = QWidget()
        self.tabview.addTab(self.tab_vehiculos, "Vehículos disponibles")
        if hasattr(self, "_build_tab_vehiculos"):
            self._build_tab_vehiculos(self.tab_vehiculos)

        # Tab: Realizar abonos
        self.tab_abonos = QWidget()
        self.tabview.addTab(self.tab_abonos, "Realizar abonos")
        if hasattr(self, "_build_tab_abonos"):
            self._build_tab_abonos(self.tab_abonos)

        # Tab: Cambiar contraseña
        self.tab_cambiar = QWidget()
        self.tabview.addTab(self.tab_cambiar, "Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tab_cambiar)

        # Tab opcional: Editar perfil
        if hasattr(self, "_build_tab_perfil"):
            self.tab_perfil = QWidget()
            self.tabview.addTab(self.tab_perfil, "Editar perfil")
            self._build_tab_perfil(self.tab_perfil)

    def _build_cambiar_contrasena_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setSpacing(5)
        label_actual = QLabel("Contraseña actual:")
        self.input_actual = QLineEdit()
        self.input_actual.setEchoMode(QLineEdit.Password)
        label_nueva = QLabel("Nueva contraseña:")
        self.input_nueva = QLineEdit()
        self.input_nueva.setEchoMode(QLineEdit.Password)
        label_confirmar = QLabel("Confirmar nueva contraseña:")
        self.input_confirmar = QLineEdit()
        self.input_confirmar.setEchoMode(QLineEdit.Password)
        btn_cambiar = QPushButton("Cambiar")
        btn_cambiar.clicked.connect(self._cambiar_contrasena)
        for w in [label_actual, self.input_actual, label_nueva, self.input_nueva,
                  label_confirmar, self.input_confirmar, btn_cambiar]:
            layout.addWidget(w)
        layout.addStretch()

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------
    def _welcome_message(self):
        return f"Bienvenido, {self.user_data.get('usuario', '')}"

    def _update_status_labels(self):
        online1 = getattr(self.db_manager, 'is_remote1_active',
                          lambda: getattr(self.db_manager, 'remote1_active', False))()
        online2 = getattr(self.db_manager, 'is_remote2_active',
                          lambda: getattr(self.db_manager, 'remote2_active', False))()
        emoji1 = "🟢" if online1 else "🔴"
        emoji2 = "🟢" if online2 else "🔴"
        estado1 = "ONLINE" if online1 else "OFFLINE"
        estado2 = "ONLINE" if online2 else "OFFLINE"
        if self._status_label1 is not None:
            self._status_label1.setText(f"{emoji1} R1: {estado1}")
        if self._status_label2 is not None:
            self._status_label2.setText(f"{emoji2} R2: {estado2}")

    def _start_status_updater(self):
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status_labels)
        self._status_timer.start(1000)

    def _cambiar_contrasena(self):
        from PyQt5.QtWidgets import QMessageBox
        actual = self.input_actual.text()
        nueva = self.input_nueva.text()
        confirmar = self.input_confirmar.text()
        if not actual or not nueva or not confirmar:
            QMessageBox.warning(self, "Error", "Complete todos los campos")
            return
        if nueva != confirmar:
            QMessageBox.warning(self, "Error",
                                "La nueva contraseña y la confirmación no coinciden")
            return
        from src.auth import AuthManager
        auth = AuthManager(self.db_manager)
        usuario = self.user_data.get("usuario")
        resultado = auth.cambiar_contrasena(usuario, actual, nueva)
        if resultado is True:
            QMessageBox.information(self, "Éxito",
                                    "Contraseña cambiada correctamente")
            self.input_actual.clear()
            self.input_nueva.clear()
            self.input_confirmar.clear()
        else:
            QMessageBox.warning(self, "Error", str(resultado))

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._stop_status = True
        if hasattr(self, '_status_timer'):
            self._status_timer.stop()
        super().closeEvent(event)

    def logout(self):
        self._stop_status = True
        if hasattr(self, '_status_timer'):
            self._status_timer.stop()
        self.close()
        if self.on_logout:
            self.on_logout()
