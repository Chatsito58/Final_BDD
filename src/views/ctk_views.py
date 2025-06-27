import customtkinter as ctk
import threading
import time
from ..services.roles import (
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
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña principal
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"), fg_color="#18191A")
        frame.pack(expand=True)
        self._status_label = ctk.CTkLabel(frame, text="", font=("Arial", 15))
        self._status_label.pack(pady=(20, 10))
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).pack(pady=20)
        # Pestaña cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

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
        from ..auth import AuthManager
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

    def _update_status_label(self):
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
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña: Mis reservas
        self.tab_reservas = self.tabview.add("Mis reservas")
        ctk.CTkLabel(self.tabview.tab("Mis reservas"), text="Ver y gestionar mis reservas").pack(pady=10)
        # Pestaña: Vehículos disponibles
        self.tab_vehiculos = self.tabview.add("Vehículos disponibles")
        ctk.CTkLabel(self.tabview.tab("Vehículos disponibles"), text="Consultar vehículos disponibles").pack(pady=10)
        # Pestaña: Editar perfil
        self.tab_perfil = self.tabview.add("Editar perfil")
        ctk.CTkLabel(self.tabview.tab("Editar perfil"), text="Editar mis datos personales").pack(pady=10)
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

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
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
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

class AdminView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido administrador, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
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

class EmpleadoView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado, {self.user_data.get('usuario', '')}"

class EmpleadoVentasView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de ventas, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña: Gestionar Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        ctk.CTkLabel(self.tabview.tab("Clientes"), text="Gestión de clientes (crear, editar, ver)").pack(pady=10)
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        ctk.CTkLabel(self.tabview.tab("Reservas"), text="Gestión de reservas").pack(pady=10)
        # Pestaña: Vehículos
        self.tab_vehiculos = self.tabview.add("Vehículos")
        ctk.CTkLabel(self.tabview.tab("Vehículos"), text="Consulta de vehículos").pack(pady=10)
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

class EmpleadoCajaView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de caja, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña: Pagos
        self.tab_pagos = self.tabview.add("Pagos")
        ctk.CTkLabel(self.tabview.tab("Pagos"), text="Procesar pagos").pack(pady=10)
        # Pestaña: Reservas
        self.tab_reservas = self.tabview.add("Reservas")
        ctk.CTkLabel(self.tabview.tab("Reservas"), text="Consultar reservas").pack(pady=10)
        # Pestaña: Clientes
        self.tab_clientes = self.tabview.add("Clientes")
        ctk.CTkLabel(self.tabview.tab("Clientes"), text="Consultar clientes").pack(pady=10)
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

class EmpleadoMantenimientoView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de mantenimiento, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña: Vehículos asignados
        self.tab_vehiculos = self.tabview.add("Vehículos asignados")
        ctk.CTkLabel(self.tabview.tab("Vehículos asignados"), text="Ver vehículos asignados").pack(pady=10)
        # Pestaña: Reportar mantenimiento
        self.tab_reportar = self.tabview.add("Reportar mantenimiento")
        ctk.CTkLabel(self.tabview.tab("Reportar mantenimiento"), text="Reportar mantenimiento").pack(pady=10)
        # Pestaña: Historial vehículos
        self.tab_historial = self.tabview.add("Historial vehículos")
        ctk.CTkLabel(self.tabview.tab("Historial vehículos"), text="Consultar historial de vehículos").pack(pady=10)
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña")) 