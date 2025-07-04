import re
import hashlib
import customtkinter as ctk
from tkinter import messagebox
import threading
import time

from ..triple_db_manager import TripleDBManager


class RegistroCTk(ctk.CTk):
    """Formulario de registro de clientes usando CustomTkinter."""

    def __init__(self, db_manager: TripleDBManager, on_back=None, correo_inicial=None):
        super().__init__()
        self.db = db_manager
        self.on_back = on_back
        self.correo_inicial = correo_inicial
        self.title("Registro de cliente")
        self.geometry("400x500")
        if self.on_back:
            self.protocol("WM_DELETE_WINDOW", self.volver)
        self._status_label1 = None
        self._status_label2 = None
        self._stop_status = False
        self.is_sqlite = getattr(self.db, "offline", False)
        self._load_options()
        self._build_form()
        self._update_status_labels()
        self._start_status_updater()
        self.after(100, self._maximize_and_focus)

    def _maximize_and_focus(self):
        self.after(100, lambda: self.wm_state('zoomed'))
        self.focus_force()

    def _load_options(self):
        """Load dropdown option lists from the active database."""
        self.tipo_doc_opts = []
        self.cod_post_opts = []
        self.licencia_opts = []
        self.cuenta_opts = []

        queries = {
            "tipo_doc_opts": (
                "SELECT id_tipo_documento, descripcion FROM Tipo_documento",
                lambda r: (r[0], r[1]),
            ),
            "cod_post_opts": (
                "SELECT id_codigo_postal, ciudad FROM Codigo_postal",
                lambda r: (r[0], f"{r[1]} ({r[0]})"),
            ),
            "licencia_opts": (
                "SELECT id_licencia FROM Licencia_conduccion",
                lambda r: r[0],
            ),
            "cuenta_opts": (
                "SELECT id_cuenta FROM Cuenta",
                lambda r: r[0],
            ),
        }

        for attr, (query, transform) in queries.items():
            rows = self.db.execute_query(query)
            if rows:
                setattr(self, attr, [transform(r) for r in rows])

    def _build_form(self):
        pad = {"padx": 10, "pady": 5}
        self._status_label1 = ctk.CTkLabel(self, text="", text_color="#F5F6FA", font=("Arial", 13))
        self._status_label1.pack(pady=(10, 0))
        self._status_label2 = ctk.CTkLabel(self, text="", text_color="#F5F6FA", font=("Arial", 13))
        self._status_label2.pack()
        ctk.CTkLabel(self, text="Documento *").pack(**pad)
        self.doc_entry = ctk.CTkEntry(self)
        self.doc_entry.pack(**pad)

        ctk.CTkLabel(self, text="Nombre *").pack(**pad)
        self.nom_entry = ctk.CTkEntry(self)
        self.nom_entry.pack(**pad)

        ctk.CTkLabel(self, text="Teléfono").pack(**pad)
        self.tel_entry = ctk.CTkEntry(self)
        self.tel_entry.pack(**pad)

        ctk.CTkLabel(self, text="Dirección").pack(**pad)
        self.dir_entry = ctk.CTkEntry(self)
        self.dir_entry.pack(**pad)

        ctk.CTkLabel(self, text="Correo *").pack(**pad)
        self.correo_entry = ctk.CTkEntry(self)
        self.correo_entry.pack(**pad)
        if self.correo_inicial:
            self.correo_entry.insert(0, self.correo_inicial)

        ctk.CTkLabel(self, text="Infracciones").pack(**pad)
        self.infra_entry = ctk.CTkEntry(self)
        self.infra_entry.insert(0, "0")
        self.infra_entry.pack(**pad)
        # Advertencia sobre la validación de infracciones
        self.infra_info_lbl = ctk.CTkLabel(
            self,
            text=(
                "Las infracciones registradas se validar\u00e1n con su documento; "
                "ingr\u00e9selas de forma precisa."
            ),
            wraplength=350,
            justify="center",
        )
        self.infra_info_lbl.pack(**pad)

        if self.licencia_opts:
            ctk.CTkLabel(self, text="Licencia").pack(**pad)
            values = [str(l) for l in self.licencia_opts]
            self.licencia_var = ctk.StringVar(value=values[0])
            self.licencia_menu = ctk.CTkOptionMenu(self, variable=self.licencia_var, values=values)
            self.licencia_menu.pack(**pad)
        else:
            self.licencia_var = None

        if self.cuenta_opts:
            ctk.CTkLabel(self, text="Cuenta").pack(**pad)
            values = [str(c) for c in self.cuenta_opts]
            self.cuenta_var = ctk.StringVar(value=values[0])
            self.cuenta_menu = ctk.CTkOptionMenu(self, variable=self.cuenta_var, values=values)
            self.cuenta_menu.pack(**pad)
        else:
            self.cuenta_var = None

        if self.tipo_doc_opts:
            ctk.CTkLabel(self, text="Tipo documento").pack(**pad)
            values = [d[1] for d in self.tipo_doc_opts]
            self.tipo_doc_var = ctk.StringVar(value=values[0])
            self.tipo_doc_menu = ctk.CTkOptionMenu(self, variable=self.tipo_doc_var, values=values)
            self.tipo_doc_menu.pack(**pad)
        else:
            self.tipo_doc_var = None

        if self.cod_post_opts:
            ctk.CTkLabel(self, text="Código postal").pack(**pad)
            values = [c[1] for c in self.cod_post_opts]
            self.cod_post_var = ctk.StringVar(value=values[0])
            self.cod_menu = ctk.CTkOptionMenu(self, variable=self.cod_post_var, values=values)
            self.cod_menu.pack(**pad)
        else:
            self.cod_post_var = None

        self.btn = ctk.CTkButton(self, text="Registrar", command=self.registrar)
        self.btn.pack(pady=15)
        self.btn_volver = ctk.CTkButton(self, text="Volver", command=self.volver, fg_color="#3A86FF", hover_color="#265DAB")
        self.btn_volver.pack(pady=5)

    def volver(self):
        if self.on_back:
            self._stop_status = True
            self.destroy()
            correo_registrado = self.correo_entry.get().strip()
            self.on_back(correo_registrado)
        else:
            messagebox.showwarning("Atención", "No se puede volver atrás porque no se definió una función de retorno al login. La ventana permanecerá abierta.")

    def _update_status_labels(self):
        r1 = getattr(self.db, 'is_remote1_active', lambda: getattr(self.db, 'remote1_active', False))()
        r2 = getattr(self.db, 'is_remote2_active', lambda: getattr(self.db, 'remote2_active', False))()
        estado1 = "ONLINE" if r1 else "OFFLINE"
        estado2 = "ONLINE" if r2 else "OFFLINE"
        if self._status_label1:
            self._status_label1.configure(text=f"Remote1: {estado1}")
        if self._status_label2:
            self._status_label2.configure(text=f"Remote2: {estado2}")

    def _start_status_updater(self):
        def updater():
            while not self._stop_status:
                try:
                    self._update_status_labels()
                    time.sleep(1)
                except Exception:
                    time.sleep(1)
        t = threading.Thread(target=updater, daemon=True)
        t.start()


    def registrar(self):
        documento = self.doc_entry.get().strip()
        nombre = self.nom_entry.get().strip()
        telefono = self.tel_entry.get().strip()
        direccion = self.dir_entry.get().strip()
        correo = self.correo_entry.get().strip()
        infracciones_str = self.infra_entry.get().strip()
        try:
            infracciones = int(infracciones_str or 0)
        except ValueError:
            messagebox.showwarning("Error", "Infracciones debe ser un número entero")
            return

        licencia_sel = None
        if self.licencia_var:
            try:
                licencia_sel = int(self.licencia_var.get())
            except ValueError:
                messagebox.showwarning("Error", "Licencia seleccionada inválida")
                return

        cuenta_sel = None
        if self.cuenta_var:
            try:
                cuenta_sel = int(self.cuenta_var.get())
            except ValueError:
                messagebox.showwarning("Error", "Cuenta seleccionada inválida")
                return

        if not documento or not nombre or not correo:
            messagebox.showwarning("Error", "Complete los campos obligatorios")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            messagebox.showwarning("Error", "Correo no válido")
            return

        # Verificar que el correo no exista ya en la tabla de usuarios
        count_q = (
            "SELECT COUNT(*) FROM Usuario WHERE usuario = %s"
            if not self.is_sqlite
            else "SELECT COUNT(*) FROM Usuario WHERE usuario = ?"
        )
        result = self.db.execute_query(count_q, (correo,))
        if result and result[0][0] > 0:
            messagebox.showwarning("Error", "El correo ya está registrado")
            return

        # Obtener IDs de tipo de documento y código postal
        id_tipo_doc = None
        if self.tipo_doc_var:
            desc = self.tipo_doc_var.get()
            id_tipo_doc = next((i for i, d in self.tipo_doc_opts if d == desc), None)
        id_codigo = None
        if self.cod_post_var:
            desc = self.cod_post_var.get()
            id_codigo = next((i for i, d in self.cod_post_opts if d == desc), None)
        
        # Crear licencia de conducción primero
        licencia_query = "INSERT INTO Licencia_conduccion (estado, fecha_emision, fecha_vencimiento, id_categoria) VALUES (?, ?, ?, ?)" if self.is_sqlite else "INSERT INTO Licencia_conduccion (estado, fecha_emision, fecha_vencimiento, id_categoria) VALUES (%s, %s, %s, %s)"
        from datetime import datetime, timedelta
        fecha_emision = datetime.now().strftime('%Y-%m-%d')
        fecha_vencimiento = (datetime.now() + timedelta(days=365*10)).strftime('%Y-%m-%d')  # 10 años
        licencia_params = ('Vigente', fecha_emision, fecha_vencimiento, 3)  # Categoría B1 por defecto
        
        try:
            # Insertar licencia si no se seleccionó una existente
            if licencia_sel is None:
                self.db.execute_query(licencia_query, licencia_params, fetch=False)

                # Obtener ID de la licencia insertada
                licencia_id_query = "SELECT last_insert_rowid()" if self.is_sqlite else "SELECT LAST_INSERT_ID()"
                licencia_result = self.db.execute_query(licencia_id_query)
                licencia_sel = licencia_result[0][0] if licencia_result else None

            # Insertar cliente con la nueva estructura
            if self.is_sqlite:
                insert_q = (
                    "INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, "
                    "infracciones, id_licencia, id_tipo_documento, id_codigo_postal, id_cuenta) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
            else:
                insert_q = (
                    "INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, "
                    "infracciones, id_licencia, id_tipo_documento, id_codigo_postal, id_cuenta) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

            cliente_id = self.db.execute_query(
                insert_q,
                params,
                fetch=False,
                return_lastrowid=True,
            )
            if not cliente_id:
                sel_q = (
                    "SELECT id_cliente FROM Cliente WHERE correo = %s ORDER BY id_cliente DESC LIMIT 1"
                    if not self.is_sqlite
                    else "SELECT id_cliente FROM Cliente WHERE correo = ? ORDER BY id_cliente DESC LIMIT 1"
                )
                row = self.db.execute_query(sel_q, (correo,))
                cliente_id = row[0][0] if row else ""

            # Crear usuario asociado
            placeholder = "?" if self.db.offline else "%s"
            rol_q = f"SELECT id_rol FROM Rol WHERE nombre = {placeholder}"
            rol_res = self.db.execute_query(rol_q, ("cliente",))
            rol_id = rol_res[0][0] if rol_res else 1
            usuario_q = (
                "INSERT INTO Usuario (usuario, contrasena, id_rol, id_cliente) VALUES (?, ?, ?, ?)"
                if self.db.offline
                else "INSERT INTO Usuario (usuario, contrasena, id_rol, id_cliente) VALUES (%s, %s, %s, %s)"
            )
            # MySQL's SHA2() devuelve el hash en mayúsculas, por lo que
            # estandarizamos la contraseña a mayúsculas para evitar
            # problemas de comparación entre bases de datos.
            hashed_doc = hashlib.sha256(documento.encode()).hexdigest().upper()
            usuario_params = (correo, hashed_doc, rol_id, cliente_id)
            if self.db.offline:
                self.db.save_pending_registro(
                    "Usuario",
                    {
                        "usuario": correo,
                        "contrasena": hashed_doc,
                        "id_rol": rol_id,
                        "id_cliente": cliente_id,
                        "id_empleado": None,
                    },
                )
            else:
                self.db.execute_query(usuario_q, usuario_params, fetch=False)
                if self.db.offline:
                    self.db.save_pending_registro(
                        "Usuario",
                        {
                            "usuario": correo,
                            "contrasena": hashed_doc,
                            "id_rol": rol_id,
                            "id_cliente": cliente_id,
                            "id_empleado": None,
                        },
                    )
            messagebox.showinfo(
                "Registro exitoso",
                "Cliente registrado exitosamente.\n\nSu contraseña inicial es su número de documento.\nPodrá cambiarla después de iniciar sesión.\n\nSerá redirigido al login para iniciar sesión.",
            )
            if self.on_back:
                self._stop_status = True
                self.destroy()
                self.on_back(correo)
            else:
                self.volver()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo registrar: {exc}")

    def destroy(self):
        self._stop_status = True
        super().destroy()

