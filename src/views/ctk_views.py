import customtkinter as ctk
import threading
import time
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre
)
from ..styles import BG_DARK, TEXT_COLOR, PRIMARY_COLOR, PRIMARY_COLOR_DARK

class BaseCTKView(ctk.CTk):
    def __init__(self, user_data, db_manager, on_logout=None):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._status_label = None
        self._stop_status = False
        self.geometry("600x400")
        self.configure(bg=BG_DARK)
        self._build_ui()
        self._update_status_label()
        self._start_status_updater()
        self.after(100, self._maximize_and_focus)

    def _maximize_and_focus(self):
        self.after(100, lambda: self.wm_state('zoomed'))
        self.focus_force()

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK, width=140, height=32).pack(side="right", padx=10, pady=8)
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
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK, width=140, height=32).pack(side="right", padx=10, pady=8)
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
        # Usar grid para todo en inner
        inner.grid_columnconfigure((0, 1, 2), weight=1)
        # Título usando grid
        ctk.CTkLabel(inner, text="Mis reservas", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
        # Contenedores por estado
        self.cards_pendientes = ctk.CTkFrame(inner, fg_color="#FFF8E1")
        self.cards_pendientes.grid(row=1, column=0, sticky="nsew", padx=5, pady=8)
        ctk.CTkLabel(self.cards_pendientes, text="⏳ Pendientes", font=("Arial", 15, "bold"), text_color="#B8860B").pack(anchor="w", padx=10, pady=(5,0))
        self.cards_pagadas = ctk.CTkFrame(inner, fg_color="#E8F5E9")
        self.cards_pagadas.grid(row=1, column=1, sticky="nsew", padx=5, pady=8)
        ctk.CTkLabel(self.cards_pagadas, text="✅ Pagadas", font=("Arial", 15, "bold"), text_color="#388E3C").pack(anchor="w", padx=10, pady=(5,0))
        self.cards_vencidas = ctk.CTkFrame(inner, fg_color="#FFEBEE")
        self.cards_vencidas.grid(row=1, column=2, sticky="nsew", padx=5, pady=8)
        ctk.CTkLabel(self.cards_vencidas, text="❌ Vencidas/Canceladas", font=("Arial", 15, "bold"), text_color="#C62828").pack(anchor="w", padx=10, pady=(5,0))
        self._cargar_reservas_cliente(id_cliente)

    def _cargar_reservas_cliente(self, id_cliente):
        # Consulta todas las reservas del cliente, sin importar el estado
        query = '''
            SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, a.valor, ra.saldo_pendiente, ra.abono, es.descripcion, s.descripcion, s.costo, d.descripcion, d.valor, d.fecha_inicio, d.fecha_fin
            FROM Reserva_alquiler ra
            JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler
            JOIN Vehiculo v ON a.id_vehiculo = v.placa
            LEFT JOIN Estado_reserva es ON ra.id_estado_reserva = es.id_estado
            LEFT JOIN Seguro_alquiler s ON a.id_seguro = s.id_seguro
            LEFT JOIN Descuento_alquiler d ON a.id_descuento = d.id_descuento
            WHERE a.id_cliente = %s
              AND a.fecha_hora_salida >= CURRENT_TIMESTAMP
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
            (
                id_reserva,
                salida,
                entrada,
                id_vehiculo,
                modelo,
                placa,
                valor,
                saldo,
                abono,
                estado,
                seguro,
                costo_seguro,
                desc,
                val_desc,
                fecha_inicio,
                fecha_fin,
            ) = r
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
        placeholder = '%s' if not self.db_manager.offline else '?'
        id_sucursal = self.user_data.get('id_sucursal')
        query = f"""
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
            WHERE v.id_estado_vehiculo = 1"""
        params = ()
        if id_sucursal is not None:
            query += f" AND v.id_sucursal = {placeholder}"
            params = (id_sucursal,)
        vehiculos = self.db_manager.execute_query(query, params)
        
        if not vehiculos:
            ctk.CTkLabel(self.cards_vehiculos, text="No hay vehículos disponibles", font=("Arial", 14)).pack(pady=20)
            return
        
        # Limitar la cantidad de tarjetas para evitar barras de desplazamiento
        max_cards = 5
        vehiculos = vehiculos[:max_cards]

        for i, vehiculo in enumerate(vehiculos):
            (placa, modelo, kilometraje, n_chasis, marca, tipo_vehiculo, tarifa_dia,
             capacidad, combustible, color, transmision, cilindraje, blindaje,
             seguro_estado, seguro_desc, sucursal, sucursal_dir, sucursal_tel) = vehiculo

            # Crear tarjeta con información completa
            card = ctk.CTkFrame(self.cards_vehiculos, fg_color="#FFFFFF", corner_radius=15)
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
        # Descuento activo
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
        for widget in [salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb, entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb]:
            widget.bind("<<ComboboxSelected>>", actualizar_total)
            widget.bind("<FocusOut>", actualizar_total)
        if seguros:
            seguro_var.trace_add('write', lambda *a: actualizar_total())
        # Inicializar valores
        actualizar_total()
        # Guardar reserva
        def guardar():
            salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
            entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
            abono = entry_abono.get().strip()
            metodo_pago = metodo_pago_var.get()
            if not salida or not entrada or not (seguros and seguro_var.get()) or not abono or not metodo_pago:
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
                id_descuento = id_descuento_act
                valor_descuento = float(desc_val) if id_descuento_act else 0
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                
                print(f"Total calculado: ${total:,.0f} (días: {dias}, tarifa: ${tarifa}, seguro: ${seguro_costo}, descuento: ${valor_descuento})")
                
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
                    INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado,
                    id_seguro, id_descuento, valor)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """
                id_alquiler = self.db_manager.execute_query(alquiler_query, (
                    fecha_hora_salida, fecha_hora_entrada, placa, id_cliente, self.user_data.get('id_empleado'),
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
                    INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado)
                    VALUES ({placeholder}, 1, {placeholder}, {placeholder}, {placeholder})
                """
                id_reserva = self.db_manager.execute_query(
                    reserva_query,
                    (id_alquiler, saldo_pendiente, abono, self.user_data.get('id_empleado')),
                    fetch=False,
                    return_lastrowid=True
                )
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

    def _obtener_descuento_activo(self):
        """Retorna el descuento activo actual (id, descripcion, valor) o None."""
        query = (
            "SELECT id_descuento, descripcion, valor "
            "FROM Descuento_alquiler "
            "WHERE fecha_inicio <= CURRENT_TIMESTAMP "
            "AND fecha_fin >= CURRENT_TIMESTAMP "
            "LIMIT 1"
        )
        rows = self.db_manager.execute_query(query)
        return rows[0] if rows else (None, None, 0)

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

        # Listar descuentos vigentes para el cliente
        lista_desc = self.db_manager.execute_query(
            "SELECT descripcion, fecha_inicio, fecha_fin FROM Descuento_alquiler "
            "WHERE fecha_inicio <= CURRENT_TIMESTAMP AND fecha_fin >= CURRENT_TIMESTAMP"
        )
        if lista_desc:
            info = ctk.CTkFrame(frame)
            info.pack(fill="x", padx=20)
            ctk.CTkLabel(info, text="Descuentos disponibles", font=("Arial", 14, "bold")).pack(anchor="w")
            for d in lista_desc:
                ctk.CTkLabel(
                    info,
                    text=f"- {d[0]} ({str(d[1])[:10]} a {str(d[2])[:10]})",
                    font=("Arial", 12),
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(frame, text="No hay descuentos disponibles actualmente").pack(padx=20)
        # Selección de vehículo
        ctk.CTkLabel(card, text="Vehículo", font=("Arial", 13, "bold")).pack(anchor="w", pady=(10,0), padx=12)
        placeholder = '%s' if not self.db_manager.offline else '?'
        vehiculos = self.db_manager.execute_query(
            f"SELECT v.placa, v.modelo, m.nombre_marca FROM Vehiculo v JOIN Marca_vehiculo m ON v.id_marca = m.id_marca WHERE v.id_estado_vehiculo = 1 AND v.id_sucursal = {placeholder}",
            (self.user_data.get('id_sucursal'),))
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
        # Descuento activo
        id_descuento_act, desc_text, desc_val = self._obtener_descuento_activo()
        if id_descuento_act:
            ctk.CTkLabel(
                card,
                text=f"Descuento aplicado: {desc_text} (-${desc_val})",
                font=("Arial", 12),
            ).pack(anchor="w", pady=(10, 0), padx=12)
        else:
            ctk.CTkLabel(card, text="Sin descuentos activos").pack(anchor="w", pady=(10, 0), padx=12)
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
                # Calcular descuento activo
                descuento_val = float(desc_val) if id_descuento_act else 0
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
                # Obtener seguro
                id_seguro = None
                if seguros and seguro_var.get():
                    seguro_seleccionado = seguro_var.get()
                    for s in seguros:
                        if f"{s[1]} (${s[2]})" == seguro_seleccionado:
                            id_seguro = s[0]
                            break
                id_descuento = id_descuento_act
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
                descuento_val = float(desc_val) if id_descuento else 0
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
                    INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado,
                    id_seguro, id_descuento, valor)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """
                id_alquiler = self.db_manager.execute_query(alquiler_query, (
                    fecha_hora_salida, fecha_hora_entrada, placa, id_cliente, self.user_data.get('id_empleado'),
                    id_seguro, id_descuento, total
                ), fetch=False, return_lastrowid=True)
                if not id_alquiler:
                    messagebox.showerror("Error", "No se pudo obtener el ID del alquiler")
                    return
                saldo_pendiente = total - abono
                reserva_query = f"""
                    INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado)
                    VALUES ({placeholder}, 1, {placeholder}, {placeholder}, {placeholder})
                """
                id_reserva = self.db_manager.execute_query(
                    reserva_query,
                    (id_alquiler, saldo_pendiente, abono, self.user_data.get('id_empleado')),
                    fetch=False,
                    return_lastrowid=True
                )
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
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            "SELECT ra.id_reserva, a.id_cliente, a.id_vehiculo "
            "FROM Reserva_alquiler ra JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"WHERE a.id_sucursal = {placeholder}"
        )
        reservas = self.db_manager.execute_query(query, (self.user_data.get('id_sucursal'),))
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
        placeholder = '%s' if not self.db_manager.offline else '?'
        id_sucursal = self.user_data.get('id_sucursal')
        query = f"""
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
            WHERE v.id_estado_vehiculo = 1"""
        params = ()
        if id_sucursal is not None:
            query += f" AND v.id_sucursal = {placeholder}"
            params = (id_sucursal,)
        vehiculos = self.db_manager.execute_query(query, params)
        
        if not vehiculos:
            ctk.CTkLabel(self.cards_vehiculos, text="No hay vehículos disponibles", font=("Arial", 14)).pack(pady=20)
            return
        
        # Limitar la cantidad de tarjetas mostradas
        max_cards = 5
        vehiculos = vehiculos[:max_cards]

        for i, vehiculo in enumerate(vehiculos):
            (placa, modelo, kilometraje, n_chasis, marca, tipo_vehiculo, tarifa_dia,
             capacidad, combustible, color, transmision, cilindraje, blindaje,
             seguro_estado, seguro_desc, sucursal, sucursal_dir, sucursal_tel) = vehiculo

            # Crear tarjeta con información completa
            card = ctk.CTkFrame(self.cards_vehiculos, fg_color="#FFFFFF", corner_radius=15)
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
        # Descuento activo
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
        for widget in [salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb, entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb]:
            widget.bind("<<ComboboxSelected>>", actualizar_total)
            widget.bind("<FocusOut>", actualizar_total)
        if seguros:
            seguro_var.trace_add('write', lambda *a: actualizar_total())
        # Inicializar valores
        actualizar_total()
        # Guardar reserva
        def guardar():
            salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
            entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
            abono = entry_abono.get().strip()
            metodo_pago = metodo_pago_var.get()
            if not salida or not entrada or not (seguros and seguro_var.get()) or not abono or not metodo_pago:
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
                id_descuento = id_descuento_act
                valor_descuento = float(desc_val) if id_descuento_act else 0
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                
                print(f"Total calculado: ${total:,.0f} (días: {dias}, tarifa: ${tarifa}, seguro: ${seguro_costo}, descuento: ${valor_descuento})")
                
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
                    INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado,
                    id_seguro, id_descuento, valor)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """
                id_alquiler = self.db_manager.execute_query(alquiler_query, (
                    fecha_hora_salida, fecha_hora_entrada, placa, id_cliente, self.user_data.get('id_empleado'),
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
                    INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado)
                    VALUES ({placeholder}, 1, {placeholder}, {placeholder}, {placeholder})
                """
                id_reserva = self.db_manager.execute_query(
                    reserva_query,
                    (id_alquiler, saldo_pendiente, abono, self.user_data.get('id_empleado')),
                    fetch=False,
                    return_lastrowid=True
                )
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
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK, width=140, height=32).pack(side="right", padx=10, pady=8)
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

        ctk.CTkLabel(frame, text="Gestión de clientes", font=("Arial", 18, "bold")).pack(pady=10)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_clientes = tk.Listbox(list_frame, height=8, width=60, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb_clientes.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_clientes.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Documento:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Dirección:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Correo:").grid(row=4, column=0, padx=5, pady=5, sticky="e")

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

        ctk.CTkButton(btn_frame, text="Nuevo", command=self._nuevo_cliente, width=100).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Guardar", command=self._guardar_cliente, width=120, fg_color="#3A86FF", hover_color="#265DAB").grid(row=0, column=1, padx=5)

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
        ctk.CTkButton(top, text="Nueva reserva", command=lambda: self._abrir_form_reserva()).pack(side="right", padx=5, pady=5)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_reservas = tk.Listbox(list_frame, height=10, width=80, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb_reservas.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_reservas.pack(side="left", fill="both", expand=True)

        btns = ctk.CTkFrame(frame)
        btns.pack(pady=5)
        ctk.CTkButton(btns, text="Editar", command=lambda: self._abrir_form_reserva(self._reserva_sel), width=120).grid(row=0, column=0, padx=5)

        self.lb_reservas.bind("<<ListboxSelect>>", lambda e: self._seleccionar_reserva())
        self._cargar_reservas()

        def refresh():
            self._cargar_reservas()

        self._refresh_reservas = refresh

    def _cargar_clientes(self):
        self.lb_clientes.delete(0, 'end')
        rows = self.db_manager.execute_query(
            "SELECT id_cliente, nombre, correo FROM Cliente"
        )
        if rows:
            for c in rows:
                self.lb_clientes.insert('end', f"{c[0]} | {c[1]} | {c[2]}")

    def _seleccionar_cliente(self, event):
        sel = self.lb_clientes.curselection()
        if not sel:
            return
        idx = sel[0]
        data = self.lb_clientes.get(idx).split('|')
        self._cliente_sel = int(data[0].strip())
        placeholder = '%s' if not self.db_manager.offline else '?'
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = {placeholder}",
            (self._cliente_sel,))
        if row:
            doc, nom, tel, dir_, cor = row[0]
            self.ent_doc.delete(0, 'end'); self.ent_doc.insert(0, doc or '')
            self.ent_nom.delete(0, 'end'); self.ent_nom.insert(0, nom or '')
            self.ent_tel.delete(0, 'end'); self.ent_tel.insert(0, tel or '')
            self.ent_dir.delete(0, 'end'); self.ent_dir.insert(0, dir_ or '')
            self.ent_cor.delete(0, 'end'); self.ent_cor.insert(0, cor or '')

    def _nuevo_cliente(self):
        self._cliente_sel = None
        for e in [self.ent_doc, self.ent_nom, self.ent_tel, self.ent_dir, self.ent_cor]:
            e.delete(0, 'end')

    def _guardar_cliente(self):
        from tkinter import messagebox
        doc = self.ent_doc.get().strip()
        nom = self.ent_nom.get().strip()
        tel = self.ent_tel.get().strip()
        dir_ = self.ent_dir.get().strip()
        cor = self.ent_cor.get().strip()
        if not doc or not nom or not cor:
            messagebox.showwarning("Aviso", "Documento, nombre y correo son obligatorios")
            return
        placeholder = '%s' if not self.db_manager.offline else '?'
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
        self.lb_reservas.delete(0, 'end')
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            "SELECT ra.id_reserva, a.id_cliente, c.nombre, a.id_vehiculo "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Cliente c ON a.id_cliente = c.id_cliente "
            f"WHERE a.id_sucursal = {placeholder} "
            "ORDER BY c.nombre"
        )
        reservas = self.db_manager.execute_query(query, (self.user_data.get('id_sucursal'),))
        if reservas:
            for r in reservas:
                res_id, cid, cname, veh = r
                self.lb_reservas.insert('end', f"{res_id} | {cname} ({cid}) | {veh}")

    def _seleccionar_reserva(self):
        sel = self.lb_reservas.curselection()
        if sel:
            self._reserva_sel = int(self.lb_reservas.get(sel[0]).split('|')[0].strip())
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
        clientes = self.db_manager.execute_query(
            "SELECT id_cliente, nombre FROM Cliente ORDER BY nombre"
        ) or []
        cliente_map = {nombre: cid for cid, nombre in clientes}
        cliente_var = ctk.StringVar(value=next(iter(cliente_map), ""))
        ctk.CTkLabel(win, text="Cliente:").pack(pady=4)
        opt_cliente = ctk.CTkOptionMenu(win, variable=cliente_var, values=list(cliente_map.keys()))
        opt_cliente.pack(pady=4)

        # Vehículos disponibles
        placeholder = '%s' if not self.db_manager.offline else '?'
        vehiculos = self.db_manager.execute_query(
            f"SELECT placa FROM Vehiculo WHERE id_estado_vehiculo = 1 AND id_sucursal = {placeholder}",
            (self.user_data.get('id_sucursal'),),
        ) or []
        veh_map = {v[0]: v[0] for v in vehiculos}
        vehiculo_var = ctk.StringVar(value=next(iter(veh_map), ""))
        if vehiculo and vehiculo in veh_map:
            vehiculo_var.set(vehiculo)
        ctk.CTkLabel(win, text="Vehículo:").pack(pady=4)
        opt_veh = ctk.CTkOptionMenu(win, variable=vehiculo_var, values=list(veh_map.keys()))
        opt_veh.pack(pady=4)

        ctk.CTkLabel(win, text="Fecha salida:").pack(pady=4)
        salida = DateEntry(win, date_pattern='yyyy-mm-dd')
        salida.pack(pady=4)
        ctk.CTkLabel(win, text="Fecha entrada:").pack(pady=4)
        entrada = DateEntry(win, date_pattern='yyyy-mm-dd')
        entrada.pack(pady=4)

        if id_reserva:
            placeholder = '%s' if not self.db_manager.offline else '?'
            q = (
                "SELECT a.id_cliente, a.id_vehiculo, a.fecha_hora_salida, a.fecha_hora_entrada "
                "FROM Reserva_alquiler ra JOIN Alquiler a ON ra.id_alquiler=a.id_alquiler WHERE ra.id_reserva=%s"
            )
            row = self.db_manager.execute_query(q.replace('%s', placeholder), (id_reserva,))
            if row:
                cid, veh, fs, fe = row[0]
                name = cliente_map.get(cid) or next((n for n, i in cliente_map.items() if i == cid), "")
                if name:
                    cliente_var.set(name)
                if veh in veh_map:
                    vehiculo_var.set(veh)
                salida.set_date(fs)
                entrada.set_date(fe)

        def guardar():
            cid = cliente_map.get(cliente_var.get())
            veh = vehiculo_var.get().strip()
            fs = salida.get_date().strftime('%Y-%m-%d')
            fe = entrada.get_date().strftime('%Y-%m-%d')
            if not cid or not veh:
                messagebox.showwarning("Aviso", "Complete todos los campos")
                return
            placeholder = '%s' if not self.db_manager.offline else '?'
            try:
                if id_reserva:
                    q = f"UPDATE Alquiler a JOIN Reserva_alquiler ra ON a.id_alquiler=ra.id_alquiler SET a.id_cliente={placeholder}, a.id_vehiculo={placeholder}, a.fecha_hora_salida={placeholder}, a.fecha_hora_entrada={placeholder} WHERE ra.id_reserva={placeholder}"
                    self.db_manager.execute_query(q, (cid, veh, fs, fe, id_reserva), fetch=False)
                else:
                    q = f"INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
                    id_alq = self.db_manager.execute_query(q, (fs, fe, veh, cid, self.user_data.get('id_empleado')), fetch=False, return_lastrowid=True)
                    if id_alq:
                        q2 = (
                            f"INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado)"
                            f" VALUES ({placeholder}, 1, 0, 0, {placeholder})"
                        )
                        self.db_manager.execute_query(
                            q2,
                            (id_alq, self.user_data.get('id_empleado')),
                            fetch=False,
                        )
                messagebox.showinfo("Éxito", "Reserva guardada")
                win.destroy()
                self._cargar_reservas()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ctk.CTkButton(win, text="Guardar", command=guardar, fg_color="#3A86FF", hover_color="#265DAB").pack(pady=10)

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 18, "bold")).pack(pady=10)
        # Contenedor de tarjetas
        self.cards_vehiculos = ctk.CTkFrame(frame, fg_color="#E3F2FD")  # Azul pastel
        self.cards_vehiculos.pack(fill="both", expand=True, padx=10, pady=10)
        # Listar vehículos disponibles con TODA la información relevante
        placeholder = '%s' if not self.db_manager.offline else '?'
        id_sucursal = self.user_data.get('id_sucursal')
        query = f"""
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
            WHERE v.id_estado_vehiculo = 1"""
        params = ()
        if id_sucursal is not None:
            query += f" AND v.id_sucursal = {placeholder}"
            params = (id_sucursal,)
        vehiculos = self.db_manager.execute_query(query, params)
        
        if not vehiculos:
            ctk.CTkLabel(self.cards_vehiculos, text="No hay vehículos disponibles", font=("Arial", 14)).pack(pady=20)
            return
        
        # Limitar la cantidad de tarjetas mostradas
        max_cards = 5
        vehiculos = vehiculos[:max_cards]

        for i, vehiculo in enumerate(vehiculos):
            (placa, modelo, kilometraje, n_chasis, marca, tipo_vehiculo, tarifa_dia,
             capacidad, combustible, color, transmision, cilindraje, blindaje,
             seguro_estado, seguro_desc, sucursal, sucursal_dir, sucursal_tel) = vehiculo

            # Crear tarjeta con información completa
            card = ctk.CTkFrame(self.cards_vehiculos, fg_color="#FFFFFF", corner_radius=15)
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
        for widget in [salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb, entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb]:
            widget.bind("<<ComboboxSelected>>", actualizar_total)
            widget.bind("<FocusOut>", actualizar_total)
        if seguros:
            seguro_var.trace_add('write', lambda *a: actualizar_total())
        # Inicializar valores
        actualizar_total()
        # Guardar reserva
        def guardar():
            salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
            entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
            abono = entry_abono.get().strip()
            metodo_pago = metodo_pago_var.get()
            if not salida or not entrada or not (seguros and seguro_var.get()) or not abono or not metodo_pago:
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
                id_descuento = id_descuento_act
                valor_descuento = float(desc_val) if id_descuento_act else 0
                total = precio + costo_seguro - valor_descuento
                if total < 0:
                    total = 0
                
                print(f"Total calculado: ${total:,.0f} (días: {dias}, tarifa: ${tarifa}, seguro: ${seguro_costo}, descuento: ${valor_descuento})")
                
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
                    INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado,
                    id_seguro, id_descuento, valor)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """
                id_alquiler = self.db_manager.execute_query(alquiler_query, (
                    fecha_hora_salida, fecha_hora_entrada, placa, id_cliente, self.user_data.get('id_empleado'),
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
                    INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado)
                    VALUES ({placeholder}, 1, {placeholder}, {placeholder}, {placeholder})
                """
                id_reserva = self.db_manager.execute_query(
                    reserva_query,
                    (id_alquiler, saldo_pendiente, abono, self.user_data.get('id_empleado')),
                    fetch=False,
                    return_lastrowid=True
                )
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
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK, width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Tab: Pagos
        self.tab_pagos = self.tabview.add("Pagos")
        self._build_tab_pagos(self.tabview.tab("Pagos"))
        # Tab: Pagos manuales
        self.tab_manuales = self.tabview.add("Pagos manuales")
        self._build_tab_pagos_manuales(self.tabview.tab("Pagos manuales"))
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        self._build_tab_reservas(self.tabview.tab("Reservas"))
        # Pestaña: Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))
        self.tabview.set("Pagos")

    def _build_tab_pagos(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Procesar pagos", font=("Arial", 18, "bold")).pack(pady=10)

        self.cards_abonos = ctk.CTkFrame(frame, fg_color="#FFF8E1")
        self.cards_abonos.pack(fill="both", expand=True, padx=10, pady=10)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=15)
        ctk.CTkLabel(input_frame, text="Monto a abonar ($):", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.input_abono = ctk.CTkEntry(input_frame, width=120, state="disabled")
        self.input_abono.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(input_frame, text="Método de pago:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]
        self.metodo_pago_var = tk.StringVar()
        self.metodo_pago_var.set(self.metodos_pago[0])
        self.metodo_pago_menu = tk.OptionMenu(input_frame, self.metodo_pago_var, *self.metodos_pago)
        self.metodo_pago_menu.grid(row=0, column=3, padx=5, pady=5)
        self.metodo_pago_menu.configure(state="disabled")

        self.btn_abonar = ctk.CTkButton(frame, text="💳 Registrar Abono", command=self._realizar_abono_global, fg_color="#00AA00", hover_color="#008800", font=("Arial", 13, "bold"), state="disabled")
        self.btn_abonar.pack(pady=10)

        self._abono_seleccionado = None
        self._cargar_reservas_pendientes_global()

    def _build_tab_pagos_manuales(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Pago manual en efectivo", font=("Arial", 16, "bold")).pack(pady=10)

        form = ctk.CTkFrame(frame)
        form.pack(pady=15)

        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            "SELECT DISTINCT c.id_cliente, c.nombre "
            "FROM Cliente c "
            "JOIN Alquiler a ON c.id_cliente = a.id_cliente "
            "JOIN Reserva_alquiler ra ON a.id_alquiler = ra.id_alquiler "
            f"WHERE a.id_sucursal = {placeholder} "
            "ORDER BY c.nombre"
        )
        clientes = self.db_manager.execute_query(query, (self.user_data.get('id_sucursal'),)) or []

        self._pm_cliente_var = tk.StringVar(value=f"{clientes[0][0]} - {clientes[0][1]}" if clientes else "")

        tk.Label(form, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.OptionMenu(form, self._pm_cliente_var, *[f"{c[0]} - {c[1]}" for c in clientes]).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Monto efectivo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self._pm_monto = ctk.CTkEntry(form, width=120)
        self._pm_monto.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(frame, text="Registrar pago", command=self._registrar_pago_manual, fg_color="#00AA00", hover_color="#008800").pack(pady=10)

    def _registrar_pago_manual(self):
        from tkinter import messagebox

        cliente_raw = self._pm_cliente_var.get()
        if not cliente_raw:
            messagebox.showwarning("Aviso", "Seleccione un cliente")
            return
        try:
            id_cliente = int(cliente_raw.split('-')[0].strip())
        except ValueError:
            messagebox.showerror("Error", "Cliente inválido")
            return

        monto_str = self._pm_monto.get().strip()
        if not monto_str:
            messagebox.showwarning("Error", "Ingrese un monto")
            return
        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showwarning("Error", "Monto inválido")
            return
        if monto <= 0:
            messagebox.showwarning("Error", "El monto debe ser mayor a 0")
            return

        placeholder = '%s' if not self.db_manager.offline else '?'
        res = self.db_manager.execute_query(
            "SELECT ra.id_reserva FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"WHERE a.id_cliente = {placeholder} AND ra.saldo_pendiente > 0 "
            "ORDER BY ra.id_reserva LIMIT 1",
            (id_cliente,)
        )
        if not res:
            messagebox.showinfo("Aviso", "El cliente no tiene reservas pendientes")
            return

        id_reserva = res[0][0]
        self._registrar_abono(id_reserva, monto, "Efectivo", None)
        self._pm_monto.delete(0, 'end')
        self._cargar_reservas_pendientes_global()

    def _build_tab_reservas(self, parent):
        import tkinter as tk
        from tkinter import ttk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas", font=("Arial", 16)).pack(pady=10)

        # Listar reservas en tabla
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            "SELECT ra.id_reserva, a.id_cliente, a.id_vehiculo, "
            "a.fecha_hora_salida, a.fecha_hora_entrada, es.descripcion "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "LEFT JOIN Estado_reserva es ON ra.id_estado_reserva = es.id_estado "
            f"WHERE a.id_sucursal = {placeholder} "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        reservas = self.db_manager.execute_query(query, (self.user_data.get('id_sucursal'),))

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
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            f"SELECT id_cliente, nombre, correo FROM Cliente "
            f"WHERE id_sucursal = {placeholder} ORDER BY nombre"
        )
        clientes = self.db_manager.execute_query(query, (self.user_data.get('id_sucursal'),))
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if clientes:
            for c in clientes:
                listbox.insert('end', f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]}")
        else:
            listbox.insert('end', "No hay clientes registrados.")

    def _cargar_reservas_pendientes_global(self):
        for w in self.cards_abonos.winfo_children():
            w.destroy()
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            "SELECT ra.id_reserva, a.id_cliente, v.modelo, v.placa, ra.saldo_pendiente "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler AND a.id_sucursal = {placeholder} "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            "WHERE ra.saldo_pendiente > 0 AND ra.id_estado_reserva IN (1,2) "
            "ORDER BY ra.id_reserva"
        )
        reservas = self.db_manager.execute_query(query, (self.user_data.get('id_sucursal'),))
        self._abono_cards = {}
        if reservas:
            for r in reservas:
                rid, cid, modelo, placa, saldo = r
                card = ctk.CTkFrame(self.cards_abonos, fg_color="white", corner_radius=12)
                card.pack(fill="x", padx=10, pady=8)
                ctk.CTkLabel(card, text=f"Reserva {rid} - Cliente {cid}", font=("Arial", 14, "bold")).pack(anchor="w", padx=12)
                ctk.CTkLabel(card, text=f"{modelo} ({placa})", font=("Arial", 12)).pack(anchor="w", padx=12)
                ctk.CTkLabel(card, text=f"Saldo: ${saldo:,.0f}", font=("Arial", 12), text_color="#B8860B").pack(anchor="w", padx=12)
                card.bind("<Button-1>", lambda e, rid=rid: self._seleccionar_abono_card(rid))
                for child in card.winfo_children():
                    child.bind("<Button-1>", lambda e, rid=rid: self._seleccionar_abono_card(rid))
                self._abono_cards[rid] = card
        else:
            ctk.CTkLabel(self.cards_abonos, text="No hay reservas pendientes", font=("Arial", 13)).pack(pady=20)
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
        placeholder = '%s' if not self.db_manager.offline else '?'
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
        if sucursal_reserva != self.user_data.get('id_sucursal'):
            messagebox.showerror("Error", "No puedes procesar reservas de otra sucursal")
            return
        if monto_f > saldo:
            messagebox.showwarning("Error", f"El monto excede el saldo (${saldo:,.0f})")
            return
        self._registrar_abono(id_reserva, monto_f, metodo, None)
        self._cargar_reservas_pendientes_global()

class EmpleadoMantenimientoView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de mantenimiento, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        # Frame superior con estado y cerrar sesión
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK, width=140, height=32).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña principal: Bienvenida y cerrar sesión
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color=TEXT_COLOR, font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK, width=180, height=38).pack(side="bottom", pady=(30, 20))
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
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Vehículos asignados", font=("Arial", 18, "bold")).pack(pady=10)

        cont = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        cont.pack(fill="both", expand=True, padx=10, pady=10)

        placeholder = '%s' if not self.db_manager.offline else '?'
        id_sucursal = self.user_data.get('id_sucursal')
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
            ctk.CTkLabel(cont, text="Sin vehículos asignados", font=("Arial", 13)).pack(pady=20)
            return

        for v in vehiculos:
            placa, modelo, marca, tipo = v
            card = ctk.CTkFrame(cont, fg_color="white", corner_radius=10)
            card.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(card, text=f"{marca} {modelo}", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card, text=f"Placa: {placa} | {tipo}", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(0,5))

    def _build_tab_reportar(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Reportar mantenimiento", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(frame, text="Placa del vehículo:").pack(pady=5)
        self.rep_placa = ctk.CTkEntry(frame, width=150)
        self.rep_placa.pack(pady=5)

        ctk.CTkLabel(frame, text="Tipo de mantenimiento:").pack(pady=5)
        tipos = self.db_manager.execute_query(
            "SELECT id_tipo, descripcion FROM Tipo_mantenimiento"
        ) or []
        self.rep_tipo_map = {t[1]: t[0] for t in tipos}
        self.rep_tipo_var = ctk.StringVar(
            value=list(self.rep_tipo_map.keys())[0] if self.rep_tipo_map else ""
        )
        self.rep_tipo = ctk.CTkOptionMenu(
            frame, variable=self.rep_tipo_var, values=list(self.rep_tipo_map.keys())
        )
        self.rep_tipo.pack(pady=5)

        ctk.CTkLabel(frame, text="Taller:").pack(pady=5)
        talleres = self.db_manager.execute_query(
            "SELECT id_taller, nombre FROM Taller_mantenimiento"
        ) or []
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
            tipo = self.rep_tipo_map.get(self.rep_tipo_var.get()) if self.rep_tipo_var.get() else None
            taller = self.rep_taller_map.get(self.rep_taller_var.get()) if self.rep_taller_var.get() else None
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            placeholder = '%s' if not self.db_manager.offline else '?'
            query = (
                "INSERT INTO Mantenimiento_vehiculo "
                f"(descripcion, fecha_hora, valor, id_tipo, id_taller, id_vehiculo) "
                f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
            )
            params = (desc, fecha, costo_val, tipo, taller, placa)
            try:
                self.db_manager.execute_query(query, params, fetch=False)
                messagebox.showinfo("Éxito", "Reporte registrado")
                self.rep_placa.delete(0, 'end')
                self.rep_desc.delete(0, 'end')
                self.rep_costo.delete(0, 'end')
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ctk.CTkButton(frame, text="Registrar", command=guardar, fg_color="#3A86FF", hover_color="#265DAB").pack(pady=10)

    def _build_tab_historial(self, parent):
        import tkinter as tk

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Historial vehículos", font=("Arial", 18, "bold")).pack(pady=10)

        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.pack(pady=(0,5))
        ctk.CTkLabel(filter_frame, text="Filtrar por placa:").pack(side="left", padx=5)
        placas = self.db_manager.execute_query(
            "SELECT placa FROM Vehiculo WHERE id_sucursal = ?",
            (self.user_data.get('id_sucursal'),)
        ) or []
        opciones = ["Todos"] + [p[0] for p in placas]
        self.hist_placa_var = tk.StringVar(value="Todos")
        tk.OptionMenu(filter_frame, self.hist_placa_var, *opciones).pack(side="left")

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.hist_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=80)
        scrollbar.config(command=self.hist_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.hist_listbox.pack(side="left", fill="both", expand=True)

        def cargar():
            self.hist_listbox.delete(0, 'end')
            placeholder = '%s' if not self.db_manager.offline else '?'
            base = (
                "SELECT m.id_vehiculo, m.descripcion, m.fecha_hora, m.valor "
                "FROM Mantenimiento_vehiculo m JOIN Vehiculo v ON m.id_vehiculo = v.placa "
                f"WHERE v.id_sucursal = {placeholder}"
            )
            params = [self.user_data.get('id_sucursal')]
            placa = self.hist_placa_var.get()
            if placa != 'Todos':
                base += f" AND m.id_vehiculo = {placeholder}"
                params.append(placa)
            base += " ORDER BY m.fecha_hora DESC"
            rows = self.db_manager.execute_query(base, tuple(params))
            if rows:
                for p, d, fch, val in rows:
                    self.hist_listbox.insert('end', f"{fch} | {p} | {d} | ${val:,.0f}")
            else:
                self.hist_listbox.insert('end', "Sin registros de mantenimiento")

        tk.Button(filter_frame, text="Aplicar", command=cargar).pack(side="left", padx=5)
        cargar()

    def _build_tab_predictivo(self, parent):
        import tkinter as tk
        from datetime import datetime, timedelta

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Mantenimiento predictivo", font=("Arial", 18, "bold")).pack(pady=10)

        # Selector de sucursal para filtrar
        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.pack(pady=(0, 10))
        sucursales = self.db_manager.execute_query("SELECT id_sucursal, nombre FROM Sucursal") or []
        opciones = [f"{s[0]} - {s[1]}" for s in sucursales]
        self.sucursal_var = tk.StringVar()
        if opciones:
            default = next((o for o in opciones if o.startswith(str(self.user_data.get('id_sucursal')))), opciones[0])
            self.sucursal_var.set(default)
            tk.OptionMenu(filter_frame, self.sucursal_var, *opciones, command=lambda *_: self._cargar_predictivo_list()).pack()
        else:
            self.sucursal_var.set(str(self.user_data.get('id_sucursal')))

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.predictivo_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=80)
        scrollbar.config(command=self.predictivo_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.predictivo_listbox.pack(side="left", fill="both", expand=True)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=8)
        ctk.CTkButton(btn_frame, text="Programar mantenimiento", command=self._programar_mantenimiento,
                      fg_color="#3A86FF", hover_color="#265DAB").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Marcar revisado", command=self._marcar_revisado,
                      fg_color="#00C853", hover_color="#009624").pack(side="left", padx=5)

        self._cargar_predictivo_list()

    def _cargar_predictivo_list(self):
        import tkinter as tk
        from datetime import datetime, timedelta

        self.predictivo_listbox.delete(0, 'end')
        try:
            id_sucursal = int(str(self.sucursal_var.get()).split(' -')[0])
        except Exception:
            id_sucursal = self.user_data.get('id_sucursal')

        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            "SELECT v.placa, v.modelo, v.kilometraje, MAX(m.fecha_hora) "
            "FROM Vehiculo v "
            "LEFT JOIN Mantenimiento_vehiculo m ON v.placa = m.id_vehiculo "
            f"WHERE v.id_sucursal = {placeholder} "
            "GROUP BY v.placa, v.modelo, v.kilometraje"
        )
        filas = self.db_manager.execute_query(query, (id_sucursal,))

        if not filas:
            self.predictivo_listbox.insert('end', "Sin vehículos registrados")
            return

        umbral_dias = 180
        aviso_dias = 150
        hoy = datetime.now()

        for placa, modelo, km, fecha in filas:
            necesita = False
            color = None
            if fecha is None:
                necesita = True
                color = '#FFCDD2'
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
                    color = '#FFCDD2'
                elif dias >= aviso_dias:
                    necesita = True
                    color = '#FFF9C4'
                fecha_txt = fecha_dt.strftime("%Y-%m-%d") if fecha_dt else str(fecha)

            if necesita:
                self.predictivo_listbox.insert('end', f"{placa} | {modelo} | {km} km | {fecha_txt}")
                idx = self.predictivo_listbox.size() - 1
                if color:
                    self.predictivo_listbox.itemconfig(idx, background=color)

    def _programar_mantenimiento(self):
        from tkinter import messagebox
        selection = self.predictivo_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione un vehículo")
            return
        item = self.predictivo_listbox.get(selection[0])
        placa = item.split('|')[0].strip()
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = f"INSERT INTO Mantenimiento (placa, descripcion) VALUES ({placeholder}, {placeholder})"
        try:
            self.db_manager.execute_query(query, (placa, 'Programado mantenimiento'), fetch=False)
            messagebox.showinfo("Éxito", "Mantenimiento programado")
            self._cargar_predictivo_list()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _marcar_revisado(self):
        from tkinter import messagebox
        selection = self.predictivo_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione un vehículo")
            return
        item = self.predictivo_listbox.get(selection[0])
        placa = item.split('|')[0].strip()
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = f"INSERT INTO Mantenimiento (placa, descripcion) VALUES ({placeholder}, {placeholder})"
        try:
            self.db_manager.execute_query(query, (placa, 'Revisión completada'), fetch=False)
            messagebox.showinfo("Éxito", "Vehículo marcado como revisado")
            self._cargar_predictivo_list()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _build_tab_editar_vehiculo(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Editar vehículo", font=("Arial", 18, "bold")).pack(pady=10)

        form = ctk.CTkFrame(frame)
        form.pack(pady=5)

        ctk.CTkLabel(form, text="Placa:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        placas = self.db_manager.execute_query(
            "SELECT placa FROM Vehiculo WHERE id_sucursal = ?",
            (self.user_data.get('id_sucursal'),)
        ) or []
        self.edit_placa_var = tk.StringVar(value=placas[0][0] if placas else "")

        ctk.CTkLabel(form, text="Color:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        colores = self.db_manager.execute_query(
            "SELECT id_color, nombre_color FROM Color_vehiculo"
        ) or []
        self.edit_color_map = {c[1]: c[0] for c in colores}
        self.edit_color_var = tk.StringVar(value=list(self.edit_color_map.keys())[0] if colores else "")
        tk.OptionMenu(form, self.edit_color_var, *self.edit_color_map.keys()).grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Kilometraje:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.edit_km = ctk.CTkEntry(form, width=150)
        self.edit_km.grid(row=2, column=1, padx=5, pady=5)

        def cargar():
            placa = self.edit_placa_var.get()
            if not placa:
                return
            placeholder = '%s' if not self.db_manager.offline else '?'
            row = self.db_manager.execute_query(
                f"SELECT id_color, kilometraje FROM Vehiculo WHERE placa={placeholder}",
                (placa,)
            )
            if row:
                id_color, km = row[0]
                nombre = next((k for k,v in self.edit_color_map.items() if v == id_color), "")
                self.edit_color_var.set(nombre)
                self.edit_km.delete(0, 'end'); self.edit_km.insert(0, str(km or ''))

        tk.OptionMenu(form, self.edit_placa_var, *[p[0] for p in placas], command=lambda *_: cargar()).grid(row=0, column=1, padx=5, pady=5)

        def guardar():
            placa = self.edit_placa_var.get().strip()
            if not placa:
                messagebox.showwarning("Aviso", "Seleccione una placa")
                return
            color = self.edit_color_map.get(self.edit_color_var.get()) if self.edit_color_var.get() else None
            km = self.edit_km.get().strip()
            try:
                km_val = int(km) if km else 0
            except ValueError:
                messagebox.showwarning("Aviso", "Kilometraje inválido")
                return
            placeholder = '%s' if not self.db_manager.offline else '?'
            query = f"UPDATE Vehiculo SET id_color={placeholder}, kilometraje={placeholder} WHERE placa={placeholder}"
            try:
                self.db_manager.execute_query(query, (color, km_val, placa), fetch=False)
                messagebox.showinfo("Éxito", "Vehículo actualizado")
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Guardar cambios", command=guardar, fg_color="#3A86FF", hover_color="#265DAB").pack()

        cargar()

class GerenteView(BaseCTKView):
    """Vista CTk para gerentes con gestión de empleados y reportes."""

    def _welcome_message(self):
        return f"Bienvenido gerente, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout,
                      fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK,
                      width=140, height=32).pack(side="right", padx=10, pady=8)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color=TEXT_COLOR,
                     font=("Arial", 20)).pack(pady=30)

        self.tab_empleados = self.tabview.add("Empleados")
        self._build_tab_empleados(self.tabview.tab("Empleados"))

        self.tab_vehiculos = self.tabview.add("Vehículos")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos"))

        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))

        self.tab_reportes = self.tabview.add("Reportes")
        self._build_tab_reportes(self.tabview.tab("Reportes"))

        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

        if puede_ejecutar_sql_libre(self.user_data.get('rol')):
            self.tab_sql_libre = self.tabview.add("SQL Libre")
            self._build_tab_sql_libre(self.tabview.tab("SQL Libre"))

    def _build_tab_empleados(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        self._emp_sel = None
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Gestión de empleados", font=("Arial", 18, "bold")).pack(pady=10)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_emp = tk.Listbox(list_frame, height=8, width=60, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb_emp.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_emp.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Documento:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Correo:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Cargo:").grid(row=4, column=0, padx=5, pady=5, sticky="e")

        self.ent_doc_e = ctk.CTkEntry(form, width=150)
        self.ent_nom_e = ctk.CTkEntry(form, width=150)
        self.ent_tel_e = ctk.CTkEntry(form, width=150)
        self.ent_cor_e = ctk.CTkEntry(form, width=150)
        cargos = cargos_permitidos_para_gerente()
        self.cargo_var = ctk.StringVar(value=cargos[0])
        self.ent_cargo_e = ctk.CTkOptionMenu(form, variable=self.cargo_var, values=cargos, width=150)

        self.ent_doc_e.grid(row=0, column=1, padx=5, pady=5)
        self.ent_nom_e.grid(row=1, column=1, padx=5, pady=5)
        self.ent_tel_e.grid(row=2, column=1, padx=5, pady=5)
        self.ent_cor_e.grid(row=3, column=1, padx=5, pady=5)
        self.ent_cargo_e.grid(row=4, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Nuevo", command=self._nuevo_empleado, width=100).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Guardar", command=self._guardar_empleado, width=120,
                      fg_color="#3A86FF", hover_color="#265DAB").grid(row=0, column=1, padx=5)

        self.lb_emp.bind("<<ListboxSelect>>", self._seleccionar_empleado)
        self._cargar_empleados()

    def _cargar_empleados(self):
        self.lb_emp.delete(0, 'end')
        rows = self.db_manager.execute_query(
            "SELECT id_empleado, nombre, cargo, documento, telefono, correo FROM Empleado "
            "WHERE LOWER(cargo) NOT IN ('gerente','administrador')"
        )
        if rows:
            for r in rows:
                id_e, nombre, cargo, doc, tel, cor = r
                self.lb_emp.insert(
                    'end', f"{id_e} | {nombre} | {cargo} | {doc} | {tel} | {cor}"
                )

    def _seleccionar_empleado(self, event=None):
        sel = self.lb_emp.curselection()
        if not sel:
            return
        self._emp_sel = int(self.lb_emp.get(sel[0]).split('|')[0].strip())
        placeholder = '%s' if not self.db_manager.offline else '?'
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, correo, cargo FROM Empleado WHERE id_empleado = {placeholder}",
            (self._emp_sel,))
        if row:
            doc, nom, tel, cor, cargo = row[0]
            self.ent_doc_e.delete(0, 'end'); self.ent_doc_e.insert(0, doc or '')
            self.ent_nom_e.delete(0, 'end'); self.ent_nom_e.insert(0, nom or '')
            self.ent_tel_e.delete(0, 'end'); self.ent_tel_e.insert(0, tel or '')
            self.ent_cor_e.delete(0, 'end'); self.ent_cor_e.insert(0, cor or '')
            self.cargo_var.set(cargo or cargos_permitidos_para_gerente()[0])

    def _nuevo_empleado(self):
        self._emp_sel = None
        for e in [self.ent_doc_e, self.ent_nom_e, self.ent_tel_e, self.ent_cor_e]:
            e.delete(0, 'end')
        self.cargo_var.set(cargos_permitidos_para_gerente()[0])

    def _guardar_empleado(self):
        from tkinter import messagebox
        doc = self.ent_doc_e.get().strip()
        nom = self.ent_nom_e.get().strip()
        tel = self.ent_tel_e.get().strip()
        cor = self.ent_cor_e.get().strip()
        cargo = self.cargo_var.get().strip()
        if not doc or not nom or not cor or not cargo:
            messagebox.showwarning("Aviso", "Documento, nombre, correo y cargo son obligatorios")
            return
        if cargo.lower() == 'gerente' and not puede_gestionar_gerentes(self.user_data.get('rol')):
            messagebox.showwarning(
                "Aviso",
                "No tiene permiso para gestionar empleados con cargo 'gerente'",
            )
            return
        if not verificar_permiso_creacion_empleado(cargo, self.user_data.get('rol')):
            messagebox.showwarning("Aviso", "No tiene permiso para crear/editar este empleado")
            return
        placeholder = '%s' if not self.db_manager.offline else '?'
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

        ctk.CTkLabel(frame, text="Agregar vehículo", font=("Arial", 18, "bold")).pack(pady=10)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        labels = [
            "Placa:", "Chasis:", "Modelo:", "Kilometraje:",
            "Marca:", "Color:", "Tipo:", "Transmisión:",
            "Proveedor:", "Taller:"
        ]
        for i, lbl in enumerate(labels):
            ctk.CTkLabel(form, text=lbl).grid(row=i, column=0, padx=5, pady=5, sticky="e")

        self.ent_placa = ctk.CTkEntry(form, width=150)
        self.ent_chasis = ctk.CTkEntry(form, width=150)
        self.ent_modelo = ctk.CTkEntry(form, width=150)
        self.ent_km = ctk.CTkEntry(form, width=150)

        self.ent_placa.grid(row=0, column=1, padx=5, pady=5)
        self.ent_chasis.grid(row=1, column=1, padx=5, pady=5)
        self.ent_modelo.grid(row=2, column=1, padx=5, pady=5)
        self.ent_km.grid(row=3, column=1, padx=5, pady=5)

        # Cargar listas iniciales
        marcas = self.db_manager.execute_query(
            "SELECT id_marca, nombre_marca FROM Marca_vehiculo"
        ) or []
        colores = self.db_manager.execute_query(
            "SELECT id_color, nombre_color FROM Color_vehiculo"
        ) or []
        tipos = self.db_manager.execute_query(
            "SELECT id_tipo, descripcion FROM Tipo_vehiculo"
        ) or []
        trans = self.db_manager.execute_query(
            "SELECT id_transmision, descripcion FROM Transmision_vehiculo"
        ) or []

        self.marca_map = {m[1]: m[0] for m in marcas}
        self.color_map = {c[1]: c[0] for c in colores}
        self.tipo_map = {t[1]: t[0] for t in tipos}
        self.trans_map = {tr[1]: tr[0] for tr in trans}

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
        self.opt_prov = ctk.CTkOptionMenu(form, variable=self.var_prov, values=[])
        self.opt_taller = ctk.CTkOptionMenu(form, variable=self.var_taller, values=[])

        self.opt_marca.grid(row=4, column=1, padx=5, pady=5)
        self.opt_color.grid(row=5, column=1, padx=5, pady=5)
        self.opt_tipo.grid(row=6, column=1, padx=5, pady=5)
        self.opt_trans.grid(row=7, column=1, padx=5, pady=5)
        self.opt_prov.grid(row=8, column=1, padx=5, pady=5)
        self.opt_taller.grid(row=9, column=1, padx=5, pady=5)

        # Cargar opciones de proveedores y talleres
        self._load_proveedores_talleres()

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Nuevo", command=self._nuevo_vehiculo, width=100).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Guardar", command=self._guardar_vehiculo, width=120, fg_color="#3A86FF", hover_color="#265DAB").grid(row=0, column=1, padx=5)

    def _nuevo_vehiculo(self):
        for ent in [self.ent_placa, self.ent_chasis, self.ent_modelo, self.ent_km]:
            ent.delete(0, 'end')
        self._load_proveedores_talleres()

    def _load_proveedores_talleres(self):
        """Recargar opciones de proveedores y talleres."""
        proveedores = self.db_manager.execute_query(
            "SELECT id_proveedor, nombre FROM Proveedor_vehiculo"
        ) or []
        talleres = self.db_manager.execute_query(
            "SELECT id_taller, nombre FROM Taller_mantenimiento"
        ) or []

        self.prov_map = {p[1]: p[0] for p in proveedores}
        self.taller_map = {t[1]: t[0] for t in talleres}

        self.opt_prov.configure(values=list(self.prov_map.keys()))
        self.opt_taller.configure(values=list(self.taller_map.keys()))

        if self.prov_map:
            self.var_prov.set(list(self.prov_map.keys())[0])
        else:
            self.var_prov.set("")
        if self.taller_map:
            self.var_taller.set(list(self.taller_map.keys())[0])
        else:
            self.var_taller.set("")

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

        marca = self.marca_map.get(self.var_marca.get()) if self.var_marca.get() else None
        color = self.color_map.get(self.var_color.get()) if self.var_color.get() else None
        tipo = self.tipo_map.get(self.var_tipo.get()) if self.var_tipo.get() else None
        trans = self.trans_map.get(self.var_trans.get()) if self.var_trans.get() else None
        prov = self.prov_map.get(self.var_prov.get()) if self.var_prov.get() else None

        placeholder = '%s' if not self.db_manager.offline else '?'
        query = (
            f"INSERT INTO Vehiculo (placa, n_chasis, modelo, kilometraje, "
            f"id_marca, id_color, id_tipo_vehiculo, id_transmision, id_proveedor) "
            f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, "
            f"{placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )
        params = (placa, chasis, modelo, km_val, marca, color, tipo, trans, prov)
        try:
            self.db_manager.execute_query(query, params, fetch=False)
            messagebox.showinfo("Éxito", "Vehículo guardado correctamente")
            self._nuevo_vehiculo()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        self._cliente_sel = None

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Gestión de clientes", font=("Arial", 18, "bold")).pack(pady=10)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_cli = tk.Listbox(list_frame, height=8, width=60, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb_cli.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_cli.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Documento:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Dirección:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Correo:").grid(row=4, column=0, padx=5, pady=5, sticky="e")

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
        ctk.CTkButton(btn_frame, text="Nuevo", command=self._nuevo_cliente, width=100).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Guardar", command=self._guardar_cliente, width=120, fg_color="#3A86FF", hover_color="#265DAB").grid(row=0, column=1, padx=5)
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
        self.lb_cli.delete(0, 'end')
        rows = self.db_manager.execute_query("SELECT id_cliente, nombre, correo FROM Cliente")
        if rows:
            for r in rows:
                self.lb_cli.insert('end', f"{r[0]} | {r[1]} | {r[2]}")

    def _seleccionar_cliente(self, event=None):
        sel = self.lb_cli.curselection()
        if not sel:
            return
        self._cliente_sel = int(self.lb_cli.get(sel[0]).split('|')[0].strip())
        placeholder = '%s' if not self.db_manager.offline else '?'
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = {placeholder}",
            (self._cliente_sel,),
        )
        if row:
            doc, nom, tel, dir_, cor = row[0]
            self.ent_doc_c.delete(0, 'end'); self.ent_doc_c.insert(0, doc or '')
            self.ent_nom_c.delete(0, 'end'); self.ent_nom_c.insert(0, nom or '')
            self.ent_tel_c.delete(0, 'end'); self.ent_tel_c.insert(0, tel or '')
            self.ent_dir_c.delete(0, 'end'); self.ent_dir_c.insert(0, dir_ or '')
            self.ent_cor_c.delete(0, 'end'); self.ent_cor_c.insert(0, cor or '')

    def _nuevo_cliente(self):
        self._cliente_sel = None
        for e in [self.ent_doc_c, self.ent_nom_c, self.ent_tel_c, self.ent_dir_c, self.ent_cor_c]:
            e.delete(0, 'end')

    def _guardar_cliente(self):
        from tkinter import messagebox

        doc = self.ent_doc_c.get().strip()
        nom = self.ent_nom_c.get().strip()
        tel = self.ent_tel_c.get().strip()
        dir_ = self.ent_dir_c.get().strip()
        cor = self.ent_cor_c.get().strip()

        if not doc or not nom or not cor:
            messagebox.showwarning("Aviso", "Documento, nombre y correo son obligatorios")
            return

        placeholder = '%s' if not self.db_manager.offline else '?'
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

        placeholder = '%s' if not self.db_manager.offline else '?'
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
                fetch=False,
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
        ctk.CTkLabel(frame, text="Reportes de ventas", font=("Arial", 18, "bold")).pack(pady=10)

        controls = ctk.CTkFrame(frame)
        controls.pack(pady=10)
        mes_var = tk.IntVar(value=datetime.now().month)
        anio_var = tk.IntVar(value=datetime.now().year)
        tk.Label(controls, text="Mes:").grid(row=0, column=0, padx=2)
        tk.Spinbox(controls, from_=1, to=12, width=4, textvariable=mes_var).grid(row=0, column=1)
        tk.Label(controls, text="Año:").grid(row=0, column=2, padx=2)
        tk.Spinbox(controls, from_=2020, to=2100, width=6, textvariable=anio_var).grid(row=0, column=3)
        ctk.CTkButton(controls, text="Ventas por sede", command=lambda: mostrar("sucursal")).grid(row=0, column=4, padx=4)
        ctk.CTkButton(controls, text="Ventas por vendedor", command=lambda: mostrar("vendedor")).grid(row=0, column=5, padx=4)

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
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Consulta SQL:").pack(pady=(10, 5))
        query_entry = ctk.CTkTextbox(frame, height=80)
        query_entry.pack(fill="x", padx=5)

        ctk.CTkLabel(frame, text="Resultado:").pack(pady=(10, 5))
        result_box = ctk.CTkTextbox(frame)
        result_box.pack(expand=True, fill="both", padx=5, pady=(0, 10))

        def ejecutar():
            query = query_entry.get("1.0", "end").strip()
            if not query:
                messagebox.showwarning("Error", "Ingrese una consulta SQL")
                return
            if not puede_ejecutar_sql_libre(self.user_data.get('rol')):
                messagebox.showwarning("Error", "No autorizado")
                return
            result_box.delete("1.0", "end")
            try:
                rows = self.db_manager.execute_query(query)
                if rows is None:
                    result_box.insert("end", "Error al ejecutar la consulta")
                elif len(rows) == 0:
                    result_box.insert("end", "Consulta ejecutada correctamente")
                else:
                    for r in rows:
                        result_box.insert("end", f"{r}\n")
            except Exception as exc:
                result_box.insert("end", str(exc))

        ctk.CTkButton(
            frame,
            text="Ejecutar",
            command=ejecutar,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_COLOR_DARK,
        ).pack(pady=5)


class AdminView(BaseCTKView):
    """Vista CTk para administradores con visión general de personal y clientes."""

    def _welcome_message(self):
        return f"Bienvenido administrador, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        topbar = ctk.CTkFrame(self, fg_color=BG_DARK)
        topbar.pack(fill="x", pady=(0,5))
        self._status_label = ctk.CTkLabel(topbar, text="", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        self._status_label.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(topbar, text="Cerrar sesión", command=self.logout,
                      fg_color=PRIMARY_COLOR, hover_color=PRIMARY_COLOR_DARK,
                      width=140, height=32).pack(side="right", padx=10, pady=8)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color=TEXT_COLOR,
                     font=("Arial", 20)).pack(pady=30)

        self.tab_personal = self.tabview.add("Personal")
        self._build_tab_personal(self.tabview.tab("Personal"))

        self.tab_clientes = self.tabview.add("Clientes")
        self._build_tab_clientes(self.tabview.tab("Clientes"))


        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

        if puede_ejecutar_sql_libre(self.user_data.get('rol')):
            self.tab_sql_libre = self.tabview.add("SQL Libre")
            self._build_tab_sql_libre(self.tabview.tab("SQL Libre"))

    def _build_tab_personal(self, parent):
        import tkinter as tk

        self._emp_sel = None
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Gestión de empleados", font=("Arial", 18, "bold")).pack(pady=10)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_staff = tk.Listbox(list_frame, height=8, width=60, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb_staff.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_staff.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Documento:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Correo:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Cargo:").grid(row=4, column=0, padx=5, pady=5, sticky="e")

        self.ent_doc_e = ctk.CTkEntry(form, width=150)
        self.ent_nom_e = ctk.CTkEntry(form, width=150)
        self.ent_tel_e = ctk.CTkEntry(form, width=150)
        self.ent_cor_e = ctk.CTkEntry(form, width=150)
        cargos_rows = self.db_manager.execute_query("SELECT descripcion FROM Tipo_empleado") or []
        cargos = [c[0].capitalize() for c in cargos_rows] or [
            "Administrador",
            "Gerente",
            "Ventas",
            "Caja",
            "Mantenimiento",
        ]
        self._cargos = cargos
        self.cargo_var = ctk.StringVar(value=cargos[0])
        self.ent_cargo_e = ctk.CTkOptionMenu(form, variable=self.cargo_var, values=cargos, width=150)

        self.ent_doc_e.grid(row=0, column=1, padx=5, pady=5)
        self.ent_nom_e.grid(row=1, column=1, padx=5, pady=5)
        self.ent_tel_e.grid(row=2, column=1, padx=5, pady=5)
        self.ent_cor_e.grid(row=3, column=1, padx=5, pady=5)
        self.ent_cargo_e.grid(row=4, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Nuevo", command=self._nuevo_empleado, width=100).grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._guardar_empleado,
            width=120,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).grid(row=0, column=1, padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=self._eliminar_empleado,
            width=120,
            fg_color="#F44336",
            hover_color="#B71C1C",
        ).grid(row=0, column=2, padx=5)

        self.lb_staff.bind("<<ListboxSelect>>", self._seleccionar_empleado)
        self._cargar_staff()

    def _cargar_staff(self):
        self.lb_staff.delete(0, 'end')
        rows = self.db_manager.execute_query("SELECT id_empleado, nombre, cargo FROM Empleado")
        if rows:
            for r in rows:
                self.lb_staff.insert('end', f"{r[0]} | {r[1]} | {r[2]}")

    def _seleccionar_empleado(self, event=None):
        sel = self.lb_staff.curselection()
        if not sel:
            return
        self._emp_sel = int(self.lb_staff.get(sel[0]).split('|')[0].strip())
        placeholder = '%s' if not self.db_manager.offline else '?'
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, correo, cargo FROM Empleado WHERE id_empleado = {placeholder}",
            (self._emp_sel,),
        )
        if row:
            doc, nom, tel, cor, cargo = row[0]
            self.ent_doc_e.delete(0, 'end'); self.ent_doc_e.insert(0, doc or '')
            self.ent_nom_e.delete(0, 'end'); self.ent_nom_e.insert(0, nom or '')
            self.ent_tel_e.delete(0, 'end'); self.ent_tel_e.insert(0, tel or '')
            self.ent_cor_e.delete(0, 'end'); self.ent_cor_e.insert(0, cor or '')
            self.cargo_var.set(cargo or (self._cargos[0] if self._cargos else ''))

    def _nuevo_empleado(self):
        self._emp_sel = None
        for e in [self.ent_doc_e, self.ent_nom_e, self.ent_tel_e, self.ent_cor_e]:
            e.delete(0, 'end')
        if self._cargos:
            self.cargo_var.set(self._cargos[0])

    def _guardar_empleado(self):
        from tkinter import messagebox

        doc = self.ent_doc_e.get().strip()
        nom = self.ent_nom_e.get().strip()
        tel = self.ent_tel_e.get().strip()
        cor = self.ent_cor_e.get().strip()
        cargo = self.cargo_var.get().strip()

        if not doc or not nom or not cor or not cargo:
            messagebox.showwarning("Aviso", "Documento, nombre, correo y cargo son obligatorios")
            return

        if cargo.lower() == 'gerente' and not puede_gestionar_gerentes(self.user_data.get('rol')):
            messagebox.showwarning(
                "Aviso",
                "No tiene permiso para gestionar empleados con cargo 'gerente'",
            )
            return

        if not verificar_permiso_creacion_empleado(cargo, self.user_data.get('rol')):
            messagebox.showwarning("Aviso", "No tiene permiso para crear/editar este empleado")
            return

        placeholder = '%s' if not self.db_manager.offline else '?'
        try:
            if self._emp_sel:
                q = (
                    f"UPDATE Empleado SET documento={placeholder}, nombre={placeholder}, "
                    f"telefono={placeholder}, correo={placeholder}, cargo={placeholder} WHERE id_empleado={placeholder}"
                )
                params = (doc, nom, tel, cor, cargo, self._emp_sel)
            else:
                q = (
                    f"INSERT INTO Empleado (documento, nombre, telefono, correo, cargo) "
                    f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
                )
                params = (doc, nom, tel, cor, cargo)
            self.db_manager.execute_query(q, params, fetch=False)
            messagebox.showinfo("Éxito", "Empleado guardado correctamente")
            self._nuevo_empleado()
            self._cargar_staff()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _eliminar_empleado(self):
        from tkinter import messagebox

        if not self._emp_sel:
            messagebox.showwarning("Aviso", "Seleccione un empleado")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar empleado seleccionado?"):
            return

        placeholder = '%s' if not self.db_manager.offline else '?'
        try:
            # Eliminar reservas, alquileres y abonos ligados al empleado para
            # replicar un borrado en cascada multiplataforma
            self.db_manager.execute_query(
                f"DELETE FROM Abono_reserva WHERE id_reserva IN ("
                f"SELECT id_reserva FROM Reserva_alquiler WHERE id_empleado = {placeholder})",
                (self._emp_sel,),
                fetch=False,
            )
            self.db_manager.execute_query(
                f"DELETE FROM Reserva_alquiler WHERE id_empleado = {placeholder}",
                (self._emp_sel,),
                fetch=False,
            )
            self.db_manager.execute_query(
                f"DELETE FROM Alquiler WHERE id_empleado = {placeholder}",
                (self._emp_sel,),
                fetch=False,
            )
            self.db_manager.execute_query(
                f"DELETE FROM Usuario WHERE id_empleado = {placeholder}",
                (self._emp_sel,),
                fetch=False,
            )
            self.db_manager.execute_query(
                f"DELETE FROM Empleado WHERE id_empleado = {placeholder}",
                (self._emp_sel,),
                fetch=False,
            )
            messagebox.showinfo("Éxito", "Empleado eliminado correctamente")
            self._nuevo_empleado()
            self._cargar_staff()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _build_tab_clientes(self, parent):
        import tkinter as tk
        from tkinter import messagebox

        self._cliente_sel = None

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Gestión de clientes", font=("Arial", 18, "bold")).pack(pady=10)

        list_frame = ctk.CTkFrame(frame, fg_color="#E3F2FD")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.lb_cli = tk.Listbox(list_frame, height=8, width=60, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb_cli.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_cli.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Documento:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Dirección:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(form, text="Correo:").grid(row=4, column=0, padx=5, pady=5, sticky="e")

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
        ctk.CTkButton(btn_frame, text="Nuevo", command=self._nuevo_cliente, width=100).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Guardar", command=self._guardar_cliente, width=120, fg_color="#3A86FF", hover_color="#265DAB").grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Eliminar", command=self._eliminar_cliente, width=120, fg_color="#F44336", hover_color="#B71C1C").grid(row=0, column=2, padx=5)

        self.lb_cli.bind("<<ListboxSelect>>", self._seleccionar_cliente)
        self._cargar_clientes()

    def _cargar_clientes(self):
        self.lb_cli.delete(0, 'end')
        rows = self.db_manager.execute_query("SELECT id_cliente, nombre, correo FROM Cliente")
        if rows:
            for r in rows:
                self.lb_cli.insert('end', f"{r[0]} | {r[1]} | {r[2]}")

    def _seleccionar_cliente(self, event=None):
        sel = self.lb_cli.curselection()
        if not sel:
            return
        self._cliente_sel = int(self.lb_cli.get(sel[0]).split('|')[0].strip())
        placeholder = '%s' if not self.db_manager.offline else '?'
        row = self.db_manager.execute_query(
            f"SELECT documento, nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = {placeholder}",
            (self._cliente_sel,),
        )
        if row:
            doc, nom, tel, dir_, cor = row[0]
            self.ent_doc_c.delete(0, 'end'); self.ent_doc_c.insert(0, doc or '')
            self.ent_nom_c.delete(0, 'end'); self.ent_nom_c.insert(0, nom or '')
            self.ent_tel_c.delete(0, 'end'); self.ent_tel_c.insert(0, tel or '')
            self.ent_dir_c.delete(0, 'end'); self.ent_dir_c.insert(0, dir_ or '')
            self.ent_cor_c.delete(0, 'end'); self.ent_cor_c.insert(0, cor or '')

    def _nuevo_cliente(self):
        self._cliente_sel = None
        for e in [self.ent_doc_c, self.ent_nom_c, self.ent_tel_c, self.ent_dir_c, self.ent_cor_c]:
            e.delete(0, 'end')

    def _guardar_cliente(self):
        from tkinter import messagebox

        doc = self.ent_doc_c.get().strip()
        nom = self.ent_nom_c.get().strip()
        tel = self.ent_tel_c.get().strip()
        dir_ = self.ent_dir_c.get().strip()
        cor = self.ent_cor_c.get().strip()

        if not doc or not nom or not cor:
            messagebox.showwarning("Aviso", "Documento, nombre y correo son obligatorios")
            return

        placeholder = '%s' if not self.db_manager.offline else '?'
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

        placeholder = '%s' if not self.db_manager.offline else '?'
        try:
            # Borrado manual de pagos, reservas y alquileres asociados para
            # simular la eliminación en cascada en MySQL y SQLite
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
                fetch=False,
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
        ctk.CTkLabel(frame, text="Reportes de ventas", font=("Arial", 18, "bold")).pack(pady=10)

        controls = ctk.CTkFrame(frame)
        controls.pack(pady=10)
        mes_var = tk.IntVar(value=datetime.now().month)
        anio_var = tk.IntVar(value=datetime.now().year)
        tk.Label(controls, text="Mes:").grid(row=0, column=0, padx=2)
        tk.Spinbox(controls, from_=1, to=12, width=4, textvariable=mes_var).grid(row=0, column=1)
        tk.Label(controls, text="Año:").grid(row=0, column=2, padx=2)
        tk.Spinbox(controls, from_=2020, to=2100, width=6, textvariable=anio_var).grid(row=0, column=3)
        ctk.CTkButton(controls, text="Ventas por sede", command=lambda: mostrar("sucursal")).grid(row=0, column=4, padx=4)
        ctk.CTkButton(controls, text="Ventas por vendedor", command=lambda: mostrar("vendedor")).grid(row=0, column=5, padx=4)

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
        from tkinter import messagebox

        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Consulta SQL:").pack(pady=(10, 5))
        query_entry = ctk.CTkTextbox(frame, height=80)
        query_entry.pack(fill="x", padx=5)

        ctk.CTkLabel(frame, text="Resultado:").pack(pady=(10, 5))
        result_box = ctk.CTkTextbox(frame)
        result_box.pack(expand=True, fill="both", padx=5, pady=(0, 10))

        def ejecutar():
            query = query_entry.get("1.0", "end").strip()
            if not query:
                messagebox.showwarning("Error", "Ingrese una consulta SQL")
                return
            if not puede_ejecutar_sql_libre(self.user_data.get('rol')):
                messagebox.showwarning("Error", "No autorizado")
                return
            result_box.delete("1.0", "end")
            try:
                rows = self.db_manager.execute_query(query)
                if rows is None:
                    result_box.insert("end", "Error al ejecutar la consulta")
                elif len(rows) == 0:
                    result_box.insert("end", "Consulta ejecutada correctamente")
                else:
                    for r in rows:
                        result_box.insert("end", f"{r}\n")
            except Exception as exc:
                result_box.insert("end", str(exc))

        ctk.CTkButton(
            frame,
            text="Ejecutar",
            command=ejecutar,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_COLOR_DARK,
        ).pack(pady=5)

