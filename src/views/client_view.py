import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QDialog, QVBoxLayout, QDateTimeEdit, QPushButton, QMenu
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDateTime, QTimer, Qt
from datetime import datetime
import hashlib

class ClienteView(QMainWindow):
    def __init__(self, user_data, db_manager, auth_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.on_logout = on_logout
        self._selected_reserva_id = None

        ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'client_view.ui')
        loadUi(ui_path, self)

        self._setup_ui()
        self._setup_reservas_tab()
        self._setup_crear_reserva_tab()
        self._setup_abonos_tab()
        self._setup_perfil_tab()
        self._setup_cambiar_contrasena_tab()

        # Inicializar seguros_data para evitar AttributeError
        self.seguros_data = []

    def _setup_ui(self):
        self.logout_button.clicked.connect(self.logout)
        self.update_connection_status()

        # Configurar menú contextual para recargar
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        context_menu = QMenu(self)
        reload_action = context_menu.addAction("Recargar")
        action = context_menu.exec_(self.mapToGlobal(pos))
        if action == reload_action:
            self._reload_all_data()

    def _reload_all_data(self):
        # Recargar todas las pestañas relevantes
        self._cargar_reservas_cliente()
        self._cargar_vehiculos_disponibles()
        self._cargar_seguros_disponibles()
        self._cargar_reservas_pendientes_abono()
        self._cargar_datos_perfil()
        QMessageBox.information(self, "Recargar", "Datos recargados correctamente.")

    def update_connection_status(self):
        status1 = "Online" if self.db_manager.is_remote1_active() else "Offline"
        status2 = "Online" if self.db_manager.is_remote2_active() else "Offline"
        self.status_label1.setText(f"BD Remota 1: {status1}")
        self.status_label2.setText(f"BD Remota 2: {status2}")

    def logout(self):
        self.close()
        self.on_logout()

    def show(self):
        super().show()

    # --- Pestaña Mis Reservas ---
    def _setup_reservas_tab(self):
        self.editar_reserva_button.clicked.connect(self._editar_reserva)
        self.cancelar_reserva_button.clicked.connect(self._cancelar_reserva)
        self.reservas_list.itemSelectionChanged.connect(self._on_reserva_selection_changed)
        self._cargar_reservas_cliente()

    def _on_reserva_selection_changed(self):
        selected_items = self.reservas_list.selectedItems()
        if selected_items:
            item_text = selected_items[0].text()
            self._selected_reserva_id = int(item_text.split(":")[0].replace("Reserva ", "").strip())
        else:
            self._selected_reserva_id = None

    def _cargar_reservas_cliente(self):
        self.reservas_list.clear()
        id_cliente = self.user_data.get("id_cliente")
        query = (
            "SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, a.valor, ra.saldo_pendiente, ra.abono, es.descripcion "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            "LEFT JOIN Estado_reserva es ON ra.id_estado_reserva = es.id_estado "
            "WHERE a.id_cliente = %s "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        params = (id_cliente,)
        reservas = self.db_manager.execute_query(query, params)

        if not reservas:
            self.reservas_list.addItem("No tienes reservas registradas")
            return

        for r in reservas:
            id_reserva, salida, entrada, id_vehiculo, modelo, placa, valor, saldo, abono, estado = r
            self.reservas_list.addItem(f"Reserva {id_reserva}: {modelo} ({placa}) - Salida: {salida} - Estado: {estado}")

    def _cancelar_reserva(self):
        if not self._selected_reserva_id:
            QMessageBox.warning(self, "Aviso", "Seleccione una reserva para cancelar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Cancelación', 
                                     "¿Está seguro que desea cancelar esta reserva?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            # Obtener id_alquiler asociado a la reserva
            alquiler_id_query = "SELECT id_alquiler FROM Reserva_alquiler WHERE id_reserva = %s"
            alquiler_id = self.db_manager.execute_query(alquiler_id_query, (self._selected_reserva_id,))[0][0]

            # Obtener placa del vehículo asociado al alquiler
            placa_query = "SELECT id_vehiculo FROM Alquiler WHERE id_alquiler = %s"
            placa = self.db_manager.execute_query(placa_query, (alquiler_id,))[0][0]

            # Actualizar estado de la reserva a cancelada (estado 3)
            update_reserva_query = "UPDATE Reserva_alquiler SET id_estado_reserva = 3 WHERE id_reserva = %s"
            self.db_manager.update(update_reserva_query, (self._selected_reserva_id,))

            # Liberar el vehículo (estado 1: disponible)
            update_vehiculo_query = "UPDATE Vehiculo SET id_estado_vehiculo = 1 WHERE placa = %s"
            self.db_manager.update(update_vehiculo_query, (placa,))

            QMessageBox.information(self, "Éxito", "Reserva cancelada correctamente.")
            self._cargar_reservas_cliente()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cancelar la reserva: {e}")

    def _editar_reserva(self):
        if not self._selected_reserva_id:
            QMessageBox.warning(self, "Aviso", "Seleccione una reserva para editar.")
            return

        # Obtener datos de la reserva
        query = (
            "SELECT a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, a.id_seguro, a.id_descuento, a.valor "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "WHERE ra.id_reserva = %s"
        )
        reserva_data = self.db_manager.execute_query(query, (self._selected_reserva_id,))

        if not reserva_data:
            QMessageBox.critical(self, "Error", "No se encontraron datos para la reserva seleccionada.")
            return

        salida_actual, entrada_actual, id_vehiculo, id_seguro, id_descuento, valor_actual = reserva_data[0]

        # Crear un diálogo para editar fechas
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Fechas de Reserva")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()

        salida_label = QLabel("Fecha y Hora de Salida:")
        salida_datetime_edit = QDateTimeEdit()
        salida_datetime_edit.setCalendarPopup(True)
        salida_datetime_edit.setDateTime(QDateTime.fromString(str(salida_actual), "yyyy-MM-dd HH:mm:ss"))
        layout.addWidget(salida_label)
        layout.addWidget(salida_datetime_edit)

        entrada_label = QLabel("Fecha y Hora de Entrada:")
        entrada_datetime_edit = QDateTimeEdit()
        entrada_datetime_edit.setCalendarPopup(True)
        entrada_datetime_edit.setDateTime(QDateTime.fromString(str(entrada_actual), "yyyy-MM-dd HH:mm:ss"))
        layout.addWidget(entrada_label)
        layout.addWidget(entrada_datetime_edit)

        # Botones de guardar y cancelar
        save_button = QPushButton("Guardar Cambios")
        save_button.clicked.connect(lambda: self._guardar_edicion_reserva(dialog, salida_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"), entrada_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"), id_vehiculo, id_seguro, id_descuento, valor_actual))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def _guardar_edicion_reserva(self, dialog, nueva_salida_str, nueva_entrada_str, id_vehiculo, id_seguro, id_descuento, valor_actual):
        try:
            nueva_salida = datetime.strptime(nueva_salida_str, "%Y-%m-%d %H:%M:%S")
            nueva_entrada = datetime.strptime(nueva_entrada_str, "%Y-%m-%d %H:%M:%S")

            if nueva_entrada <= nueva_salida:
                QMessageBox.warning(self, "Error", "La fecha de entrada debe ser posterior a la de salida.")
                return
            
            # Recalcular valor de la reserva
            dias = (nueva_entrada - nueva_salida).days
            if dias < 1:
                dias = 1
            
            tarifa_query = "SELECT t.tarifa_dia FROM Vehiculo v JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo WHERE v.placa = %s"
            tarifa_result = self.db_manager.execute_query(tarifa_query, (id_vehiculo,))
            tarifa_dia = float(tarifa_result[0][0]) if tarifa_result else 0
            
            nuevo_valor = dias * tarifa_dia

            if id_seguro:
                seguro_query = "SELECT costo FROM Seguro_alquiler WHERE id_seguro = %s"
                seguro_result = self.db_manager.execute_query(seguro_query, (id_seguro,))
                if seguro_result: nuevo_valor += float(seguro_result[0][0])
            
            if id_descuento:
                descuento_query = "SELECT valor FROM Descuento_alquiler WHERE id_descuento = %s"
                descuento_result = self.db_manager.execute_query(descuento_query, (id_descuento,))
                if descuento_result: nuevo_valor -= float(descuento_result[0][0])

            if nuevo_valor < 0: nuevo_valor = 0

            # Actualizar la reserva en la base de datos
            update_alquiler_query = "UPDATE Alquiler SET fecha_hora_salida = %s, fecha_hora_entrada = %s, valor = %s WHERE id_alquiler = (SELECT id_alquiler FROM Reserva_alquiler WHERE id_reserva = %s)"
            self.db_manager.update(update_alquiler_query, (nueva_salida_str, nueva_entrada_str, nuevo_valor, self._selected_reserva_id))

            # Obtener el abono actual de la reserva
            abono_actual_query = "SELECT abono FROM Reserva_alquiler WHERE id_reserva = %s"
            abono_actual_result = self.db_manager.execute_query(abono_actual_query, (self._selected_reserva_id,))
            abono_actual = float(abono_actual_result[0][0]) if abono_actual_result else 0

            # Recalcular saldo pendiente
            nuevo_saldo_pendiente = nuevo_valor - abono_actual
            if nuevo_saldo_pendiente < 0: nuevo_saldo_pendiente = 0

            # Actualizar saldo pendiente en Reserva_alquiler
            update_reserva_saldo_query = "UPDATE Reserva_alquiler SET saldo_pendiente = %s WHERE id_reserva = %s"
            self.db_manager.update(update_reserva_saldo_query, (nuevo_saldo_pendiente, self._selected_reserva_id))

            QMessageBox.information(self, "Éxito", "Reserva actualizada correctamente.")
            dialog.accept()
            self._cargar_reservas_cliente()
            self._cargar_reservas_pendientes_abono()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la reserva: {e}")

    # --- Pestaña Crear Reserva ---
    def _setup_crear_reserva_tab(self):
        self.guardar_reserva_button.clicked.connect(self._guardar_reserva)
        self.salida_datetime.setDateTime(QDateTime.currentDateTime())
        self.entrada_datetime.setDateTime(QDateTime.currentDateTime().addDays(1))
        
        # Cargar datos antes de conectar eventos
        self._cargar_vehiculos_disponibles()
        self._cargar_seguros_disponibles()
        
        # Conectar eventos después de cargar datos
        self.salida_datetime.dateTimeChanged.connect(self._recalcular_total_reserva)
        self.entrada_datetime.dateTimeChanged.connect(self._recalcular_total_reserva)
        self.vehiculo_combo.currentIndexChanged.connect(self._recalcular_total_reserva)
        self.seguro_combo.currentIndexChanged.connect(self._recalcular_total_reserva)

        self._recalcular_total_reserva()

        self.metodo_pago_combo.addItems(["Efectivo", "Tarjeta", "Transferencia"])

    def _cargar_vehiculos_disponibles(self):
        self.vehiculo_combo.clear()
        id_sucursal = self.user_data.get("id_sucursal")
        query = (
            "SELECT v.placa, v.modelo, m.nombre_marca, t.descripcion, t.tarifa_dia "
            "FROM Vehiculo v "
            "JOIN Marca_vehiculo m ON v.id_marca = m.id_marca "
            "JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo "
            "WHERE v.id_estado_vehiculo = 1"
        )
        params = ()
        if id_sucursal is not None:
            query += f" AND v.id_sucursal = %s"
            params = (id_sucursal,)
        
        self.vehiculos_data = self.db_manager.execute_query(query, params) or []
        for v in self.vehiculos_data:
            self.vehiculo_combo.addItem(f"{v[0]} - {v[1]} {v[2]} ({v[3]}) - ${v[4]:,.0f}/día")

    def _cargar_seguros_disponibles(self):
        self.seguro_combo.clear()
        self.seguro_combo.addItem("Ninguno")
        self.seguros_data = self.db_manager.execute_query("SELECT id_seguro, descripcion, costo FROM Seguro_alquiler") or []
        for s in self.seguros_data:
            self.seguro_combo.addItem(f"{s[1]} (${s[2]:,.0f})")

    def _obtener_descuento_activo(self, fecha_salida, fecha_entrada):
        query = (
            "SELECT id_descuento, descripcion, valor "
            "FROM Descuento_alquiler "
            "WHERE fecha_inicio <= %s AND fecha_fin >= %s "
            "LIMIT 1"
        )
        rows = self.db_manager.execute_query(query, (fecha_entrada, fecha_salida))
        return rows[0] if rows else (None, None, 0)

    def _recalcular_total_reserva(self):
        if not self.vehiculos_data:
            self.total_label.setText("Total: $0")
            self.abono_min_label.setText("Abono Mínimo (30%): $0")
            self.descuento_label.setText("Descuento Aplicado: Ninguno")
            return

        try:
            selected_vehiculo_text = self.vehiculo_combo.currentText()
            if not selected_vehiculo_text: return

            placa = selected_vehiculo_text.split(" - ")[0]
            vehiculo_info = next((v for v in self.vehiculos_data if v[0] == placa), None)
            if not vehiculo_info: return

            tarifa_dia = float(vehiculo_info[4])

            fecha_salida = self.salida_datetime.dateTime().toPyDateTime()
            fecha_entrada = self.entrada_datetime.dateTime().toPyDateTime()

            if fecha_entrada <= fecha_salida:
                self.total_label.setText("Total: $0")
                self.abono_min_label.setText("Abono Mínimo (30%): $0")
                self.descuento_label.setText("Descuento Aplicado: Ninguno")
                return

            dias = (fecha_entrada - fecha_salida).days
            if dias < 1: dias = 1

            precio_base = dias * tarifa_dia
            
            # Calcular seguro
            seguro_costo = 0
            selected_seguro_text = self.seguro_combo.currentText()
            if selected_seguro_text != "Ninguno":
                seguro_info = next((s for s in self.seguros_data if f"{s[1]} (${float(s[2]):,.0f})" == selected_seguro_text), None)
                if seguro_info: seguro_costo = float(seguro_info[2])

            # Calcular descuento
            id_descuento, desc_text, desc_val = self._obtener_descuento_activo(fecha_salida, fecha_entrada)
            if id_descuento: self.descuento_label.setText(f"Descuento Aplicado: {desc_text} (-${float(desc_val):,.0f})")
            else: self.descuento_label.setText("Descuento Aplicado: Ninguno")

            total = precio_base + seguro_costo - float(desc_val)
            if total < 0: total = 0

            abono_min = round(total * 0.3, 2)

            self.total_label.setText(f"Total: ${total:,.0f}")
            self.abono_min_label.setText(f"Abono Mínimo (30%): ${abono_min:,.0f}")

        except Exception as e:
            print(f"Error al recalcular total: {e}")
            self.total_label.setText("Total: $0")
            self.abono_min_label.setText("Abono Mínimo (30%): $0")
            self.descuento_label.setText("Descuento Aplicado: Ninguno")

    def _guardar_reserva(self):
        try:
            selected_vehiculo_text = self.vehiculo_combo.currentText()
            if not selected_vehiculo_text:
                QMessageBox.warning(self, "Error", "Seleccione un vehículo.")
                return
            placa = selected_vehiculo_text.split(" - ")[0]

            fecha_hora_salida = self.salida_datetime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            fecha_hora_entrada = self.entrada_datetime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            dt_salida = self.salida_datetime.dateTime().toPyDateTime()
            dt_entrada = self.entrada_datetime.dateTime().toPyDateTime()

            if dt_salida < datetime.now():
                QMessageBox.warning(self, "Error", "La fecha de salida no puede ser en el pasado.")
                return
            if dt_entrada <= dt_salida:
                QMessageBox.warning(self, "Error", "La fecha de entrada debe ser posterior a la de salida.")
                return

            abono_str = self.abono_edit.text().strip()
            if not abono_str:
                QMessageBox.warning(self, "Error", "Ingrese el monto del abono inicial.")
                return
            abono = float(abono_str)

            metodo_pago = self.metodo_pago_combo.currentText()

            # Recalcular total y abono mínimo para validación final
            self._recalcular_total_reserva()
            total_str = self.total_label.text().replace("Total: $", "").replace(",", "")
            total = float(total_str)
            abono_min_str = self.abono_min_label.text().replace("Abono Mínimo (30%): $", "").replace(",", "")
            abono_min = float(abono_min_str)

            if abono < abono_min:
                QMessageBox.warning(self, "Error", f"El abono inicial debe ser al menos el 30%: ${abono_min:,.0f}")
                return
            
            # Obtener id_seguro
            id_seguro = None
            selected_seguro_text = self.seguro_combo.currentText()
            if selected_seguro_text != "Ninguno":
                seguro_info = next((s for s in self.seguros_data if f"{s[1]} (${float(s[2]):,.0f})" == selected_seguro_text), None)
                if seguro_info: id_seguro = seguro_info[0]

            # Obtener id_descuento
            id_descuento, _, _ = self._obtener_descuento_activo(dt_salida, dt_entrada)

            # Insertar en Alquiler
            alquiler_query = "INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado, id_seguro, id_descuento, valor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            id_alquiler = self.db_manager.insert(
                alquiler_query,
                (fecha_hora_salida, fecha_hora_entrada, placa, self.user_data.get("id_cliente"), self.user_data.get("id_empleado"), id_seguro, id_descuento, total)
            )

            if not id_alquiler:
                QMessageBox.critical(self, "Error", "No se pudo obtener el ID del alquiler.")
                return

            # Cambiar estado del vehículo a reservado (estado 2)
            update_vehiculo_query = "UPDATE Vehiculo SET id_estado_vehiculo = 2 WHERE placa = %s"
            self.db_manager.update(update_vehiculo_query, (placa,))

            # Insertar en Reserva_alquiler
            saldo_pendiente = total - abono
            reserva_query = "INSERT INTO Reserva_alquiler (id_alquiler, id_estado_reserva, saldo_pendiente, abono, id_empleado) VALUES (%s, %s, %s, %s, %s)"
            id_reserva = self.db_manager.insert(
                reserva_query,
                (id_alquiler, 1, saldo_pendiente, abono, self.user_data.get("id_empleado"))
            )

            if not id_reserva:
                QMessageBox.critical(self, "Error", "No se pudo obtener el ID de la reserva.")
                return

            # Insertar abono inicial
            id_medio_pago = {"Efectivo": 1, "Tarjeta": 2, "Transferencia": 3}.get(metodo_pago, 1)
            abono_inicial_query = "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) VALUES (%s, CURRENT_TIMESTAMP, %s, %s)"
            self.db_manager.insert(abono_inicial_query, (abono, id_reserva, id_medio_pago))

            if metodo_pago == "Efectivo":
                QMessageBox.information(self, "Reserva Registrada", "Su reserva ha sido registrada. Por favor, diríjase a la sucursal para realizar el pago en efectivo.")
            else:
                self._simular_pasarela_pago(id_reserva, abono, metodo_pago)

            self._cargar_reservas_cliente()
            self.abono_edit.clear()
            self._recalcular_total_reserva()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar la reserva: {e}")

    def _simular_pasarela_pago(self, id_reserva, monto, metodo):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Pasarela de Pago - {metodo}")
        layout = QVBoxLayout()
        label = QLabel(f"Simulando pago de ${monto:,.0f} con {metodo}...")
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.setModal(False) # Asegurarse de que no sea modal
        dialog.show()

        QTimer.singleShot(2000, lambda: self._finalizar_simulacion_pago(dialog, id_reserva, monto, metodo))

    def _finalizar_simulacion_pago(self, dialog, id_reserva, monto, metodo):
        dialog.close()
        try:
            # Actualizar estado de la reserva a Aprobada (estado 2)
            update_reserva_query = "UPDATE Reserva_alquiler SET id_estado_reserva = 2 WHERE id_reserva = %s"
            self.db_manager.update(update_reserva_query, (id_reserva,))
            QMessageBox.information(self, "Pago Exitoso", f"El pago de ${monto:,.0f} ha sido procesado exitosamente con {metodo}. Su reserva ha sido aprobada.")
            self._cargar_reservas_cliente()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al finalizar el pago: {e}")

    # --- Pestaña Realizar Abonos ---
    def _setup_abonos_tab(self):
        self.realizar_abono_button.clicked.connect(self._realizar_abono)
        self.abonos_reservas_list.itemSelectionChanged.connect(self._on_abono_reserva_selection_changed)
        self.metodo_abono_combo.addItems(["Efectivo", "Tarjeta", "Transferencia"])
        self._cargar_reservas_pendientes_abono()

    def _on_abono_reserva_selection_changed(self):
        selected_items = self.abonos_reservas_list.selectedItems()
        if selected_items:
            item_text = selected_items[0].text()
            self._selected_reserva_id = int(item_text.split(":")[0].replace("Reserva ", "").strip())
        else:
            self._selected_reserva_id = None

    def _cargar_reservas_pendientes_abono(self):
        self.abonos_reservas_list.clear()
        id_cliente = self.user_data.get("id_cliente")
        query = (
            "SELECT ra.id_reserva, v.modelo, v.placa, ra.saldo_pendiente, a.valor "
            "FROM Reserva_alquiler ra "
            "JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            "JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            "WHERE a.id_cliente = %s AND ra.saldo_pendiente > 0 AND ra.id_estado_reserva IN (1,2) "
            "ORDER BY a.fecha_hora_salida DESC"
        )
        reservas = self.db_manager.execute_query(query, (id_cliente,))

        if not reservas:
            self.abonos_reservas_list.addItem("No tienes reservas pendientes de pago.")
            return

        for r in reservas:
            id_reserva, modelo, placa, saldo_pendiente, valor_total = r
            self.abonos_reservas_list.addItem(f"Reserva {id_reserva}: {modelo} ({placa}) - Saldo: ${float(saldo_pendiente):,.0f} / Total: ${float(valor_total):,.0f}")

    def _realizar_abono(self):
        if not self._selected_reserva_id:
            QMessageBox.warning(self, "Aviso", "Seleccione una reserva para abonar.")
            return

        monto_str = self.monto_abono_edit.text().strip()
        if not monto_str:
            QMessageBox.warning(self, "Error", "Ingrese el monto a abonar.")
            return
        try:
            # Limpiar el string de entrada de comas y puntos de miles.
            monto_str_limpio = monto_str.replace(',', '').replace('.', '')
            monto = float(monto_str_limpio)
        except ValueError:
            QMessageBox.warning(self, "Error", f"Monto inválido: '{monto_str}'. Ingrese un número válido.")
            return

        if monto <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0.")
            return

        # Obtener saldo pendiente actual y convertirlo a float
        saldo_query = "SELECT saldo_pendiente FROM Reserva_alquiler WHERE id_reserva = %s"
        resultado_saldo = self.db_manager.execute_query(saldo_query, (self._selected_reserva_id,))
        if not resultado_saldo:
            QMessageBox.critical(self, "Error", "No se pudo obtener el saldo de la reserva.")
            return
        
        saldo_actual = float(resultado_saldo[0][0])

        if monto > saldo_actual:
            QMessageBox.warning(self, "Error", f"El monto a abonar (${monto:,.0f}) no puede ser mayor al saldo pendiente (${saldo_actual:,.0f}).")
            return

        metodo_pago = self.metodo_abono_combo.currentText()
        id_medio_pago = {"Efectivo": 1, "Tarjeta": 2, "Transferencia": 3}.get(metodo_pago, 1)

        try:
            # Insertar el abono
            insert_abono_query = "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) VALUES (%s, CURRENT_TIMESTAMP, %s, %s)"
            self.db_manager.insert(insert_abono_query, (monto, self._selected_reserva_id, id_medio_pago))

            # Actualizar saldo pendiente de la reserva
            nuevo_saldo = saldo_actual - monto
            update_reserva_query = "UPDATE Reserva_alquiler SET saldo_pendiente = %s WHERE id_reserva = %s"
            self.db_manager.update(update_reserva_query, (nuevo_saldo, self._selected_reserva_id))

            if nuevo_saldo <= 0:
                # Si el saldo es 0 o menos, la reserva está pagada (estado 2)
                update_estado_query = "UPDATE Reserva_alquiler SET id_estado_reserva = 2 WHERE id_reserva = %s"
                self.db_manager.update(update_estado_query, (self._selected_reserva_id,))
                QMessageBox.information(self, "Reserva Pagada", "¡La reserva ha sido completamente pagada!")
            
            if metodo_pago == "Efectivo":
                QMessageBox.information(self, "Abono Registrado", "Su abono ha sido registrado. Por favor, diríjase a la sucursal para realizar el pago en efectivo.")
            else:
                self._simular_pasarela_pago(self._selected_reserva_id, monto, metodo_pago)

            self.monto_abono_edit.clear()
            self._cargar_reservas_pendientes_abono()
            self._cargar_reservas_cliente() # Para actualizar el estado en la otra pestaña

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al realizar el abono: {e}")

    # --- Pestaña Mi Perfil ---
    def _setup_perfil_tab(self):
        self.guardar_perfil_button.clicked.connect(self._guardar_perfil)
        self._cargar_datos_perfil()

    def _cargar_datos_perfil(self):
        id_cliente = self.user_data.get("id_cliente")
        query = "SELECT nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = %s"
        datos = self.db_manager.execute_query(query, (id_cliente,))
        if datos:
            nombre, telefono, direccion, correo = datos[0]
            self.nombre_perfil_edit.setText(nombre or "")
            self.telefono_perfil_edit.setText(telefono or "")
            self.direccion_perfil_edit.setText(direccion or "")
            self.correo_perfil_edit.setText(correo or "")

    def _guardar_perfil(self):
        nombre = self.nombre_perfil_edit.text().strip()
        telefono = self.telefono_perfil_edit.text().strip()
        direccion = self.direccion_perfil_edit.text().strip()
        correo = self.correo_perfil_edit.text().strip()
        id_cliente = self.user_data.get("id_cliente")

        if not nombre or not correo:
            QMessageBox.warning(self, "Aviso", "Nombre y correo son obligatorios.")
            return

        try:
            query = "UPDATE Cliente SET nombre = %s, telefono = %s, direccion = %s, correo = %s WHERE id_cliente = %s"
            self.db_manager.update(query, (nombre, telefono, direccion, correo, id_cliente))
            QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente.")
            # Actualizar user_data para reflejar los cambios en la sesión actual
            self.user_data["usuario"] = nombre # Asumiendo que el nombre es el usuario para el mensaje de bienvenida
            self._setup_ui() # Para actualizar el mensaje de bienvenida si aplica
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar el perfil: {e}")

    # --- Pestaña Cambiar Contraseña ---
    def _setup_cambiar_contrasena_tab(self):
        self.cambiar_pass_button.clicked.connect(self._cambiar_contrasena)

    def _cambiar_contrasena(self):
        nueva_pass = self.nueva_pass_edit.text()
        confirmar_pass = self.confirmar_pass_edit.text()

        if not nueva_pass or not confirmar_pass:
            QMessageBox.warning(self, "Aviso", "Todos los campos son obligatorios.")
            return

        if nueva_pass != confirmar_pass:
            QMessageBox.warning(self, "Error", "La nueva contraseña y la confirmación no coinciden.")
            return

        try:
            user_email = self.user_data.get("usuario")
            auth_result = self.auth_manager.cambiar_contrasena(user_email, nueva_pass)

            if auth_result is True:
                QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente.")
                self.nueva_pass_edit.clear()
                self.confirmar_pass_edit.clear()
            else:
                QMessageBox.warning(self, "Error", auth_result)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar la contraseña: {e}")
