import customtkinter as ctk
from .base_view import BaseCTKView
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre,
)
from ..styles import BG_DARK, TEXT_COLOR, PRIMARY_COLOR, PRIMARY_COLOR_DARK

class EmpleadoVentasView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de ventas, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
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
        # Pestaña: Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        self._build_tab_reservas(self.tabview.tab("Reservas"))
        # Pestaña: Vehículos
        self.tab_vehiculos = self.tabview.add("Vehículos")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos"))

        self.tab_vehiculos_reg = self.tabview.add("Vehículos registrados")
        self._build_tab_vehiculos_registrados(self.tabview.tab("Vehículos registrados"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))
        # Abrir directamente la pestaña de reservas
        self.tabview.set("Reservas")

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
        self.lb_clientes = tk.Listbox(
            list_frame, height=8, width=60, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.lb_clientes.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_clientes.pack(side="left", fill="both", expand=True)

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

        self.ent_doc = ctk.CTkEntry(form, width=150)
        self.ent_nom = ctk.CTkEntry(form, width=150)
        self.ent_tel = ctk.CTkEntry(form, width=150)
        self.ent_dir = ctk.CTkEntry(form, width=150)
        self.ent_cor = ctk.CTkEntry(form, width=150)

        self.ent_doc.grid(row=0, column=1, padx=5, pady=5)
        self.ent_nom.grid(row=1, column=1, padx=5, pady=5)
        self.ent_tel.grid(row=2, column=1, padx=5, pady=5)
        self.ent_dir.grid(row=3, column=1, padx=5, pady=5)
        self.ent_cor.grid(row=4, column=1, padx=5, pady=5)

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

        self.lb_clientes.bind("<<ListboxSelect>>", self._seleccionar_cliente)
        self._cargar_clientes()

        def refresh():
            self._cargar_clientes()

        self._refresh_clientes = refresh

    def _build_tab_reservas(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        from tkcalendar import DateEntry

        self._reserva_sel = None

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        top = ctk.CTkFrame(frame)
        top.pack(fill="x")
        ctk.CTkButton(
            top, text="Nueva reserva", command=lambda: self._abrir_form_reserva()
        ).pack(side="right", padx=5, pady=5)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_reservas = tk.Listbox(
            list_frame, height=10, width=80, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.lb_reservas.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_reservas.pack(side="left", fill="both", expand=True)

        btns = ctk.CTkFrame(frame)
        btns.pack(pady=5)
        ctk.CTkButton(
            btns,
            text="Editar",
            command=lambda: self._abrir_form_reserva(self._reserva_sel),
            width=120,
        ).grid(row=0, column=0, padx=5)

        self.lb_reservas.bind(
            "<<ListboxSelect>>", lambda e: self._seleccionar_reserva()
        )
        self._cargar_reservas()

        def refresh():
            self._cargar_reservas()

        self._refresh_reservas = refresh

    def _cargar_clientes(self):
        self.lb_clientes.delete(0, "end")
        rows = self.db_manager.execute_query(
            "SELECT id_cliente, nombre, correo FROM Cliente"
        )
        if rows:
            for c in rows:
                self.lb_clientes.insert("end", f"{c[0]} | {c[1]} | {c[2]}")

    def _seleccionar_cliente(self, event):
        sel = self.lb_clientes.curselection()
        if not sel:
            return
        idx = sel[0]
        data = self.lb_clientes.get(idx).split("|")
        self._cliente_sel = int(data[0].strip())
        placeholder = "%s" if not self.db_manager.offline else "?"
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = {placeholder}",
            (self._cliente_sel,),
        )
        if row:
            doc, nom, tel, dir_, cor = row[0]
            self.ent_doc.delete(0, "end")
            self.ent_doc.insert(0, doc or "")
            self.ent_nom.delete(0, "end")
            self.ent_nom.insert(0, nom or "")
            self.ent_tel.delete(0, "end")
            self.ent_tel.insert(0, tel or "")
            self.ent_dir.delete(0, "end")
            self.ent_dir.insert(0, dir_ or "")
            self.ent_cor.delete(0, "end")
            self.ent_cor.insert(0, cor or "")

    def _nuevo_cliente(self):
        self._cliente_sel = None
        for e in [self.ent_doc, self.ent_nom, self.ent_tel, self.ent_dir, self.ent_cor]:
            e.delete(0, "end")

    def _guardar_cliente(self):
        from tkinter import messagebox

        doc = self.ent_doc.get().strip()
        nom = self.ent_nom.get().strip()
        tel = self.ent_tel.get().strip()
        dir_ = self.ent_dir.get().strip()
        cor = self.ent_cor.get().strip()
        if not doc or not nom or not cor:
            messagebox.showwarning(
                "Aviso", "Documento, nombre y correo son obligatorios"
            )
            return
        placeholder = "%s" if not self.db_manager.offline else "?"
        try:
            if self._cliente_sel:
                q = f"UPDATE Cliente SET documento={placeholder}, nombre={placeholder}, telefono={placeholder}, direccion={placeholder}, correo={placeholder} WHERE id_cliente={placeholder}"
                params = (doc, nom, tel, dir_, cor, self._cliente_sel)
            else:
                q = f"INSERT INTO Cliente (documento, nombre, telefono, direccion, correo) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
                params = (doc, nom, tel, dir_, cor)
            self.db_manager.execute_query(q, params, fetch=False)
            messagebox.showinfo("Éxito", "Cliente guardado correctamente")
            self._nuevo_cliente()
            self._cargar_clientes()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _cargar_reservas(self):
        self.lb_reservas.delete(0, "end")
        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            "SELECT ra.id_reserva, a.id_cliente, c.nombre, a.id_vehiculo "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            f"WHERE a.id_sucursal = {placeholder} "
            "ORDER BY c.nombre"
        )
        reservas = self.db_manager.execute_query(
            query, (self.user_data.get("id_sucursal"),)
        )
        if reservas:
            for r in reservas:
                res_id, cid, cname, veh = r
                self.lb_reservas.insert("end", f"{res_id} | {cname} ({cid}) | {veh}")

    def _seleccionar_reserva(self):
        sel = self.lb_reservas.curselection()
        if sel:
            self._reserva_sel = int(self.lb_reservas.get(sel[0]).split("|")[0].strip())
        else:
            self._reserva_sel = None

    def _abrir_form_reserva(self, id_reserva=None, vehiculo=None):
        from tkinter import messagebox
        from tkcalendar import DateEntry
        import tkinter as tk
        from datetime import datetime

        win = ctk.CTkToplevel(self)
        win.title("Reserva")
        win.geometry("400x500")
        win.configure(fg_color="#222831")
        win.transient(self)
        win.grab_set()

        # Clientes disponibles
        clientes = (
            self.db_manager.execute_query(
                "SELECT id_cliente, nombre FROM Cliente ORDER BY nombre"
            )
            or []
        )
        cliente_map = {nombre: cid for cid, nombre in clientes}
        cliente_var = ctk.StringVar(value=next(iter(cliente_map), ""))
        ctk.CTkLabel(win, text="Cliente:").pack(pady=4)
        opt_cliente = ctk.CTkOptionMenu(
            win, variable=cliente_var, values=list(cliente_map.keys())
        )
        opt_cliente.pack(pady=4)

        # Vehículos disponibles
        if hasattr(self.db_manager, "update_maintenance_states"):
            self.db_manager.update_maintenance_states()
        placeholder = "%s" if not self.db_manager.offline else "?"
        vehiculos = (
            self.db_manager.execute_query(
                f"SELECT placa FROM Vehiculo WHERE id_estado_vehiculo = 1 AND id_sucursal = {placeholder}",
                (self.user_data.get("id_sucursal"),),
            )
            or []
        )
        veh_map = {v[0]: v[0] for v in vehiculos}
        vehiculo_var = ctk.StringVar(value=next(iter(veh_map), ""))
        if vehiculo and vehiculo in veh_map:
            vehiculo_var.set(vehiculo)
        ctk.CTkLabel(win, text="Vehículo:").pack(pady=4)
        opt_veh = ctk.CTkOptionMenu(
            win, variable=vehiculo_var, values=list(veh_map.keys())
        )
        opt_veh.pack(pady=4)

        ctk.CTkLabel(win, text="Fecha salida:").pack(pady=4)
        salida = DateEntry(win, date_pattern="yyyy-mm-dd")
        salida.pack(pady=4)
        ctk.CTkLabel(win, text="Fecha entrada:").pack(pady=4)
        entrada = DateEntry(win, date_pattern="yyyy-mm-dd")
        entrada.pack(pady=4)

        if id_reserva:
            placeholder = "%s" if not self.db_manager.offline else "?"
            q = (
                "SELECT a.id_cliente, a.id_vehiculo, a.fecha_hora_salida, a.fecha_hora_entrada "
                "FROM Reserva_alquiler ra JOIN Alquiler a ON ra.id_alquiler=a.id_alquiler WHERE ra.id_reserva=%s"
            )
            row = self.db_manager.execute_query(
                q.replace("%s", placeholder), (id_reserva,)
            )
            if row:
                cid, veh, fs, fe = row[0]
                name = cliente_map.get(cid) or next(
                    (n for n, i in cliente_map.items() if i == cid), ""
                )
                if name:
                    cliente_var.set(name)
                if veh in veh_map:
                    vehiculo_var.set(veh)
                salida.set_date(fs)
                entrada.set_date(fe)

        def guardar():
            cid = cliente_map.get(cliente_var.get())
            veh = vehiculo_var.get().strip()
            fs = salida.get_date().strftime("%Y-%m-%d")
            fe = entrada.get_date().strftime("%Y-%m-%d")
            if not cid or not veh:
                messagebox.showwarning("Aviso", "Complete todos los campos")
                return
            placeholder = "%s" if not self.db_manager.offline else "?"
            # Validar estado actual del vehículo
            estado_q = f"SELECT id_estado_vehiculo FROM Vehiculo WHERE placa = {placeholder}"
            estado = self.db_manager.execute_query(estado_q, (veh,)) or []
            if not estado or int(estado[0][0]) != 1:
                messagebox.showerror("Error", "El vehículo seleccionado no está disponible")
                return
            try:
                if id_reserva:
                    q = f"UPDATE Alquiler a JOIN Reserva_alquiler ra ON a.id_alquiler=ra.id_alquiler SET a.id_cliente={placeholder}, a.id_vehiculo={placeholder}, a.fecha_hora_salida={placeholder}, a.fecha_hora_entrada={placeholder} WHERE ra.id_reserva={placeholder}"
                    self.db_manager.execute_query(
                        q, (cid, veh, fs, fe, id_reserva), fetch=False
                    )
                else:
                    q = f"INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
                    id_alq = self.db_manager.execute_query(
                        q,
                        (fs, fe, veh, cid, self.user_data.get("id_empleado")),
                        fetch=False,
                        return_lastrowid=True,
                    )
                    if id_alq:
                        update_vehicle = (
                            f"UPDATE Vehiculo SET id_estado_vehiculo = 2 WHERE placa = {placeholder}"
                        )
                        self.db_manager.execute_query(update_vehicle, (veh,), fetch=False)
                        q2 = (
                            f"INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado)"
                            f" VALUES ({placeholder}, 1, 0, 0, {placeholder})"
                        )
                        self.db_manager.execute_query(
                            q2,
                            (id_alq, self.user_data.get("id_empleado")),
                            fetch=False,
                        )
                messagebox.showinfo("Éxito", "Reserva guardada")
                win.destroy()
                self._cargar_reservas()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ctk.CTkButton(
            win,
            text="Guardar",
            command=guardar,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).pack(pady=10)

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(
            frame, text="Vehículos disponibles", font=("Arial", 18, "bold")
        ).pack(pady=10)
        # Contenedor de tarjetas
        self.cards_vehiculos = ctk.CTkFrame(frame, fg_color="#E3F2FD")  # Azul pastel
        self.cards_vehiculos.pack(fill="both", expand=True, padx=10, pady=10)
        # Listar vehículos disponibles con TODA la información relevante
        placeholder = "%s" if not self.db_manager.offline else "?"
        id_sucursal = self.user_data.get("id_sucursal")
        query = f"""
            SELECT v.placa, v.modelo, v.kilometraje, v.n_chasis,
                   m.nombre_marca, t.descripcion as tipo_vehiculo, t.tarifa_dia, t.capacidad, t.combustible,
                   c.nombre_color, tr.descripcion as transmision, ci.descripcion as cilindraje,
                   b.descripcion as blindaje, s.estado as seguro_estado, s.descripcion as seguro_desc,
                   su.nombre as sucursal, su.direccion as sucursal_dir, su.telefono as sucursal_tel, su.gerente as sucursal_mgr
            FROM Vehiculo v
            JOIN Marca_vehiculo m ON v.id_marca = m.id_marca
            JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo
            LEFT JOIN Color_vehiculo c ON v.id_color = c.id_color
            LEFT JOIN Transmision_vehiculo tr ON v.id_transmision = tr.id_transmision
            LEFT JOIN Cilindraje_vehiculo ci ON v.id_cilindraje = ci.id_cilindraje
            LEFT JOIN Blindaje_vehiculo b ON v.id_blindaje = b.id_blindaje
            LEFT JOIN Seguro_vehiculo s ON v.id_seguro_vehiculo = s.id_seguro
            LEFT JOIN Sucursal su ON v.id_sucursal = su.id_sucursal
            WHERE v.id_estado_vehiculo = 1"""
        params = ()
        if id_sucursal is not None:
            query += f" AND v.id_sucursal = {placeholder}"
            params = (id_sucursal,)
        vehiculos = self.db_manager.execute_query(query, params)

        if not vehiculos:
            ctk.CTkLabel(
                self.cards_vehiculos,
                text="No hay vehículos disponibles",
                font=("Arial", 14),
            ).pack(pady=20)
            return

        # Limitar la cantidad de tarjetas mostradas
        max_cards = 5
        vehiculos = vehiculos[:max_cards]

        for i, vehiculo in enumerate(vehiculos):
            (
                placa,
                modelo,
                kilometraje,
                n_chasis,
                marca,
                tipo_vehiculo,
                tarifa_dia,
                capacidad,
                combustible,
                color,
                transmision,
                cilindraje,
                blindaje,
                seguro_estado,
                seguro_desc,
                sucursal,
                sucursal_dir,
                sucursal_tel,
                sucursal_mgr,
            ) = vehiculo

            # Crear tarjeta con información completa
            card = ctk.CTkFrame(
                self.cards_vehiculos, fg_color="#FFFFFF", corner_radius=15
            )
            card.pack(fill="x", padx=10, pady=5)

            # Header de la tarjeta
            header_frame = ctk.CTkFrame(card, fg_color="#2196F3", corner_radius=10)
            header_frame.pack(fill="x", padx=10, pady=(10, 5))

            ctk.CTkLabel(
                header_frame,
                text=f"{marca} {modelo}",
                font=("Arial", 16, "bold"),
                text_color="white",
            ).pack(pady=5)
            ctk.CTkLabel(
                header_frame,
                text=f"Placa: {placa}",
                font=("Arial", 12),
                text_color="white",
            ).pack()

            # Información principal
            main_frame = ctk.CTkFrame(card, fg_color="transparent")
            main_frame.pack(fill="x", padx=10, pady=5)

            # Primera fila de información
            row1 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row1.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row1,
                text=f"💰 Tarifa: ${tarifa_dia:,.0f}/día",
                font=("Arial", 12, "bold"),
                text_color="#2E7D32",
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                row1,
                text=f"👥 Capacidad: {capacidad} personas",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                row1,
                text=f"⛽ Combustible: {combustible}",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)

            # Segunda fila de información
            row2 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row2.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row2,
                text=f"🎨 Color: {color or 'No especificado'}",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                row2,
                text=f"⚙️ Transmisión: {transmision or 'No especificado'}",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                row2,
                text=f"🔧 Cilindraje: {cilindraje or 'No especificado'}",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)

            # Tercera fila de información
            row3 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row3.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row3,
                text=f"🛡️ Blindaje: {blindaje or 'No especificado'}",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                row3,
                text=f"📊 Kilometraje: {kilometraje:,} km",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                row3,
                text=f"🔒 Seguro: {seguro_estado or 'No especificado'}",
                font=("Arial", 12),
                text_color="#424242",
            ).pack(side="left", padx=5)

            # Información de sucursal
            if sucursal:
                row4 = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=5)
                row4.pack(fill="x", pady=5)

                ctk.CTkLabel(
                    row4,
                    text=f"🏢 Sucursal: {sucursal}",
                    font=("Arial", 11, "bold"),
                    text_color="#1976D2",
                ).pack(anchor="w", padx=5, pady=2)
                if sucursal_dir:
                    ctk.CTkLabel(
                        row4,
                        text=f"📍 {sucursal_dir}",
                        font=("Arial", 10),
                        text_color="#666666",
                    ).pack(anchor="w", padx=5)
                if sucursal_tel:
                    ctk.CTkLabel(
                        row4,
                        text=f"📞 {sucursal_tel}",
                        font=("Arial", 10),
                        text_color="#666666",
                    ).pack(anchor="w", padx=5)

            # Botón de reservar (solo para empleados de ventas)
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(5, 10))

            if (self.user_data.get("tipo_empleado") or "").lower() == "ventas":
                ctk.CTkButton(
                    btn_frame,
                    text="🚗 Reservar este vehículo",
                    command=lambda p=placa: self._abrir_form_reserva(None, p),
                    fg_color="#4CAF50",
                    hover_color="#388E3C",
                    font=("Arial", 12, "bold"),
                ).pack(pady=5)

    def _abrir_nueva_reserva_vehiculo(self, vehiculo):
        import tkinter as tk
        from tkinter import messagebox
        from datetime import datetime
        from tkcalendar import DateEntry

        win = ctk.CTkToplevel(self)
        win.title("Nueva reserva")
        win.geometry("600x700")
        win.configure(fg_color="#222831")
        win.transient(self)
        win.grab_set()
        win.focus_set()
        # Centrar ventana
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (600 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (700 // 2)
        win.geometry(f"600x700+{x}+{y}")
        placa, modelo, marca, tipo, tarifa_dia = vehiculo
        ctk.CTkLabel(
            win,
            text=f"Placa: {placa} | {modelo} {marca} ({tipo})",
            font=("Arial", 15, "bold"),
        ).pack(pady=8)
        ctk.CTkLabel(
            win, text=f"Tarifa por día: ${tarifa_dia}", font=("Arial", 13)
        ).pack(pady=4)
        # Frame de fecha y hora salida (solo uno, tipo tk.Frame)
        salida_frame = tk.Frame(win, bg="#222831")
        salida_frame.pack(fill="x", pady=8)
        tk.Label(
            salida_frame,
            text="Fecha y hora salida:",
            font=("Arial", 12),
            bg="#222831",
            fg="#F5F6FA",
        ).pack(anchor="w")
        salida_date = DateEntry(salida_frame, date_pattern="yyyy-mm-dd", width=12)
        salida_date.pack(side="left", padx=2)
        # Combobox para hora (1-12), minutos y AM/PM usando solo tkinter
        horas_12 = [f"{h:02d}" for h in range(1, 13)]
        minutos = ["00", "15", "30", "45"]
        ampm = ["AM", "PM"]
        salida_hora_cb = tk.ttk.Combobox(
            salida_frame, values=horas_12, width=3, state="readonly"
        )
        salida_hora_cb.set("08")
        salida_hora_cb.pack(side="left", padx=2)
        tk.Label(salida_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        salida_min_cb = tk.ttk.Combobox(
            salida_frame, values=minutos, width=3, state="readonly"
        )
        salida_min_cb.set("00")
        salida_min_cb.pack(side="left", padx=2)
        salida_ampm_cb = tk.ttk.Combobox(
            salida_frame, values=ampm, width=3, state="readonly"
        )
        salida_ampm_cb.set("AM")
        salida_ampm_cb.pack(side="left", padx=2)
        # Frame de fecha y hora entrada (solo uno, tipo tk.Frame)
        entrada_frame = tk.Frame(win, bg="#222831")
        entrada_frame.pack(fill="x", pady=8)
        tk.Label(
            entrada_frame,
            text="Fecha y hora entrada:",
            font=("Arial", 12),
            bg="#222831",
            fg="#F5F6FA",
        ).pack(anchor="w")
        entrada_date = DateEntry(entrada_frame, date_pattern="yyyy-mm-dd", width=12)
        entrada_date.pack(side="left", padx=2)
        entrada_hora_cb = tk.ttk.Combobox(
            entrada_frame, values=horas_12, width=3, state="readonly"
        )
        entrada_hora_cb.set("09")
        entrada_hora_cb.pack(side="left", padx=2)
        tk.Label(entrada_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        entrada_min_cb = tk.ttk.Combobox(
            entrada_frame, values=minutos, width=3, state="readonly"
        )
        entrada_min_cb.set("00")
        entrada_min_cb.pack(side="left", padx=2)
        entrada_ampm_cb = tk.ttk.Combobox(
            entrada_frame, values=ampm, width=3, state="readonly"
        )
        entrada_ampm_cb.set("AM")
        entrada_ampm_cb.pack(side="left", padx=2)
        # Seguros disponibles
        ctk.CTkLabel(win, text="Seguro:", font=("Arial", 12)).pack(pady=4)
        seguros = self.db_manager.execute_query(
            "SELECT id_seguro, descripcion, costo FROM Seguro_alquiler"
        )
        seguro_var = tk.StringVar()
        if seguros:
            seguro_menu = tk.OptionMenu(
                win, seguro_var, *[f"{s[1]} (${s[2]})" for s in seguros]
            )
            seguro_menu.pack(fill="x", pady=4)
            seguro_var.set(f"{seguros[0][1]} (${seguros[0][2]})")
        else:
            ctk.CTkLabel(
                win, text="No hay seguros disponibles", text_color="#FF5555"
            ).pack(pady=4)
        # Descuentos disponibles
        ctk.CTkLabel(win, text="Descuento:", font=("Arial", 12)).pack(pady=4)
        id_descuento_act, desc_text, desc_val = self._obtener_descuento_activo()
        if id_descuento_act:
            ctk.CTkLabel(
                win,
                text=f"Descuento aplicado: {desc_text} (-${desc_val})",
                font=("Arial", 12),
            ).pack(pady=4)
        else:
            ctk.CTkLabel(win, text="Sin descuentos activos").pack(pady=4)
        # Etiquetas para mostrar el total y el abono mínimo
        total_label = ctk.CTkLabel(
            win,
            text="Total a pagar: $0",
            font=("Arial", 14, "bold"),
            text_color="#00FF99",
        )
        total_label.pack(pady=8)
        abono_min_label = ctk.CTkLabel(
            win, text="Abono mínimo (30%): $0", font=("Arial", 13), text_color="#FFD700"
        )
        abono_min_label.pack(pady=4)
        # Abono y método de pago
        ctk.CTkLabel(
            win, text="Abono inicial ($, mínimo 30%):", font=("Arial", 12)
        ).pack(pady=4)
        entry_abono = ctk.CTkEntry(win, width=120)  # Ampliado para mejor visibilidad
        entry_abono.pack(pady=4)
        ctk.CTkLabel(win, text="Método de pago:", font=("Arial", 12)).pack(pady=4)
        metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]
        metodo_pago_var = tk.StringVar()
        metodo_pago_var.set(metodos_pago[0])
        metodo_pago_menu = tk.OptionMenu(win, metodo_pago_var, *metodos_pago)
        metodo_pago_menu.pack(pady=4)

        # Modifico la función para obtener la hora en formato 24h
        def get_24h(date, hora_cb, min_cb, ampm_cb):
            h = int(hora_cb.get())
            m = int(min_cb.get())
            ampm = ampm_cb.get()
            if ampm == "PM" and h != 12:
                h += 12
            if ampm == "AM" and h == 12:
                h = 0
            return f"{date.get()} {h:02d}:{m:02d}"

        # Función para calcular y mostrar el total y abono mínimo
        def actualizar_total(*args):
            try:
                fmt = "%Y-%m-%d %H:%M"
                salida = get_24h(
                    salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb
                )
                entrada = get_24h(
                    entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb
                )
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                idx_seg = [
                    i
                    for i, s in enumerate(seguros)
                    if f"{s[1]} (${s[2]})" == seguro_var.get()
                ]
                costo_seguro = float(seguros[idx_seg[0]][2]) if idx_seg else 0
                valor_descuento = float(desc_val) if id_descuento_act else 0
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                abono_min = round(total * 0.3, 2)
                total_label.configure(text=f"Total a pagar: ${total:,.2f}")
                abono_min_label.configure(text=f"Abono mínimo (30%): ${abono_min:,.2f}")
            except Exception:
                total_label.configure(text="Total a pagar: $0")
                abono_min_label.configure(text="Abono mínimo (30%): $0")

        # Asociar eventos para recalcular
        for widget in [
            salida_date,
            salida_hora_cb,
            salida_min_cb,
            salida_ampm_cb,
            entrada_date,
            entrada_hora_cb,
            entrada_min_cb,
            entrada_ampm_cb,
        ]:
            widget.bind("<<ComboboxSelected>>", actualizar_total)
            widget.bind("<FocusOut>", actualizar_total)
        if seguros:
            seguro_var.trace_add("write", lambda *a: actualizar_total())
        # Inicializar valores
        actualizar_total()

        # Guardar reserva
        def guardar():
            salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
            entrada = get_24h(
                entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb
            )
            abono = entry_abono.get().strip()
            metodo_pago = metodo_pago_var.get()
            if (
                not salida
                or not entrada
                or not (seguros and seguro_var.get())
                or not abono
                or not metodo_pago
            ):
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            fmt = "%Y-%m-%d %H:%M"
            try:
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                if dt_salida < datetime.now():
                    messagebox.showwarning(
                        "Error", "La fecha de salida no puede ser en el pasado"
                    )
                    return
                if dt_entrada <= dt_salida:
                    messagebox.showwarning(
                        "Error", "La fecha de entrada debe ser posterior a la de salida"
                    )
                    return
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                idx_seg = [
                    i
                    for i, s in enumerate(seguros)
                    if f"{s[1]} (${s[2]})" == seguro_var.get()
                ]
                id_seguro = seguros[idx_seg[0]][0] if idx_seg else None
                costo_seguro = float(seguros[idx_seg[0]][2]) if idx_seg else 0
                id_descuento = id_descuento_act
                valor_descuento = float(desc_val) if id_descuento_act else 0
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0

                print(
                    f"Total calculado: ${total:,.0f} (días: {dias}, tarifa: ${tarifa}, seguro: ${seguro_costo}, descuento: ${valor_descuento})"
                )

                # Validar abono mínimo
                abono_min = int(total * 0.3)
                abono = int(entry_abono.get().strip())
                if abono < abono_min:
                    messagebox.showwarning(
                        "Error",
                        f"El abono inicial debe ser al menos el 30%: ${abono_min:,.0f}",
                    )
                    return

                metodo = metodo_var.get()
                id_cliente = self.user_data.get("id_cliente")

                print(f"Insertando en Alquiler...")
                # Insertar en Alquiler
                placeholder = "%s" if not self.db_manager.offline else "?"
                alquiler_query = f"""
                    INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado,
                    id_seguro, id_descuento, valor)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """
                id_alquiler = self.db_manager.execute_query(
                    alquiler_query,
                    (
                        fecha_hora_salida,
                        fecha_hora_entrada,
                        placa,
                        id_cliente,
                        self.user_data.get("id_empleado"),
                        id_seguro,
                        id_descuento,
                        total,
                    ),
                    fetch=False,
                    return_lastrowid=True,
                )

                if not id_alquiler:
                    messagebox.showerror(
                        "Error", "No se pudo obtener el ID del alquiler"
                    )
                    return

                print(f"ID Alquiler obtenido: {id_alquiler}")

                # Cambiar estado del vehículo a reservado
                update_vehicle = (
                    f"UPDATE Vehiculo SET id_estado_vehiculo = 2 WHERE placa = {placeholder}"
                )
                self.db_manager.execute_query(update_vehicle, (placa,), fetch=False)

                # Insertar en Reserva_alquiler
                saldo_pendiente = total - abono
                print(
                    f"Insertando en Reserva_alquiler con saldo pendiente: ${saldo_pendiente}"
                )
                reserva_query = f"""
                    INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado)
                    VALUES ({placeholder}, 1, {placeholder}, {placeholder}, {placeholder})
                """
                id_reserva = self.db_manager.execute_query(
                    reserva_query,
                    (
                        id_alquiler,
                        saldo_pendiente,
                        abono,
                        self.user_data.get("id_empleado"),
                    ),
                    fetch=False,
                    return_lastrowid=True,
                )
                if not id_reserva:
                    raise Exception("No se pudo obtener el ID de la reserva")

                print(f"ID Reserva obtenido: {id_reserva}")

                # Insertar abono inicial
                id_medio_pago = (
                    1 if metodo == "Efectivo" else (2 if metodo == "Tarjeta" else 3)
                )
                print(
                    f"Insertando abono inicial de ${abono} con medio de pago {id_medio_pago}"
                )
                abono_query = f"""
                    INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) 
                    VALUES ({placeholder}, NOW(), {placeholder}, {placeholder})
                """
                self.db_manager.execute_query(
                    abono_query, (abono, id_reserva, id_medio_pago), fetch=False
                )

                print(f"Reserva creada exitosamente. ID: {id_reserva}")

                # Mostrar mensaje según método de pago
                if metodo in ("Tarjeta", "Transferencia"):
                    self._simular_pasarela_pago(id_reserva, abono, metodo)
                else:
                    messagebox.showinfo(
                        "Reserva registrada",
                        "Debes acercarte a la sede para validar y abonar el pago.",
                    )

                # Recargar lista de reservas
                print(f"Recargando lista de reservas...")
                self._cargar_reservas_cliente(id_cliente)
                self._cargar_reservas_pendientes(id_cliente)

                # Limpiar formulario
                entry_abono.delete(0, "end")

            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo crear la reserva: {exc}")
                print(f"Error detallado: {exc}")

        ctk.CTkButton(
            frame,
            text="Guardar reserva",
            command=guardar,
            fg_color="#3A86FF",
            hover_color="#265DAB",
            font=("Arial", 13, "bold"),
        ).pack(pady=18)

    def _build_tab_reservas(self, parent):
        from tkinter import ttk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas", font=("Arial", 16)).pack(pady=10)

        # Listar reservas en tabla
        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            "SELECT ra.id_reserva, a.id_cliente, a.id_vehiculo, "
            "a.fecha_hora_salida, a.fecha_hora_entrada, es.descripcion "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "LEFT JOIN Estado_reserva es ON ra.id_estado_reserva = es.id_estado "
            f"WHERE a.id_sucursal = {placeholder} "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        reservas = self.db_manager.execute_query(
            query, (self.user_data.get("id_sucursal"),)
        )

        cols = ("c1", "c2", "c3", "c4", "c5", "c6")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        headers = [
            ("c1", "ID"),
            ("c2", "Cliente"),
            ("c3", "Vehículo"),
            ("c4", "Salida"),
            ("c5", "Entrada"),
            ("c6", "Estado"),
        ]
        widths = [60, 80, 80, 140, 140, 100]
        for (cid, text), w in zip(headers, widths):
            tree.heading(cid, text=text)
            tree.column(cid, width=w, anchor="center")
        tree.pack(fill="both", expand=True, pady=10)

        if reservas:
            for r in reservas:
                rid, cid_, veh, sal, ent, est = r
                tree.insert("", "end", values=(rid, cid_, veh, str(sal), str(ent), est))
        else:
            tree.insert("", "end", values=("No hay reservas registradas",))

    def _build_tab_clientes(self, parent):
        import tkinter as tk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Clientes", font=("Arial", 16)).pack(pady=10)
        # Listar clientes
        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            f"SELECT id_cliente, nombre, correo FROM Cliente "
            f"WHERE id_sucursal = {placeholder} ORDER BY nombre"
        )
        clientes = self.db_manager.execute_query(
            query, (self.user_data.get("id_sucursal"),)
        )
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if clientes:
            for c in clientes:
                listbox.insert("end", f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]}")
        else:
            listbox.insert("end", "No hay clientes registrados.")

    def _cargar_reservas_pendientes_global(self):
        for w in self.cards_abonos.winfo_children():
            w.destroy()
        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            "SELECT ra.id_reserva, a.id_cliente, v.modelo, v.placa, ra.saldo_pendiente "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler AND a.id_sucursal = {placeholder} "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            "WHERE ra.saldo_pendiente > 0 AND ra.id_estado_reserva IN (1,2) "
            "ORDER BY ra.id_reserva"
        )
        reservas = self.db_manager.execute_query(
            query, (self.user_data.get("id_sucursal"),)
        )
        self._abono_cards = {}
        if reservas:
            for r in reservas:
                rid, cid, modelo, placa, saldo = r
                card = ctk.CTkFrame(
                    self.cards_abonos, fg_color="white", corner_radius=12
                )
                card.pack(fill="x", padx=10, pady=8)
                ctk.CTkLabel(
                    card,
                    text=f"Reserva {rid} - Cliente {cid}",
                    font=("Arial", 14, "bold"),
                ).pack(anchor="w", padx=12)
                ctk.CTkLabel(card, text=f"{modelo} ({placa})", font=("Arial", 12)).pack(
                    anchor="w", padx=12
                )
                ctk.CTkLabel(
                    card,
                    text=f"Saldo: ${saldo:,.0f}",
                    font=("Arial", 12),
                    text_color="#B8860B",
                ).pack(anchor="w", padx=12)
                card.bind(
                    "<Button-1>", lambda e, rid=rid: self._seleccionar_abono_card(rid)
                )
                for child in card.winfo_children():
                    child.bind(
                        "<Button-1>",
                        lambda e, rid=rid: self._seleccionar_abono_card(rid),
                    )
                self._abono_cards[rid] = card
        else:
            ctk.CTkLabel(
                self.cards_abonos, text="No hay reservas pendientes", font=("Arial", 13)
            ).pack(pady=20)
        self._abono_seleccionado = None
        self.input_abono.configure(state="disabled")
        self.metodo_pago_menu.configure(state="disabled")
        self.btn_abonar.configure(state="disabled")

    def _realizar_abono_global(self):
        from tkinter import messagebox

        id_reserva = self._abono_seleccionado
        if not id_reserva:
            messagebox.showwarning("Aviso", "Seleccione una reserva")
            return
        monto = self.input_abono.get().strip()
        metodo = self.metodo_pago_var.get()
        if not monto:
            messagebox.showwarning("Error", "Ingrese un monto")
            return
        try:
            monto_f = float(monto)
        except ValueError:
            messagebox.showwarning("Error", "Monto inválido")
            return
        if monto_f <= 0:
            messagebox.showwarning("Error", "El monto debe ser mayor a 0")
            return
        placeholder = "%s" if not self.db_manager.offline else "?"
        val_query = (
            "SELECT ra.saldo_pendiente, a.id_sucursal "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"WHERE ra.id_reserva={placeholder}"
        )
        row = self.db_manager.execute_query(val_query, (id_reserva,))
        if not row:
            messagebox.showerror("Error", "Reserva no encontrada")
            return
        saldo = float(row[0][0])
        sucursal_reserva = row[0][1]
        if sucursal_reserva != self.user_data.get("id_sucursal"):
            messagebox.showerror(
                "Error", "No puedes procesar reservas de otra sucursal"
            )
            return
        if monto_f > saldo:
            messagebox.showwarning("Error", f"El monto excede el saldo (${saldo:,.0f})")
            return
        self._registrar_abono(id_reserva, monto_f, metodo, None)
        self._cargar_reservas_pendientes_global()


