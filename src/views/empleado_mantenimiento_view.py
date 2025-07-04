import customtkinter as ctk
from .base_view import BaseCTKView
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre,
)
from ..styles import BG_DARK, TEXT_COLOR, PRIMARY_COLOR, PRIMARY_COLOR_DARK

class EmpleadoMantenimientoView(BaseCTKView):
    def _welcome_message(self):
        return (
            f"Bienvenido empleado de mantenimiento, {self.user_data.get('usuario', '')}"
        )

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
        # Pestaña principal: Bienvenida y cerrar sesión
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(
            frame,
            text=self._welcome_message(),
            text_color=TEXT_COLOR,
            font=("Arial", 20),
        ).pack(pady=30)
        ctk.CTkButton(
            frame,
            text="Cerrar sesión",
            command=self.logout,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_COLOR_DARK,
            width=180,
            height=38,
        ).pack(side="bottom", pady=(30, 20))
        # Pestaña: Vehículos
        self.tab_vehiculos = self.tabview.add("Vehículos")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos"))
        # Pestaña: Reportar
        self.tab_reportar = self.tabview.add("Reportar")
        self._build_tab_reportar(self.tabview.tab("Reportar"))
        # Pestaña: Editar vehículo
        self.tab_edit = self.tabview.add("Editar vehículo")
        self._build_tab_editar_vehiculo(self.tabview.tab("Editar vehículo"))
        # Pestaña: Historial
        self.tab_historial = self.tabview.add("Historial")
        self._build_tab_historial(self.tabview.tab("Historial"))
        # Pestaña: Predictivo
        self.tab_predictivo = self.tabview.add("Predictivo")
        self._build_tab_predictivo(self.tabview.tab("Predictivo"))
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        self._build_tab_reservas(self.tabview.tab("Reservas"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Vehículos asignados", font=("Arial", 18, "bold")
        ).pack(pady=10)

        cont = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        cont.pack(fill="both", expand=True, padx=10, pady=10)

        placeholder = "%s" if not self.db_manager.offline else "?"
        id_sucursal = self.user_data.get("id_sucursal")
        query = (
            "SELECT v.placa, v.modelo, m.nombre_marca, t.descripcion "
            "FROM Vehiculo v "
            "JOIN Marca_vehiculo m ON v.id_marca = m.id_marca "
            "JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo "
        )
        params = ()
        if id_sucursal is not None:
            query += f"WHERE v.id_sucursal = {placeholder}"
            params = (id_sucursal,)
        vehiculos = self.db_manager.execute_query(query, params)

        if not vehiculos:
            ctk.CTkLabel(cont, text="Sin vehículos asignados", font=("Arial", 13)).pack(
                pady=20
            )
            return

        for v in vehiculos:
            placa, modelo, marca, tipo = v
            card = ctk.CTkFrame(cont, fg_color="white", corner_radius=10)
            card.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(
                card, text=f"{marca} {modelo}", font=("Arial", 14, "bold")
            ).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(
                card, text=f"Placa: {placa} | {tipo}", font=("Arial", 12)
            ).pack(anchor="w", padx=10, pady=(0, 5))

    def _build_tab_reportar(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Reportar mantenimiento", font=("Arial", 18, "bold")
        ).pack(pady=10)

        ctk.CTkLabel(frame, text="Placa del vehículo:").pack(pady=5)
        self.rep_placa = ctk.CTkEntry(frame, width=150)
        self.rep_placa.pack(pady=5)

        ctk.CTkLabel(frame, text="Tipo de mantenimiento:").pack(pady=5)
        tipos = (
            self.db_manager.execute_query(
                "SELECT id_tipo, descripcion FROM Tipo_mantenimiento"
            )
            or []
        )
        self.rep_tipo_map = {t[1]: t[0] for t in tipos}
        self.rep_tipo_var = ctk.StringVar(
            value=list(self.rep_tipo_map.keys())[0] if self.rep_tipo_map else ""
        )
        self.rep_tipo = ctk.CTkOptionMenu(
            frame, variable=self.rep_tipo_var, values=list(self.rep_tipo_map.keys())
        )
        self.rep_tipo.pack(pady=5)

        ctk.CTkLabel(frame, text="Taller:").pack(pady=5)
        talleres = (
            self.db_manager.execute_query(
                "SELECT id_taller, nombre FROM Taller_mantenimiento"
            )
            or []
        )
        self.rep_taller_map = {t[1]: t[0] for t in talleres}
        self.rep_taller_var = ctk.StringVar(
            value=list(self.rep_taller_map.keys())[0] if self.rep_taller_map else ""
        )
        self.rep_taller = ctk.CTkOptionMenu(
            frame, variable=self.rep_taller_var, values=list(self.rep_taller_map.keys())
        )
        self.rep_taller.pack(pady=5)

        ctk.CTkLabel(frame, text="Costo:").pack(pady=5)
        self.rep_costo = ctk.CTkEntry(frame, width=150)
        self.rep_costo.pack(pady=5)

        ctk.CTkLabel(frame, text="Descripción del mantenimiento:").pack(pady=5)
        self.rep_desc = ctk.CTkEntry(frame, width=300)
        self.rep_desc.pack(pady=5)

        def guardar():
            from datetime import datetime

            placa = self.rep_placa.get().strip()
            desc = self.rep_desc.get().strip()
            costo = self.rep_costo.get().strip()
            if not placa or not desc or not costo:
                messagebox.showwarning("Aviso", "Complete todos los campos")
                return
            try:
                costo_val = float(costo)
            except ValueError:
                messagebox.showwarning("Aviso", "Costo inválido")
                return
            tipo = (
                self.rep_tipo_map.get(self.rep_tipo_var.get())
                if self.rep_tipo_var.get()
                else None
            )
            taller = (
                self.rep_taller_map.get(self.rep_taller_var.get())
                if self.rep_taller_var.get()
                else None
            )
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            placeholder = "%s" if not self.db_manager.offline else "?"
            query = (
                "INSERT INTO Mantenimiento_vehiculo "
                f"(descripcion, fecha_hora, valor, id_tipo, id_taller, id_vehiculo) "
                f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
            )
            params = (desc, fecha, costo_val, tipo, taller, placa)
            try:
                self.db_manager.execute_query(query, params, fetch=False)
                messagebox.showinfo("Éxito", "Reporte registrado")
                self.rep_placa.delete(0, "end")
                self.rep_desc.delete(0, "end")
                self.rep_costo.delete(0, "end")
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ctk.CTkButton(
            frame,
            text="Registrar",
            command=guardar,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).pack(pady=10)

    def _build_tab_historial(self, parent):
        import tkinter as tk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Historial vehículos", font=("Arial", 18, "bold")
        ).pack(pady=10)

        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.pack(pady=(0, 5))
        ctk.CTkLabel(filter_frame, text="Filtrar por placa:").pack(side="left", padx=5)
        placas = (
            self.db_manager.execute_query(
                "SELECT placa FROM Vehiculo WHERE id_sucursal = ?",
                (self.user_data.get("id_sucursal"),),
            )
            or []
        )
        opciones = ["Todos"] + [p[0] for p in placas]
        self.hist_placa_var = tk.StringVar(value="Todos")
        tk.OptionMenu(filter_frame, self.hist_placa_var, *opciones).pack(side="left")

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.hist_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, width=80
        )
        scrollbar.config(command=self.hist_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.hist_listbox.pack(side="left", fill="both", expand=True)

        def cargar():
            self.hist_listbox.delete(0, "end")
            placeholder = "%s" if not self.db_manager.offline else "?"
            base = (
                "SELECT m.id_vehiculo, m.descripcion, m.fecha_hora, m.valor "
                "FROM Mantenimiento_vehiculo m JOIN Vehiculo v ON m.id_vehiculo = v.placa "
                f"WHERE v.id_sucursal = {placeholder}"
            )
            params = [self.user_data.get("id_sucursal")]
            placa = self.hist_placa_var.get()
            if placa != "Todos":
                base += f" AND m.id_vehiculo = {placeholder}"
                params.append(placa)
            base += " ORDER BY m.fecha_hora DESC"
            rows = self.db_manager.execute_query(base, tuple(params))
            if rows:
                for p, d, fch, val in rows:
                    self.hist_listbox.insert("end", f"{fch} | {p} | {d} | ${val:,.0f}")
            else:
                self.hist_listbox.insert("end", "Sin registros de mantenimiento")

        tk.Button(filter_frame, text="Aplicar", command=cargar).pack(
            side="left", padx=5
        )
        cargar()

    def _build_tab_predictivo(self, parent):
        import tkinter as tk
        from datetime import datetime, timedelta

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Mantenimiento predictivo", font=("Arial", 18, "bold")
        ).pack(pady=10)

        # Selector de sucursal para filtrar
        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.pack(pady=(0, 10))
        sucursales = (
            self.db_manager.execute_query("SELECT id_sucursal, nombre FROM Sucursal")
            or []
        )
        opciones = [f"{s[0]} - {s[1]}" for s in sucursales]
        self.sucursal_var = tk.StringVar()
        if opciones:
            default = next(
                (
                    o
                    for o in opciones
                    if o.startswith(str(self.user_data.get("id_sucursal")))
                ),
                opciones[0],
            )
            self.sucursal_var.set(default)
            tk.OptionMenu(
                filter_frame,
                self.sucursal_var,
                *opciones,
                command=lambda *_: self._cargar_predictivo_list(),
            ).pack()
        else:
            self.sucursal_var.set(str(self.user_data.get("id_sucursal")))

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.predictivo_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, width=80
        )
        scrollbar.config(command=self.predictivo_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.predictivo_listbox.pack(side="left", fill="both", expand=True)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=8)
        ctk.CTkButton(
            btn_frame,
            text="Programar mantenimiento",
            command=self._programar_mantenimiento,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Marcar revisado",
            command=self._marcar_revisado,
            fg_color="#00C853",
            hover_color="#009624",
        ).pack(side="left", padx=5)

        self._cargar_predictivo_list()

    def _cargar_predictivo_list(self):
        import tkinter as tk
        from datetime import datetime, timedelta

        self.predictivo_listbox.delete(0, "end")
        try:
            id_sucursal = int(str(self.sucursal_var.get()).split(" -")[0])
        except Exception:
            id_sucursal = self.user_data.get("id_sucursal")

        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            "SELECT v.placa, v.modelo, v.kilometraje, MAX(m.fecha_hora) "
            "FROM Vehiculo v "
            "LEFT JOIN Mantenimiento_vehiculo m ON v.placa = m.id_vehiculo "
            f"WHERE v.id_sucursal = {placeholder} "
            "GROUP BY v.placa, v.modelo, v.kilometraje"
        )
        filas = self.db_manager.execute_query(query, (id_sucursal,))

        if not filas:
            self.predictivo_listbox.insert("end", "Sin vehículos registrados")
            return

        umbral_dias = 180
        aviso_dias = 150
        hoy = datetime.now()

        for placa, modelo, km, fecha in filas:
            necesita = False
            color = None
            if fecha is None:
                necesita = True
                color = "#FFCDD2"
                fecha_txt = "N/A"
            else:
                try:
                    fecha_dt = datetime.fromisoformat(str(fecha))
                except Exception:
                    try:
                        fecha_dt = datetime.strptime(str(fecha), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        fecha_dt = None
                dias = (hoy - fecha_dt).days if fecha_dt else umbral_dias + 1
                if dias >= umbral_dias:
                    necesita = True
                    color = "#FFCDD2"
                elif dias >= aviso_dias:
                    necesita = True
                    color = "#FFF9C4"
                fecha_txt = fecha_dt.strftime("%Y-%m-%d") if fecha_dt else str(fecha)

            if necesita:
                self.predictivo_listbox.insert(
                    "end", f"{placa} | {modelo} | {km} km | {fecha_txt}"
                )
                idx = self.predictivo_listbox.size() - 1
                if color:
                    self.predictivo_listbox.itemconfig(idx, background=color)

    def _programar_mantenimiento(self):
        from tkinter import messagebox
        import tkinter as tk
        from tkcalendar import DateEntry

        selection = self.predictivo_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione un vehículo")
            return
        item = self.predictivo_listbox.get(selection[0])
        placa = item.split("|")[0].strip()
        placeholder = "%s" if not self.db_manager.offline else "?"

        estado_q = f"SELECT id_estado_vehiculo FROM Vehiculo WHERE placa = {placeholder}"
        estado = self.db_manager.execute_query(estado_q, (placa,)) or []
        if estado and int(estado[0][0]) in (2, 3):
            messagebox.showerror(
                "Error", "El vehículo seleccionado no se puede programar"
            )
            return

        win = ctk.CTkToplevel(self)
        win.title("Programar mantenimiento")
        win.geometry("300x180")
        win.configure(fg_color="#222831")
        win.transient(self)
        win.grab_set()
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (300 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (180 // 2)
        win.geometry(f"300x180+{x}+{y}")

        ctk.CTkLabel(win, text="Fecha fin:").pack(pady=10)
        fecha_entry = DateEntry(win, date_pattern="yyyy-mm-dd")
        fecha_entry.pack(pady=5)

        def guardar():
            fecha_fin = fecha_entry.get_date().strftime("%Y-%m-%d")
            query = (
                f"INSERT INTO Mantenimiento (placa, descripcion, fecha_fin) "
                f"VALUES ({placeholder}, {placeholder}, {placeholder})"
            )
            try:
                self.db_manager.execute_query(
                    query,
                    (placa, "Programado mantenimiento", fecha_fin),
                    fetch=False,
                )
                upd = (
                    f"UPDATE Vehiculo SET id_estado_vehiculo = 3 WHERE placa = {placeholder}"
                )
                self.db_manager.execute_query(upd, (placa,), fetch=False)
                messagebox.showinfo("Éxito", "Mantenimiento programado")
                win.destroy()
                self._cargar_predictivo_list()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ctk.CTkButton(
            win,
            text="Guardar",
            command=guardar,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).pack(pady=15)

    def _marcar_revisado(self):
        from tkinter import messagebox

        selection = self.predictivo_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione un vehículo")
            return
        item = self.predictivo_listbox.get(selection[0])
        placa = item.split("|")[0].strip()
        placeholder = "%s" if not self.db_manager.offline else "?"
        estado_q = f"SELECT id_estado_vehiculo FROM Vehiculo WHERE placa = {placeholder}"
        estado = self.db_manager.execute_query(estado_q, (placa,)) or []
        if estado and int(estado[0][0]) in (2, 3):
            messagebox.showerror(
                "Error", "El vehículo seleccionado no se puede marcar"
            )
            return
        query = f"INSERT INTO Mantenimiento (placa, descripcion) VALUES ({placeholder}, {placeholder})"
        try:
            self.db_manager.execute_query(
                query, (placa, "Revisión completada"), fetch=False
            )
            messagebox.showinfo("Éxito", "Vehículo marcado como revisado")
            self._cargar_predictivo_list()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _build_tab_reservas(self, parent):
        from tkinter import ttk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame, text="Reservas programadas", font=("Arial", 18, "bold")
        ).pack(pady=10)

        placeholder = "%s" if not self.db_manager.offline else "?"
        query = (
            "SELECT ra.id_reserva, v.placa, c.nombre, a.fecha_hora_salida, a.fecha_hora_entrada "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            f"WHERE a.id_sucursal = {placeholder} "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        reservas = (
            self.db_manager.execute_query(query, (self.user_data.get("id_sucursal"),))
            or []
        )

        cols = ("c1", "c2", "c3", "c4", "c5")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)

        headers = [
            ("c1", "ID"),
            ("c2", "Vehículo"),
            ("c3", "Cliente"),
            ("c4", "Salida"),
            ("c5", "Entrada"),
        ]

        def sort_by(treeview, col, descending):
            data = [
                (treeview.set(child, col), child) for child in treeview.get_children("")
            ]
            try:
                data.sort(key=lambda t: float(t[0]), reverse=descending)
            except ValueError:
                data.sort(reverse=descending)
            for index, (val, k) in enumerate(data):
                treeview.move(k, "", index)
            treeview.heading(
                col, command=lambda: sort_by(treeview, col, not descending)
            )

        for cid, text in headers:
            tree.heading(cid, text=text, command=lambda c=cid: sort_by(tree, c, False))
            tree.column(cid, anchor="center", width=120)
        tree.pack(fill="both", expand=True, pady=10)

        for r in reservas:
            rid, veh, cli, sal, ent = r
            tree.insert("", "end", values=(rid, veh, cli, str(sal), str(ent)))

    def _build_tab_editar_vehiculo(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Editar vehículo", font=("Arial", 18, "bold")).pack(
            pady=10
        )

        form = ctk.CTkFrame(frame)
        form.pack(pady=5)

        ctk.CTkLabel(form, text="Placa:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        placas = (
            self.db_manager.execute_query(
                "SELECT placa FROM Vehiculo WHERE id_sucursal = ?",
                (self.user_data.get("id_sucursal"),),
            )
            or []
        )
        self.edit_placa_var = tk.StringVar(value=placas[0][0] if placas else "")

        ctk.CTkLabel(form, text="Color:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        colores = (
            self.db_manager.execute_query(
                "SELECT id_color, nombre_color FROM Color_vehiculo"
            )
            or []
        )
        self.edit_color_map = {c[1]: c[0] for c in colores}
        self.edit_color_var = tk.StringVar(
            value=list(self.edit_color_map.keys())[0] if colores else ""
        )
        tk.OptionMenu(form, self.edit_color_var, *self.edit_color_map.keys()).grid(
            row=1, column=1, padx=5, pady=5
        )

        ctk.CTkLabel(form, text="Kilometraje:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.edit_km = ctk.CTkEntry(form, width=150)
        self.edit_km.grid(row=2, column=1, padx=5, pady=5)

        def cargar():
            placa = self.edit_placa_var.get()
            if not placa:
                return
            placeholder = "%s" if not self.db_manager.offline else "?"
            row = self.db_manager.execute_query(
                f"SELECT id_color, kilometraje FROM Vehiculo WHERE placa={placeholder}",
                (placa,),
            )
            if row:
                id_color, km = row[0]
                nombre = next(
                    (k for k, v in self.edit_color_map.items() if v == id_color), ""
                )
                self.edit_color_var.set(nombre)
                self.edit_km.delete(0, "end")
                self.edit_km.insert(0, str(km or ""))

        tk.OptionMenu(
            form,
            self.edit_placa_var,
            *[p[0] for p in placas],
            command=lambda *_: cargar(),
        ).grid(row=0, column=1, padx=5, pady=5)

        def guardar():
            placa = self.edit_placa_var.get().strip()
            if not placa:
                messagebox.showwarning("Aviso", "Seleccione una placa")
                return
            color = (
                self.edit_color_map.get(self.edit_color_var.get())
                if self.edit_color_var.get()
                else None
            )
            km = self.edit_km.get().strip()
            try:
                km_val = int(km) if km else 0
            except ValueError:
                messagebox.showwarning("Aviso", "Kilometraje inválido")
                return
            placeholder = "%s" if not self.db_manager.offline else "?"
            query = f"UPDATE Vehiculo SET id_color={placeholder}, kilometraje={placeholder} WHERE placa={placeholder}"
            try:
                self.db_manager.execute_query(
                    query, (color, km_val, placa), fetch=False
                )
                messagebox.showinfo("Éxito", "Vehículo actualizado")
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(
            btn_frame,
            text="Guardar cambios",
            command=guardar,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).pack()

        cargar()


