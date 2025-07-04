import customtkinter as ctk
import threading
import time
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre,
)
from ..styles import BG_DARK, TEXT_COLOR, PRIMARY_COLOR, PRIMARY_COLOR_DARK


class BaseCTKView(ctk.CTk):
    def __init__(self, user_data, db_manager, on_logout=None):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self._status_label1 = None
        self._status_label2 = None
        self._stop_status = False
        self.geometry("600x400")
        self.configure(bg=BG_DARK)
        self._build_ui()
        self._update_status_labels()
        self._start_status_updater()
        self.after(100, self._maximize_and_focus)

    def _maximize_and_focus(self):
        self.after(100, lambda: self.wm_state("zoomed"))
        self.focus_force()

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
        if hasattr(self, "_build_tab_perfil"):
            self.tab_perfil = self.tabview.add("Editar perfil")
            self._build_tab_perfil(self.tabview.tab("Editar perfil"))
        self._update_status_labels()

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
        ctk.CTkButton(
            parent,
            text="Cambiar",
            command=self._cambiar_contrasena,
            fg_color="#3A86FF",
            hover_color="#265DAB",
        ).pack(pady=20)

    def _cambiar_contrasena(self):
        from tkinter import messagebox

        actual = self.input_actual.get()
        nueva = self.input_nueva.get()
        confirmar = self.input_confirmar.get()
        if not actual or not nueva or not confirmar:
            messagebox.showwarning("Error", "Complete todos los campos")
            return
        if nueva != confirmar:
            messagebox.showwarning(
                "Error", "La nueva contraseña y la confirmación no coinciden"
            )
            return
        from src.auth import AuthManager

        auth = AuthManager(self.db_manager)
        usuario = self.user_data.get("usuario")
        resultado = auth.cambiar_contrasena(usuario, actual, nueva)
        if resultado is True:
            messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
            self.input_actual.delete(0, "end")
            self.input_nueva.delete(0, "end")
            self.input_confirmar.delete(0, "end")
        else:
            messagebox.showwarning("Error", str(resultado))

    def _welcome_message(self):
        return f"Bienvenido, {self.user_data.get('usuario', '')}"

    def _update_status_labels(self):
        online1 = getattr(self.db_manager, 'is_remote1_active', lambda: getattr(self.db_manager, 'remote1_active', False))()
        online2 = getattr(self.db_manager, 'is_remote2_active', lambda: getattr(self.db_manager, 'remote2_active', False))()
        emoji1 = "🟢" if online1 else "🔴"
        emoji2 = "🟢" if online2 else "🔴"
        estado1 = "ONLINE" if online1 else "OFFLINE"
        estado2 = "ONLINE" if online2 else "OFFLINE"
        if self._status_label1 is not None:
            self._status_label1.configure(text=f"{emoji1} R1: {estado1}")
        if self._status_label2 is not None:
            self._status_label2.configure(text=f"{emoji2} R2: {estado2}")

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


