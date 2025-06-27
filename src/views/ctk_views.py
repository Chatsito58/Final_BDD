import customtkinter as ctk

class BaseCTKView(ctk.CTk):
    def __init__(self, user_data, db_manager, on_logout=None):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self.geometry("400x300")
        self.configure(bg="#18191A")
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 18)).pack(pady=30)
        ctk.CTkButton(self, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB").pack(pady=20)

    def _welcome_message(self):
        return f"Bienvenido, {self.user_data.get('usuario', '')}"

    def logout(self):
        self.destroy()
        if self.on_logout:
            self.on_logout()

class ClienteView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido cliente, {self.user_data.get('usuario', '')}"

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

class AdminView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido administrador, {self.user_data.get('usuario', '')}"

class EmpleadoView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado, {self.user_data.get('usuario', '')}"

class EmpleadoVentasView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de ventas, {self.user_data.get('usuario', '')}"

class EmpleadoMantenimientoView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de mantenimiento, {self.user_data.get('usuario', '')}"

class EmpleadoCajaView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de caja, {self.user_data.get('usuario', '')}" 