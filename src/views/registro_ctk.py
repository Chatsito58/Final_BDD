import re
import customtkinter as ctk
from tkinter import messagebox
import threading
import time

from ..db_manager import DBManager


class RegistroCTk(ctk.CTk):
    """Formulario de registro de clientes usando CustomTkinter."""

    def __init__(self, db_manager: DBManager, on_back=None, correo_inicial=None):
        super().__init__()
        self.db = db_manager
        self.on_back = on_back
        self.correo_inicial = correo_inicial
        self.title("Registro de cliente")
        self.geometry("400x500")
        self._status_label = None
        self._stop_status = False
        self.is_sqlite = getattr(self.db, "offline", False)
        self._load_options()
        self._build_form()
        self._update_status_label()
        self._start_status_updater()
        self.after(100, self._maximize_and_focus)

    def _maximize_and_focus(self):
        self.after(100, lambda: self.wm_state('zoomed'))
        self.focus_force()

    def _load_options(self):
        """Cargar listas de tipos de documento y códigos postales."""
        self.tipo_doc_opts = []
        self.cod_post_opts = []
        if not self.is_sqlite:
            rows = self.db.execute_query(
                "SELECT id_tipo_documento, descripcion FROM Tipo_documento"
            )
            if rows:
                self.tipo_doc_opts = [(r[0], r[1]) for r in rows]
            rows = self.db.execute_query(
                "SELECT id_codigo_postal, ciudad FROM Codigo_postal"
            )
            if rows:
                self.cod_post_opts = [(r[0], f"{r[1]} ({r[0]})") for r in rows]

    def _build_form(self):
        pad = {"padx": 10, "pady": 5}
        self._status_label = ctk.CTkLabel(self, text="", text_color="#F5F6FA", font=("Arial", 13))
        self._status_label.pack(pady=(10, 0))
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
            self.withdraw()
            correo_registrado = self.correo_entry.get().strip()
            self.on_back(correo_registrado)
        else:
            messagebox.showwarning("Atención", "No se puede volver atrás porque no se definió una función de retorno al login. La ventana permanecerá abierta.")

    def _update_status_label(self):
        estado = "ONLINE" if not getattr(self.db, 'offline', False) else "OFFLINE"
        if self._status_label:
            self._status_label.configure(text=f"Estado: {estado}")

    def _start_status_updater(self):
        def updater():
            while not self._stop_status:
                self._update_status_label()
                time.sleep(2)
        t = threading.Thread(target=updater, daemon=True)
        t.start()

    def _get_regular_tipo(self):
        if self.is_sqlite:
            return None
        row = self.db.execute_query(
            "SELECT id_tipo FROM Tipo_cliente WHERE LOWER(descripcion)='regular' LIMIT 1"
        )
        if row:
            return row[0][0]
        self.db.execute_query(
            "INSERT INTO Tipo_cliente (descripcion) VALUES ('regular')",
            fetch=False,
        )
        row = self.db.execute_query(
            "SELECT id_tipo FROM Tipo_cliente WHERE LOWER(descripcion)='regular' LIMIT 1"
        )
        return row[0][0] if row else None

    def registrar(self):
        documento = self.doc_entry.get().strip()
        nombre = self.nom_entry.get().strip()
        telefono = self.tel_entry.get().strip()
        direccion = self.dir_entry.get().strip()
        correo = self.correo_entry.get().strip()

        if not documento or not nombre or not correo:
            messagebox.showwarning("Error", "Complete los campos obligatorios")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            messagebox.showwarning("Error", "Correo no válido")
            return

        count_q = "SELECT COUNT(*) FROM Cliente WHERE correo = %s" if not self.is_sqlite else "SELECT COUNT(*) FROM Cliente WHERE correo = ?"
        if self.db.execute_query(count_q, (correo,)) and self.db.execute_query(count_q, (correo,))[0][0] > 0:
            messagebox.showwarning("Error", "El correo ya está registrado")
            return

        if self.is_sqlite:
            insert_q = "INSERT INTO Cliente (documento, nombre, telefono, correo) VALUES (?, ?, ?, ?)"
            params = (documento, nombre, telefono, correo)
        else:
            id_tipo_doc = None
            if self.tipo_doc_var:
                desc = self.tipo_doc_var.get()
                id_tipo_doc = next((i for i, d in self.tipo_doc_opts if d == desc), None)
            id_codigo = None
            if self.cod_post_var:
                desc = self.cod_post_var.get()
                id_codigo = next((i for i, d in self.cod_post_opts if d == desc), None)
            id_tipo_cliente = self._get_regular_tipo()
            insert_q = (
                "INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, id_tipo_documento, id_tipo_cliente, id_codigo_postal) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )
            params = (
                documento,
                nombre,
                telefono,
                direccion,
                correo,
                id_tipo_doc,
                id_tipo_cliente,
                id_codigo,
            )
        try:
            self.db.execute_query(insert_q, params, fetch=False)
            sel_q = "SELECT id_cliente FROM Cliente WHERE correo = %s ORDER BY id_cliente DESC LIMIT 1" if not self.is_sqlite else "SELECT id_cliente FROM Cliente WHERE correo = ? ORDER BY id_cliente DESC LIMIT 1"
            row = self.db.execute_query(sel_q, (correo,))
            cliente_id = row[0][0] if row else ""
            messagebox.showinfo(
                "Registro exitoso",
                "Cliente registrado exitosamente.\n\nSu contraseña inicial es su número de documento.\nPodrá cambiarla después de iniciar sesión.\n\nSerá redirigido al login para iniciar sesión.",
            )
            if self.on_back:
                self._stop_status = True
                self.withdraw()
                self.on_back(correo)
            else:
                self.volver()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo registrar: {exc}")

    def destroy(self):
        self._stop_status = True
        super().destroy()

