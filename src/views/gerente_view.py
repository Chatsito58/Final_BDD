import customtkinter as ctk
from .base_view import BaseCTKView
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre,
)
from ..styles import BG_DARK, TEXT_COLOR, PRIMARY_COLOR, PRIMARY_COLOR_DARK

class GerenteView(BaseCTKView):
    """Vista CTk para gerentes con gestión de empleados y reportes."""

    def _welcome_message(self):
        return f"Bienvenido gerente, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0, 5))
        self._status_label1 = ctk.CTkLabel(
            topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR
        )
        self._status_label1.pack(side="left", padx=10, pady=8)
        self._status_label2 = ctk.CTkLabel(
            topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR
        )
        self._status_label2.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(
            topbar,
            text="Cerrar sesión",
            command=self.logout,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_COLOR_DARK,
            width=140,
            height=32,
        ).pack(side="right", padx=10, pady=8)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

        self.tab_empleados = self.tabview.add("Empleados")
        self._build_tab_empleados(self.tabview.tab("Empleados"))

        self.tab_vehiculos = self.tabview.add("Vehículos")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos"))
        self.tab_vehiculos_reg = self.tabview.add("Vehículos registrados")
        self._build_tab_vehiculos_registrados(self.tabview.tab("Vehículos registrados"))

        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))

        self.tab_reportes = self.tabview.add("Reportes")
        self._build_tab_reportes(self.tabview.tab("Reportes"))

        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

        if puede_ejecutar_sql_libre(self.user_data.get("rol")):
            self.tab_sql_libre = self.tabview.add("SQL Libre")
            self._build_tab_sql_libre(self.tabview.tab("SQL Libre"))

        # Abrir inicialmente en la pestaña de Reportes
        self.tabview.set("Reportes")

    def _build_tab_empleados(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        self._emp_sel = None
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Gestión de empleados", font=("Arial", 18, "bold")
        ).pack(pady=10)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_emp = tk.Listbox(
            list_frame, height=8, width=60, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.lb_emp.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_emp.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Documento:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Nombre:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Teléfono:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Correo:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Cargo:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )

        self.ent_doc_e = ctk.CTkEntry(form, width=150)
        self.ent_nom_e = ctk.CTkEntry(form, width=150)
        self.ent_tel_e = ctk.CTkEntry(form, width=150)
        self.ent_cor_e = ctk.CTkEntry(form, width=150)
        cargos = cargos_permitidos_para_gerente()
        self.cargo_var = ctk.StringVar(value=cargos[0])
        self.ent_cargo_e = ctk.CTkOptionMenu(
            form, variable=self.cargo_var, values=cargos, width=150
        )

        self.ent_doc_e.grid(row=0, column=1, padx=5, pady=5)
        self.ent_nom_e.grid(row=1, column=1, padx=5, pady=5)
        self.ent_tel_e.grid(row=2, column=1, padx=5, pady=5)
        self.ent_cor_e.grid(row=3, column=1, padx=5, pady=5)
        self.ent_cargo_e.grid(row=4, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(
            btn_frame, text="Nuevo", command=self._nuevo_empleado, width=100
        ).grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._guardar_empleado,
            width=120,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).grid(row=0, column=1, padx=5)

        self.lb_emp.bind("<<ListboxSelect>>", self._seleccionar_empleado)
        self._cargar_empleados()

    def _cargar_empleados(self):
        self.lb_emp.delete(0, "end")
        rows = self.db_manager.execute_query(
            "SELECT id_empleado, nombre, cargo, documento, telefono, correo FROM Empleado "
            "WHERE LOWER(cargo) NOT IN ('gerente','administrador')"
        )
        if rows:
            for r in rows:
                id_e, nombre, cargo, doc, tel, cor = r
                self.lb_emp.insert(
                    "end", f"{id_e} | {nombre} | {cargo} | {doc} | {tel} | {cor}"
                )

    def _seleccionar_empleado(self, event=None):
        sel = self.lb_emp.curselection()
        if not sel:
            return
        self._emp_sel = int(self.lb_emp.get(sel[0]).split("|")[0].strip())
        placeholder = "%s" if not self.db_manager.offline else "?"
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, correo, cargo FROM Empleado WHERE id_empleado = {placeholder}",
            (self._emp_sel,),
        )
        if row:
            doc, nom, tel, cor, cargo = row[0]
            self.ent_doc_e.delete(0, "end")
            self.ent_doc_e.insert(0, doc or "")
            self.ent_nom_e.delete(0, "end")
            self.ent_nom_e.insert(0, nom or "")
            self.ent_tel_e.delete(0, "end")
            self.ent_tel_e.insert(0, tel or "")
            self.ent_cor_e.delete(0, "end")
            self.ent_cor_e.insert(0, cor or "")
            self.cargo_var.set(cargo or cargos_permitidos_para_gerente()[0])

    def _nuevo_empleado(self):
        self._emp_sel = None
        for e in [self.ent_doc_e, self.ent_nom_e, self.ent_tel_e, self.ent_cor_e]:
            e.delete(0, "end")
        self.cargo_var.set(cargos_permitidos_para_gerente()[0])

    def _guardar_empleado(self):
        from tkinter import messagebox

        doc = self.ent_doc_e.get().strip()
        nom = self.ent_nom_e.get().strip()
        tel = self.ent_tel_e.get().strip()
        cor = self.ent_cor_e.get().strip()
        cargo = self.cargo_var.get().strip()
        if not doc or not nom or not cor or not cargo:
            messagebox.showwarning(
                "Aviso", "Documento, nombre, correo y cargo son obligatorios"
            )
            return
        if cargo.lower() == "gerente" and not puede_gestionar_gerentes(
            self.user_data.get("rol")
        ):
            messagebox.showwarning(
                "Aviso",
                "No tiene permiso para gestionar empleados con cargo 'gerente'",
            )
            return
        if not verificar_permiso_creacion_empleado(cargo, self.user_data.get("rol")):
            messagebox.showwarning(
                "Aviso", "No tiene permiso para crear/editar este empleado"
            )
            return
        placeholder = "%s" if not self.db_manager.offline else "?"
        try:
            if self._emp_sel:
                q = f"UPDATE Empleado SET documento={placeholder}, nombre={placeholder}, telefono={placeholder}, correo={placeholder}, cargo={placeholder} WHERE id_empleado={placeholder}"
                params = (doc, nom, tel, cor, cargo, self._emp_sel)
            else:
                q = f"INSERT INTO Empleado (documento, nombre, telefono, correo, cargo) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
                params = (doc, nom, tel, cor, cargo)
            self.db_manager.execute_query(q, params, fetch=False)
            messagebox.showinfo("Éxito", "Empleado guardado correctamente")
            self._nuevo_empleado()
            self._cargar_empleados()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Agregar vehículo", font=("Arial", 18, "bold")).pack(
            pady=10
        )

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        labels = [
            "Placa:",
            "Chasis:",
            "Modelo:",
            "Kilometraje:",
            "Marca:",
            "Color:",
            "Tipo:",
            "Transmisión:",
            "Blindaje:",
            "Seguro:",
            "Proveedor:",
            "Taller:",
        ]
        for i, lbl in enumerate(labels):
            ctk.CTkLabel(form, text=lbl).grid(
                row=i, column=0, padx=5, pady=5, sticky="e"
            )

        self.ent_placa = ctk.CTkEntry(form, width=150)
        self.ent_chasis = ctk.CTkEntry(form, width=150)
        self.ent_modelo = ctk.CTkEntry(form, width=150)
        self.ent_km = ctk.CTkEntry(form, width=150)

        self.ent_placa.grid(row=0, column=1, padx=5, pady=5)
        self.ent_chasis.grid(row=1, column=1, padx=5, pady=5)
        self.ent_modelo.grid(row=2, column=1, padx=5, pady=5)
        self.ent_km.grid(row=3, column=1, padx=5, pady=5)

        # Cargar listas iniciales
        marcas = (
            self.db_manager.execute_query(
                "SELECT id_marca, nombre_marca FROM Marca_vehiculo"
            )
            or []
        )
        colores = (
            self.db_manager.execute_query(
                "SELECT id_color, nombre_color FROM Color_vehiculo"
            )
            or []
        )
        tipos = (
            self.db_manager.execute_query(
                "SELECT id_tipo, descripcion FROM Tipo_vehiculo"
            )
            or []
        )
        trans = (
            self.db_manager.execute_query(
                "SELECT id_transmision, descripcion FROM Transmision_vehiculo"
            )
            or []
        )
        blindajes = (
            self.db_manager.execute_query(
                "SELECT id_blindaje, descripcion FROM Blindaje_vehiculo"
            )
            or []
        )
        seguros = (
            self.db_manager.execute_query(
                "SELECT id_seguro, descripcion FROM Seguro_vehiculo WHERE estado = 'Activo'"
            )
            or []
        )

        self.marca_map = {m[1]: m[0] for m in marcas}
        self.color_map = {c[1]: c[0] for c in colores}
        self.tipo_map = {t[1]: t[0] for t in tipos}
        self.trans_map = {tr[1]: tr[0] for tr in trans}
        self.blindaje_map = {b[1]: b[0] for b in blindajes}
        self.seguro_map = {s[1]: s[0] for s in seguros}

        self.var_marca = ctk.StringVar(
            value=list(self.marca_map.keys())[0] if self.marca_map else ""
        )
        self.var_color = ctk.StringVar(
            value=list(self.color_map.keys())[0] if self.color_map else ""
        )
        self.var_tipo = ctk.StringVar(
            value=list(self.tipo_map.keys())[0] if self.tipo_map else ""
        )
        self.var_trans = ctk.StringVar(
            value=list(self.trans_map.keys())[0] if self.trans_map else ""
        )
        self.var_blindaje = ctk.StringVar(
            value=list(self.blindaje_map.keys())[0] if self.blindaje_map else ""
        )
        self.var_seguro = ctk.StringVar(
            value=list(self.seguro_map.keys())[0] if self.seguro_map else ""
        )
        self.var_prov = ctk.StringVar()
        self.var_taller = ctk.StringVar()

        self.opt_marca = ctk.CTkOptionMenu(
            form, variable=self.var_marca, values=list(self.marca_map.keys())
        )
        self.opt_color = ctk.CTkOptionMenu(
            form, variable=self.var_color, values=list(self.color_map.keys())
        )
        self.opt_tipo = ctk.CTkOptionMenu(
            form, variable=self.var_tipo, values=list(self.tipo_map.keys())
        )
        self.opt_trans = ctk.CTkOptionMenu(
            form, variable=self.var_trans, values=list(self.trans_map.keys())
        )
        self.opt_blindaje = ctk.CTkOptionMenu(
            form, variable=self.var_blindaje, values=list(self.blindaje_map.keys())
        )
        self.opt_seguro = ctk.CTkOptionMenu(
            form, variable=self.var_seguro, values=list(self.seguro_map.keys())
        )
        self.opt_prov = ctk.CTkOptionMenu(form, variable=self.var_prov, values=[])
        self.opt_taller = ctk.CTkOptionMenu(form, variable=self.var_taller, values=[])

        self.opt_marca.grid(row=4, column=1, padx=5, pady=5)
        self.opt_color.grid(row=5, column=1, padx=5, pady=5)
        self.opt_tipo.grid(row=6, column=1, padx=5, pady=5)
        self.opt_trans.grid(row=7, column=1, padx=5, pady=5)
        self.opt_blindaje.grid(row=8, column=1, padx=5, pady=5)
        self.opt_seguro.grid(row=9, column=1, padx=5, pady=5)
        self.opt_prov.grid(row=10, column=1, padx=5, pady=5)
        self.opt_taller.grid(row=11, column=1, padx=5, pady=5)

        # Cargar opciones de catálogo
        self._load_catalogos()

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(
            btn_frame, text="Nuevo", command=self._nuevo_vehiculo, width=100
        ).grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._guardar_vehiculo,
            width=120,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).grid(row=0, column=1, padx=5)

    def _nuevo_vehiculo(self):
        for ent in [self.ent_placa, self.ent_chasis, self.ent_modelo, self.ent_km]:
            ent.delete(0, "end")
        self._load_catalogos()

    def _load_catalogos(self):
        """Recargar opciones de proveedores, talleres, blindaje y seguros."""
        proveedores = (
            self.db_manager.execute_query(
                "SELECT id_proveedor, nombre FROM Proveedor_vehiculo"
            )
            or []
        )
        talleres = (
            self.db_manager.execute_query(
                "SELECT id_taller, nombre FROM Taller_mantenimiento"
            )
            or []
        )
        blindajes = (
            self.db_manager.execute_query(
                "SELECT id_blindaje, descripcion FROM Blindaje_vehiculo"
            )
            or []
        )
        seguros = (
            self.db_manager.execute_query(
                "SELECT id_seguro, descripcion FROM Seguro_vehiculo WHERE estado = 'Activo'"
            )
            or []
        )

        self.prov_map = {p[1]: p[0] for p in proveedores}
        self.taller_map = {t[1]: t[0] for t in talleres}
        self.blindaje_map = {b[1]: b[0] for b in blindajes}
        self.seguro_map = {s[1]: s[0] for s in seguros}

        self.opt_prov.configure(values=list(self.prov_map.keys()))
        self.opt_taller.configure(values=list(self.taller_map.keys()))
        self.opt_blindaje.configure(values=list(self.blindaje_map.keys()))
        self.opt_seguro.configure(values=list(self.seguro_map.keys()))

        if self.prov_map:
            self.var_prov.set(list(self.prov_map.keys())[0])
        else:
            self.var_prov.set("")
        if self.taller_map:
            self.var_taller.set(list(self.taller_map.keys())[0])
        else:
            self.var_taller.set("")
        if self.blindaje_map:
            self.var_blindaje.set(list(self.blindaje_map.keys())[0])
        else:
            self.var_blindaje.set("")
        if self.seguro_map:
            self.var_seguro.set(list(self.seguro_map.keys())[0])
        else:
            self.var_seguro.set("")

    def _guardar_vehiculo(self):
        from tkinter import messagebox

        placa = self.ent_placa.get().strip()
        chasis = self.ent_chasis.get().strip()
        modelo = self.ent_modelo.get().strip()
        km = self.ent_km.get().strip()

        if not placa or not modelo:
            messagebox.showwarning("Aviso", "Placa y modelo son obligatorios")
            return

        try:
            km_val = int(km) if km else 0
        except ValueError:
            messagebox.showwarning("Aviso", "Kilometraje inválido")
            return

        marca = (
            self.marca_map.get(self.var_marca.get()) if self.var_marca.get() else None
        )
        color = (
            self.color_map.get(self.var_color.get()) if self.var_color.get() else None
        )
        tipo = self.tipo_map.get(self.var_tipo.get()) if self.var_tipo.get() else None
        trans = (
            self.trans_map.get(self.var_trans.get()) if self.var_trans.get() else None
        )
        prov = self.prov_map.get(self.var_prov.get()) if self.var_prov.get() else None
        blindaje = (
            self.blindaje_map.get(self.var_blindaje.get())
            if self.var_blindaje.get()
            else None
        )
        seguro = (
            self.seguro_map.get(self.var_seguro.get())
            if self.var_seguro.get()
            else None
        )
        sucursal = self.user_data.get("id_sucursal")

        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            f"INSERT INTO Vehiculo (placa, n_chasis, modelo, kilometraje, "
            f"id_marca, id_color, id_tipo_vehiculo, id_transmision, "
            f"id_blindaje, id_seguro_vehiculo, id_estado_vehiculo, "
            f"id_proveedor, id_sucursal) "
            f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, "
            f"{placeholder}, {placeholder}, {placeholder}, {placeholder}, "
            f"{placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )
        params = (
            placa,
            chasis,
            modelo,
            km_val,
            marca,
            color,
            tipo,
            trans,
            blindaje,
            seguro,
            1,
            prov,
            sucursal,
        )
        try:
            self.db_manager.execute_query(query, params, fetch=False)
            messagebox.showinfo("Éxito", "Vehículo guardado correctamente")
            self._nuevo_vehiculo()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _build_tab_vehiculos_registrados(self, parent):
        import tkinter as tk
        from tkinter import ttk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(
            frame, text="Vehículos registrados", font=("Arial", 18, "bold")
        ).pack(pady=10)

        query = (
            "SELECT v.placa, v.modelo, su.nombre, su.direccion, su.telefono, su.gerente "
            "FROM Vehiculo v LEFT JOIN Sucursal su ON v.id_sucursal = su.id_sucursal"
        )
        rows = self.db_manager.execute_query(query) or []

        cols = ("c1", "c2", "c3", "c4", "c5", "c6")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        headers = [
            ("c1", "Placa"),
            ("c2", "Modelo"),
            ("c3", "Sucursal"),
            ("c4", "Dirección"),
            ("c5", "Teléfono"),
            ("c6", "Gerente"),
        ]
        for cid, text in headers:
            tree.heading(cid, text=text)
            tree.column(cid, width=120, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for r in rows:
            tree.insert("", "end", values=r)

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        self._cliente_sel = None

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Gestión de clientes", font=("Arial", 18, "bold")
        ).pack(pady=10)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_cli = tk.Listbox(
            list_frame, height=8, width=60, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.lb_cli.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_cli.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Documento:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Nombre:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Teléfono:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Dirección:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        ctk.CTkLabel(form, text="Correo:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )

        self.ent_doc_c = ctk.CTkEntry(form, width=150)
        self.ent_nom_c = ctk.CTkEntry(form, width=150)
        self.ent_tel_c = ctk.CTkEntry(form, width=150)
        self.ent_dir_c = ctk.CTkEntry(form, width=150)
        self.ent_cor_c = ctk.CTkEntry(form, width=150)

        self.ent_doc_c.grid(row=0, column=1, padx=5, pady=5)
        self.ent_nom_c.grid(row=1, column=1, padx=5, pady=5)
        self.ent_tel_c.grid(row=2, column=1, padx=5, pady=5)
        self.ent_dir_c.grid(row=3, column=1, padx=5, pady=5)
        self.ent_cor_c.grid(row=4, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(
            btn_frame, text="Nuevo", command=self._nuevo_cliente, width=100
        ).grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._guardar_cliente,
            width=120,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).grid(row=0, column=1, padx=5)
        # Botón para eliminar el cliente seleccionado
        self.btn_eliminar_cliente = ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=self._eliminar_cliente,
            width=120,
            fg_color="#F44336",
            hover_color="#B71C1C",
        )
        self.btn_eliminar_cliente.grid(row=0, column=2, padx=5)

        self.lb_cli.bind("<<ListboxSelect>>", self._seleccionar_cliente)
        self._cargar_clientes()

    def _cargar_clientes(self):
        self.lb_cli.delete(0, "end")
        rows = self.db_manager.execute_query(
            "SELECT id_cliente, nombre, correo FROM Cliente"
        )
        if rows:
            for r in rows:
                self.lb_cli.insert("end", f"{r[0]} | {r[1]} | {r[2]}")

    def _seleccionar_cliente(self, event=None):
        sel = self.lb_cli.curselection()
        if not sel:
            return
        self._cliente_sel = int(self.lb_cli.get(sel[0]).split("|")[0].strip())
        placeholder = "%s" if not self.db_manager.offline else "?"
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = {placeholder}",
            (self._cliente_sel,),
        )
        if row:
            doc, nom, tel, dir_, cor = row[0]
            self.ent_doc_c.delete(0, "end")
            self.ent_doc_c.insert(0, doc or "")
            self.ent_nom_c.delete(0, "end")
            self.ent_nom_c.insert(0, nom or "")
            self.ent_tel_c.delete(0, "end")
            self.ent_tel_c.insert(0, tel or "")
            self.ent_dir_c.delete(0, "end")
            self.ent_dir_c.insert(0, dir_ or "")
            self.ent_cor_c.delete(0, "end")
            self.ent_cor_c.insert(0, cor or "")

    def _nuevo_cliente(self):
        self._cliente_sel = None
        for e in [
            self.ent_doc_c,
            self.ent_nom_c,
            self.ent_tel_c,
            self.ent_dir_c,
            self.ent_cor_c,
        ]:
            e.delete(0, "end")

    def _guardar_cliente(self):
        from tkinter import messagebox

        doc = self.ent_doc_c.get().strip()
        nom = self.ent_nom_c.get().strip()
        tel = self.ent_tel_c.get().strip()
        dir_ = self.ent_dir_c.get().strip()
        cor = self.ent_cor_c.get().strip()

        if not doc or not nom or not cor:
            messagebox.showwarning(
                "Aviso", "Documento, nombre y correo son obligatorios"
            )
            return

        placeholder = "%s" if not self.db_manager.offline else "?"
        try:
            if self._cliente_sel:
                q = (
                    f"UPDATE Cliente SET documento={placeholder}, nombre={placeholder}, telefono={placeholder}, "
                    f"direccion={placeholder}, correo={placeholder} WHERE id_cliente={placeholder}"
                )
                params = (doc, nom, tel, dir_, cor, self._cliente_sel)
            else:
                q = (
                    f"INSERT INTO Cliente (documento, nombre, telefono, direccion, correo) "
                    f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
                )
                params = (doc, nom, tel, dir_, cor)
            self.db_manager.execute_query(q, params, fetch=False)
            messagebox.showinfo("Éxito", "Cliente guardado correctamente")
            self._nuevo_cliente()
            self._cargar_clientes()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _eliminar_cliente(self):
        from tkinter import messagebox

        if not self._cliente_sel:
            messagebox.showwarning("Aviso", "Seleccione un cliente")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar cliente seleccionado?"):
            return

        placeholder = "%s" if not self.db_manager.offline else "?"
        try:
            # Eliminar de forma manual los registros dependientes para imitar
            # un comportamiento ON DELETE CASCADE en ambas bases de datos
            self.db_manager.execute_query(
                f"DELETE FROM Abono_reserva WHERE id_reserva IN ("
                f"SELECT ra.id_reserva FROM Reserva_alquiler ra "
                f"JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
                f"WHERE a.id_cliente = {placeholder})",
                (self._cliente_sel,),
                fetch=False,
            )
            self.db_manager.execute_query(
                f"DELETE FROM Reserva_alquiler WHERE id_alquiler IN ("
                f"SELECT id_alquiler FROM Alquiler WHERE id_cliente = {placeholder})",
                (self._cliente_sel,),
                fetch=False,
            )
            self.db_manager.execute_query(
                f"DELETE FROM Alquiler WHERE id_cliente = {placeholder}",
                (self._cliente_sel,),
            )
            self.db_manager.execute_query(
                f"DELETE FROM Usuario WHERE id_cliente = {placeholder}",
                (self._cliente_sel,),
                fetch=False,
            )
            self.db_manager.execute_query(
                f"DELETE FROM Cliente WHERE id_cliente = {placeholder}",
                (self._cliente_sel,),
                fetch=False,
            )
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
            self._nuevo_cliente()
            self._cargar_clientes()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _build_tab_reportes(self, parent):
        import tkinter as tk
        from tkinter import ttk
        from datetime import datetime
        from src.services import reports

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reportes de ventas", font=("Arial", 18, "bold")).pack(
            pady=10
        )

        controls = ctk.CTkFrame(frame)
        controls.pack(pady=10)
        mes_var = tk.IntVar(value=datetime.now().month)
        anio_var = tk.IntVar(value=datetime.now().year)
        tk.Label(controls, text="Mes:").grid(row=0, column=0, padx=2)
        tk.Spinbox(controls, from_=1, to=12, width=4, textvariable=mes_var).grid(
            row=0, column=1
        )
        tk.Label(controls, text="Año:").grid(row=0, column=2, padx=2)
        tk.Spinbox(controls, from_=2020, to=2100, width=6, textvariable=anio_var).grid(
            row=0, column=3
        )
        ctk.CTkButton(
            controls, text="Ventas por sede", command=lambda: mostrar("sucursal")
        ).grid(row=0, column=4, padx=4)
        ctk.CTkButton(
            controls, text="Ventas por vendedor", command=lambda: mostrar("vendedor")
        ).grid(row=0, column=5, padx=4)

        tree = ttk.Treeview(frame, columns=("c1", "c2"), show="headings", height=8)
        tree.heading("c1", text="ID")
        tree.heading("c2", text="Total")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def mostrar(tipo):
            for row in tree.get_children():
                tree.delete(row)
            mes = mes_var.get()
            anio = anio_var.get()
            if tipo == "sucursal":
                rows = reports.ventas_por_sucursal(self.db_manager, mes, anio)
                tree.heading("c1", text="Sucursal")
            else:
                rows = reports.ventas_por_vendedor(self.db_manager, mes, anio)
                tree.heading("c1", text="Empleado")
            for r in rows:
                tree.insert("", "end", values=r)

    def _build_tab_sql_libre(self, parent):
        import tkinter as tk
        from tkinter import messagebox, ttk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Consulta SQL:").pack(pady=(10, 5))
        query_entry = ctk.CTkTextbox(frame, height=80)
        query_entry.pack(fill="x", padx=5)

        ctk.CTkLabel(frame, text="Resultado:").pack(pady=(10, 5))
        tree = ttk.Treeview(frame, show="headings")
        tree.pack(expand=True, fill="both", padx=5, pady=(0, 10))

        def ejecutar():
            query = query_entry.get("1.0", "end").strip()
            if not query:
                messagebox.showwarning("Error", "Ingrese una consulta SQL")
                return
            if not puede_ejecutar_sql_libre(self.user_data.get("rol")):
                messagebox.showwarning("Error", "No autorizado")
                return
            for row in tree.get_children():
                tree.delete(row)
            try:
                rows, headers = self.db_manager.execute_query_with_headers(query)
                if rows is None:
                    messagebox.showerror("Error", "Error al ejecutar la consulta")
                    return
                tree.configure(columns=[f"c{i}" for i in range(len(headers))])
                for i, h in enumerate(headers):
                    cid = f"c{i}"
                    tree.heading(cid, text=h)
                    tree.column(cid, width=120, anchor="center")
                if not rows:
                    tree.insert("", "end", values=("Consulta ejecutada correctamente",))
                else:
                    for r in rows:
                        tree.insert("", "end", values=r)
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ctk.CTkButton(
            frame,
            text="Ejecutar",
            command=ejecutar,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_COLOR_DARK,
        ).pack(pady=5)


