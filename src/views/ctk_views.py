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
        # Pestaña: Realizar abonos
        self.tab_abonos = self.tabview.add("Realizar abonos")
        self._build_tab_abonos(self.tabview.tab("Realizar abonos"))
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
        self._stop_status = True
        # Destruir la ventana actual completamente
        self.destroy()
        # Llamar al callback para volver al login
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
        # Pestaña: Realizar abonos
        self.tab_abonos = self.tabview.add("Realizar abonos")
        self._build_tab_abonos(self.tabview.tab("Realizar abonos"))
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
        ctk.CTkLabel(inner, text="Mis reservas", font=("Arial", 20, "bold")).pack(pady=10)
        # Contenedores para cada estado
        self.cards_pendientes = ctk.CTkFrame(inner, fg_color="#FFF8E1")  # Amarillo pastel
        self.cards_pendientes.pack(pady=8, fill="x")
        ctk.CTkLabel(self.cards_pendientes, text="⏳ Pendientes", font=("Arial", 15, "bold"), text_color="#B8860B").pack(anchor="w", padx=10, pady=(5,0))
        self.cards_pagadas = ctk.CTkFrame(inner, fg_color="#E8F5E9")  # Verde pastel
        self.cards_pagadas.pack(pady=8, fill="x")
        ctk.CTkLabel(self.cards_pagadas, text="✅ Pagadas", font=("Arial", 15, "bold"), text_color="#388E3C").pack(anchor="w", padx=10, pady=(5,0))
        self.cards_vencidas = ctk.CTkFrame(inner, fg_color="#FFEBEE")  # Rojo pastel
        self.cards_vencidas.pack(pady=8, fill="x")
        ctk.CTkLabel(self.cards_vencidas, text="❌ Vencidas/Canceladas", font=("Arial", 15, "bold"), text_color="#C62828").pack(anchor="w", padx=10, pady=(5,0))
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
        reservas = self.db_manager.execute_query(query, params)
        # Limpiar frames
        for frame in [self.cards_pendientes, self.cards_pagadas, self.cards_vencidas]:
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.destroy()
        if not reservas:
            ctk.CTkLabel(self.cards_pendientes, text="No tienes reservas registradas", font=("Arial", 12)).pack(pady=10)
            return
        for r in reservas:
            id_reserva, salida, entrada, id_vehiculo, modelo, placa, valor, saldo, abono, estado, seguro, costo_seguro, desc, val_desc = r
            # Determinar estado y color
            if estado and ("pendiente" in estado.lower() or "aprob" in estado.lower()):
                estado_str = "⏳ Pendiente"
                card_parent = self.cards_pendientes
                badge_color = "#FFD54F"  # Amarillo pastel
                text_color = "#B8860B"
            elif estado and "confirm" in estado.lower():
                estado_str = "✅ Pagada"
                card_parent = self.cards_pagadas
                badge_color = "#A5D6A7"  # Verde pastel
                text_color = "#388E3C"
            elif estado and ("cancel" in estado.lower() or "venc" in estado.lower()):
                estado_str = "❌ Cancelada/Vencida"
                card_parent = self.cards_vencidas
                badge_color = "#FFCDD2"  # Rojo pastel
                text_color = "#C62828"
            else:
                estado_str = estado or "Desconocido"
                card_parent = self.cards_vencidas
                badge_color = "#E0E0E0"
                text_color = "#616161"
            # Tarjeta visual
            card = ctk.CTkFrame(card_parent, fg_color="white", corner_radius=12)
            card.pack(fill="x", padx=10, pady=6)
            # Encabezado
            header = ctk.CTkFrame(card, fg_color="white")
            header.pack(fill="x", pady=(0,2))
            ctk.CTkLabel(header, text=f"{modelo} ({placa})", font=("Arial", 14, "bold")).pack(side="left", padx=8)
            ctk.CTkLabel(header, text=estado_str, font=("Arial", 12, "bold"), text_color=text_color, fg_color=badge_color, corner_radius=8, padx=8, pady=2).pack(side="right", padx=8)
            # Fechas
            fechas = ctk.CTkFrame(card, fg_color="white")
            fechas.pack(fill="x")
            ctk.CTkLabel(fechas, text=f"Salida: {salida:%Y-%m-%d %H:%M}", font=("Arial", 12)).pack(side="left", padx=8)
            ctk.CTkLabel(fechas, text=f"Entrada: {entrada:%Y-%m-%d %H:%M}", font=("Arial", 12)).pack(side="left", padx=8)
            # Montos
            montos = ctk.CTkFrame(card, fg_color="white")
            montos.pack(fill="x")
            ctk.CTkLabel(montos, text=f"Total: ${valor:,.0f}", font=("Arial", 12)).pack(side="left", padx=8)
            ctk.CTkLabel(montos, text=f"Abonado: ${abono:,.0f}", font=("Arial", 12)).pack(side="left", padx=8)
            ctk.CTkLabel(montos, text=f"Saldo: ${saldo:,.0f}", font=("Arial", 12)).pack(side="left", padx=8)
            # Seguro y descuento si aplica
            if seguro and costo_seguro:
                ctk.CTkLabel(card, text=f"Seguro: {seguro} (${costo_seguro:,.0f})", font=("Arial", 11), text_color="#1976D2").pack(anchor="w", padx=12)
            if desc and val_desc:
                ctk.CTkLabel(card, text=f"Descuento: {desc} (-${val_desc:,.0f})", font=("Arial", 11), text_color="#388E3C").pack(anchor="w", padx=12)
            # Botones de acción solo para pendientes
            if "pendiente" in estado_str.lower():
                btns = ctk.CTkFrame(card, fg_color="white")
                btns.pack(fill="x", pady=4)
                ctk.CTkButton(btns, text="Cancelar reserva", command=lambda rid=id_reserva: self._cancelar_reserva_card(rid)).pack(side="left", padx=8)
                ctk.CTkButton(btns, text="Editar fechas", command=lambda rid=id_reserva: self._editar_reserva_card(rid)).pack(side="left", padx=8)

    def _cancelar_reserva_card(self, id_reserva):
        from tkinter import messagebox
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

    def _editar_reserva_card(self, id_reserva):
        import tkinter as tk
        from tkinter import messagebox
        from datetime import datetime
        from tkcalendar import DateEntry
        placeholder = '%s' if not self.db_manager.offline else '?'
        
        # Obtener información completa de la reserva
        reserva_query = """
            SELECT a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, a.id_seguro, a.id_descuento, a.valor
            FROM Reserva_alquiler ra 
            JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler 
            WHERE ra.id_reserva = %s
        """
        reserva_data = self.db_manager.execute_query(reserva_query, (id_reserva,))
        if not reserva_data:
            messagebox.showerror("Error", "No se pudo obtener la información de la reserva.")
            return
        
        salida_actual, entrada_actual, id_vehiculo, id_seguro, id_descuento, valor_actual = reserva_data[0]
        
        # Convertir fechas a formato más amigable
        def formatear_fecha(fecha):
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
            return fecha.strftime("%Y-%m-%d %H:%M")
        
        salida_formateada = formatear_fecha(salida_actual)
        entrada_formateada = formatear_fecha(entrada_actual)
        
        win = ctk.CTkToplevel(self)
        win.title("Editar fechas de reserva")
        win.geometry("500x400")
        win.configure(fg_color="#222831")
        
        # Centrar ventana
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (500 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (400 // 2)
        win.geometry(f"500x400+{x}+{y}")
        
        ctk.CTkLabel(win, text="Editar Fechas de Reserva", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame para fechas con DateEntry y comboboxes como en crear reserva
        fechas_frame = ctk.CTkFrame(win)
        fechas_frame.pack(fill="x", padx=20, pady=10)
        
        # Fecha y hora salida
        ctk.CTkLabel(fechas_frame, text="Nueva fecha y hora salida:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        salida_frame = tk.Frame(fechas_frame, bg="#2A2D35")
        salida_frame.pack(fill="x", pady=5)
        
        salida_date = DateEntry(salida_frame, date_pattern='yyyy-mm-dd', width=12)
        salida_date.pack(side="left", padx=2)
        
        horas_12 = [f"{h:02d}" for h in range(1, 13)]
        minutos = ["00", "15", "30", "45"]
        ampm = ["AM", "PM"]
        
        salida_hora_cb = tk.ttk.Combobox(salida_frame, values=horas_12, width=3, state="readonly")
        salida_hora_cb.pack(side="left", padx=2)
        tk.Label(salida_frame, text=":", bg="#2A2D35", fg="#F5F6FA").pack(side="left")
        salida_min_cb = tk.ttk.Combobox(salida_frame, values=minutos, width=3, state="readonly")
        salida_min_cb.pack(side="left", padx=2)
        salida_ampm_cb = tk.ttk.Combobox(salida_frame, values=ampm, width=3, state="readonly")
        salida_ampm_cb.pack(side="left", padx=2)
        
        # Fecha y hora entrada
        ctk.CTkLabel(fechas_frame, text="Nueva fecha y hora entrada:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        entrada_frame = tk.Frame(fechas_frame, bg="#2A2D35")
        entrada_frame.pack(fill="x", pady=5)
        
        entrada_date = DateEntry(entrada_frame, date_pattern='yyyy-mm-dd', width=12)
        entrada_date.pack(side="left", padx=2)
        
        entrada_hora_cb = tk.ttk.Combobox(entrada_frame, values=horas_12, width=3, state="readonly")
        entrada_hora_cb.pack(side="left", padx=2)
        tk.Label(entrada_frame, text=":", bg="#2A2D35", fg="#F5F6FA").pack(side="left")
        entrada_min_cb = tk.ttk.Combobox(entrada_frame, values=minutos, width=3, state="readonly")
        entrada_min_cb.pack(side="left", padx=2)
        entrada_ampm_cb = tk.ttk.Combobox(entrada_frame, values=ampm, width=3, state="readonly")
        entrada_ampm_cb.pack(side="left", padx=2)
        
        # Establecer valores por defecto
        salida_dt = datetime.strptime(salida_formateada, "%Y-%m-%d %H:%M")
        entrada_dt = datetime.strptime(entrada_formateada, "%Y-%m-%d %H:%M")
        
        # Configurar fecha de salida
        salida_date.set_date(salida_dt.date())
        hora_salida = salida_dt.hour
        if hora_salida == 0:
            salida_hora_cb.set("12")
            salida_ampm_cb.set("AM")
        elif hora_salida < 12:
            salida_hora_cb.set(f"{hora_salida:02d}")
            salida_ampm_cb.set("AM")
        elif hora_salida == 12:
            salida_hora_cb.set("12")
            salida_ampm_cb.set("PM")
        else:
            salida_hora_cb.set(f"{hora_salida-12:02d}")
            salida_ampm_cb.set("PM")
        salida_min_cb.set(f"{salida_dt.minute:02d}")
        
        # Configurar fecha de entrada
        entrada_date.set_date(entrada_dt.date())
        hora_entrada = entrada_dt.hour
        if hora_entrada == 0:
            entrada_hora_cb.set("12")
            entrada_ampm_cb.set("AM")
        elif hora_entrada < 12:
            entrada_hora_cb.set(f"{hora_entrada:02d}")
            entrada_ampm_cb.set("AM")
        elif hora_entrada == 12:
            entrada_hora_cb.set("12")
            entrada_ampm_cb.set("PM")
        else:
            entrada_hora_cb.set(f"{hora_entrada-12:02d}")
            entrada_ampm_cb.set("PM")
        entrada_min_cb.set(f"{entrada_dt.minute:02d}")
        
        # Etiqueta para mostrar el nuevo valor calculado
        nuevo_valor_label = ctk.CTkLabel(win, text=f"Valor actual: ${valor_actual:,.0f}", font=("Arial", 12, "bold"), text_color="#FFD700")
        nuevo_valor_label.pack(pady=10)
        
        def get_24h(date, hora_cb, min_cb, ampm_cb):
            h = int(hora_cb.get())
            m = int(min_cb.get())
            ampm = ampm_cb.get()
            if ampm == "PM" and h != 12:
                h += 12
            if ampm == "AM" and h == 12:
                h = 0
            return f"{date.get()} {h:02d}:{m:02d}"
        
        def calcular_nuevo_valor(*args):
            try:
                nueva_salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
                nueva_entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
                
                # Validar formato de fechas
                fmt = "%Y-%m-%d %H:%M"
                fecha_salida_dt = datetime.strptime(nueva_salida, fmt)
                fecha_entrada_dt = datetime.strptime(nueva_entrada, fmt)
                
                if fecha_entrada_dt <= fecha_salida_dt:
                    nuevo_valor_label.configure(text="Error: Fecha entrada debe ser posterior a salida")
                    return
                
                # Calcular días
                dias = (fecha_entrada_dt - fecha_salida_dt).days
                if dias < 1:
                    dias = 1
                
                # Obtener tarifa del vehículo
                tarifa_query = """
                    SELECT t.tarifa_dia
                    FROM Vehiculo v
                    JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo
                    WHERE v.placa = %s
                """
                tarifa_result = self.db_manager.execute_query(tarifa_query, (id_vehiculo,))
                if not tarifa_result:
                    nuevo_valor_label.configure(text="Error: No se pudo obtener la tarifa")
                    return
                
                tarifa_dia = float(tarifa_result[0][0])
                nuevo_valor = dias * tarifa_dia
                
                # Agregar costo del seguro
                if id_seguro:
                    seguro_query = "SELECT costo FROM Seguro_alquiler WHERE id_seguro = %s"
                    seguro_result = self.db_manager.execute_query(seguro_query, (id_seguro,))
                    if seguro_result:
                        nuevo_valor += float(seguro_result[0][0])
                
                # Restar descuento
                if id_descuento:
                    descuento_query = "SELECT valor FROM Descuento_alquiler WHERE id_descuento = %s"
                    descuento_result = self.db_manager.execute_query(descuento_query, (id_descuento,))
                    if descuento_result:
                        nuevo_valor -= float(descuento_result[0][0])
                
                if nuevo_valor < 0:
                    nuevo_valor = 0
                
                nuevo_valor_label.configure(text=f"Nuevo valor: ${nuevo_valor:,.0f}")
                
            except ValueError:
                nuevo_valor_label.configure(text="Error: Formato de fecha inválido")
            except Exception as e:
                nuevo_valor_label.configure(text=f"Error: {str(e)}")
        
        # Vincular eventos para recalcular
        for widget in [salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb, entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb]:
            widget.bind("<<ComboboxSelected>>", calcular_nuevo_valor)
            widget.bind("<FocusOut>", calcular_nuevo_valor)
        
        # Calcular valor inicial
        calcular_nuevo_valor()
        
        def guardar():
            nueva_salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
            nueva_entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
            
            try:
                # Validar fechas
                fmt = "%Y-%m-%d %H:%M"
                fecha_salida_dt = datetime.strptime(nueva_salida, fmt)
                fecha_entrada_dt = datetime.strptime(nueva_entrada, fmt)
                
                if fecha_entrada_dt <= fecha_salida_dt:
                    messagebox.showwarning("Error", "La fecha de entrada debe ser posterior a la de salida")
                    return
                
                # Usar el método _actualizar_reserva que ya incluye validación de abonos
                if self._actualizar_reserva(id_reserva, nueva_salida, nueva_entrada, id_vehiculo, id_seguro, id_descuento):
                    win.destroy()
                    self._cargar_reservas_cliente(self.user_data.get('id_cliente'))
                
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD HH:MM")
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo actualizar la reserva: {exc}")
        
        ctk.CTkButton(win, text="Guardar cambios", command=guardar, fg_color="#3A86FF", hover_color="#265DAB").pack(pady=15)

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 18, "bold")).pack(pady=10)
        # Contenedor de tarjetas
        self.cards_vehiculos = ctk.CTkFrame(frame, fg_color="#E3F2FD")  # Azul pastel
        self.cards_vehiculos.pack(fill="both", expand=True, padx=10, pady=10)
        # Listar vehículos disponibles con TODA la información relevante
        query = ("""
            SELECT v.placa, v.modelo, v.kilometraje, v.n_chasis,
                   m.nombre_marca, t.descripcion as tipo_vehiculo, t.tarifa_dia, t.capacidad, t.combustible,
                   c.nombre_color, tr.descripcion as transmision, ci.descripcion as cilindraje,
                   b.descripcion as blindaje, s.estado as seguro_estado, s.descripcion as seguro_desc,
                   su.nombre as sucursal, su.direccion as sucursal_dir, su.telefono as sucursal_tel
            FROM Vehiculo v 
            JOIN Marca_vehiculo m ON v.id_marca = m.id_marca 
            JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo 
            LEFT JOIN Color_vehiculo c ON v.id_color = c.id_color 
            LEFT JOIN Transmision_vehiculo tr ON v.id_transmision = tr.id_transmision 
            LEFT JOIN Cilindraje_vehiculo ci ON v.id_cilindraje = ci.id_cilindraje
            LEFT JOIN Blindaje_vehiculo b ON v.id_blindaje = b.id_blindaje
            LEFT JOIN Seguro_vehiculo s ON v.id_seguro_vehiculo = s.id_seguro
            LEFT JOIN Sucursal su ON v.id_sucursal = su.id_sucursal
            WHERE v.id_estado_vehiculo = 1
        """)
        vehiculos = self.db_manager.execute_query(query)
        
        if not vehiculos:
            ctk.CTkLabel(self.cards_vehiculos, text="No hay vehículos disponibles", font=("Arial", 14)).pack(pady=20)
            return
        
        # Crear scrollable frame para las tarjetas
        canvas = tk.Canvas(self.cards_vehiculos, bg="#E3F2FD")
        scrollbar = tk.Scrollbar(self.cards_vehiculos, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#E3F2FD")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, vehiculo in enumerate(vehiculos):
            (placa, modelo, kilometraje, n_chasis, marca, tipo_vehiculo, tarifa_dia, 
             capacidad, combustible, color, transmision, cilindraje, blindaje, 
             seguro_estado, seguro_desc, sucursal, sucursal_dir, sucursal_tel) = vehiculo
            
            # Crear tarjeta con información completa
            card = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
            card.pack(fill="x", padx=10, pady=5)
            
            # Header de la tarjeta
            header_frame = ctk.CTkFrame(card, fg_color="#2196F3", corner_radius=10)
            header_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(header_frame, text=f"{marca} {modelo}", 
                        font=("Arial", 16, "bold"), text_color="white").pack(pady=5)
            ctk.CTkLabel(header_frame, text=f"Placa: {placa}", 
                        font=("Arial", 12), text_color="white").pack()
            
            # Información principal
            main_frame = ctk.CTkFrame(card, fg_color="transparent")
            main_frame.pack(fill="x", padx=10, pady=5)
            
            # Primera fila de información
            row1 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row1.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row1, text=f"💰 Tarifa: ${tarifa_dia:,.0f}/día", 
                        font=("Arial", 12, "bold"), text_color="#2E7D32").pack(side="left", padx=5)
            ctk.CTkLabel(row1, text=f"👥 Capacidad: {capacidad} personas", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row1, text=f"⛽ Combustible: {combustible}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Segunda fila de información
            row2 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row2.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row2, text=f"🎨 Color: {color or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row2, text=f"⚙️ Transmisión: {transmision or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row2, text=f"🔧 Cilindraje: {cilindraje or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Tercera fila de información
            row3 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row3.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row3, text=f"🛡️ Blindaje: {blindaje or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row3, text=f"📊 Kilometraje: {kilometraje:,} km", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row3, text=f"🔒 Seguro: {seguro_estado or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Información de sucursal
            if sucursal:
                row4 = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=5)
                row4.pack(fill="x", pady=5)
                
                ctk.CTkLabel(row4, text=f"🏢 Sucursal: {sucursal}", 
                            font=("Arial", 11, "bold"), text_color="#1976D2").pack(anchor="w", padx=5, pady=2)
                if sucursal_dir:
                    ctk.CTkLabel(row4, text=f"📍 {sucursal_dir}", 
                                font=("Arial", 10), text_color="#666666").pack(anchor="w", padx=5)
                if sucursal_tel:
                    ctk.CTkLabel(row4, text=f"📞 {sucursal_tel}", 
                                font=("Arial", 10), text_color="#666666").pack(anchor="w", padx=5)
            
            # Botón de reservar
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(5, 10))
            
            ctk.CTkButton(btn_frame, text="🚗 Reservar este vehículo", 
                         command=lambda p=placa: self._abrir_nueva_reserva_vehiculo(p),
                         fg_color="#4CAF50", hover_color="#388E3C", 
                         font=("Arial", 12, "bold")).pack(pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
        
        ctk.CTkButton(frame, text="Guardar reserva", command=guardar, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

    def _registrar_abono(self, id_reserva, monto, metodo, referencia=None):
        from tkinter import messagebox
        from datetime import datetime
        try:
            # Insertar el abono en la base de datos
            placeholder = '%s' if not self.db_manager.offline else '?'
            id_medio_pago = 1 if metodo == "Efectivo" else (2 if metodo == "Tarjeta" else 3)
            
            abono_query = f"""
                INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) 
                VALUES ({placeholder}, NOW(), {placeholder}, {placeholder})
            """
            self.db_manager.execute_query(abono_query, (monto, id_reserva, id_medio_pago), fetch=False)
            
            # Obtener el valor total de la reserva y calcular el nuevo saldo pendiente correctamente
            reserva_query = f"""
                SELECT a.valor, COALESCE(SUM(ar.valor), 0) as total_abonado
                FROM Reserva_alquiler ra
                JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler
                LEFT JOIN Abono_reserva ar ON ra.id_reserva = ar.id_reserva
                WHERE ra.id_reserva = {placeholder}
                GROUP BY a.valor
            """
            result = self.db_manager.execute_query(reserva_query, (id_reserva,))
            
            if not result:
                messagebox.showerror("Error", "No se pudo obtener la información de la reserva")
                return
            
            valor_total = float(result[0][0])
            total_abonado = float(result[0][1])  # Este total ya incluye el abono que acabamos de insertar
            
            # Calcular nuevo saldo pendiente
            nuevo_saldo_pendiente = max(0, valor_total - total_abonado)
            
            # Actualizar saldo pendiente en la reserva
            update_query = f"""
                UPDATE Reserva_alquiler 
                SET saldo_pendiente = {placeholder}
                WHERE id_reserva = {placeholder}
            """
            self.db_manager.execute_query(update_query, (nuevo_saldo_pendiente, id_reserva), fetch=False)
            
            # Verificar si la reserva está completamente pagada
            if nuevo_saldo_pendiente <= 0:
                # Cambiar estado a pagada
                estado_query = f"""
                    UPDATE Reserva_alquiler 
                    SET id_estado_reserva = 2 
                    WHERE id_reserva = {placeholder}
                """
                self.db_manager.execute_query(estado_query, (id_reserva,), fetch=False)
                messagebox.showinfo("¡Reserva pagada!", "¡Felicidades! Tu reserva ha sido completamente pagada.")
            
            # Mostrar mensaje de éxito
            if metodo == "Efectivo":
                messagebox.showinfo("Abono registrado", f"Abono de ${monto:,.0f} registrado exitosamente.\nDebes acercarte a la sede para entregar el dinero.")
            else:
                messagebox.showinfo("Abono procesado", f"Abono de ${monto:,.0f} procesado exitosamente con {metodo}.")
            
            # Recargar la lista de reservas
            self._cargar_reservas_pendientes(self.user_data.get('id_cliente'))
            
            # Limpiar campos y HABILITAR para nuevo abono
            self.input_abono.delete(0, 'end')
            self._abono_seleccionado = None
            # HABILITAR los campos para nuevo abono
            self.input_abono.configure(state="normal")
            self.metodo_pago_menu.configure(state="normal")
            self.btn_abonar.configure(state="normal")
            
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo registrar el abono: {exc}")

    def _simular_pasarela_pago(self, id_reserva, monto, metodo):
        from tkinter import messagebox
        import tkinter as tk
        from datetime import datetime
        
        # Crear ventana modal para simular pasarela de pago
        win = ctk.CTkToplevel(self)
        win.title(f"Pasarela de Pago - {metodo}")
        win.geometry("500x400")
        win.configure(fg_color="#1E1E1E")
        win.transient(self)
        win.grab_set()
        win.focus_set()
        
        # Centrar ventana
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (500 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (400 // 2)
        win.geometry(f"500x400+{x}+{y}")
        
        # Contenido de la pasarela
        ctk.CTkLabel(win, text="💳 Pasarela de Pago", font=("Arial", 18, "bold"), text_color="#00FF99").pack(pady=20)
        ctk.CTkLabel(win, text=f"Método: {metodo}", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(win, text=f"Monto: ${monto:,.0f}", font=("Arial", 16, "bold"), text_color="#FFD700").pack(pady=10)
        
        # Simular procesamiento
        progress_label = ctk.CTkLabel(win, text="Procesando pago...", font=("Arial", 12))
        progress_label.pack(pady=20)
        
        def procesar_pago():
            import time
            
            # Simular tiempo de procesamiento
            for i in range(3):
                progress_label.configure(text=f"Procesando pago... ({i+1}/3)")
                win.update()
                time.sleep(0.5)
            
            # Siempre aprobar el pago (eliminado el random)
            progress_label.configure(text="✅ Pago procesado exitosamente", text_color="#00FF99")
            win.update()
            time.sleep(1)
            
            # Registrar el abono
            self._registrar_abono(id_reserva, monto, metodo, f"REF_{int(time.time())}")
            
            win.destroy()
        
        # Iniciar procesamiento después de un breve delay
        win.after(1000, procesar_pago)

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
                ok = self.db_manager.update_cliente_info_both(
                    id_cliente,
                    entry_nombre.get(),
                    entry_telefono.get(),
                    entry_direccion.get(),
                    entry_correo.get()
                )
                if ok:
                    messagebox.showinfo("Éxito", "Perfil actualizado correctamente (ambas bases)")
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el perfil en ambas bases")
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo actualizar el perfil: {exc}")
        ctk.CTkButton(frame, text="Guardar cambios", command=guardar).pack(pady=10)

    def _build_tab_abonos(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        id_cliente = self.user_data.get('id_cliente')
        # Frame principal
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Realizar Abonos", font=("Arial", 18, "bold")).pack(pady=10)
        info_frame = ctk.CTkFrame(frame, fg_color="#2A2D35")
        info_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text="ℹ️ Información importante:", font=("Arial", 12, "bold"), text_color="#FFD700").pack(pady=5)
        ctk.CTkLabel(info_frame, text="• El primer abono debe ser al menos el 30% del valor total", font=("Arial", 11)).pack(pady=2)
        ctk.CTkLabel(info_frame, text="• Los siguientes abonos pueden ser de cualquier valor", font=("Arial", 11)).pack(pady=2)
        ctk.CTkLabel(info_frame, text="• Seleccione una reserva y complete los campos para abonar", font=("Arial", 11)).pack(pady=2)
        # Contenedor de tarjetas de reservas pendientes
        self.cards_abonos = ctk.CTkFrame(frame, fg_color="#FFF8E1")  # Amarillo pastel
        self.cards_abonos.pack(fill="both", expand=True, padx=10, pady=10)
        # Frame para entrada de monto y método de pago
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=15)
        ctk.CTkLabel(input_frame, text="Monto a abonar ($):", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.input_abono = ctk.CTkEntry(input_frame, width=120, state="disabled", placeholder_text="Ej: 50000")
        self.input_abono.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(input_frame, text="Método de pago:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]
        self.metodo_pago_var = tk.StringVar()
        self.metodo_pago_var.set(self.metodos_pago[0])
        self.metodo_pago_menu = tk.OptionMenu(input_frame, self.metodo_pago_var, *self.metodos_pago)
        self.metodo_pago_menu.grid(row=0, column=3, padx=5, pady=5)
        self.metodo_pago_menu.configure(state="disabled")
        self.btn_abonar = ctk.CTkButton(frame, text="💳 Realizar Abono", command=self._realizar_abono, fg_color="#00AA00", hover_color="#008800", font=("Arial", 13, "bold"), state="disabled")
        self.btn_abonar.pack(pady=10)
        self._abono_seleccionado = None
        self._cargar_reservas_pendientes(id_cliente)

    def _cargar_reservas_pendientes(self, id_cliente):
        # Limpiar tarjetas
        for widget in self.cards_abonos.winfo_children():
            widget.destroy()
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            f"SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, ra.saldo_pendiente, a.valor "
            f"FROM Reserva_alquiler ra "
            f"JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            f"WHERE a.id_cliente = {placeholder} AND ra.saldo_pendiente > 0 AND ra.id_estado_reserva IN (1,2) "
            f"ORDER BY a.fecha_hora_salida DESC"
        )
        reservas = self.db_manager.execute_query(query, (id_cliente,))
        self._abono_cards = {}
        if reservas:
            for r in reservas:
                id_reserva = r[0]
                salida = r[1]
                entrada = r[2]
                placa = r[5]
                modelo = r[4]
                saldo_pendiente = r[6]
                valor_total = r[7]
                abono_query = f"SELECT COALESCE(SUM(valor), 0) FROM Abono_reserva WHERE id_reserva = {placeholder}"
                abonos = self.db_manager.execute_query(abono_query, (id_reserva,))
                abonado = abonos[0][0] if abonos and abonos[0] else 0
                # Usar directamente el saldo_pendiente de la BD (ya está actualizado)
                saldo_real = saldo_pendiente
                if saldo_real > 0:
                    porcentaje_abonado = (abonado / valor_total) * 100 if valor_total > 0 else 0
                    es_primer_abono = abonado == 0
                    monto_minimo = valor_total * 0.30 if es_primer_abono else 0
                    # Tarjeta visual
                    card = ctk.CTkFrame(self.cards_abonos, fg_color="white", corner_radius=12)
                    card.pack(fill="x", padx=10, pady=8)
                    ctk.CTkLabel(card, text=f"{modelo} ({placa})", font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(6,0))
                    ctk.CTkLabel(card, text=f"Saldo pendiente: ${saldo_real:,.0f}", font=("Arial", 12), text_color="#B8860B").pack(anchor="w", padx=12)
                    ctk.CTkLabel(card, text=f"Abonado: ${abonado:,.0f} ({porcentaje_abonado:.1f}%)", font=("Arial", 12)).pack(anchor="w", padx=12)
                    if es_primer_abono:
                        ctk.CTkLabel(card, text=f"Mínimo 1er abono: ${monto_minimo:,.0f}", font=("Arial", 11), text_color="#C62828").pack(anchor="w", padx=12)
                    # Selección de tarjeta
                    card.bind("<Button-1>", lambda e, rid=id_reserva: self._seleccionar_abono_card(rid))
                    for child in card.winfo_children():
                        child.bind("<Button-1>", lambda e, rid=id_reserva: self._seleccionar_abono_card(rid))
                    self._abono_cards[id_reserva] = card
            if len(self.cards_abonos.winfo_children()) == 0:
                ctk.CTkLabel(self.cards_abonos, text="No tienes reservas pendientes de pago.", font=("Arial", 13), text_color="#C62828").pack(pady=20)
        else:
            ctk.CTkLabel(self.cards_abonos, text="No tienes reservas pendientes de pago.", font=("Arial", 13), text_color="#C62828").pack(pady=20)
        # Reset selección
        self._abono_seleccionado = None
        self.input_abono.configure(state="disabled")
        self.metodo_pago_menu.configure(state="disabled")
        self.btn_abonar.configure(state="disabled")

    def _seleccionar_abono_card(self, id_reserva):
        # Resalta la tarjeta seleccionada y habilita los campos
        for rid, card in self._abono_cards.items():
            if rid == id_reserva:
                card.configure(fg_color="#FFF59D")  # Amarillo más fuerte
            else:
                card.configure(fg_color="white")
        self._abono_seleccionado = id_reserva
        self.input_abono.configure(state="normal")
        self.metodo_pago_menu.configure(state="normal")
        self.btn_abonar.configure(state="normal")

    def _realizar_abono(self):
        from tkinter import messagebox
        import tkinter as tk
        from datetime import datetime
        id_reserva = self._abono_seleccionado
        if not id_reserva:
            messagebox.showwarning("Aviso", "Seleccione una reserva para abonar")
            return
        monto = self.input_abono.get().strip()
        metodo = self.metodo_pago_var.get()
        # Validaciones del monto
        if not monto:
            messagebox.showwarning("Error", "Ingrese un monto")
            return
        try:
            monto_float = float(monto)
        except ValueError:
            messagebox.showwarning("Error", "El monto debe ser un número válido")
            return
        if monto_float <= 0:
            messagebox.showwarning("Error", "El monto debe ser mayor a 0")
            return
        # Obtener información de la reserva para validaciones
        placeholder = '%s' if not self.db_manager.offline else '?'
        valor_query = f"""
            SELECT a.valor, ra.saldo_pendiente 
            FROM Reserva_alquiler ra 
            JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler 
            WHERE ra.id_reserva = {placeholder}
        """
        valor_result = self.db_manager.execute_query(valor_query, (id_reserva,))
        if not valor_result:
            messagebox.showerror("Error", "No se pudo obtener información de la reserva")
            return
        valor_total = valor_result[0][0]
        saldo_pendiente = valor_result[0][1]
        abonos_query = f"SELECT COALESCE(SUM(valor), 0) FROM Abono_reserva WHERE id_reserva = {placeholder}"
        abonos_result = self.db_manager.execute_query(abonos_query, (id_reserva,))
        abonado_anterior = abonos_result[0][0] if abonos_result and abonos_result[0] else 0
        # Validar 30% mínimo para el primer abono
        if abonado_anterior == 0:
            monto_minimo = valor_total * 0.30
            if monto_float < monto_minimo:
                messagebox.showwarning("Error", f"El primer abono debe ser al menos el 30% del valor total (${monto_minimo:,.0f})")
                return
        # Validar que no exceda el saldo pendiente (usar directamente el saldo_pendiente de la BD)
        if isinstance(saldo_pendiente, float) or isinstance(saldo_pendiente, int):
            saldo_pendiente_float = float(saldo_pendiente)
        else:
            saldo_pendiente_float = float(saldo_pendiente)
        
        if monto_float > saldo_pendiente_float:
            messagebox.showwarning("Error", f"El monto excede el saldo pendiente (${saldo_pendiente_float:,.0f})")
            return
        # Lógica de abono según método de pago
        if metodo == "Efectivo":
            self._registrar_abono(id_reserva, monto_float, metodo, None)
        else:
            self._simular_pasarela_pago(id_reserva, monto_float, metodo)

    def _build_tab_crear_reserva(self, parent):
        from tkcalendar import DateEntry
        import tkinter as tk
        # Frame principal
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Crear nueva reserva", font=("Arial", 20, "bold")).pack(pady=10)
        card = ctk.CTkFrame(frame, fg_color="#E3F2FD", corner_radius=16)
        card.pack(padx=20, pady=20, fill="x")
        # Selección de vehículo
        ctk.CTkLabel(card, text="Vehículo", font=("Arial", 13, "bold")).pack(anchor="w", pady=(10,0), padx=12)
        vehiculos = self.db_manager.execute_query("SELECT v.placa, v.modelo, m.nombre_marca FROM Vehiculo v JOIN Marca_vehiculo m ON v.id_marca = m.id_marca WHERE v.id_estado_vehiculo = 1")
        vehiculo_var = tk.StringVar()
        if vehiculos:
            vehiculo_menu = tk.OptionMenu(card, vehiculo_var, *[f"{v[0]} - {v[1]} {v[2]}" for v in vehiculos])
            vehiculo_menu.pack(fill="x", pady=4, padx=12)
            vehiculo_var.set(f"{vehiculos[0][0]} - {vehiculos[0][1]} {vehiculos[0][2]}")
        else:
            ctk.CTkLabel(card, text="No hay vehículos disponibles", text_color="#FF5555").pack(pady=4, padx=12)
        # Fecha y hora salida
        ctk.CTkLabel(card, text="Fecha y hora salida", font=("Arial", 12)).pack(anchor="w", pady=(10,0), padx=12)
        salida_frame = tk.Frame(card, bg="#E3F2FD")
        salida_frame.pack(fill="x", pady=4, padx=12)
        salida_date = DateEntry(salida_frame, date_pattern='yyyy-mm-dd', width=12)
        salida_date.pack(side="left", padx=2)
        horas_12 = [f"{h:02d}" for h in range(1, 13)]
        minutos = ["00", "15", "30", "45"]
        ampm = ["AM", "PM"]
        salida_hora_cb = tk.ttk.Combobox(salida_frame, values=horas_12, width=3, state="readonly")
        salida_hora_cb.set("08")
        salida_hora_cb.pack(side="left", padx=2)
        tk.Label(salida_frame, text=":", bg="#E3F2FD", fg="#222831").pack(side="left")
        salida_min_cb = tk.ttk.Combobox(salida_frame, values=minutos, width=3, state="readonly")
        salida_min_cb.set("00")
        salida_min_cb.pack(side="left", padx=2)
        salida_ampm_cb = tk.ttk.Combobox(salida_frame, values=ampm, width=3, state="readonly")
        salida_ampm_cb.set("AM")
        salida_ampm_cb.pack(side="left", padx=2)
        # Fecha y hora entrada
        ctk.CTkLabel(card, text="Fecha y hora entrada", font=("Arial", 12)).pack(anchor="w", pady=(10,0), padx=12)
        entrada_frame = tk.Frame(card, bg="#E3F2FD")
        entrada_frame.pack(fill="x", pady=4, padx=12)
        entrada_date = DateEntry(entrada_frame, date_pattern='yyyy-mm-dd', width=12)
        entrada_date.pack(side="left", padx=2)
        entrada_hora_cb = tk.ttk.Combobox(entrada_frame, values=horas_12, width=3, state="readonly")
        entrada_hora_cb.set("09")
        entrada_hora_cb.pack(side="left", padx=2)
        tk.Label(entrada_frame, text=":", bg="#E3F2FD", fg="#222831").pack(side="left")
        entrada_min_cb = tk.ttk.Combobox(entrada_frame, values=minutos, width=3, state="readonly")
        entrada_min_cb.set("00")
        entrada_min_cb.pack(side="left", padx=2)
        entrada_ampm_cb = tk.ttk.Combobox(entrada_frame, values=ampm, width=3, state="readonly")
        entrada_ampm_cb.set("AM")
        entrada_ampm_cb.pack(side="left", padx=2)
        # Seguro
        ctk.CTkLabel(card, text="Seguro", font=("Arial", 12)).pack(anchor="w", pady=(10,0), padx=12)
        seguros = self.db_manager.execute_query("SELECT id_seguro, descripcion, costo FROM Seguro_alquiler")
        seguro_var = tk.StringVar()
        if seguros:
            seguro_menu = tk.OptionMenu(card, seguro_var, *[f"{s[1]} (${s[2]})" for s in seguros])
            seguro_menu.pack(fill="x", pady=4, padx=12)
            seguro_var.set(f"{seguros[0][1]} (${seguros[0][2]})")
        else:
            ctk.CTkLabel(card, text="No hay seguros disponibles", text_color="#FF5555").pack(pady=4, padx=12)
        # Descuento
        ctk.CTkLabel(card, text="Descuento", font=("Arial", 12)).pack(anchor="w", pady=(10,0), padx=12)
        descuentos = self.db_manager.execute_query("SELECT id_descuento, descripcion, valor FROM Descuento_alquiler")
        descuento_var = tk.StringVar()
        if descuentos:
            descuento_menu = tk.OptionMenu(card, descuento_var, *[f"{d[1]} (-${d[2]})" for d in descuentos])
            descuento_menu.pack(fill="x", pady=4, padx=12)
            descuento_var.set(f"{descuentos[0][1]} (-${descuentos[0][2]})")
        else:
            ctk.CTkLabel(card, text="No hay descuentos disponibles", text_color="#FF5555").pack(pady=4, padx=12)
        # Método de pago
        ctk.CTkLabel(card, text="Método de pago", font=("Arial", 12)).pack(anchor="w", pady=(10,0), padx=12)
        metodos = ["Efectivo", "Tarjeta", "Transferencia"]
        metodo_var = tk.StringVar()
        metodo_menu = tk.OptionMenu(card, metodo_var, *metodos)
        metodo_menu.pack(fill="x", pady=4, padx=12)
        metodo_var.set(metodos[0])
        # Total y abono mínimo
        total_label = ctk.CTkLabel(card, text="Total: $0", font=("Arial", 13, "bold"), text_color="#1976D2")
        total_label.pack(pady=8, padx=12)
        abono_label = ctk.CTkLabel(card, text="Abono mínimo (30%): $0", font=("Arial", 12), text_color="#FFD700")
        abono_label.pack(pady=4, padx=12)
        # Campo de abono inicial
        ctk.CTkLabel(card, text="Abono inicial ($)", font=("Arial", 12)).pack(anchor="w", pady=(10,0), padx=12)
        entry_abono = ctk.CTkEntry(card, width=120)
        entry_abono.pack(pady=4, padx=12)
        # Función para calcular total y abono mínimo (igual que antes)
        def calcular_total(*_):
            try:
                if not vehiculos or not vehiculo_var.get():
                    total_label.configure(text="Total: $0")
                    abono_label.configure(text="Abono mínimo (30%): $0")
                    return
                placa = vehiculo_var.get().split(" - ")[0]
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
        calcular_total()
        # Botón para crear reserva
        def crear_reserva():
            import tkinter as tk
            from tkinter import messagebox
            from datetime import datetime
            try:
                # Validaciones básicas
                if not vehiculos or not vehiculo_var.get():
                    messagebox.showwarning("Error", "Seleccione un vehículo")
                    return
                if not entry_abono.get().strip():
                    messagebox.showwarning("Error", "Ingrese el abono inicial")
                    return
                # Obtener datos del vehículo
                placa = vehiculo_var.get().split(" - ")[0]
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
                abono_min = int(total * 0.3)
                abono = int(entry_abono.get().strip())
                if abono < abono_min:
                    messagebox.showwarning("Error", f"El abono inicial debe ser al menos el 30%: ${abono_min:,.0f}")
                    return
                metodo = metodo_var.get()
                id_cliente = self.user_data.get('id_cliente')
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
                saldo_pendiente = total - abono
                reserva_query = f"""
                    INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono) 
                    VALUES ({placeholder}, 1, {placeholder}, {placeholder})
                """
                id_reserva = self.db_manager.execute_query(reserva_query, (id_alquiler, saldo_pendiente, abono), fetch=False, return_lastrowid=True)
                if not id_reserva:
                    raise Exception("No se pudo obtener el ID de la reserva")
                id_medio_pago = 1 if metodo == "Efectivo" else (2 if metodo == "Tarjeta" else 3)
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
        
        ctk.CTkButton(frame, text="Guardar reserva", command=crear_reserva, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

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
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 18, "bold")).pack(pady=10)
        # Contenedor de tarjetas
        self.cards_vehiculos = ctk.CTkFrame(frame, fg_color="#E3F2FD")  # Azul pastel
        self.cards_vehiculos.pack(fill="both", expand=True, padx=10, pady=10)
        # Listar vehículos disponibles con TODA la información relevante
        query = ("""
            SELECT v.placa, v.modelo, v.kilometraje, v.n_chasis,
                   m.nombre_marca, t.descripcion as tipo_vehiculo, t.tarifa_dia, t.capacidad, t.combustible,
                   c.nombre_color, tr.descripcion as transmision, ci.descripcion as cilindraje,
                   b.descripcion as blindaje, s.estado as seguro_estado, s.descripcion as seguro_desc,
                   su.nombre as sucursal, su.direccion as sucursal_dir, su.telefono as sucursal_tel
            FROM Vehiculo v 
            JOIN Marca_vehiculo m ON v.id_marca = m.id_marca 
            JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo 
            LEFT JOIN Color_vehiculo c ON v.id_color = c.id_color 
            LEFT JOIN Transmision_vehiculo tr ON v.id_transmision = tr.id_transmision 
            LEFT JOIN Cilindraje_vehiculo ci ON v.id_cilindraje = ci.id_cilindraje
            LEFT JOIN Blindaje_vehiculo b ON v.id_blindaje = b.id_blindaje
            LEFT JOIN Seguro_vehiculo s ON v.id_seguro_vehiculo = s.id_seguro
            LEFT JOIN Sucursal su ON v.id_sucursal = su.id_sucursal
            WHERE v.id_estado_vehiculo = 1
        """)
        vehiculos = self.db_manager.execute_query(query)
        
        if not vehiculos:
            ctk.CTkLabel(self.cards_vehiculos, text="No hay vehículos disponibles", font=("Arial", 14)).pack(pady=20)
            return
        
        # Crear scrollable frame para las tarjetas
        canvas = tk.Canvas(self.cards_vehiculos, bg="#E3F2FD")
        scrollbar = tk.Scrollbar(self.cards_vehiculos, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#E3F2FD")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, vehiculo in enumerate(vehiculos):
            (placa, modelo, kilometraje, n_chasis, marca, tipo_vehiculo, tarifa_dia, 
             capacidad, combustible, color, transmision, cilindraje, blindaje, 
             seguro_estado, seguro_desc, sucursal, sucursal_dir, sucursal_tel) = vehiculo
            
            # Crear tarjeta con información completa
            card = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
            card.pack(fill="x", padx=10, pady=5)
            
            # Header de la tarjeta
            header_frame = ctk.CTkFrame(card, fg_color="#2196F3", corner_radius=10)
            header_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(header_frame, text=f"{marca} {modelo}", 
                        font=("Arial", 16, "bold"), text_color="white").pack(pady=5)
            ctk.CTkLabel(header_frame, text=f"Placa: {placa}", 
                        font=("Arial", 12), text_color="white").pack()
            
            # Información principal
            main_frame = ctk.CTkFrame(card, fg_color="transparent")
            main_frame.pack(fill="x", padx=10, pady=5)
            
            # Primera fila de información
            row1 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row1.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row1, text=f"💰 Tarifa: ${tarifa_dia:,.0f}/día", 
                        font=("Arial", 12, "bold"), text_color="#2E7D32").pack(side="left", padx=5)
            ctk.CTkLabel(row1, text=f"👥 Capacidad: {capacidad} personas", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row1, text=f"⛽ Combustible: {combustible}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Segunda fila de información
            row2 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row2.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row2, text=f"🎨 Color: {color or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row2, text=f"⚙️ Transmisión: {transmision or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row2, text=f"🔧 Cilindraje: {cilindraje or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Tercera fila de información
            row3 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row3.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row3, text=f"🛡️ Blindaje: {blindaje or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row3, text=f"📊 Kilometraje: {kilometraje:,} km", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row3, text=f"🔒 Seguro: {seguro_estado or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Información de sucursal
            if sucursal:
                row4 = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=5)
                row4.pack(fill="x", pady=5)
                
                ctk.CTkLabel(row4, text=f"🏢 Sucursal: {sucursal}", 
                            font=("Arial", 11, "bold"), text_color="#1976D2").pack(anchor="w", padx=5, pady=2)
                if sucursal_dir:
                    ctk.CTkLabel(row4, text=f"📍 {sucursal_dir}", 
                                font=("Arial", 10), text_color="#666666").pack(anchor="w", padx=5)
                if sucursal_tel:
                    ctk.CTkLabel(row4, text=f"📞 {sucursal_tel}", 
                                font=("Arial", 10), text_color="#666666").pack(anchor="w", padx=5)
            
            # Botón de reservar
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(5, 10))
            
            ctk.CTkButton(btn_frame, text="🚗 Reservar este vehículo", 
                         command=lambda p=placa: self._abrir_nueva_reserva_vehiculo(p),
                         fg_color="#4CAF50", hover_color="#388E3C", 
                         font=("Arial", 12, "bold")).pack(pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
        
        ctk.CTkButton(frame, text="Guardar reserva", command=guardar, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

    def _actualizar_reserva(self, id_reserva, fecha_salida, fecha_entrada, id_vehiculo, id_seguro, id_descuento):
        """Actualizar una reserva existente con validación de abonos"""
        try:
            from datetime import datetime
            from tkinter import messagebox
            
            # Calcular nuevo valor
            fecha_salida_dt = datetime.strptime(fecha_salida, "%Y-%m-%d %H:%M")
            fecha_entrada_dt = datetime.strptime(fecha_entrada, "%Y-%m-%d %H:%M")
            dias = (fecha_entrada_dt - fecha_salida_dt).days
            
            # Obtener tarifa del vehículo
            tarifa_query = """
                SELECT t.tarifa_dia
                FROM Vehiculo v
                JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo
                WHERE v.placa = %s
            """
            tarifa_result = self.db_manager.execute_query(tarifa_query, (id_vehiculo,))
            if not tarifa_result:
                messagebox.showerror("Error", "No se pudo obtener la tarifa del vehículo")
                return False
            
            tarifa_dia = float(tarifa_result[0][0])
            nuevo_valor = dias * tarifa_dia
            
            # Obtener costo del seguro
            if id_seguro:
                seguro_query = "SELECT costo FROM Seguro_alquiler WHERE id_seguro = %s"
                seguro_result = self.db_manager.execute_query(seguro_query, (id_seguro,))
                if seguro_result:
                    nuevo_valor += float(seguro_result[0][0])
            
            # Obtener descuento
            if id_descuento:
                descuento_query = "SELECT valor FROM Descuento_alquiler WHERE id_descuento = %s"
                descuento_result = self.db_manager.execute_query(descuento_query, (id_descuento,))
                if descuento_result:
                    nuevo_valor -= float(descuento_result[0][0])
            
            # Obtener total de abonos realizados
            abonos_query = "SELECT COALESCE(SUM(valor), 0) FROM Abono_reserva WHERE id_reserva = %s"
            abonos_result = self.db_manager.execute_query(abonos_query, (id_reserva,))
            total_abonos = float(abonos_result[0][0]) if abonos_result else 0
            
            # Validar si los abonos superan el nuevo valor
            if total_abonos > nuevo_valor:
                exceso = total_abonos - nuevo_valor
                mensaje = f"""⚠️ ATENCIÓN: Los abonos realizados (${total_abonos:,.0f}) superan el nuevo valor de la reserva (${nuevo_valor:,.0f}).

Exceso: ${exceso:,.0f}

Debe contactar a la empresa para solicitar el reembolso del exceso.

¿Desea continuar con la actualización?"""
                
                if not messagebox.askyesno("Exceso de Abonos", mensaje):
                    return False
            
            # Actualizar alquiler
            alquiler_query = """
                UPDATE Alquiler 
                SET fecha_hora_salida = %s, fecha_hora_entrada = %s, 
                    id_vehiculo = %s, id_seguro = %s, id_descuento = %s, valor = %s
                WHERE id_alquiler = (SELECT id_alquiler FROM Reserva_alquiler WHERE id_reserva = %s)
            """
            self.db_manager.execute_query(alquiler_query, 
                (fecha_salida, fecha_entrada, id_vehiculo, id_seguro, id_descuento, nuevo_valor, id_reserva), 
                fetch=False)
            
            # Actualizar saldo pendiente en reserva
            nuevo_saldo = max(0, nuevo_valor - total_abonos)
            reserva_query = """
                UPDATE Reserva_alquiler 
                SET saldo_pendiente = %s
                WHERE id_reserva = %s
            """
            self.db_manager.execute_query(reserva_query, (nuevo_saldo, id_reserva), fetch=False)
            
            messagebox.showinfo("Éxito", f"Reserva actualizada correctamente.\nNuevo valor: ${nuevo_valor:,.0f}\nSaldo pendiente: ${nuevo_saldo:,.0f}")
            # Corregir el nombre del método
            self._cargar_reservas_cliente(self.user_data.get('id_cliente'))
            # También actualizar la tabla de abonos si está activa
            self._cargar_reservas_pendientes(self.user_data.get('id_cliente'))
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la reserva: {str(e)}")
            return False

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
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 18, "bold")).pack(pady=10)
        # Contenedor de tarjetas
        self.cards_vehiculos = ctk.CTkFrame(frame, fg_color="#E3F2FD")  # Azul pastel
        self.cards_vehiculos.pack(fill="both", expand=True, padx=10, pady=10)
        # Listar vehículos disponibles con TODA la información relevante
        query = ("""
            SELECT v.placa, v.modelo, v.kilometraje, v.n_chasis,
                   m.nombre_marca, t.descripcion as tipo_vehiculo, t.tarifa_dia, t.capacidad, t.combustible,
                   c.nombre_color, tr.descripcion as transmision, ci.descripcion as cilindraje,
                   b.descripcion as blindaje, s.estado as seguro_estado, s.descripcion as seguro_desc,
                   su.nombre as sucursal, su.direccion as sucursal_dir, su.telefono as sucursal_tel
            FROM Vehiculo v 
            JOIN Marca_vehiculo m ON v.id_marca = m.id_marca 
            JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo 
            LEFT JOIN Color_vehiculo c ON v.id_color = c.id_color 
            LEFT JOIN Transmision_vehiculo tr ON v.id_transmision = tr.id_transmision 
            LEFT JOIN Cilindraje_vehiculo ci ON v.id_cilindraje = ci.id_cilindraje
            LEFT JOIN Blindaje_vehiculo b ON v.id_blindaje = b.id_blindaje
            LEFT JOIN Seguro_vehiculo s ON v.id_seguro_vehiculo = s.id_seguro
            LEFT JOIN Sucursal su ON v.id_sucursal = su.id_sucursal
            WHERE v.id_estado_vehiculo = 1
        """)
        vehiculos = self.db_manager.execute_query(query)
        
        if not vehiculos:
            ctk.CTkLabel(self.cards_vehiculos, text="No hay vehículos disponibles", font=("Arial", 14)).pack(pady=20)
            return
        
        # Crear scrollable frame para las tarjetas
        canvas = tk.Canvas(self.cards_vehiculos, bg="#E3F2FD")
        scrollbar = tk.Scrollbar(self.cards_vehiculos, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#E3F2FD")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, vehiculo in enumerate(vehiculos):
            (placa, modelo, kilometraje, n_chasis, marca, tipo_vehiculo, tarifa_dia, 
             capacidad, combustible, color, transmision, cilindraje, blindaje, 
             seguro_estado, seguro_desc, sucursal, sucursal_dir, sucursal_tel) = vehiculo
            
            # Crear tarjeta con información completa
            card = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
            card.pack(fill="x", padx=10, pady=5)
            
            # Header de la tarjeta
            header_frame = ctk.CTkFrame(card, fg_color="#2196F3", corner_radius=10)
            header_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(header_frame, text=f"{marca} {modelo}", 
                        font=("Arial", 16, "bold"), text_color="white").pack(pady=5)
            ctk.CTkLabel(header_frame, text=f"Placa: {placa}", 
                        font=("Arial", 12), text_color="white").pack()
            
            # Información principal
            main_frame = ctk.CTkFrame(card, fg_color="transparent")
            main_frame.pack(fill="x", padx=10, pady=5)
            
            # Primera fila de información
            row1 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row1.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row1, text=f"💰 Tarifa: ${tarifa_dia:,.0f}/día", 
                        font=("Arial", 12, "bold"), text_color="#2E7D32").pack(side="left", padx=5)
            ctk.CTkLabel(row1, text=f"👥 Capacidad: {capacidad} personas", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row1, text=f"⛽ Combustible: {combustible}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Segunda fila de información
            row2 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row2.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row2, text=f"🎨 Color: {color or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row2, text=f"⚙️ Transmisión: {transmision or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row2, text=f"🔧 Cilindraje: {cilindraje or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Tercera fila de información
            row3 = ctk.CTkFrame(main_frame, fg_color="transparent")
            row3.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row3, text=f"🛡️ Blindaje: {blindaje or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row3, text=f"📊 Kilometraje: {kilometraje:,} km", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            ctk.CTkLabel(row3, text=f"🔒 Seguro: {seguro_estado or 'No especificado'}", 
                        font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
            
            # Información de sucursal
            if sucursal:
                row4 = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=5)
                row4.pack(fill="x", pady=5)
                
                ctk.CTkLabel(row4, text=f"🏢 Sucursal: {sucursal}", 
                            font=("Arial", 11, "bold"), text_color="#1976D2").pack(anchor="w", padx=5, pady=2)
                if sucursal_dir:
                    ctk.CTkLabel(row4, text=f"📍 {sucursal_dir}", 
                                font=("Arial", 10), text_color="#666666").pack(anchor="w", padx=5)
                if sucursal_tel:
                    ctk.CTkLabel(row4, text=f"📞 {sucursal_tel}", 
                                font=("Arial", 10), text_color="#666666").pack(anchor="w", padx=5)
            
            # Botón de reservar
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(5, 10))
            
            ctk.CTkButton(btn_frame, text="🚗 Reservar este vehículo", 
                         command=lambda p=placa: self._abrir_nueva_reserva_vehiculo(p),
                         fg_color="#4CAF50", hover_color="#388E3C", 
                         font=("Arial", 12, "bold")).pack(pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
        
        ctk.CTkButton(frame, text="Guardar reserva", command=guardar, fg_color="#3A86FF", hover_color="#265DAB", font=("Arial", 13, "bold")).pack(pady=18)

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