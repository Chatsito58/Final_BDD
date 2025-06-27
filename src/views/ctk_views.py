import customtkinter as ctk
import threading
import time
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre
)

class BaseCTKView(ctk.CTk):
    def __init__(self, user_data, db_manager, on_logout=None):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._status_label = None
        self._stop_status = False
        self.geometry("600x400")
        self.configure(bg="#18191A")
        self._build_ui()
        self._update_status_label()
        self._start_status_updater()
        self.after(100, self._maximize_and_focus)

    def _maximize_and_focus(self):
        self.after(100, lambda: self.wm_state('zoomed'))
        self.focus_force()

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña: Mis reservas
        self.tab_reservas = self.tabview.add("Mis reservas")
        self._build_tab_mis_reservas(self.tabview.tab("Mis reservas"))
        # Pestaña: Crear reserva
        self.tab_crear = self.tabview.add("Crear reserva")
        self._build_tab_crear_reserva(self.tabview.tab("Crear reserva"))
        # Pestaña: Vehículos disponibles
        self.tab_vehiculos = self.tabview.add("Vehículos disponibles")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos disponibles"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))
        # Pestaña: Editar perfil (si aplica)
        if hasattr(self, '_build_tab_perfil'):
            self.tab_perfil = self.tabview.add("Editar perfil")
            self._build_tab_perfil(self.tabview.tab("Editar perfil"))
        self._update_status_label()

    def _build_cambiar_contrasena_tab(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        ctk.CTkLabel(parent, text="Contraseña actual:").pack(pady=(20, 5))
        self.input_actual = ctk.CTkEntry(parent, show="*")
        self.input_actual.pack(pady=5)
        ctk.CTkLabel(parent, text="Nueva contraseña:").pack(pady=5)
        self.input_nueva = ctk.CTkEntry(parent, show="*")
        self.input_nueva.pack(pady=5)
        ctk.CTkLabel(parent, text="Confirmar nueva contraseña:").pack(pady=5)
        self.input_confirmar = ctk.CTkEntry(parent, show="*")
        self.input_confirmar.pack(pady=5)
        ctk.CTkButton(parent, text="Cambiar", command=self._cambiar_contrasena, fg_color="#3A86FF", hover_color="#265DAB").pack(pady=20)

    def _cambiar_contrasena(self):
        from tkinter import messagebox
        actual = self.input_actual.get()
        nueva = self.input_nueva.get()
        confirmar = self.input_confirmar.get()
        if not actual or not nueva or not confirmar:
            messagebox.showwarning("Error", "Complete todos los campos")
            return
        if nueva != confirmar:
            messagebox.showwarning("Error", "La nueva contraseña y la confirmación no coinciden")
            return
        from src.auth import AuthManager
        auth = AuthManager(self.db_manager)
        usuario = self.user_data.get('usuario')
        resultado = auth.cambiar_contrasena(usuario, actual, nueva)
        if resultado is True:
            messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
            self.input_actual.delete(0, 'end')
            self.input_nueva.delete(0, 'end')
            self.input_confirmar.delete(0, 'end')
        else:
            messagebox.showwarning("Error", str(resultado))

    def _welcome_message(self):
        return f"Bienvenido, {self.user_data.get('usuario', '')}"

    def _update_status_label(self, estado="Conectado", emoji="🟢"):
        if self._status_label is not None:
            online = not self.db_manager.offline
            emoji = "🟢" if online else "🔴"
            estado = "ONLINE" if online else "OFFLINE"
            self._status_label.configure(text=f"{emoji} Estado: {estado}")

    def _start_status_updater(self):
        def updater():
            while not self._stop_status:
                self._update_status_label()
                time.sleep(2)
        t = threading.Thread(target=updater, daemon=True)
        t.start()

    def destroy(self):
        self._stop_status = True
        super().destroy()

    def logout(self):
        self.destroy()
        if self.on_logout:
            self.on_logout()

class ClienteView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido cliente, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña: Mis reservas
        self.tab_reservas = self.tabview.add("Mis reservas")
        self._build_tab_mis_reservas(self.tabview.tab("Mis reservas"))
        # Pestaña: Crear reserva
        self.tab_crear = self.tabview.add("Crear reserva")
        self._build_tab_crear_reserva(self.tabview.tab("Crear reserva"))
        # Pestaña: Vehículos disponibles
        self.tab_vehiculos = self.tabview.add("Vehículos disponibles")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos disponibles"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))
        # Pestaña: Editar perfil (si aplica)
        if hasattr(self, '_build_tab_perfil'):
            self.tab_perfil = self.tabview.add("Editar perfil")
            self._build_tab_perfil(self.tabview.tab("Editar perfil"))
        self._update_status_label()

    def _build_tab_mis_reservas(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        id_cliente = self.user_data.get('id_cliente')
        # Frame principal centrado
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        inner = ctk.CTkFrame(frame)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(inner, text="Mis reservas", font=("Arial", 18)).pack(pady=10)
        self.reservas_listbox = tk.Listbox(inner, height=14, width=100)
        self.reservas_listbox.pack(pady=10)
        ctk.CTkButton(inner, text="Recargar", command=lambda: self._cargar_reservas_cliente(id_cliente), fg_color="#3A86FF", hover_color="#265DAB").pack(pady=4)
        # Botones de acción
        btn_frame = ctk.CTkFrame(inner)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Cancelar reserva", command=self._cancelar_reserva).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Editar fechas", command=self._editar_reserva).pack(side="left", padx=10)
        self._cargar_reservas_cliente(id_cliente)

    def _cargar_reservas_cliente(self, id_cliente):
        # Consulta todas las reservas del cliente, sin importar el estado
        query = '''
            SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, a.valor, ra.saldo_pendiente, ra.abono, es.descripcion, s.descripcion, s.costo, d.descripcion, d.valor
            FROM Reserva_alquiler ra
            JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler
            JOIN Vehiculo v ON a.id_vehiculo = v.placa
            LEFT JOIN Estado_reserva es ON ra.id_estado_reserva = es.id_estado
            LEFT JOIN Seguro_alquiler s ON a.id_seguro = s.id_seguro
            LEFT JOIN Descuento_alquiler d ON a.id_descuento = d.id_descuento
            WHERE a.id_cliente = %s
            ORDER BY a.fecha_hora_salida DESC
        '''
        params = (id_cliente,)
        print(f"Ejecutando consulta de reservas para cliente {id_cliente}")
        reservas = self.db_manager.execute_query(query, params)
        print(f"Reservas encontradas: {len(reservas) if reservas else 0}")
        self.reservas_listbox.delete(0, "end")
        if not reservas:
            self.reservas_listbox.insert("end", "No tienes reservas registradas")
            return
        for r in reservas:
            id_reserva, salida, entrada, id_vehiculo, modelo, placa, valor, saldo, abono, estado, seguro, costo_seguro, desc, val_desc = r
            print(f"Procesando reserva ID: {id_reserva}")
            # Estado visual
            if estado and ("pendiente" in estado.lower() or "aprob" in estado.lower()):
                estado_str = "⏳ PENDIENTE DE APROBACIÓN"
            elif estado and "confirm" in estado.lower():
                estado_str = "✅ CONFIRMADA"
            elif estado and "cancel" in estado.lower():
                estado_str = "❌ CANCELADA"
            else:
                estado_str = f"{estado or 'Desconocido'}"
            texto = f"ID: {id_reserva} | {modelo} ({placa}) | Salida: {salida:%Y-%m-%d %H:%M} | Entrada: {entrada:%Y-%m-%d %H:%M} | Estado: {estado_str} | Total: ${valor:,.0f} | Abono: ${abono:,.0f} | Saldo: ${saldo:,.0f} | Seguro: {seguro or '-'} | Descuento: {desc or '-'}"
            self.reservas_listbox.insert("end", texto)

    def _cancelar_reserva(self):
        from tkinter import messagebox
        sel = self.reservas_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una reserva para cancelar")
            return
        texto = self.reservas_listbox.get(sel[0])
        if "ID: " not in texto:
            messagebox.showwarning("Aviso", "No hay reserva seleccionada")
            return
        id_reserva = texto.split("ID: ")[1].split("|")[0].strip()
        # Verificar estado antes de cancelar
        placeholder = '%s' if not self.db_manager.offline else '?'
        estado_query = f"SELECT id_estado_reserva FROM Reserva_alquiler WHERE id_reserva = {placeholder}"
        estado = self.db_manager.execute_query(estado_query, (id_reserva,))
        if estado and estado[0][0] != 1:  # Solo permite cancelar si está 'Pendiente'
            messagebox.showwarning("Aviso", "Solo puedes cancelar reservas en estado 'Pendiente'.")
            return
        query = f"UPDATE Reserva_alquiler SET id_estado_reserva = 3 WHERE id_reserva = {placeholder}"
        try:
            self.db_manager.execute_query(query, (id_reserva,), fetch=False)
            messagebox.showinfo("Éxito", "Reserva cancelada")
            self._cargar_reservas_cliente(self.user_data.get('id_cliente'))
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo cancelar la reserva: {exc}")

    def _editar_reserva(self):
        import tkinter as tk
        from tkinter import messagebox
        sel = self.reservas_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una reserva para editar")
            return
        texto = self.reservas_listbox.get(sel[0])
        if "ID: " not in texto:
            messagebox.showwarning("Aviso", "No hay reserva seleccionada")
            return
        id_reserva = texto.split("ID: ")[1].split("|")[0].strip()
        # Obtener fechas actuales
        placeholder = '%s' if not self.db_manager.offline else '?'
        fechas_query = (
            f"SELECT a.fecha_hora_salida, a.fecha_hora_entrada FROM Reserva_alquiler ra "
            f"JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler WHERE ra.id_reserva = {placeholder}"
        )
        fechas = self.db_manager.execute_query(fechas_query, (id_reserva,))
        if not fechas:
            messagebox.showerror("Error", "No se pudo obtener la información de la reserva.")
            return
        salida_actual, entrada_actual = fechas[0]
        win = tk.Toplevel(self)
        win.title("Editar fechas de reserva")
        win.geometry("350x200")
        ctk.CTkLabel(win, text="Nueva fecha y hora salida (YYYY-MM-DD HH:MM):").pack(pady=5)
        entry_salida = ctk.CTkEntry(win)
        entry_salida.insert(0, str(salida_actual))
        entry_salida.pack(pady=5)
        ctk.CTkLabel(win, text="Nueva fecha y hora entrada (YYYY-MM-DD HH:MM):").pack(pady=5)
        entry_entrada = ctk.CTkEntry(win)
        entry_entrada.insert(0, str(entrada_actual))
        entry_entrada.pack(pady=5)
        def guardar():
            nueva_salida = entry_salida.get().strip()
            nueva_entrada = entry_entrada.get().strip()
            if not nueva_salida or not nueva_entrada:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            # Actualizar fechas en Alquiler
            update_query = (
                f"UPDATE Alquiler SET fecha_hora_salida = {placeholder}, fecha_hora_entrada = {placeholder} "
                f"WHERE id_alquiler = (SELECT id_alquiler FROM Reserva_alquiler WHERE id_reserva = {placeholder})"
            )
            try:
                self.db_manager.execute_query(update_query, (nueva_salida, nueva_entrada, id_reserva), fetch=False)
                messagebox.showinfo("Éxito", "Fechas actualizadas correctamente")
                win.destroy()
                self._cargar_reservas_cliente(self.user_data.get('id_cliente'))
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo actualizar la reserva: {exc}")
        ctk.CTkButton(win, text="Guardar cambios", command=guardar).pack(pady=15)

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 16)).pack(pady=10)
        # Listar vehículos disponibles con info completa
        query = ("SELECT v.placa, v.modelo, m.nombre_marca, t.descripcion, t.tarifa_dia "
                 "FROM Vehiculo v "
                 "JOIN Marca_vehiculo m ON v.id_marca = m.id_marca "
                 "JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo "
                 "WHERE v.id_estado_vehiculo = 1")
        vehiculos = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=80)
        listbox.pack(pady=10)
        self._vehiculos_cache = []
        if vehiculos:
            for v in vehiculos:
                self._vehiculos_cache.append(v)
                listbox.insert('end', f"Placa: {v[0]} | Modelo: {v[1]} | Marca: {v[2]} | Tipo: {v[3]} | Tarifa/día: {v[4]}")
        else:
            listbox.insert('end', "No hay vehículos disponibles.")
        # Botón para reservar vehículo seleccionado
        def reservar():
            sel = listbox.curselection()
            if not sel:
                tk.messagebox.showwarning("Aviso", "Seleccione un vehículo para reservar")
                return
            idx = sel[0]
            vehiculo = self._vehiculos_cache[idx]
            self._abrir_nueva_reserva_vehiculo(vehiculo)
        ctk.CTkButton(frame, text="Reservar seleccionado", command=reservar).pack(pady=5)

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
        ctk.CTkLabel(win, text=f"Placa: {placa} | {modelo} {marca} ({tipo})", font=("Arial", 15, "bold")).pack(pady=8)
        ctk.CTkLabel(win, text=f"Tarifa por día: ${tarifa_dia}", font=("Arial", 13)).pack(pady=4)
        # Frame de fecha y hora salida (solo uno, tipo tk.Frame)
        salida_frame = tk.Frame(win, bg="#222831")
        salida_frame.pack(fill="x", pady=8)
        tk.Label(salida_frame, text="Fecha y hora salida:", font=("Arial", 12), bg="#222831", fg="#F5F6FA").pack(anchor="w")
        salida_date = DateEntry(salida_frame, date_pattern='yyyy-mm-dd', width=12)
        salida_date.pack(side="left", padx=2)
        # Combobox para hora (1-12), minutos y AM/PM usando solo tkinter
        horas_12 = [f"{h:02d}" for h in range(1, 13)]
        minutos = ["00", "15", "30", "45"]
        ampm = ["AM", "PM"]
        salida_hora_cb = tk.ttk.Combobox(salida_frame, values=horas_12, width=3, state="readonly")
        salida_hora_cb.set("08")
        salida_hora_cb.pack(side="left", padx=2)
        tk.Label(salida_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        salida_min_cb = tk.ttk.Combobox(salida_frame, values=minutos, width=3, state="readonly")
        salida_min_cb.set("00")
        salida_min_cb.pack(side="left", padx=2)
        salida_ampm_cb = tk.ttk.Combobox(salida_frame, values=ampm, width=3, state="readonly")
        salida_ampm_cb.set("AM")
        salida_ampm_cb.pack(side="left", padx=2)
        # Frame de fecha y hora entrada (solo uno, tipo tk.Frame)
        entrada_frame = tk.Frame(win, bg="#222831")
        entrada_frame.pack(fill="x", pady=8)
        tk.Label(entrada_frame, text="Fecha y hora entrada:", font=("Arial", 12), bg="#222831", fg="#F5F6FA").pack(anchor="w")
        entrada_date = DateEntry(entrada_frame, date_pattern='yyyy-mm-dd', width=12)
        entrada_date.pack(side="left", padx=2)
        entrada_hora_cb = tk.ttk.Combobox(entrada_frame, values=horas_12, width=3, state="readonly")
        entrada_hora_cb.set("09")
        entrada_hora_cb.pack(side="left", padx=2)
        tk.Label(entrada_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        entrada_min_cb = tk.ttk.Combobox(entrada_frame, values=minutos, width=3, state="readonly")
        entrada_min_cb.set("00")
        entrada_min_cb.pack(side="left", padx=2)
        entrada_ampm_cb = tk.ttk.Combobox(entrada_frame, values=ampm, width=3, state="readonly")
        entrada_ampm_cb.set("AM")
        entrada_ampm_cb.pack(side="left", padx=2)
        # Seguros disponibles
        ctk.CTkLabel(win, text="Seguro:", font=("Arial", 12)).pack(pady=4)
        seguros = self.db_manager.execute_query("SELECT id_seguro, descripcion, costo FROM Seguro_alquiler")
        seguro_var = tk.StringVar()
        if seguros:
            seguro_menu = tk.OptionMenu(win, seguro_var, *[f"{s[1]} (${s[2]})" for s in seguros])
            seguro_menu.pack(fill="x", pady=4)
            seguro_var.set(f"{seguros[0][1]} (${seguros[0][2]})")
        else:
            ctk.CTkLabel(win, text="No hay seguros disponibles", text_color="#FF5555").pack(pady=4)
        # Descuentos disponibles
        ctk.CTkLabel(win, text="Descuento:", font=("Arial", 12)).pack(pady=4)
        descuentos = self.db_manager.execute_query("SELECT id_descuento, descripcion, valor FROM Descuento_alquiler")
        descuento_var = tk.StringVar()
        if descuentos:
            descuento_menu = tk.OptionMenu(win, descuento_var, *[f"{d[1]} (-${d[2]})" for d in descuentos])
            descuento_menu.pack(fill="x", pady=4)
            descuento_var.set(f"{descuentos[0][1]} (-${descuentos[0][2]})")
        else:
            ctk.CTkLabel(win, text="No hay descuentos disponibles", text_color="#FF5555").pack(pady=4)
        # Etiquetas para mostrar el total y el abono mínimo
        total_label = ctk.CTkLabel(win, text="Total a pagar: $0", font=("Arial", 14, "bold"), text_color="#00FF99")
        total_label.pack(pady=8)
        abono_min_label = ctk.CTkLabel(win, text="Abono mínimo (30%): $0", font=("Arial", 13), text_color="#FFD700")
        abono_min_label.pack(pady=4)
        # Abono y método de pago
        ctk.CTkLabel(win, text="Abono inicial ($, mínimo 30%):", font=("Arial", 12)).pack(pady=4)
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
                salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
                entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                idx_seg = [i for i, s in enumerate(seguros) if f"{s[1]} (${s[2]})" == seguro_var.get()]
                costo_seguro = float(seguros[idx_seg[0]][2]) if idx_seg else 0
                idx_desc = [i for i, d in enumerate(descuentos) if f"{d[1]} (-${d[2]})" == descuento_var.get()]
                valor_descuento = float(descuentos[idx_desc[0]][2]) if idx_desc else 0
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
        for widget in [salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb, entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb]:
            widget.bind("<<ComboboxSelected>>", actualizar_total)
            widget.bind("<FocusOut>", actualizar_total)
        if seguros:
            seguro_var.trace_add('write', lambda *a: actualizar_total())
        if descuentos:
            descuento_var.trace_add('write', lambda *a: actualizar_total())
        # Inicializar valores
        actualizar_total()
        # Guardar reserva
        def guardar():
            salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
            entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
            abono = entry_abono.get().strip()
            metodo_pago = metodo_pago_var.get()
            if not salida or not entrada or not (seguros and seguro_var.get()) or not (descuentos and descuento_var.get()) or not abono or not metodo_pago:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            fmt = "%Y-%m-%d %H:%M"
            try:
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                if dt_salida < datetime.now():
                    messagebox.showwarning("Error", "La fecha de salida no puede ser en el pasado")
                    return
                if dt_entrada <= dt_salida:
                    messagebox.showwarning("Error", "La fecha de entrada debe ser posterior a la de salida")
                    return
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                idx_seg = [i for i, s in enumerate(seguros) if f"{s[1]} (${s[2]})" == seguro_var.get()]
                id_seguro = seguros[idx_seg[0]][0] if idx_seg else None
                costo_seguro = float(seguros[idx_seg[0]][2]) if idx_seg else 0
                idx_desc = [i for i, d in enumerate(descuentos) if f"{d[1]} (-${d[2]})" == descuento_var.get()]
                id_descuento = descuentos[idx_desc[0]][0] if idx_desc else None
                valor_descuento = float(descuentos[idx_desc[0]][2]) if idx_desc else 0
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                # Validar abono mínimo
                try:
                    abono_val = float(abono)
                except ValueError:
                    messagebox.showwarning("Error", "El monto de abono debe ser un número válido")
                    return
                abono_min = round(total * 0.3, 2)
                if abono_val < abono_min:
                    messagebox.showwarning("Error", f"El abono mínimo es de $ {abono_min:,.2f}")
                    return
                id_cliente = self.user_data.get('id_cliente')
                placeholder = '%s' if not self.db_manager.offline else '?'
                # Insertar en Alquiler
                query_alquiler = (f"INSERT INTO Alquiler (fecha_hora_salida, valor, fecha_hora_entrada, id_vehiculo, id_cliente, id_sucursal, id_medio_pago, id_estado, id_seguro, id_descuento) "
                                  f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, 1, 1, 1, {placeholder}, {placeholder})")
                id_alquiler = self.db_manager.execute_query(query_alquiler, (salida, total, entrada, placa, id_cliente, id_seguro, id_descuento), fetch=False, return_lastrowid=True)
                if not id_alquiler:
                    raise Exception("No se pudo obtener el ID del alquiler")
                # Estado de reserva según método de pago
                if metodo_pago == "Efectivo":
                    estado_reserva = 1  # Pendiente de aprobación
                else:
                    estado_reserva = 2  # Confirmada
                # Insertar en Reserva_alquiler
                query_reserva = (f"INSERT INTO Reserva_alquiler (fecha_hora, abono, saldo_pendiente, id_estado_reserva, id_alquiler) "
                                 f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})")
                saldo_pendiente = total - abono_val
                id_reserva = self.db_manager.execute_query(query_reserva, (salida, abono_val, saldo_pendiente, estado_reserva, id_alquiler), fetch=False, return_lastrowid=True)
                if not id_reserva:
                    raise Exception("No se pudo obtener el ID de la reserva")
                # Insertar abono
                query_abono = (f"INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
                               f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})")
                id_medio_pago = 1 if metodo_pago == "Efectivo" else (2 if metodo_pago == "Tarjeta" else 3)
                self.db_manager.execute_query(query_abono, (abono_val, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_reserva, id_medio_pago), fetch=False)
                # Simulación de pasarela de pago si corresponde
                if metodo_pago in ("Tarjeta", "Transferencia"):
                    win.withdraw()
                    # Llamada sin on_finish, la recarga y cierre se hace al finalizar el pago
                    self._simular_pasarela_pago(id_reserva, abono_val, metodo_pago)
                else:
                    messagebox.showinfo("Reserva en espera", "Reserva creada. Debe acercarse a la oficina para entregar el dinero y que un empleado apruebe el alquiler.")
                win.destroy()
                # Solo recargar si el widget existe
                if hasattr(self, 'reservas_listbox'):
                    self._cargar_reservas_cliente(id_cliente)
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo crear la reserva: {exc}")
        ctk.CTkButton(win, text="Guardar reserva", command=guardar, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

    def _build_tab_perfil(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        id_cliente = self.user_data.get('id_cliente')
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Editar perfil", font=("Arial", 16)).pack(pady=10)
        # Obtener datos actuales
        placeholder = '%s' if not self.db_manager.offline else '?'
        datos = self.db_manager.execute_query(f"SELECT nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = {placeholder}", (id_cliente,))
        nombre = tk.StringVar(value=datos[0][0] if datos else "")
        telefono = tk.StringVar(value=datos[0][1] if datos else "")
        direccion = tk.StringVar(value=datos[0][2] if datos else "")
        correo = tk.StringVar(value=datos[0][3] if datos else "")
        ctk.CTkLabel(frame, text="Nombre:").pack()
        entry_nombre = ctk.CTkEntry(frame, textvariable=nombre)
        entry_nombre.pack()
        ctk.CTkLabel(frame, text="Teléfono:").pack()
        entry_telefono = ctk.CTkEntry(frame, textvariable=telefono)
        entry_telefono.pack()
        ctk.CTkLabel(frame, text="Dirección:").pack()
        entry_direccion = ctk.CTkEntry(frame, textvariable=direccion)
        entry_direccion.pack()
        ctk.CTkLabel(frame, text="Correo:").pack()
        entry_correo = ctk.CTkEntry(frame, textvariable=correo)
        entry_correo.pack()
        def guardar():
            try:
                placeholder = '%s' if not self.db_manager.offline else '?'
                self.db_manager.execute_query(
                    f"UPDATE Cliente SET nombre = {placeholder}, telefono = {placeholder}, direccion = {placeholder}, correo = {placeholder} WHERE id_cliente = {placeholder}",
                    (entry_nombre.get(), entry_telefono.get(), entry_direccion.get(), entry_correo.get(), id_cliente),
                    fetch=False
                )
                messagebox.showinfo("Éxito", "Perfil actualizado correctamente")
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo actualizar el perfil: {exc}")
        ctk.CTkButton(frame, text="Guardar cambios", command=guardar).pack(pady=10)

    def _build_tab_abonos(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        id_cliente = self.user_data.get('id_cliente')
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas pendientes de pago", font=("Arial", 18)).pack(pady=10)
        self.abonos_listbox = tk.Listbox(frame, height=18, width=180)
        self.abonos_listbox.pack(pady=10)
        self._cargar_reservas_pendientes(id_cliente)
        ctk.CTkLabel(frame, text="Monto a abonar:").pack(pady=5)
        self.input_abono = ctk.CTkEntry(frame, width=20)
        self.input_abono.pack(pady=5)
        ctk.CTkButton(frame, text="Abonar", command=self._realizar_abono, fg_color="#3A86FF", hover_color="#265DAB").pack(pady=10)

    def _cargar_reservas_pendientes(self, id_cliente):
        self.abonos_listbox.delete(0, 'end')
        placeholder = '%s' if not self.db_manager.offline else '?'
        # Nueva consulta: obtener reservas pendientes del cliente usando Reserva_alquiler y Alquiler
        query = (
            f"SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, ra.saldo_pendiente "
            f"FROM Reserva_alquiler ra "
            f"JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            f"WHERE a.id_cliente = {placeholder} AND ra.saldo_pendiente > 0 AND ra.id_estado_reserva IN (1,2) "
            f"ORDER BY a.fecha_hora_salida DESC"
        )
        reservas = self.db_manager.execute_query(query, (id_cliente,))
        if reservas:
            for r in reservas:
                id_reserva = r[0]
                salida = r[1]
                entrada = r[2]
                placa = r[5]
                modelo = r[4]
                saldo_pendiente = r[6]
                # Sumar abonos realizados
                abono_query = f"SELECT COALESCE(SUM(valor), 0) FROM Abono_reserva WHERE id_reserva = {placeholder}"
                abonos = self.db_manager.execute_query(abono_query, (id_reserva,))
                abonado = abonos[0][0] if abonos and abonos[0] else 0
                saldo_real = saldo_pendiente - abonado
                if saldo_real > 0:
                    self.abonos_listbox.insert('end', f"ID: {id_reserva} | Vehículo: {modelo} ({placa}) | Saldo pendiente: ${saldo_real} | Salida: {salida} | Entrada: {entrada}")
            if self.abonos_listbox.size() == 0:
                self.abonos_listbox.insert('end', "No tienes reservas pendientes de pago.")
        else:
            self.abonos_listbox.insert('end', "No tienes reservas pendientes de pago.")

    def _realizar_abono(self):
        from tkinter import messagebox
        import tkinter as tk
        from datetime import datetime
        sel = self.abonos_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una reserva para abonar")
            return
        texto = self.abonos_listbox.get(sel[0])
        if "ID: " not in texto:
            messagebox.showwarning("Aviso", "No hay reserva seleccionada")
            return
        id_reserva = texto.split("ID: ")[1].split("|")[0].strip()
        monto = self.input_abono.get().strip()
        if not monto or not monto.replace('.', '', 1).isdigit() or float(monto) <= 0:
            messagebox.showwarning("Error", "Ingrese un monto válido")
            return
        # Selección de método de pago
        win_pago = ctk.CTkToplevel(self)
        win_pago.title("Seleccionar método de pago")
        win_pago.geometry("400x320")
        win_pago.configure(fg_color="#222831")
        win_pago.transient(self)
        win_pago.grab_set()
        win_pago.focus_set()
        win_pago.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (320 // 2)
        win_pago.geometry(f"400x320+{x}+{y}")
        ctk.CTkLabel(win_pago, text="Método de pago", font=("Arial", 15, "bold")).pack(pady=10)
        metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]
        metodo_pago_var = tk.StringVar()
        metodo_pago_var.set(metodos_pago[0])
        metodo_pago_menu = tk.OptionMenu(win_pago, metodo_pago_var, *metodos_pago)
        metodo_pago_menu.pack(pady=10)
        def continuar():
            metodo = metodo_pago_var.get()
            win_pago.destroy()
            if metodo == "Efectivo":
                self._registrar_abono(id_reserva, monto, metodo, None)
            else:
                self._simular_pasarela_pago(id_reserva, monto, metodo)
        ctk.CTkButton(win_pago, text="Continuar", command=continuar, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

    def _registrar_abono(self, id_reserva, monto, metodo, datos_pago=None):
        from tkinter import messagebox
        from datetime import datetime
        try:
            placeholder = '%s' if not self.db_manager.offline else '?'
            id_medio_pago = 1 if metodo == "Efectivo" else (2 if metodo == "Tarjeta" else 3)
            query = f"INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
            self.db_manager.execute_query(query, (float(monto), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_reserva, id_medio_pago), fetch=False)
            if metodo == "Efectivo":
                messagebox.showinfo("Abono en espera", "Abono registrado. Debe acercarse a la oficina para validar el pago.")
            else:
                messagebox.showinfo("Éxito", "Abono realizado y validado correctamente.")
            # Solo limpiar input_abono si existe (pestaña de abonos)
            if hasattr(self, 'input_abono'):
                self.input_abono.delete(0, 'end')
            # Actualizar abonos inmediatamente si existe la pestaña
            if hasattr(self, 'abonos_listbox'):
                self._cargar_reservas_pendientes(self.user_data.get('id_cliente'))
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo realizar el abono: {exc}")

    def _simular_pasarela_pago(self, id_reserva, monto, metodo):
        import tkinter as tk
        import threading
        import itertools
        win = ctk.CTkToplevel(self)
        win.title("Pasarela de pago")
        win.geometry("420x400")
        win.configure(fg_color="#23272F")
        win.grab_set()
        win.focus_set()
        win.update_idletasks()
        # Centrar ventana
        x = self.winfo_x() + (self.winfo_width() // 2) - (420 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (400 // 2)
        win.geometry(f"420x400+{x}+{y}")
        # Íconos realistas
        icono = "💳" if metodo == "Tarjeta" else ("🏦" if metodo == "Transferencia" else "💵")
        ctk.CTkLabel(win, text=icono, font=("Arial", 40)).pack(pady=2)
        ctk.CTkLabel(win, text=f"Simulación de pago - {metodo}", font=("Arial", 15, "bold")).pack(pady=6)
        if metodo == "Tarjeta":
            ctk.CTkLabel(win, text="Número de tarjeta:", font=("Arial", 12)).pack(pady=4)
            entry_tarjeta = ctk.CTkEntry(win)
            entry_tarjeta.insert(0, "4111 1111 1111 1111")
            entry_tarjeta.pack(pady=4)
            ctk.CTkLabel(win, text="CVV:", font=("Arial", 12)).pack(pady=4)
            entry_cvv = ctk.CTkEntry(win)
            entry_cvv.insert(0, "123")
            entry_cvv.pack(pady=4)
            ctk.CTkLabel(win, text="Fecha vencimiento (MM/AA):", font=("Arial", 12)).pack(pady=4)
            entry_fecha = ctk.CTkEntry(win)
            entry_fecha.insert(0, "12/29")
            entry_fecha.pack(pady=4)
        elif metodo == "Transferencia":
            ctk.CTkLabel(win, text="Cuenta destino:", font=("Arial", 12)).pack(pady=4)
            entry_cuenta = ctk.CTkEntry(win)
            entry_cuenta.insert(0, "1234567890")
            entry_cuenta.pack(pady=4)
            ctk.CTkLabel(win, text="Banco: Banco Simulado", font=("Arial", 12)).pack(pady=4)
        ctk.CTkLabel(win, text=f"Monto a pagar: ${monto}", font=("Arial", 13, "bold"), text_color="#FFD700").pack(pady=10)
        status_label = ctk.CTkLabel(win, text="Procesando pago...", font=("Arial", 12), text_color="#3A86FF")
        status_label.pack(pady=10)
        def procesar():
            import time
            status_label.configure(text="Procesando pago...", text_color="#3A86FF")
            win.update()
            time.sleep(2)
            status_label.configure(text="Pago autorizado ✔", text_color="#00FF99")
            win.update()
            time.sleep(1)
            win.grab_release()
            win.destroy()
            # Solo mostrar mensaje de éxito, no registrar abono adicional
            from tkinter import messagebox
            messagebox.showinfo("Éxito", "Reserva creada y pago procesado correctamente.")
            # Recargar lista de reservas
            if hasattr(self, 'reservas_listbox'):
                self._cargar_reservas_cliente(self.user_data.get('id_cliente'))
        threading.Thread(target=procesar, daemon=True).start()

    def _build_tab_crear_reserva(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        from datetime import datetime
        from tkcalendar import DateEntry
        # Frame principal
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Crear nueva reserva", font=("Arial", 18, "bold")).pack(pady=10)
        # Selección de vehículo
        ctk.CTkLabel(frame, text="Vehículo:", font=("Arial", 12)).pack(anchor="w", pady=(10,0))
        vehiculos = self.db_manager.execute_query("SELECT v.placa, v.modelo, m.nombre_marca FROM Vehiculo v JOIN Marca_vehiculo m ON v.id_marca = m.id_marca WHERE v.id_estado_vehiculo = 1")
        vehiculo_var = tk.StringVar()
        if vehiculos:
            vehiculo_menu = tk.OptionMenu(frame, vehiculo_var, *[f"{v[0]} - {v[1]} {v[2]}" for v in vehiculos])
            vehiculo_menu.pack(fill="x", pady=4)
            vehiculo_var.set(f"{vehiculos[0][0]} - {vehiculos[0][1]} {vehiculos[0][2]}")
        else:
            ctk.CTkLabel(frame, text="No hay vehículos disponibles", text_color="#FF5555").pack(pady=4)
        # Fecha y hora salida
        ctk.CTkLabel(frame, text="Fecha y hora salida:", font=("Arial", 12)).pack(anchor="w", pady=(10,0))
        salida_frame = tk.Frame(frame, bg="#222831")
        salida_frame.pack(fill="x", pady=4)
        salida_date = DateEntry(salida_frame, date_pattern='yyyy-mm-dd', width=12)
        salida_date.pack(side="left", padx=2)
        horas_12 = [f"{h:02d}" for h in range(1, 13)]
        minutos = ["00", "15", "30", "45"]
        ampm = ["AM", "PM"]
        salida_hora_cb = tk.ttk.Combobox(salida_frame, values=horas_12, width=3, state="readonly")
        salida_hora_cb.set("08")
        salida_hora_cb.pack(side="left", padx=2)
        tk.Label(salida_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        salida_min_cb = tk.ttk.Combobox(salida_frame, values=minutos, width=3, state="readonly")
        salida_min_cb.set("00")
        salida_min_cb.pack(side="left", padx=2)
        salida_ampm_cb = tk.ttk.Combobox(salida_frame, values=ampm, width=3, state="readonly")
        salida_ampm_cb.set("AM")
        salida_ampm_cb.pack(side="left", padx=2)
        # Fecha y hora entrada
        ctk.CTkLabel(frame, text="Fecha y hora entrada:", font=("Arial", 12)).pack(anchor="w", pady=(10,0))
        entrada_frame = tk.Frame(frame, bg="#222831")
        entrada_frame.pack(fill="x", pady=4)
        entrada_date = DateEntry(entrada_frame, date_pattern='yyyy-mm-dd', width=12)
        entrada_date.pack(side="left", padx=2)
        entrada_hora_cb = tk.ttk.Combobox(entrada_frame, values=horas_12, width=3, state="readonly")
        entrada_hora_cb.set("09")
        entrada_hora_cb.pack(side="left", padx=2)
        tk.Label(entrada_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        entrada_min_cb = tk.ttk.Combobox(entrada_frame, values=minutos, width=3, state="readonly")
        entrada_min_cb.set("00")
        entrada_min_cb.pack(side="left", padx=2)
        entrada_ampm_cb = tk.ttk.Combobox(entrada_frame, values=ampm, width=3, state="readonly")
        entrada_ampm_cb.set("AM")
        entrada_ampm_cb.pack(side="left", padx=2)
        # Seguro
        ctk.CTkLabel(frame, text="Seguro:", font=("Arial", 12)).pack(anchor="w", pady=(10,0))
        seguros = self.db_manager.execute_query("SELECT id_seguro, descripcion, costo FROM Seguro_alquiler")
        seguro_var = tk.StringVar()
        if seguros:
            seguro_menu = tk.OptionMenu(frame, seguro_var, *[f"{s[1]} (${s[2]})" for s in seguros])
            seguro_menu.pack(fill="x", pady=4)
            seguro_var.set(f"{seguros[0][1]} (${seguros[0][2]})")
        else:
            ctk.CTkLabel(frame, text="No hay seguros disponibles", text_color="#FF5555").pack(pady=4)
        # Descuento
        ctk.CTkLabel(frame, text="Descuento:", font=("Arial", 12)).pack(anchor="w", pady=(10,0))
        descuentos = self.db_manager.execute_query("SELECT id_descuento, descripcion, valor FROM Descuento_alquiler")
        descuento_var = tk.StringVar()
        if descuentos:
            descuento_menu = tk.OptionMenu(frame, descuento_var, *[f"{d[1]} (-${d[2]})" for d in descuentos])
            descuento_menu.pack(fill="x", pady=4)
            descuento_var.set(f"{descuentos[0][1]} (-${descuentos[0][2]})")
        else:
            ctk.CTkLabel(frame, text="No hay descuentos disponibles", text_color="#FF5555").pack(pady=4)
        # Método de pago
        ctk.CTkLabel(frame, text="Método de pago:", font=("Arial", 12)).pack(anchor="w", pady=(10,0))
        metodos = ["Efectivo", "Tarjeta", "Transferencia"]
        metodo_var = tk.StringVar()
        metodo_menu = tk.OptionMenu(frame, metodo_var, *metodos)
        metodo_menu.pack(fill="x", pady=4)
        metodo_var.set(metodos[0])
        # Total y abono mínimo
        total_label = ctk.CTkLabel(frame, text="Total: $0", font=("Arial", 13, "bold"))
        total_label.pack(pady=8)
        abono_label = ctk.CTkLabel(frame, text="Abono mínimo (30%): $0", font=("Arial", 12))
        abono_label.pack(pady=4)
        # Campo de abono inicial
        ctk.CTkLabel(frame, text="Abono inicial ($):", font=("Arial", 12)).pack(anchor="w", pady=(10,0))
        entry_abono = ctk.CTkEntry(frame, width=120)  # Ampliado para mejor visibilidad
        entry_abono.pack(pady=4)
        # Función para calcular total y abono mínimo
        def calcular_total(*_):
            try:
                if not vehiculos or not vehiculo_var.get():
                    total_label.configure(text="Total: $0")
                    abono_label.configure(text="Abono mínimo (30%): $0")
                    return
                
                placa = vehiculo_var.get().split(" - ")[0]
                # Consulta corregida para obtener tarifa desde Tipo_vehiculo
                vehiculo_query = """
                    SELECT t.tarifa_dia 
                    FROM Vehiculo v 
                    JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo 
                    WHERE v.placa = %s
                """
                vehiculo_result = self.db_manager.execute_query(vehiculo_query, (placa,))
                if not vehiculo_result:
                    total_label.configure(text="Total: $0")
                    abono_label.configure(text="Abono mínimo (30%): $0")
                    return
                
                tarifa = float(vehiculo_result[0][0]) if vehiculo_result[0][0] else 0
                fecha_salida = salida_date.get_date()
                fecha_entrada = entrada_date.get_date()
                dias = (fecha_entrada - fecha_salida).days
                if dias < 1:
                    dias = 1
                
                # Calcular costo del seguro
                seguro_costo = 0
                if seguros and seguro_var.get():
                    try:
                        seguro_seleccionado = seguro_var.get()
                        for s in seguros:
                            if f"{s[1]} (${s[2]})" == seguro_seleccionado:
                                seguro_costo = float(s[2])
                                break
                    except:
                        seguro_costo = 0
                
                # Calcular descuento
                descuento_val = 0
                if descuentos and descuento_var.get():
                    try:
                        descuento_seleccionado = descuento_var.get()
                        for d in descuentos:
                            if f"{d[1]} (-${d[2]})" == descuento_seleccionado:
                                descuento_val = float(d[2])
                                break
                    except:
                        descuento_val = 0
                
                total = dias * tarifa + seguro_costo - descuento_val
                if total < 0:
                    total = 0
                
                total_label.configure(text=f"Total: ${total:,.0f}")
                abono_min = int(total * 0.3)
                abono_label.configure(text=f"Abono mínimo (30%): ${abono_min:,.0f}")
                
            except Exception as e:
                print(f"Error en calcular_total: {e}")
                total_label.configure(text="Total: $0")
                abono_label.configure(text="Abono mínimo (30%): $0")
        
        # Vincular cambios para recalcular automáticamente
        if vehiculos:
            vehiculo_var.trace_add('write', calcular_total)
        if seguros:
            seguro_var.trace_add('write', calcular_total)
        if descuentos:
            descuento_var.trace_add('write', calcular_total)
        salida_date.bind('<<DateEntrySelected>>', calcular_total)
        entrada_date.bind('<<DateEntrySelected>>', calcular_total)
        
        # Calcular total inicial
        calcular_total()
        # Botón para crear reserva
        def crear_reserva():
            try:
                print("Iniciando creación de reserva...")
                # Validaciones básicas
                if not vehiculos or not vehiculo_var.get():
                    messagebox.showwarning("Error", "Seleccione un vehículo")
                    return
                
                if not entry_abono.get().strip():
                    messagebox.showwarning("Error", "Ingrese el abono inicial")
                    return
                
                # Obtener datos del vehículo
                placa = vehiculo_var.get().split(" - ")[0]
                print(f"Vehículo seleccionado: {placa}")
                
                # Obtener fechas y horas
                fecha_salida = salida_date.get_date().strftime("%Y-%m-%d")
                hora_salida = salida_hora_cb.get()
                min_salida = salida_min_cb.get()
                ampm_salida = salida_ampm_cb.get()
                if ampm_salida == "PM" and hora_salida != "12":
                    hora_salida_24 = str(int(hora_salida) + 12)
                elif ampm_salida == "AM" and hora_salida == "12":
                    hora_salida_24 = "00"
                else:
                    hora_salida_24 = hora_salida
                fecha_hora_salida = f"{fecha_salida} {hora_salida_24}:{min_salida}:00"
                
                fecha_entrada = entrada_date.get_date().strftime("%Y-%m-%d")
                hora_entrada = entrada_hora_cb.get()
                min_entrada = entrada_min_cb.get()
                ampm_entrada = entrada_ampm_cb.get()
                if ampm_entrada == "PM" and hora_entrada != "12":
                    hora_entrada_24 = str(int(hora_entrada) + 12)
                elif ampm_entrada == "AM" and hora_entrada == "12":
                    hora_entrada_24 = "00"
                else:
                    hora_entrada_24 = hora_entrada
                fecha_hora_entrada = f"{fecha_entrada} {hora_entrada_24}:{min_entrada}:00"
                
                print(f"Fechas: Salida {fecha_hora_salida}, Entrada {fecha_hora_entrada}")
                
                # Obtener seguro y descuento
                id_seguro = None
                if seguros and seguro_var.get():
                    seguro_seleccionado = seguro_var.get()
                    for s in seguros:
                        if f"{s[1]} (${s[2]})" == seguro_seleccionado:
                            id_seguro = s[0]
                            break
                
                id_descuento = None
                if descuentos and descuento_var.get():
                    descuento_seleccionado = descuento_var.get()
                    for d in descuentos:
                        if f"{d[1]} (-${d[2]})" == descuento_seleccionado:
                            id_descuento = d[0]
                            break
                
                print(f"Seguro ID: {id_seguro}, Descuento ID: {id_descuento}")
                
                # Calcular total real
                vehiculo_query = """
                    SELECT t.tarifa_dia 
                    FROM Vehiculo v 
                    JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo 
                    WHERE v.placa = %s
                """
                vehiculo_result = self.db_manager.execute_query(vehiculo_query, (placa,))
                if not vehiculo_result:
                    messagebox.showerror("Error", "No se pudo obtener la tarifa del vehículo")
                    return
                
                tarifa = float(vehiculo_result[0][0]) if vehiculo_result[0][0] else 0
                fecha_salida_obj = salida_date.get_date()
                fecha_entrada_obj = entrada_date.get_date()
                dias = (fecha_entrada_obj - fecha_salida_obj).days
                if dias < 1:
                    dias = 1
                
                seguro_costo = 0
                if id_seguro and seguros:
                    for s in seguros:
                        if s[0] == id_seguro:
                            seguro_costo = float(s[2])
                            break
                
                descuento_val = 0
                if id_descuento and descuentos:
                    for d in descuentos:
                        if d[0] == id_descuento:
                            descuento_val = float(d[2])
                            break
                
                total = dias * tarifa + seguro_costo - descuento_val
                if total < 0:
                    total = 0
                
                print(f"Total calculado: ${total:,.0f} (días: {dias}, tarifa: ${tarifa}, seguro: ${seguro_costo}, descuento: ${descuento_val})")
                
                # Validar abono mínimo
                abono_min = int(total * 0.3)
                abono = int(entry_abono.get().strip())
                if abono < abono_min:
                    messagebox.showwarning("Error", f"El abono inicial debe ser al menos el 30%: ${abono_min:,.0f}")
                    return
                
                metodo = metodo_var.get()
                id_cliente = self.user_data.get('id_cliente')
                
                print(f"Insertando en Alquiler...")
                # Insertar en Alquiler
                placeholder = '%s' if not self.db_manager.offline else '?'
                alquiler_query = f"""
                    INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, 
                    id_seguro, id_descuento, valor) 
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """
                id_alquiler = self.db_manager.execute_query(alquiler_query, (
                    fecha_hora_salida, fecha_hora_entrada, placa, id_cliente, 
                    id_seguro, id_descuento, total
                ), fetch=False, return_lastrowid=True)
                
                if not id_alquiler:
                    messagebox.showerror("Error", "No se pudo obtener el ID del alquiler")
                    return
                
                print(f"ID Alquiler obtenido: {id_alquiler}")
                
                # Insertar en Reserva_alquiler
                saldo_pendiente = total - abono
                print(f"Insertando en Reserva_alquiler con saldo pendiente: ${saldo_pendiente}")
                reserva_query = f"""
                    INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono) 
                    VALUES ({placeholder}, 1, {placeholder}, {placeholder})
                """
                id_reserva = self.db_manager.execute_query(reserva_query, (id_alquiler, saldo_pendiente, abono), fetch=False, return_lastrowid=True)
                if not id_reserva:
                    raise Exception("No se pudo obtener el ID de la reserva")
                
                print(f"ID Reserva obtenido: {id_reserva}")
                
                # Insertar abono inicial
                id_medio_pago = 1 if metodo == "Efectivo" else (2 if metodo == "Tarjeta" else 3)
                print(f"Insertando abono inicial de ${abono} con medio de pago {id_medio_pago}")
                abono_query = f"""
                    INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) 
                    VALUES ({placeholder}, NOW(), {placeholder}, {placeholder})
                """
                self.db_manager.execute_query(abono_query, (abono, id_reserva, id_medio_pago), fetch=False)
                
                print(f"Reserva creada exitosamente. ID: {id_reserva}")
                
                # Mostrar mensaje según método de pago
                if metodo in ("Tarjeta", "Transferencia"):
                    self._simular_pasarela_pago(id_reserva, abono, metodo)
                else:
                    messagebox.showinfo("Reserva registrada", "Debes acercarte a la sede para validar y abonar el pago.")
                
                # Recargar lista de reservas
                print(f"Recargando lista de reservas...")
                self._cargar_reservas_cliente(id_cliente)
                
                # Limpiar formulario
                entry_abono.delete(0, 'end')
                
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo crear la reserva: {exc}")
                print(f"Error detallado: {exc}")
        
        ctk.CTkButton(frame, text="Crear reserva", command=crear_reserva, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(pady=20)

class GerenteView(BaseCTKView):
    def _welcome_message(self):
        # Obtener nombre de la base de datos
        db_name = self._get_db_name()
        return f"Bienvenido gerente, {self.user_data.get('usuario', '')}\nBase de datos: {db_name}"
    def _get_db_name(self):
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return db_name
        except Exception:
            return "(desconocida)"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(side="bottom", pady=(30, 20))
        # Pestaña: Gestionar Empleados (excepto gerentes y admin)
        self.tab_empleados = self.tabview.add("Empleados")
        ctk.CTkLabel(self.tabview.tab("Empleados"), text="Gestión de empleados (ventas, caja, mantenimiento)").pack(pady=10)
        # Pestaña: Gestionar Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        ctk.CTkLabel(self.tabview.tab("Clientes"), text="Gestión de clientes").pack(pady=10)
        # Pestaña: Reportes
        self.tab_reportes = self.tabview.add("Reportes")
        ctk.CTkLabel(self.tabview.tab("Reportes"), text="Reportes de sucursal").pack(pady=10)
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_empleados(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Empleados (ventas, caja, mantenimiento)", font=("Arial", 16)).pack(pady=10)
        # Listar empleados permitidos
        cargos = cargos_permitidos_para_gerente()
        query = f"SELECT id_empleado, nombre, cargo FROM Empleado WHERE LOWER(cargo) IN ({','.join(['?']*len(cargos))})"
        empleados = self.db_manager.execute_query(query, tuple(cargos))
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if empleados:
            for e in empleados:
                listbox.insert('end', f"ID: {e[0]} | Nombre: {e[1]} | Cargo: {e[2]}")
        else:
            listbox.insert('end', "No hay empleados registrados.")
        # Botón para crear empleado (solo cargos permitidos)
        def crear():
            win = tk.Toplevel(self)
            win.title("Nuevo empleado")
            win.geometry("400x300")
            ctk.CTkLabel(win, text="Nombre:").pack()
            entry_nombre = ctk.CTkEntry(win)
            entry_nombre.pack()
            ctk.CTkLabel(win, text="Cargo:").pack()
            cargo_var = tk.StringVar(value=cargos[0])
            cargo_menu = ctk.CTkOptionMenu(win, variable=cargo_var, values=cargos)
            cargo_menu.pack()
            def guardar():
                nombre = entry_nombre.get().strip()
                cargo = cargo_var.get()
                if not nombre or not cargo:
                    messagebox.showwarning("Error", "Todos los campos son obligatorios")
                    return
                # Validar permiso
                if not verificar_permiso_creacion_empleado(cargo, self.user_data['rol']):
                    messagebox.showwarning("Acceso denegado", "No tiene permisos para crear este tipo de empleado.")
                    return
                try:
                    self.db_manager.execute_query(
                        "INSERT INTO Empleado (nombre, cargo) VALUES (?, ?)",
                        (nombre, cargo), fetch=False
                    )
                    messagebox.showinfo("Éxito", "Empleado creado correctamente")
                    win.destroy()
                except Exception as exc:
                    messagebox.showerror("Error", f"No se pudo crear el empleado: {exc}")
            ctk.CTkButton(win, text="Guardar", command=guardar).pack(pady=10)
        ctk.CTkButton(frame, text="Nuevo empleado", command=crear).pack(pady=10)

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Clientes", font=("Arial", 16)).pack(pady=10)
        # Listar clientes
        query = "SELECT id_cliente, nombre, correo FROM Cliente"
        clientes = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if clientes:
            for c in clientes:
                listbox.insert('end', f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]}")
        else:
            listbox.insert('end', "No hay clientes registrados.")

    def _build_tab_reportes(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reportes de sucursal (en desarrollo)", font=("Arial", 16)).pack(pady=10)

class AdminView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido administrador, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(side="bottom", pady=(30, 20))
        # Pestaña: Gestionar Gerentes
        self.tab_gerentes = self.tabview.add("Gerentes")
        ctk.CTkLabel(self.tabview.tab("Gerentes"), text="Gestión de gerentes (crear, editar, eliminar)").pack(pady=10)
        # Pestaña: Gestionar Empleados
        self.tab_empleados = self.tabview.add("Empleados")
        ctk.CTkLabel(self.tabview.tab("Empleados"), text="Gestión de empleados (todos los cargos)").pack(pady=10)
        # Pestaña: Gestionar Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        ctk.CTkLabel(self.tabview.tab("Clientes"), text="Gestión de clientes").pack(pady=10)
        # Pestaña: SQL Libre (solo admin)
        if puede_ejecutar_sql_libre(self.user_data.get('rol', '')):
            self.tab_sql = self.tabview.add("SQL Libre")
            ctk.CTkLabel(self.tabview.tab("SQL Libre"), text="Ejecutar consultas SQL (solo admin)").pack(pady=10)
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_gerentes(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Gerentes", font=("Arial", 16)).pack(pady=10)
        # Listar gerentes
        query = "SELECT id_empleado, nombre FROM Empleado WHERE LOWER(cargo) = 'gerente'"
        gerentes = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if gerentes:
            for g in gerentes:
                listbox.insert('end', f"ID: {g[0]} | Nombre: {g[1]}")
        else:
            listbox.insert('end', "No hay gerentes registrados.")
        # Botón para crear gerente
        def crear():
            win = tk.Toplevel(self)
            win.title("Nuevo gerente")
            win.geometry("400x200")
            ctk.CTkLabel(win, text="Nombre:").pack()
            entry_nombre = ctk.CTkEntry(win)
            entry_nombre.pack()
            def guardar():
                nombre = entry_nombre.get().strip()
                if not nombre:
                    messagebox.showwarning("Error", "El nombre es obligatorio")
                    return
                if not puede_gestionar_gerentes(self.user_data['rol']):
                    messagebox.showwarning("Acceso denegado", "Solo un admin puede crear o editar gerentes.")
                    return
                try:
                    self.db_manager.execute_query(
                        "INSERT INTO Empleado (nombre, cargo) VALUES (?, 'gerente')",
                        (nombre,), fetch=False
                    )
                    messagebox.showinfo("Éxito", "Gerente creado correctamente")
                    win.destroy()
                except Exception as exc:
                    messagebox.showerror("Error", f"No se pudo crear el gerente: {exc}")
            ctk.CTkButton(win, text="Guardar", command=guardar).pack(pady=10)
        ctk.CTkButton(frame, text="Nuevo gerente", command=crear).pack(pady=10)

    def _build_tab_empleados(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Empleados (todos los cargos)", font=("Arial", 16)).pack(pady=10)
        # Listar empleados
        query = "SELECT id_empleado, nombre, cargo FROM Empleado"
        empleados = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if empleados:
            for e in empleados:
                listbox.insert('end', f"ID: {e[0]} | Nombre: {e[1]} | Cargo: {e[2]}")
        else:
            listbox.insert('end', "No hay empleados registrados.")

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Clientes", font=("Arial", 16)).pack(pady=10)
        # Listar clientes
        query = "SELECT id_cliente, nombre, correo FROM Cliente"
        clientes = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if clientes:
            for c in clientes:
                listbox.insert('end', f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]}")
        else:
            listbox.insert('end', "No hay clientes registrados.")

    def _build_tab_sql(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="SQL Libre (solo admin)", font=("Arial", 16)).pack(pady=10)
        entry_sql = tk.Text(frame, height=5, width=60)
        entry_sql.pack(pady=10)
        def ejecutar():
            sql = entry_sql.get("1.0", "end").strip()
            if not sql:
                messagebox.showwarning("Error", "Ingrese una consulta SQL")
                return
            try:
                res = self.db_manager.execute_query(sql)
                messagebox.showinfo("Resultado", str(res))
            except Exception as exc:
                messagebox.showerror("Error", f"Error al ejecutar SQL: {exc}")
        ctk.CTkButton(frame, text="Ejecutar", command=ejecutar).pack(pady=10)

class EmpleadoView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(side="bottom", pady=(30, 20))
        # Pestaña: Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        self._build_tab_reservas(self.tabview.tab("Reservas"))
        # Pestaña: Vehículos
        self.tab_vehiculos = self.tabview.add("Vehículos")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Clientes (crear, editar, ver)", font=("Arial", 16)).pack(pady=10)
        # Listar clientes
        query = "SELECT id_cliente, nombre, correo FROM Cliente"
        clientes = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if clientes:
            for c in clientes:
                listbox.insert('end', f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]}")
        else:
            listbox.insert('end', "No hay clientes registrados.")

    def _build_tab_reservas(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas", font=("Arial", 16)).pack(pady=10)
        # Listar reservas
        query = "SELECT id_reserva, id_cliente, id_vehiculo FROM Reserva"
        reservas = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=18, width=180)
        listbox.pack(pady=10)
        if reservas:
            for r in reservas:
                listbox.insert('end', f"ID: {r[0]} | Cliente: {r[1]} | Vehículo: {r[2]}")
        else:
            listbox.insert('end', "No hay reservas registradas.")

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 16)).pack(pady=10)
        # Listar vehículos disponibles con info completa
        query = ("SELECT v.placa, v.modelo, m.nombre_marca, t.descripcion, t.tarifa_dia "
                 "FROM Vehiculo v "
                 "JOIN Marca_vehiculo m ON v.id_marca = m.id_marca "
                 "JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo "
                 "WHERE v.id_estado_vehiculo = 1")
        vehiculos = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=80)
        listbox.pack(pady=10)
        self._vehiculos_cache = []
        if vehiculos:
            for v in vehiculos:
                self._vehiculos_cache.append(v)
                listbox.insert('end', f"Placa: {v[0]} | Modelo: {v[1]} | Marca: {v[2]} | Tipo: {v[3]} | Tarifa/día: {v[4]}")
        else:
            listbox.insert('end', "No hay vehículos disponibles.")
        # Botón para reservar vehículo seleccionado
        def reservar():
            sel = listbox.curselection()
            if not sel:
                tk.messagebox.showwarning("Aviso", "Seleccione un vehículo para reservar")
                return
            idx = sel[0]
            vehiculo = self._vehiculos_cache[idx]
            self._abrir_nueva_reserva_vehiculo(vehiculo)
        ctk.CTkButton(frame, text="Reservar seleccionado", command=reservar).pack(pady=5)

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
        ctk.CTkLabel(win, text=f"Placa: {placa} | {modelo} {marca} ({tipo})", font=("Arial", 15, "bold")).pack(pady=8)
        ctk.CTkLabel(win, text=f"Tarifa por día: ${tarifa_dia}", font=("Arial", 13)).pack(pady=4)
        # Frame de fecha y hora salida (solo uno, tipo tk.Frame)
        salida_frame = tk.Frame(win, bg="#222831")
        salida_frame.pack(fill="x", pady=8)
        tk.Label(salida_frame, text="Fecha y hora salida:", font=("Arial", 12), bg="#222831", fg="#F5F6FA").pack(anchor="w")
        salida_date = DateEntry(salida_frame, date_pattern='yyyy-mm-dd', width=12)
        salida_date.pack(side="left", padx=2)
        # Combobox para hora (1-12), minutos y AM/PM usando solo tkinter
        horas_12 = [f"{h:02d}" for h in range(1, 13)]
        minutos = ["00", "15", "30", "45"]
        ampm = ["AM", "PM"]
        salida_hora_cb = tk.ttk.Combobox(salida_frame, values=horas_12, width=3, state="readonly")
        salida_hora_cb.set("08")
        salida_hora_cb.pack(side="left", padx=2)
        tk.Label(salida_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        salida_min_cb = tk.ttk.Combobox(salida_frame, values=minutos, width=3, state="readonly")
        salida_min_cb.set("00")
        salida_min_cb.pack(side="left", padx=2)
        salida_ampm_cb = tk.ttk.Combobox(salida_frame, values=ampm, width=3, state="readonly")
        salida_ampm_cb.set("AM")
        salida_ampm_cb.pack(side="left", padx=2)
        # Frame de fecha y hora entrada (solo uno, tipo tk.Frame)
        entrada_frame = tk.Frame(win, bg="#222831")
        entrada_frame.pack(fill="x", pady=8)
        tk.Label(entrada_frame, text="Fecha y hora entrada:", font=("Arial", 12), bg="#222831", fg="#F5F6FA").pack(anchor="w")
        entrada_date = DateEntry(entrada_frame, date_pattern='yyyy-mm-dd', width=12)
        entrada_date.pack(side="left", padx=2)
        entrada_hora_cb = tk.ttk.Combobox(entrada_frame, values=horas_12, width=3, state="readonly")
        entrada_hora_cb.set("09")
        entrada_hora_cb.pack(side="left", padx=2)
        tk.Label(entrada_frame, text=":", bg="#222831", fg="#F5F6FA").pack(side="left")
        entrada_min_cb = tk.ttk.Combobox(entrada_frame, values=minutos, width=3, state="readonly")
        entrada_min_cb.set("00")
        entrada_min_cb.pack(side="left", padx=2)
        entrada_ampm_cb = tk.ttk.Combobox(entrada_frame, values=ampm, width=3, state="readonly")
        entrada_ampm_cb.set("AM")
        entrada_ampm_cb.pack(side="left", padx=2)
        # Seguros disponibles
        ctk.CTkLabel(win, text="Seguro:", font=("Arial", 12)).pack(pady=4)
        seguros = self.db_manager.execute_query("SELECT id_seguro, descripcion, costo FROM Seguro_alquiler")
        seguro_var = tk.StringVar()
        if seguros:
            seguro_menu = tk.OptionMenu(win, seguro_var, *[f"{s[1]} (${s[2]})" for s in seguros])
            seguro_menu.pack(fill="x", pady=4)
            seguro_var.set(f"{seguros[0][1]} (${seguros[0][2]})")
        else:
            ctk.CTkLabel(win, text="No hay seguros disponibles", text_color="#FF5555").pack(pady=4)
        # Descuentos disponibles
        ctk.CTkLabel(win, text="Descuento:", font=("Arial", 12)).pack(pady=4)
        descuentos = self.db_manager.execute_query("SELECT id_descuento, descripcion, valor FROM Descuento_alquiler")
        descuento_var = tk.StringVar()
        if descuentos:
            descuento_menu = tk.OptionMenu(win, descuento_var, *[f"{d[1]} (-${d[2]})" for d in descuentos])
            descuento_menu.pack(fill="x", pady=4)
            descuento_var.set(f"{descuentos[0][1]} (-${descuentos[0][2]})")
        else:
            ctk.CTkLabel(win, text="No hay descuentos disponibles", text_color="#FF5555").pack(pady=4)
        # Etiquetas para mostrar el total y el abono mínimo
        total_label = ctk.CTkLabel(win, text="Total a pagar: $0", font=("Arial", 14, "bold"), text_color="#00FF99")
        total_label.pack(pady=8)
        abono_min_label = ctk.CTkLabel(win, text="Abono mínimo (30%): $0", font=("Arial", 13), text_color="#FFD700")
        abono_min_label.pack(pady=4)
        # Abono y método de pago
        ctk.CTkLabel(win, text="Abono inicial ($, mínimo 30%):", font=("Arial", 12)).pack(pady=4)
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
                salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
                entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                idx_seg = [i for i, s in enumerate(seguros) if f"{s[1]} (${s[2]})" == seguro_var.get()]
                costo_seguro = float(seguros[idx_seg[0]][2]) if idx_seg else 0
                idx_desc = [i for i, d in enumerate(descuentos) if f"{d[1]} (-${d[2]})" == descuento_var.get()]
                valor_descuento = float(descuentos[idx_desc[0]][2]) if idx_desc else 0
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
        for widget in [salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb, entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb]:
            widget.bind("<<ComboboxSelected>>", actualizar_total)
            widget.bind("<FocusOut>", actualizar_total)
        if seguros:
            seguro_var.trace_add('write', lambda *a: actualizar_total())
        if descuentos:
            descuento_var.trace_add('write', lambda *a: actualizar_total())
        # Inicializar valores
        actualizar_total()
        # Guardar reserva
        def guardar():
            salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
            entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
            abono = entry_abono.get().strip()
            metodo_pago = metodo_pago_var.get()
            if not salida or not entrada or not (seguros and seguro_var.get()) or not (descuentos and descuento_var.get()) or not abono or not metodo_pago:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            fmt = "%Y-%m-%d %H:%M"
            try:
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                if dt_salida < datetime.now():
                    messagebox.showwarning("Error", "La fecha de salida no puede ser en el pasado")
                    return
                if dt_entrada <= dt_salida:
                    messagebox.showwarning("Error", "La fecha de entrada debe ser posterior a la de salida")
                    return
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                idx_seg = [i for i, s in enumerate(seguros) if f"{s[1]} (${s[2]})" == seguro_var.get()]
                id_seguro = seguros[idx_seg[0]][0] if idx_seg else None
                costo_seguro = float(seguros[idx_seg[0]][2]) if idx_seg else 0
                idx_desc = [i for i, d in enumerate(descuentos) if f"{d[1]} (-${d[2]})" == descuento_var.get()]
                id_descuento = descuentos[idx_desc[0]][0] if idx_desc else None
                valor_descuento = float(descuentos[idx_desc[0]][2]) if idx_desc else 0
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                # Validar abono mínimo
                try:
                    abono_val = float(abono)
                except ValueError:
                    messagebox.showwarning("Error", "El monto de abono debe ser un número válido")
                    return
                abono_min = round(total * 0.3, 2)
                if abono_val < abono_min:
                    messagebox.showwarning("Error", f"El abono mínimo es de $ {abono_min:,.2f}")
                    return
                id_cliente = self.user_data.get('id_cliente')
                placeholder = '%s' if not self.db_manager.offline else '?'
                # Insertar en Alquiler
                query_alquiler = (f"INSERT INTO Alquiler (fecha_hora_salida, valor, fecha_hora_entrada, id_vehiculo, id_cliente, id_sucursal, id_medio_pago, id_estado, id_seguro, id_descuento) "
                                  f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, 1, 1, 1, {placeholder}, {placeholder})")
                id_alquiler = self.db_manager.execute_query(query_alquiler, (salida, total, entrada, placa, id_cliente, id_seguro, id_descuento), fetch=False, return_lastrowid=True)
                if not id_alquiler:
                    raise Exception("No se pudo obtener el ID del alquiler")
                # Estado de reserva según método de pago
                if metodo_pago == "Efectivo":
                    estado_reserva = 1  # Pendiente de aprobación
                else:
                    estado_reserva = 2  # Confirmada
                # Insertar en Reserva_alquiler
                query_reserva = (f"INSERT INTO Reserva_alquiler (fecha_hora, abono, saldo_pendiente, id_estado_reserva, id_alquiler) "
                                 f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})")
                saldo_pendiente = total - abono_val
                id_reserva = self.db_manager.execute_query(query_reserva, (salida, abono_val, saldo_pendiente, estado_reserva, id_alquiler), fetch=False, return_lastrowid=True)
                if not id_reserva:
                    raise Exception("No se pudo obtener el ID de la reserva")
                # Insertar abono
                query_abono = (f"INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
                               f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})")
                id_medio_pago = 1 if metodo_pago == "Efectivo" else (2 if metodo_pago == "Tarjeta" else 3)
                self.db_manager.execute_query(query_abono, (abono_val, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_reserva, id_medio_pago), fetch=False)
                # Simulación de pasarela de pago si corresponde
                if metodo_pago in ("Tarjeta", "Transferencia"):
                    win.withdraw()
                    # Llamada sin on_finish, la recarga y cierre se hace al finalizar el pago
                    self._simular_pasarela_pago(id_reserva, abono_val, metodo_pago)
                else:
                    messagebox.showinfo("Reserva en espera", "Reserva creada. Debe acercarse a la oficina para entregar el dinero y que un empleado apruebe el alquiler.")
                win.destroy()
                # Solo recargar si el widget existe
                if hasattr(self, 'reservas_listbox'):
                    self._cargar_reservas_cliente(id_cliente)
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo crear la reserva: {exc}")
        ctk.CTkButton(win, text="Guardar reserva", command=guardar, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

    def _build_tab_reservas(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas", font=("Arial", 16)).pack(pady=10)
        # Listar reservas
        query = "SELECT id_reserva, id_cliente, id_vehiculo FROM Reserva"
        reservas = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=18, width=180)
        listbox.pack(pady=10)
        if reservas:
            for r in reservas:
                listbox.insert('end', f"ID: {r[0]} | Cliente: {r[1]} | Vehículo: {r[2]}")
        else:
            listbox.insert('end', "No hay reservas registradas.")

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 16)).pack(pady=10)
        # Listar vehículos disponibles con info completa
        query = ("SELECT v.placa, v.modelo, m.nombre_marca, t.descripcion, t.tarifa_dia "
                 "FROM Vehiculo v "
                 "JOIN Marca_vehiculo m ON v.id_marca = m.id_marca "
                 "JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo "
                 "WHERE v.id_estado_vehiculo = 1")
        vehiculos = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=80)
        listbox.pack(pady=10)
        self._vehiculos_cache = []
        if vehiculos:
            for v in vehiculos:
                self._vehiculos_cache.append(v)
                listbox.insert('end', f"Placa: {v[0]} | Modelo: {v[1]} | Marca: {v[2]} | Tipo: {v[3]} | Tarifa/día: {v[4]}")
        else:
            listbox.insert('end', "No hay vehículos disponibles.")
        # Botón para reservar vehículo seleccionado
        def reservar():
            sel = listbox.curselection()
            if not sel:
                tk.messagebox.showwarning("Aviso", "Seleccione un vehículo para reservar")
                return
            idx = sel[0]
            vehiculo = self._vehiculos_cache[idx]
            self._abrir_nueva_reserva_vehiculo(vehiculo)
        ctk.CTkButton(frame, text="Reservar seleccionado", command=reservar).pack(pady=5)

class EmpleadoVentasView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de ventas, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(side="bottom", pady=(30, 20))
        # Pestaña: Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        self._build_tab_reservas(self.tabview.tab("Reservas"))
        # Pestaña: Vehículos
        self.tab_vehiculos = self.tabview.add("Vehículos")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Clientes (crear, editar, ver)", font=("Arial", 16)).pack(pady=10)
        # Listar clientes
        query = "SELECT id_cliente, nombre, correo FROM Cliente"
        clientes = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if clientes:
            for c in clientes:
                listbox.insert('end', f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]}")
        else:
            listbox.insert('end', "No hay clientes registrados.")

    def _build_tab_reservas(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas", font=("Arial", 16)).pack(pady=10)
        # Listar reservas
        query = "SELECT id_reserva, id_cliente, id_vehiculo FROM Reserva"
        reservas = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=18, width=180)
        listbox.pack(pady=10)
        if reservas:
            for r in reservas:
                listbox.insert('end', f"ID: {r[0]} | Cliente: {r[1]} | Vehículo: {r[2]}")
        else:
            listbox.insert('end', "No hay reservas registradas.")

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 16)).pack(pady=10)
        # Listar vehículos disponibles con info completa
        query = ("SELECT v.placa, v.modelo, m.nombre_marca, t.descripcion, t.tarifa_dia "
                 "FROM Vehiculo v "
                 "JOIN Marca_vehiculo m ON v.id_marca = m.id_marca "
                 "JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo "
                 "WHERE v.id_estado_vehiculo = 1")
        vehiculos = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=80)
        listbox.pack(pady=10)
        self._vehiculos_cache = []
        if vehiculos:
            for v in vehiculos:
                self._vehiculos_cache.append(v)
                listbox.insert('end', f"Placa: {v[0]} | Modelo: {v[1]} | Marca: {v[2]} | Tipo: {v[3]} | Tarifa/día: {v[4]}")
        else:
            listbox.insert('end', "No hay vehículos disponibles.")
        # Botón para reservar vehículo seleccionado
        def reservar():
            sel = listbox.curselection()
            if not sel:
                tk.messagebox.showwarning("Aviso", "Seleccione un vehículo para reservar")
                return
            idx = sel[0]
            vehiculo = self._vehiculos_cache[idx]
            self._abrir_nueva_reserva_vehiculo(vehiculo)
        ctk.CTkButton(frame, text="Reservar seleccionado", command=reservar).pack(pady=5)

    def _abrir_nueva_reserva_vehiculo(self, vehiculo):
        import tkinter as tk
        from tkinter import messagebox
        from datetime import datetime
        from tkcalendar import DateEntry
        from ttkbootstrap import Style
        from ttkbootstrap.widgets import Combobox
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
        ctk.CTkLabel(win, text=f"Placa: {placa} | {modelo} {marca} ({tipo})", font=("Arial", 15, "bold")).pack(pady=8)
        ctk.CTkLabel(win, text=f"Tarifa por día: ${tarifa_dia}", font=("Arial", 13)).pack(pady=4)
        ctk.CTkLabel(win, text="Fecha y hora salida:", font=("Arial", 12)).pack(pady=4)
        salida_frame = ctk.CTkFrame(win)
        salida_frame.pack(pady=2)
        salida_date = DateEntry(salida_frame, date_pattern='yyyy-mm-dd', width=16)
        salida_date.pack(side="left", padx=2)
        # Combobox para hora y minutos de salida
        style = Style("darkly")
        horas = [f"{h:02d}" for h in range(8, 21)]
        minutos = ["00", "15", "30", "45"]
        salida_hora_cb = Combobox(salida_frame, values=horas, width=3, bootstyle="info")
        salida_hora_cb.set("08")
        salida_hora_cb.pack(side="left", padx=2)
        ctk.CTkLabel(salida_frame, text=":").pack(side="left")
        salida_min_cb = Combobox(salida_frame, values=minutos, width=3, bootstyle="info")
        salida_min_cb.set("00")
        salida_min_cb.pack(side="left", padx=2)
        ctk.CTkLabel(win, text="Fecha y hora entrada:", font=("Arial", 12)).pack(pady=4)
        entrada_frame = ctk.CTkFrame(win)
        entrada_frame.pack(pady=2)
        entrada_date = DateEntry(entrada_frame, date_pattern='yyyy-mm-dd', width=16)
        entrada_date.pack(side="left", padx=2)
        entrada_hora_cb = Combobox(entrada_frame, values=horas, width=3, bootstyle="info")
        entrada_hora_cb.set("09")
        entrada_hora_cb.pack(side="left", padx=2)
        ctk.CTkLabel(entrada_frame, text=":").pack(side="left")
        entrada_min_cb = Combobox(entrada_frame, values=minutos, width=3, bootstyle="info")
        entrada_min_cb.set("00")
        entrada_min_cb.pack(side="left", padx=2)
        # Seguros disponibles
        ctk.CTkLabel(win, text="Seguro:", font=("Arial", 12)).pack(pady=4)
        seguros = self.db_manager.execute_query("SELECT id_seguro, descripcion, costo FROM Seguro_alquiler")
        seguro_var = tk.StringVar()
        if seguros:
            seguro_menu = tk.OptionMenu(win, seguro_var, *[f"{s[1]} (${s[2]})" for s in seguros])
            seguro_menu.pack(fill="x", pady=4)
            seguro_var.set(f"{seguros[0][1]} (${seguros[0][2]})")
        else:
            ctk.CTkLabel(win, text="No hay seguros disponibles", text_color="#FF5555").pack(pady=4)
        # Descuentos disponibles
        ctk.CTkLabel(win, text="Descuento:", font=("Arial", 12)).pack(pady=4)
        descuentos = self.db_manager.execute_query("SELECT id_descuento, descripcion, valor FROM Descuento_alquiler")
        descuento_var = tk.StringVar()
        if descuentos:
            descuento_menu = tk.OptionMenu(win, descuento_var, *[f"{d[1]} (-${d[2]})" for d in descuentos])
            descuento_menu.pack(fill="x", pady=4)
            descuento_var.set(f"{descuentos[0][1]} (-${descuentos[0][2]})")
        else:
            ctk.CTkLabel(win, text="No hay descuentos disponibles", text_color="#FF5555").pack(pady=4)
        # Método de pago
        ctk.CTkLabel(win, text="Método de pago:", font=("Arial", 12)).pack(pady=4)
        metodos = ["Efectivo", "Tarjeta"]
        metodo_var = tk.StringVar()
        metodo_menu = tk.OptionMenu(win, metodo_var, *metodos)
        metodo_menu.pack(pady=4)
        metodo_var.set(metodos[0])
        # Precio calculado
        precio_label = ctk.CTkLabel(win, text="Precio total: $", font=("Arial", 13, "bold"))
        precio_label.pack(pady=8)
        # Mensaje de abono mínimo
        abono_min_label = ctk.CTkLabel(win, text="Abono mínimo requerido: 30% del valor total", text_color="#FFD700", font=("Arial", 12, "bold"))
        abono_min_label.pack(pady=4)
        ctk.CTkLabel(win, text="Monto a abonar:", font=("Arial", 12)).pack(pady=4)
        entry_abono = ctk.CTkEntry(win, width=20)
        entry_abono.pack(pady=4)
        # Cálculo de precio
        def calcular_precio(*_):
            try:
                salida = entry_salida.get().strip()
                entrada = entry_entrada.get().strip()
                if not salida or not entrada:
                    precio_label.configure(text="Precio total: $")
                    return
                fmt = "%Y-%m-%d %H:%M"
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                # Seguro
                idx_seg = 0
                costo_seguro = 0
                if seguros and seguro_var.get():
                    idx_seg = [i for i, s in enumerate(seguros) if f"{s[1]} (${s[2]})" == seguro_var.get()]
                    if idx_seg:
                        idx_seg = idx_seg[0]
                        costo_seguro = float(seguros[idx_seg][2])
                # Descuento
                idx_desc = 0
                valor_descuento = 0
                if descuentos and descuento_var.get():
                    idx_desc = [i for i, d in enumerate(descuentos) if f"{d[1]} (-${d[2]})" == descuento_var.get()]
                    if idx_desc:
                        idx_desc = idx_desc[0]
                        valor_descuento = float(descuentos[idx_desc][2])
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                precio_label.configure(text=f"Precio total: ${total}")
                return total
            except Exception:
                precio_label.configure(text="Precio total: $")
                return None
        entry_salida.bind('<FocusOut>', calcular_precio)
        entry_entrada.bind('<FocusOut>', calcular_precio)
        seguro_var.trace('w', calcular_precio)
        descuento_var.trace('w', calcular_precio)
        # Guardar reserva
        def guardar():
            salida = entry_salida.get().strip()
            entrada = entry_entrada.get().strip()
            abono = entry_abono.get().strip()
            metodo_pago = metodo_var.get()
            if not salida or not entrada or not (seguros and seguro_var.get()) or not (descuentos and descuento_var.get()) or not abono or not metodo_pago:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            fmt = "%Y-%m-%d %H:%M"
            try:
                dt_salida = datetime.strptime(salida, fmt)
                dt_entrada = datetime.strptime(entrada, fmt)
                if dt_salida < datetime.now():
                    messagebox.showwarning("Error", "La fecha de salida no puede ser en el pasado")
                    return
                if dt_entrada <= dt_salida:
                    messagebox.showwarning("Error", "La fecha de entrada debe ser posterior a la de salida")
                    return
                dias = (dt_entrada - dt_salida).days
                if dias < 1:
                    dias = 1
                precio = dias * float(tarifa_dia)
                idx_seg = [i for i, s in enumerate(seguros) if f"{s[1]} (${s[2]})" == seguro_var.get()][0]
                id_seguro = seguros[idx_seg][0]
                costo_seguro = float(seguros[idx_seg][2])
                idx_desc = [i for i, d in enumerate(descuentos) if f"{d[1]} (-${d[2]})" == descuento_var.get()][0]
                id_descuento = descuentos[idx_desc][0]
                valor_descuento = float(descuentos[idx_desc][2])
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                # Validar abono mínimo
                try:
                    abono_val = float(abono)
                except ValueError:
                    messagebox.showwarning("Error", "El monto de abono debe ser un número válido")
                    return
                abono_min = round(total * 0.3, 2)
                if abono_val < abono_min:
                    messagebox.showwarning("Error", f"El abono mínimo es de $ {abono_min}")
                    return
                id_cliente = self.user_data.get('id_cliente')
                placeholder = '%s' if not self.db_manager.offline else '?'
                # Insertar en Alquiler
                query_alquiler = (f"INSERT INTO Alquiler (fecha_hora_salida, valor, fecha_hora_entrada, id_vehiculo, id_cliente, id_sucursal, id_medio_pago, id_estado, id_seguro, id_descuento) "
                                  f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, 1, 1, 1, {placeholder}, {placeholder})")
                id_alquiler = self.db_manager.execute_query(query_alquiler, (salida, total, entrada, placa, id_cliente, id_seguro, id_descuento), fetch=False, return_lastrowid=True)
                if not id_alquiler:
                    raise Exception("No se pudo obtener el ID del alquiler")
                # Estado de reserva según método de pago
                if metodo_pago == "Efectivo":
                    estado_reserva = 1  # Pendiente de aprobación
                else:
                    estado_reserva = 2  # Confirmada
                # Insertar en Reserva_alquiler
                query_reserva = (f"INSERT INTO Reserva_alquiler (fecha_hora, abono, saldo_pendiente, id_estado_reserva, id_alquiler) "
                                 f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})")
                saldo_pendiente = total - abono_val
                id_reserva = self.db_manager.execute_query(query_reserva, (salida, abono_val, saldo_pendiente, estado_reserva, id_alquiler), fetch=False, return_lastrowid=True)
                if not id_reserva:
                    raise Exception("No se pudo obtener el ID de la reserva")
                # Insertar abono
                query_abono = (f"INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
                               f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})")
                id_medio_pago = 1 if metodo_pago == "Efectivo" else (2 if metodo_pago == "Tarjeta" else 3)
                self.db_manager.execute_query(query_abono, (abono_val, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_reserva, id_medio_pago), fetch=False)
                # Simulación de pasarela de pago si corresponde
                if metodo_pago in ("Tarjeta", "Transferencia"):
                    win.withdraw()
                    # Llamada sin on_finish, la recarga y cierre se hace al finalizar el pago
                    self._simular_pasarela_pago(id_reserva, abono_val, metodo_pago)
                else:
                    messagebox.showinfo("Reserva en espera", "Reserva creada. Debe acercarse a la oficina para entregar el dinero y que un empleado apruebe el alquiler.")
                win.destroy()
                # Solo recargar si el widget existe
                if hasattr(self, 'reservas_listbox'):
                    self._cargar_reservas_cliente(id_cliente)
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo crear la reserva: {exc}")
        ctk.CTkButton(win, text="Guardar reserva", command=guardar, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

class EmpleadoCajaView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de caja, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña principal: Bienvenida y cerrar sesión
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(side="bottom", pady=(30, 20))
        # Pestaña: Pagos
        self.tab_pagos = self.tabview.add("Pagos")
        self._build_tab_pagos(self.tabview.tab("Pagos"))
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        self._build_tab_reservas(self.tabview.tab("Reservas"))
        # Pestaña: Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_pagos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Procesar pagos", font=("Arial", 16)).pack(pady=10)
        # Listar pagos (en desarrollo)
        ctk.CTkLabel(frame, text="Funcionalidad en desarrollo").pack(pady=10)

    def _build_tab_reservas(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas", font=("Arial", 16)).pack(pady=10)
        # Listar reservas
        query = "SELECT id_reserva, id_cliente, id_vehiculo FROM Reserva"
        reservas = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=18, width=180)
        listbox.pack(pady=10)
        if reservas:
            for r in reservas:
                listbox.insert('end', f"ID: {r[0]} | Cliente: {r[1]} | Vehículo: {r[2]}")
        else:
            listbox.insert('end', "No hay reservas registradas.")

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Clientes", font=("Arial", 16)).pack(pady=10)
        # Listar clientes
        query = "SELECT id_cliente, nombre, correo FROM Cliente"
        clientes = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if clientes:
            for c in clientes:
                listbox.insert('end', f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]}")
        else:
            listbox.insert('end', "No hay clientes registrados.")

class EmpleadoMantenimientoView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de mantenimiento, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color="#18191A")
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color="#F5F6FA")
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña principal: Bienvenida y cerrar sesión
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(side="bottom", pady=(30, 20))
        # Pestaña: Vehículos
        self.tab_vehiculos = self.tabview.add("Vehículos")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos"))
        # Pestaña: Reportar
        self.tab_reportar = self.tabview.add("Reportar")
        self._build_tab_reportar(self.tabview.tab("Reportar"))
        # Pestaña: Historial
        self.tab_historial = self.tabview.add("Historial")
        self._build_tab_historial(self.tabview.tab("Historial"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos asignados", font=("Arial", 16)).pack(pady=10)
        # Listar vehículos asignados (en desarrollo)
        ctk.CTkLabel(frame, text="Funcionalidad en desarrollo").pack(pady=10)

    def _build_tab_reportar(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reportar mantenimiento", font=("Arial", 16)).pack(pady=10)
        # Reportar mantenimiento (en desarrollo)
        ctk.CTkLabel(frame, text="Funcionalidad en desarrollo").pack(pady=10)

    def _build_tab_historial(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Historial vehículos", font=("Arial", 16)).pack(pady=10)
        # Historial de vehículos (en desarrollo)
        ctk.CTkLabel(frame, text="Funcionalidad en desarrollo").pack(pady=10) 