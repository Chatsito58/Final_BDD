from __future__ import annotations

import re
import hashlib
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from PyQt5 import QtWidgets, uic

from ..triple_db_manager import TripleDBManager


class RegistroViewQt(QtWidgets.QDialog):
    """Formulario de registro de clientes usando PyQt."""

    def __init__(self, db_manager: TripleDBManager, parent: Optional[QtWidgets.QWidget] = None, correo_inicial: Optional[str] = None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve().parents[2] / 'ui' / 'registro.ui'
        uic.loadUi(ui_path, self)

        self.db = db_manager
        self.correo_inicial = correo_inicial
        self._stop_status = False
        self._status_label1: Optional[QtWidgets.QLabel] = None
        self._status_label2: Optional[QtWidgets.QLabel] = None
        self.is_sqlite = getattr(self.db, 'offline', False)

        self._load_options()
        self._bind_widgets()
        self._update_status_labels()
        self._start_status_updater()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def _bind_widgets(self) -> None:
        self.documento_edit = self.findChild(QtWidgets.QLineEdit, 'documentoLineEdit')
        self.nombre_edit = self.findChild(QtWidgets.QLineEdit, 'nombreLineEdit')
        self.telefono_edit = self.findChild(QtWidgets.QLineEdit, 'telefonoLineEdit')
        self.direccion_edit = getattr(self, 'direccionLineEdit', None)
        self.correo_edit = self.findChild(QtWidgets.QLineEdit, 'correoLineEdit')
        self.infra_edit = getattr(self, 'infraccionesLineEdit', None)
        self.licencia_combo = getattr(self, 'licenciaComboBox', None)
        self.cuenta_combo = getattr(self, 'cuentaComboBox', None)
        self.tipo_doc_combo = getattr(self, 'tipoDocComboBox', None)
        self.cod_post_combo = getattr(self, 'codigoPostalComboBox', None)
        self.btn_registrar = self.findChild(QtWidgets.QPushButton, 'btn_registrar')
        self.btn_volver = getattr(self, 'btn_volver', None)
        self._status_label1 = getattr(self, 'statusLabel1', None)
        self._status_label2 = getattr(self, 'statusLabel2', None)

        if self.btn_registrar:
            self.btn_registrar.clicked.connect(self.registrar)
        if self.btn_volver:
            self.btn_volver.clicked.connect(self.reject)
        if self.correo_inicial and self.correo_edit:
            self.correo_edit.setText(self.correo_inicial)

    def _load_options(self) -> None:
        self.tipo_doc_opts = []
        self.cod_post_opts = []
        self.licencia_opts = []
        self.cuenta_opts = []

        queries = {
            'tipo_doc_opts': (
                'SELECT id_tipo_documento, descripcion FROM Tipo_documento',
                lambda r: (r[0], r[1]),
            ),
            'cod_post_opts': (
                'SELECT id_codigo_postal, ciudad FROM Codigo_postal',
                lambda r: (r[0], f"{r[1]} ({r[0]})"),
            ),
            'licencia_opts': (
                'SELECT id_licencia FROM Licencia_conduccion',
                lambda r: r[0],
            ),
            'cuenta_opts': (
                'SELECT id_cuenta FROM Cuenta',
                lambda r: r[0],
            ),
        }

        for attr, (query, transform) in queries.items():
            rows = self.db.execute_query(query)
            if rows:
                setattr(self, attr, [transform(r) for r in rows])

        # Populate combos if present
        if self.licencia_combo is not None and self.licencia_opts:
            self.licencia_combo.addItems([str(l) for l in self.licencia_opts])
        if self.cuenta_combo is not None and self.cuenta_opts:
            self.cuenta_combo.addItems([str(c) for c in self.cuenta_opts])
        if self.tipo_doc_combo is not None and self.tipo_doc_opts:
            self.tipo_doc_combo.addItems([d[1] for d in self.tipo_doc_opts])
        if self.cod_post_combo is not None and self.cod_post_opts:
            self.cod_post_combo.addItems([c[1] for c in self.cod_post_opts])

    # ------------------------------------------------------------------
    # Status updates
    # ------------------------------------------------------------------
    def _update_status_labels(self) -> None:
        r1 = getattr(self.db, 'is_remote1_active', lambda: getattr(self.db, 'remote1_active', False))()
        r2 = getattr(self.db, 'is_remote2_active', lambda: getattr(self.db, 'remote2_active', False))()
        estado1 = 'ONLINE' if r1 else 'OFFLINE'
        estado2 = 'ONLINE' if r2 else 'OFFLINE'
        if self._status_label1:
            self._status_label1.setText(f"Remote1: {estado1}")
        if self._status_label2:
            self._status_label2.setText(f"Remote2: {estado2}")

    def _start_status_updater(self) -> None:
        def updater():
            while not self._stop_status:
                try:
                    self._update_status_labels()
                    time.sleep(1)
                except Exception:
                    time.sleep(1)
        t = threading.Thread(target=updater, daemon=True)
        t.start()

    # ------------------------------------------------------------------
    # Registration logic
    # ------------------------------------------------------------------
    def registrar(self) -> None:
        documento = self.documento_edit.text().strip() if self.documento_edit else ''
        nombre = self.nombre_edit.text().strip() if self.nombre_edit else ''
        telefono = self.telefono_edit.text().strip() if self.telefono_edit else ''
        direccion = self.direccion_edit.text().strip() if self.direccion_edit else ''
        correo = self.correo_edit.text().strip() if self.correo_edit else ''
        infracciones_str = self.infra_edit.text().strip() if self.infra_edit else ''
        try:
            infracciones = int(infracciones_str or 0)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Infracciones debe ser un número entero')
            return

        licencia_sel = None
        if self.licencia_combo and self.licencia_combo.currentIndex() >= 0:
            try:
                licencia_sel = int(self.licencia_combo.currentText())
            except ValueError:
                QtWidgets.QMessageBox.warning(self, 'Error', 'Licencia seleccionada inválida')
                return

        cuenta_sel = None
        if self.cuenta_combo and self.cuenta_combo.currentIndex() >= 0:
            try:
                cuenta_sel = int(self.cuenta_combo.currentText())
            except ValueError:
                QtWidgets.QMessageBox.warning(self, 'Error', 'Cuenta seleccionada inválida')
                return

        if not documento or not nombre or not correo:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Complete los campos obligatorios')
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            QtWidgets.QMessageBox.warning(self, 'Error', 'Correo no válido')
            return

        # Verificar que el correo no exista ya
        count_q = 'SELECT COUNT(*) FROM Usuario WHERE usuario = ?' if self.is_sqlite else 'SELECT COUNT(*) FROM Usuario WHERE usuario = %s'
        result = self.db.execute_query(count_q, (correo,))
        if result and result[0][0] > 0:
            QtWidgets.QMessageBox.warning(self, 'Error', 'El correo ya está registrado')
            return

        # Obtener IDs de tipo de documento y código postal
        id_tipo_doc = None
        if self.tipo_doc_combo and self.tipo_doc_opts:
            desc = self.tipo_doc_combo.currentText()
            id_tipo_doc = next((i for i, d in self.tipo_doc_opts if d == desc), None)
        id_codigo = None
        if self.cod_post_combo and self.cod_post_opts:
            desc = self.cod_post_combo.currentText()
            id_codigo = next((i for i, d in self.cod_post_opts if d == desc), None)

        licencia_query = 'INSERT INTO Licencia_conduccion (estado, fecha_emision, fecha_vencimiento, id_categoria) VALUES (?, ?, ?, ?)' if self.is_sqlite else 'INSERT INTO Licencia_conduccion (estado, fecha_emision, fecha_vencimiento, id_categoria) VALUES (%s, %s, %s, %s)'
        fecha_emision = datetime.now().strftime('%Y-%m-%d')
        fecha_vencimiento = (datetime.now() + timedelta(days=365*10)).strftime('%Y-%m-%d')
        licencia_params = ('Vigente', fecha_emision, fecha_vencimiento, 3)

        try:
            if licencia_sel is None:
                self.db.execute_query(licencia_query, licencia_params, fetch=False)
                licencia_id_query = 'SELECT last_insert_rowid()' if self.is_sqlite else 'SELECT LAST_INSERT_ID()'
                licencia_result = self.db.execute_query(licencia_id_query)
                licencia_sel = licencia_result[0][0] if licencia_result else None

            if self.is_sqlite:
                insert_q = (
                    'INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, '
                    'infracciones, id_licencia, id_tipo_documento, id_codigo_postal, id_cuenta) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                )
            else:
                insert_q = (
                    'INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, '
                    'infracciones, id_licencia, id_tipo_documento, id_codigo_postal, id_cuenta) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                )
            params = (
                documento,
                nombre,
                telefono,
                direccion,
                correo,
                infracciones,
                licencia_sel,
                id_tipo_doc,
                id_codigo,
                cuenta_sel,
            )
            cliente_id = self.db.execute_query(insert_q, params, fetch=False, return_lastrowid=True)
            if not cliente_id:
                sel_q = 'SELECT id_cliente FROM Cliente WHERE correo = ? ORDER BY id_cliente DESC LIMIT 1' if self.is_sqlite else 'SELECT id_cliente FROM Cliente WHERE correo = %s ORDER BY id_cliente DESC LIMIT 1'
                row = self.db.execute_query(sel_q, (correo,))
                cliente_id = row[0][0] if row else ''

            placeholder = '?' if self.is_sqlite else '%s'
            rol_q = f'SELECT id_rol FROM Rol WHERE nombre = {placeholder}'
            rol_res = self.db.execute_query(rol_q, ('cliente',))
            rol_id = rol_res[0][0] if rol_res else 1
            usuario_q = 'INSERT INTO Usuario (usuario, contrasena, id_rol, id_cliente) VALUES (?, ?, ?, ?)' if self.is_sqlite else 'INSERT INTO Usuario (usuario, contrasena, id_rol, id_cliente) VALUES (%s, %s, %s, %s)'
            hashed_doc = hashlib.sha256(documento.encode()).hexdigest().upper()
            usuario_params = (correo, hashed_doc, rol_id, cliente_id)
            if self.db.offline:
                self.db.save_pending_registro(
                    'Usuario',
                    {
                        'usuario': correo,
                        'contrasena': hashed_doc,
                        'id_rol': rol_id,
                        'id_cliente': cliente_id,
                        'id_empleado': None,
                    },
                )
            else:
                self.db.execute_query(usuario_q, usuario_params, fetch=False)
                if self.db.offline:
                    self.db.save_pending_registro(
                        'Usuario',
                        {
                            'usuario': correo,
                            'contrasena': hashed_doc,
                            'id_rol': rol_id,
                            'id_cliente': cliente_id,
                            'id_empleado': None,
                        },
                    )
            QtWidgets.QMessageBox.information(
                self,
                'Registro exitoso',
                'Cliente registrado exitosamente.\n\nSu contraseña inicial es su número de documento.\nPodrá cambiarla después de iniciar sesión.'
            )
            self.accept()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, 'Error', f'No se pudo registrar: {exc}')

    def closeEvent(self, event):
        self._stop_status = True
        super().closeEvent(event)

