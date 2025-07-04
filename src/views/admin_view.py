import customtkinter as ctk
from .base_view import BaseCTKView
from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre,
)
from ..styles import BG_DARK, TEXT_COLOR, PRIMARY_COLOR, PRIMARY_COLOR_DARK

class AdminView(BaseCTKView):
    """Vista CTk para administradores con visión general de personal y clientes."""
    def _welcome_message(self):
        return f"Bienvenido administrador, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        topbar = ctk.CTkFrame(self, fg_color="#222831")
        topbar.pack(fill="x", pady=(0, 5))
        self._status_label1 = ctk.CTkLabel(
            topbar, text="", font=("Arial", 12, "bold"), text_color="#FFFFFF"
        )
        self._status_label1.pack(side="left", padx=10, pady=8)
        self._status_label2 = ctk.CTkLabel(
            topbar, text="", font=("Arial", 12, "bold"), text_color="#FFFFFF"
        )
        self._status_label2.pack(side="left", padx=10, pady=8)
        ctk.CTkButton(
            topbar,
            text="Cerrar sesión",
            command=self.logout,
            fg_color="#3A86FF",
            hover_color="#265DAB",
            width=140,
            height=32,
        ).pack(side="right", padx=10, pady=8)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        self.tab_principal = self.tabview.add("Principal")
        frame = ctk.CTkFrame(self.tabview.tab("Principal"))
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(
            frame,
            text=self._welcome_message(),
            text_color="#222831",
            font=("Arial", 20),
        ).pack(pady=30)
