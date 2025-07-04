import customtkinter as ctk
from .base_view import BaseCTKView
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre,
)
from ..styles import BG_DARK, TEXT_COLOR, PRIMARY_COLOR, PRIMARY_COLOR_DARK

class EmpleadoCajaView(BaseCTKView):
    """Vista para empleados de caja."""

    def _welcome_message(self):
        return f"Bienvenido empleado de caja, {self.user_data.get('usuario', '')}"

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

        self.tab_pagos = self.tabview.add("Pagos en efectivo")
        self._build_tab_pagos_efectivo(self.tabview.tab("Pagos en efectivo"))

        self.tab_caja_dia = self.tabview.add("Caja del día")
        self._build_tab_caja_dia(self.tabview.tab("Caja del día"))

        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))

        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

        self.tab_perfil = self.tabview.add("Editar perfil")
        self._build_tab_perfil(self.tabview.tab("Editar perfil"))

    def _build_tab_pagos_efectivo(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Pagos en efectivo", font=("Arial", 18, "bold")
        ).pack(pady=10)

        canvas = tk.Canvas(
            frame,
            borderwidth=0,
            background="#FFF8E1",
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_y.pack(side="right", fill="y", pady=10)

        scrollable = ctk.CTkFrame(canvas, fg_color="#FFF8E1")
        inner_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")

        def _resize_inner(event):
            canvas_width = event.width
            canvas.itemconfig(inner_id, width=canvas_width)

        canvas.bind("<Configure>", _resize_inner)

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable.bind("<Configure>", _on_frame_configure)
        canvas.configure(yscrollcommand=scroll_y.set)

        self.cards_efectivo = ctk.CTkFrame(scrollable, fg_color="#FFF8E1")
        self.cards_efectivo.pack(fill="both", expand=True, padx=10, pady=10)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=10)

        ctk.CTkLabel(
            input_frame, text="Monto recibido ($):", font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.entry_monto_efectivo = ctk.CTkEntry(
            input_frame, width=120, state="disabled", placeholder_text="Ej: 50000"
        )
        self.entry_monto_efectivo.grid(row=0, column=1, padx=5, pady=5)

        self.btn_aprobar_efectivo = ctk.CTkButton(
            frame,
            text="Aprobar pago",
            command=self._aprobar_pago_efectivo,
            fg_color="#00AA00",
            hover_color="#008800",
            state="disabled",
        )
        self.btn_aprobar_efectivo.pack(pady=10)

        self._reserva_efectivo_sel = None
        self._refresh_reservas_pendientes_efectivo()

    def _cargar_reservas_pendientes_efectivo(self):
        """Return pending reservations for cash payments."""
        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            "SELECT ra.id_reserva, c.nombre, v.placa, ra.saldo_pendiente, a.fecha_hora_salida "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            f"WHERE ra.saldo_pendiente > 0 AND a.id_sucursal = {placeholder}"
        )
        return (
            self.db_manager.execute_query(
                query, (self.user_data.get("id_sucursal"),)
            )
            or []
        )

    def _refresh_reservas_pendientes_efectivo(self):
        for w in self.cards_efectivo.winfo_children():
            w.destroy()
        reservas = self._cargar_reservas_pendientes_efectivo()
        self._efectivo_cards = {}
        for rid, nombre, placa, saldo, fecha in reservas:
            card = ctk.CTkFrame(self.cards_efectivo, fg_color="white", corner_radius=12)
            card.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(
                card, text=f"Reserva {rid} - Cliente {nombre}", font=("Arial", 13, "bold")
            ).pack(anchor="w", padx=10, pady=(4, 0))
            ctk.CTkLabel(card, text=f"Vehículo: {placa}", font=("Arial", 12)).pack(
                anchor="w", padx=10
            )
            ctk.CTkLabel(
                card,
                text=f"Saldo pendiente: ${saldo:,.0f}",
                font=("Arial", 12),
                text_color="#B8860B",
            ).pack(anchor="w", padx=10)
            ctk.CTkLabel(
                card,
                text=f"Fecha: {str(fecha)[:16]}",
                font=("Arial", 11),
            ).pack(anchor="w", padx=10)
            ctk.CTkButton(
                card,
                text="Seleccionar",
                command=lambda rid=rid: self._seleccionar_reserva_efectivo(rid),
                width=120,
                fg_color=PRIMARY_COLOR,
                hover_color=PRIMARY_COLOR_DARK,
            ).pack(padx=10, pady=6, anchor="e")
            self._efectivo_cards[rid] = card
        if not reservas:
            ctk.CTkLabel(
                self.cards_efectivo, text="No hay reservas pendientes", font=("Arial", 13)
            ).pack(pady=20)
        self._reserva_efectivo_sel = None
        self.entry_monto_efectivo.configure(state="disabled")
        self.btn_aprobar_efectivo.configure(state="disabled")

    def _seleccionar_reserva_efectivo(self, id_reserva):
        for rid, card in self._efectivo_cards.items():
            card.configure(fg_color="#FFF59D" if rid == id_reserva else "white")
        self._reserva_efectivo_sel = id_reserva
        self.entry_monto_efectivo.configure(state="normal")
        self.btn_aprobar_efectivo.configure(state="normal")

    def _aprobar_pago_efectivo(self):
        from tkinter import messagebox

        rid = self._reserva_efectivo_sel
        if not rid:
            messagebox.showwarning("Aviso", "Seleccione una reserva")
            return
        monto = self.entry_monto_efectivo.get().strip()
        if not monto:
            messagebox.showwarning("Error", "Ingrese el monto recibido")
            return
        self._procesar_pago_efectivo(rid, monto)

    def _procesar_pago_efectivo(self, id_reserva, monto):
        """Registrar un pago en efectivo para la reserva indicada."""
        from tkinter import messagebox

        try:
            monto_f = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
            return

        if monto_f <= 0:
            messagebox.showerror("Error", "El monto debe ser mayor a 0")
            return

        placeholder = "%s" if not self.db_manager.offline else "?"
        val_q = (
            "SELECT ra.saldo_pendiente, a.id_sucursal "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"WHERE ra.id_reserva = {placeholder}"
        )
        row = self.db_manager.execute_query(val_q, (id_reserva,))
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

        if monto_f < saldo:
            messagebox.showerror(
                "Error",
                f"El monto no cubre el saldo pendiente (${saldo:,.0f})",
            )
            return

        # Registrar el abono en efectivo
        insert_q = f"""
            INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago)
            VALUES ({placeholder}, CURRENT_TIMESTAMP, {placeholder}, 1)
        """
        self.db_manager.execute_query(insert_q, (monto_f, id_reserva), fetch=False)

        # Actualizar saldo pendiente de la reserva
        nuevo_saldo = max(0, saldo - monto_f)
        update_q = f"UPDATE Reserva_alquiler SET saldo_pendiente = {placeholder}"
        params = [nuevo_saldo]
        if nuevo_saldo <= 0:
            update_q += ", id_estado_reserva = 2"
        update_q += f" WHERE id_reserva = {placeholder}"
        params.append(id_reserva)
        self.db_manager.execute_query(update_q, tuple(params), fetch=False)

        messagebox.showinfo("Pago registrado", f"Pago de ${monto_f:,.0f} registrado")

        self.entry_monto_efectivo.delete(0, "end")
        # Recalcular transacciones del día y actualizar los totales
        self._transacciones_dia = self._cargar_transacciones_dia()
        self._actualizar_caja_dia()
        self._refresh_reservas_pendientes_efectivo()

    def _build_tab_caja_dia(self, parent):
        """Construir pestaña que muestra el total de caja del día."""
        import tkinter as tk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.lbl_caja_total = ctk.CTkLabel(
            frame, text="Total efectivo del día: $0", font=("Arial", 16, "bold")
        )
        self.lbl_caja_total.pack(pady=(10, 0))

        self.lbl_caja_count = ctk.CTkLabel(frame, text="Transacciones: 0")
        self.lbl_caja_count.pack()

        self.lbl_caja_avg = ctk.CTkLabel(frame, text="Promedio: $0")
        self.lbl_caja_avg.pack(pady=(0, 10))

        canvas = tk.Canvas(
            frame, borderwidth=0, highlightthickness=0, background="#E3F2FD"
        )
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_y.pack(side="right", fill="y", pady=10)

        self.transaccion_frame = ctk.CTkFrame(canvas, fg_color="#E3F2FD")
        inner_id = canvas.create_window((0, 0), window=self.transaccion_frame, anchor="nw")

        def _resize_inner(event):
            canvas.itemconfig(inner_id, width=event.width)

        canvas.bind("<Configure>", _resize_inner)

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.transaccion_frame.bind("<Configure>", _on_frame_configure)
        canvas.configure(yscrollcommand=scroll_y.set)

        ctk.CTkButton(
            frame,
            text="Cerrar Caja",
            command=self._cerrar_caja,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_COLOR_DARK,
        ).pack(pady=5)

        # Inicializar lista de transacciones y mostrar totales
        self._transacciones_dia = self._cargar_transacciones_dia()
        self._actualizar_caja_dia()

    def _actualizar_caja_dia(self):
        """Actualizar el resumen de caja del día y la lista de transacciones."""
        transacciones = getattr(self, "_transacciones_dia", [])
        total = sum(float(t[1]) for t in transacciones)
        count = len(transacciones)
        promedio = total / count if count else 0

        if hasattr(self, "lbl_caja_total"):
            self.lbl_caja_total.configure(
                text=f"Total efectivo del día: ${total:,.0f}"
            )
        if hasattr(self, "lbl_caja_count"):
            self.lbl_caja_count.configure(text=f"Transacciones: {count}")
        if hasattr(self, "lbl_caja_avg"):
            self.lbl_caja_avg.configure(text=f"Promedio: ${promedio:,.0f}")

        if hasattr(self, "transaccion_frame"):
            for w in self.transaccion_frame.winfo_children():
                w.destroy()
            for cliente, valor, fecha in transacciones:
                hora = str(fecha)[11:16] if fecha else ""
                row = ctk.CTkFrame(
                    self.transaccion_frame, fg_color="white", corner_radius=8
                )
                row.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(row, text=cliente, width=200, anchor="w").pack(
                    side="left", padx=5
                )
                ctk.CTkLabel(
                    row, text=f"${float(valor):,.0f}", width=80, anchor="e"
                ).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=hora, anchor="e").pack(
                    side="right", padx=5
                )

    def _cargar_transacciones_dia(self):
        """Obtener transacciones de efectivo del día."""
        placeholder = "%s" if not self.db_manager.offline else "?"
        date_fn = "CURDATE()" if not self.db_manager.offline else "date('now')"
        query = (
            "SELECT ab.valor, c.nombre, ab.fecha_hora "
            "FROM Abono_reserva ab "
            "JOIN Reserva_alquiler ra ON ab.id_reserva = ra.id_reserva "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            f"WHERE DATE(ab.fecha_hora) = {date_fn} "
            "AND ab.id_medio_pago = 1 "
            f"AND a.id_sucursal = {placeholder}"
        )
        return (
            self.db_manager.execute_query(
                query, (self.user_data.get("id_sucursal"),)
            )
            or []
        )

    def _cerrar_caja(self):
        """Limpiar el contador local de caja y refrescar la vista."""
        self._transacciones_dia = []
        self._actualizar_caja_dia()

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Abonos por cliente", font=("Arial", 18, "bold")
        ).pack(pady=10)

        # --- Dropdown con los clientes disponibles ---
        rows = (
            self.db_manager.execute_query(
                "SELECT id_cliente, nombre FROM Cliente ORDER BY nombre"
            )
            or []
        )
        self._cliente_map = {f"{cid} - {nom}": cid for cid, nom in rows}
        self._cliente_var = ctk.StringVar(
            value=next(iter(self._cliente_map), "")
        )

        opt = ctk.CTkOptionMenu(
            frame,
            variable=self._cliente_var,
            values=list(self._cliente_map.keys()),
            command=lambda _: _cargar_reservas(),
        )
        opt.pack(pady=5)

        # --- Listado de reservas activas del cliente seleccionado ---
        list_frame = ctk.CTkFrame(frame, fg_color="#FFF8E1")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_res_cli = tk.Listbox(
            list_frame, height=8, width=60, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.lb_res_cli.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_res_cli.pack(side="left", fill="both", expand=True)

        self.lb_res_cli.bind("<<ListboxSelect>>", lambda e: _seleccionar())

        # --- Entrada de monto y botón para registrar abono ---
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=10)
        ctk.CTkLabel(input_frame, text="Monto ($):").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.ent_abono_cli = ctk.CTkEntry(input_frame, width=120)
        self.ent_abono_cli.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(
            input_frame,
            text="Registrar abono",
            command=lambda: _registrar_abono(),
            width=140,
            fg_color="#00AA00",
            hover_color="#008800",
        ).grid(row=0, column=2, padx=5, pady=5)

        self._reserva_cli_sel = None

        def _cargar_reservas():
            self.lb_res_cli.delete(0, "end")
            self._reserva_cli_sel = None
            cli = self._cliente_var.get()
            cid = self._cliente_map.get(cli)
            if not cid:
                return
            placeholder = "%s" if not self.db_manager.offline else "?"
            query = (
                "SELECT ra.id_reserva, v.placa, ra.saldo_pendiente "
                "FROM Reserva_alquiler ra "
                "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
                "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
                f"WHERE a.id_cliente = {placeholder} "
                "AND ra.saldo_pendiente > 0 AND ra.id_estado_reserva IN (1,2)"
            )
            rows = self.db_manager.execute_query(query, (cid,)) or []
            for rid, placa, saldo in rows:
                self.lb_res_cli.insert(
                    "end", f"{rid} | {placa} | ${float(saldo):,.0f}"
                )

        def _seleccionar():
            sel = self.lb_res_cli.curselection()
            if sel:
                self._reserva_cli_sel = int(
                    self.lb_res_cli.get(sel[0]).split("|")[0].strip()
                )
            else:
                self._reserva_cli_sel = None

        def _registrar_abono():
            rid = self._reserva_cli_sel
            if not rid:
                messagebox.showwarning("Aviso", "Seleccione una reserva")
                return
            monto = self.ent_abono_cli.get().strip()
            if not monto:
                messagebox.showwarning("Error", "Ingrese un monto")
                return
            self._procesar_pago_efectivo(rid, monto)
            self.ent_abono_cli.delete(0, "end")
            _cargar_reservas()

        _cargar_reservas()

    def _build_tab_perfil(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        id_emp = self.user_data.get("id_empleado")

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Editar perfil", font=("Arial", 16)).pack(pady=10)

        placeholder = "%s" if not self.db_manager.offline else "?"
        datos = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, correo FROM Empleado WHERE id_empleado = {placeholder}",
            (id_emp,),
        ) or []

        documento = tk.StringVar(value=datos[0][0] if datos else "")
        nombre = tk.StringVar(value=datos[0][1] if datos else "")
        telefono = tk.StringVar(value=datos[0][2] if datos else "")
        correo = tk.StringVar(value=datos[0][3] if datos else "")

        ctk.CTkLabel(frame, text="Documento:").pack()
        entry_doc = ctk.CTkEntry(frame, textvariable=documento)
        entry_doc.pack()
        ctk.CTkLabel(frame, text="Nombre:").pack()
        entry_nombre = ctk.CTkEntry(frame, textvariable=nombre)
        entry_nombre.pack()
        ctk.CTkLabel(frame, text="Teléfono:").pack()
        entry_tel = ctk.CTkEntry(frame, textvariable=telefono)
        entry_tel.pack()
        ctk.CTkLabel(frame, text="Correo:").pack()
        entry_correo = ctk.CTkEntry(frame, textvariable=correo)
        entry_correo.pack()

        def guardar():
            params = (
                entry_doc.get(),
                entry_nombre.get(),
                entry_tel.get(),
                entry_correo.get(),
                id_emp,
            )
            query = (
                "UPDATE Empleado SET documento = %s, nombre = %s, telefono = %s, correo = %s "
                "WHERE id_empleado = %s"
            )
            prev_offline = self.db_manager.offline
            try:
                if not self.db_manager.offline:
                    self.db_manager.execute_query(query, params, fetch=False)
                self.db_manager.offline = True
                self.db_manager.execute_query(query, params, fetch=False)
                messagebox.showinfo("Éxito", "Perfil actualizado correctamente")
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo actualizar el perfil: {exc}")
            finally:
                self.db_manager.offline = prev_offline

        ctk.CTkButton(frame, text="Guardar cambios", command=guardar).pack(pady=10)


