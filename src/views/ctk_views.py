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
        frame = ctk.CTkFrame(self.tabview.tab("Mis reservas"))
        frame.grid(row=0, column=0, sticky="ew")
        self._status_label = ctk.CTkLabel(frame, text="", font=("Arial", 15))
        self._status_label.grid(row=0, column=0, pady=(20, 10))
        ctk.CTkLabel(frame, text=self._welcome_message(), text_color="#F5F6FA", font=("Arial", 20)).grid(row=1, column=0, pady=30)
        # Botón cerrar sesión al final, centrado
        ctk.CTkButton(frame, text="Cerrar sesión", command=self.logout, fg_color="#3A86FF", hover_color="#265DAB", width=180, height=38).grid(row=99, column=0, pady=(30, 20), sticky="s")
        # Pestaña: Vehículos disponibles
        self.tab_vehiculos = self.tabview.add("Vehículos disponibles")
        self._build_tab_vehiculos(self.tabview.tab("Vehículos disponibles"))
        # Pestaña: Editar perfil
        self.tab_perfil = self.tabview.add("Editar perfil")
        self._build_tab_perfil(self.tabview.tab("Editar perfil"))
        # Pestaña: Abonar reserva
        self.tab_abonar = self.tabview.add("Abonar reserva")
        self._build_tab_abonar(self.tabview.tab("Abonar reserva"))
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = self.tabview.add("Cambiar contraseña")
        self._build_cambiar_contrasena_tab(self.tabview.tab("Cambiar contraseña"))

    def _build_tab_mis_reservas(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        id_cliente = self.user_data.get('id_cliente')
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Mis reservas", font=("Arial", 18)).pack(pady=10)
        self.reservas_listbox = tk.Listbox(frame, height=10, width=80)
        self.reservas_listbox.pack(pady=10)
        self._cargar_reservas_cliente(id_cliente)
        # Botones para crear y cancelar reserva
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Nueva reserva", command=self._abrir_nueva_reserva).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar reserva", command=self._cancelar_reserva).pack(side="left", padx=10)

    def _cargar_reservas_cliente(self, id_cliente):
        self.reservas_listbox.delete(0, 'end')
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = f"SELECT id_reserva, fecha_hora_salida, fecha_hora_entrada, id_vehiculo FROM Reserva WHERE id_cliente = {placeholder}"
        reservas = self.db_manager.execute_query(query, (id_cliente,))
        if reservas:
            for r in reservas:
                self.reservas_listbox.insert('end', f"ID: {r[0]} | Vehículo: {r[3]} | Salida: {r[1]} | Entrada: {r[2]}")
        else:
            self.reservas_listbox.insert('end', "No tienes reservas registradas.")

    def _abrir_nueva_reserva(self):
        import tkinter as tk
        from tkinter import messagebox
        win = tk.Toplevel(self)
        win.title("Nueva reserva")
        win.geometry("400x300")
        ctk.CTkLabel(win, text="Placa del vehículo:").pack(pady=5)
        entry_vehiculo = ctk.CTkEntry(win)
        entry_vehiculo.pack(pady=5)
        ctk.CTkLabel(win, text="Fecha salida (YYYY-MM-DD):").pack(pady=5)
        entry_salida = ctk.CTkEntry(win)
        entry_salida.pack(pady=5)
        ctk.CTkLabel(win, text="Fecha entrada (YYYY-MM-DD):").pack(pady=5)
        entry_entrada = ctk.CTkEntry(win)
        entry_entrada.pack(pady=5)
        def guardar():
            placa = entry_vehiculo.get().strip()
            salida = entry_salida.get().strip()
            entrada = entry_entrada.get().strip()
            if not placa or not salida or not entrada:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            id_cliente = self.user_data.get('id_cliente')
            placeholder = '%s' if not self.db_manager.offline else '?'
            query = f"INSERT INTO Reserva (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
            try:
                self.db_manager.execute_query(query, (salida, entrada, placa, id_cliente), fetch=False)
                messagebox.showinfo("Éxito", "Reserva creada correctamente")
                win.destroy()
                self._cargar_reservas_cliente(id_cliente)
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo crear la reserva: {exc}")
        ctk.CTkButton(win, text="Guardar", command=guardar).pack(pady=15)

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
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = f"DELETE FROM Reserva WHERE id_reserva = {placeholder} AND id_cliente = {placeholder}"
        try:
            self.db_manager.execute_query(query, (id_reserva, self.user_data.get('id_cliente')), fetch=False)
            messagebox.showinfo("Éxito", "Reserva cancelada")
            self._cargar_reservas_cliente(self.user_data.get('id_cliente'))
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo cancelar la reserva: {exc}")

    def _build_tab_vehiculos(self, parent):
        import tkinter as tk
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 16)).pack(pady=10)
        # Listar vehículos disponibles
        query = "SELECT placa, modelo, id_marca FROM Vehiculo WHERE id_estado_vehiculo = 1"
        vehiculos = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if vehiculos:
            for v in vehiculos:
                listbox.insert('end', f"Placa: {v[0]} | Modelo: {v[1]} | Marca: {v[2]}")
        else:
            listbox.insert('end', "No hay vehículos disponibles.")
        # Botón para reservar vehículo seleccionado
        def reservar():
            sel = listbox.curselection()
            if not sel:
                tk.messagebox.showwarning("Aviso", "Seleccione un vehículo para reservar")
                return
            texto = listbox.get(sel[0])
            placa = texto.split("Placa: ")[1].split("|")[0].strip()
            # Abrir ventana de reserva con placa prellenada
            self._abrir_nueva_reserva_placa(placa)
        ctk.CTkButton(frame, text="Reservar seleccionado", command=reservar).pack(pady=5)

    def _abrir_nueva_reserva_placa(self, placa):
        import tkinter as tk
        from tkinter import messagebox
        win = tk.Toplevel(self)
        win.title("Nueva reserva")
        win.geometry("400x250")
        ctk.CTkLabel(win, text=f"Placa: {placa}").pack(pady=5)
        ctk.CTkLabel(win, text="Fecha salida (YYYY-MM-DD):").pack(pady=5)
        entry_salida = ctk.CTkEntry(win)
        entry_salida.pack(pady=5)
        ctk.CTkLabel(win, text="Fecha entrada (YYYY-MM-DD):").pack(pady=5)
        entry_entrada = ctk.CTkEntry(win)
        entry_entrada.pack(pady=5)
        def guardar():
            salida = entry_salida.get().strip()
            entrada = entry_entrada.get().strip()
            if not salida or not entrada:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            id_cliente = self.user_data.get('id_cliente')
            placeholder = '%s' if not self.db_manager.offline else '?'
            query = f"INSERT INTO Reserva (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
            try:
                self.db_manager.execute_query(query, (salida, entrada, placa, id_cliente), fetch=False)
                messagebox.showinfo("Éxito", "Reserva creada correctamente")
                win.destroy()
                self._cargar_reservas_cliente(id_cliente)
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo crear la reserva: {exc}")
        ctk.CTkButton(win, text="Guardar", command=guardar).pack(pady=15)

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

    def _build_tab_abonar(self, parent):
        import tkinter as tk
        from tkinter import messagebox
        id_cliente = self.user_data.get('id_cliente')
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Reservas pendientes de abono", font=("Arial", 16)).pack(pady=10)
        # Listar reservas pendientes (ejemplo: aquellas con saldo > 0)
        placeholder = '%s' if not self.db_manager.offline else '?'
        query = f"SELECT id_reserva, fecha_hora_salida, fecha_hora_entrada, saldo_pendiente FROM Reserva WHERE id_cliente = {placeholder} AND saldo_pendiente > 0"
        reservas = self.db_manager.execute_query(query, (id_cliente,))
        self.abono_listbox = tk.Listbox(frame, height=10, width=80)
        self.abono_listbox.pack(pady=10)
        if reservas:
            for r in reservas:
                self.abono_listbox.insert('end', f"ID: {r[0]} | Salida: {r[1]} | Entrada: {r[2]} | Saldo pendiente: {r[3]}")
        else:
            self.abono_listbox.insert('end', "No tienes reservas pendientes de abono.")
        # Campo para monto a abonar
        ctk.CTkLabel(frame, text="Monto a abonar:").pack(pady=5)
        self.input_abono = ctk.CTkEntry(frame)
        self.input_abono.pack(pady=5)
        def abonar():
            sel = self.abono_listbox.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Seleccione una reserva para abonar")
                return
            texto = self.abono_listbox.get(sel[0])
            if "ID: " not in texto:
                messagebox.showwarning("Aviso", "No hay reserva seleccionada")
                return
            id_reserva = texto.split("ID: ")[1].split("|")[0].strip()
            try:
                monto = float(self.input_abono.get())
                if monto <= 0:
                    raise ValueError
            except Exception:
                messagebox.showwarning("Error", "Ingrese un monto válido")
                return
            # Actualizar saldo pendiente
            placeholder = '%s' if not self.db_manager.offline else '?'
            # Obtener saldo actual
            q_saldo = f"SELECT saldo_pendiente FROM Reserva WHERE id_reserva = {placeholder}"
            row = self.db_manager.execute_query(q_saldo, (id_reserva,))
            if not row:
                messagebox.showerror("Error", "No se encontró la reserva")
                return
            saldo_actual = float(row[0][0])
            if monto > saldo_actual:
                messagebox.showwarning("Error", "El monto excede el saldo pendiente")
                return
            nuevo_saldo = saldo_actual - monto
            q_update = f"UPDATE Reserva SET saldo_pendiente = {placeholder} WHERE id_reserva = {placeholder}"
            try:
                self.db_manager.execute_query(q_update, (nuevo_saldo, id_reserva), fetch=False)
                messagebox.showinfo("Éxito", "Abono realizado correctamente")
                self.input_abono.delete(0, 'end')
                # Recargar lista
                self.abono_listbox.delete(0, 'end')
                reservas = self.db_manager.execute_query(query, (id_cliente,))
                if reservas:
                    for r in reservas:
                        self.abono_listbox.insert('end', f"ID: {r[0]} | Salida: {r[1]} | Entrada: {r[2]} | Saldo pendiente: {r[3]}")
                else:
                    self.abono_listbox.insert('end', "No tienes reservas pendientes de abono.")
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo realizar el abono: {exc}")
        ctk.CTkButton(frame, text="Abonar", command=abonar).pack(pady=10)

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
        # Pestaña principal: Bienvenida y cerrar sesión
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
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña principal: Bienvenida y cerrar sesión
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
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña principal: Bienvenida y cerrar sesión
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
        listbox = tk.Listbox(frame, height=10, width=60)
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
        query = "SELECT placa, modelo, id_marca FROM Vehiculo WHERE id_estado_vehiculo = 1"
        vehiculos = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if vehiculos:
            for v in vehiculos:
                listbox.insert('end', f"Placa: {v[0]} | Modelo: {v[1]} | Marca: {v[2]}")
        else:
            listbox.insert('end', "No hay vehículos disponibles.")

class EmpleadoVentasView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de ventas, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")
        # Pestaña principal: Bienvenida y cerrar sesión
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
        listbox = tk.Listbox(frame, height=10, width=60)
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
        query = "SELECT placa, modelo, id_marca FROM Vehiculo WHERE id_estado_vehiculo = 1"
        vehiculos = self.db_manager.execute_query(query)
        listbox = tk.Listbox(frame, height=10, width=60)
        listbox.pack(pady=10)
        if vehiculos:
            for v in vehiculos:
                listbox.insert('end', f"Placa: {v[0]} | Modelo: {v[1]} | Marca: {v[2]}")
        else:
            listbox.insert('end', "No hay vehículos disponibles.")

class EmpleadoCajaView(BaseCTKView):
    def _welcome_message(self):
        return f"Bienvenido empleado de caja, {self.user_data.get('usuario', '')}"

    def _build_ui(self):
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
        listbox = tk.Listbox(frame, height=10, width=60)
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