from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QScrollArea, QHBoxLayout, QMessageBox, QGridLayout, QFrame, QSizePolicy, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QLocale
from datetime import datetime

class ClienteViewQt(QWidget):
    def __init__(self, user_data, db_manager, on_logout):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.on_logout = on_logout
        self.descuento_labels = []  # Inicializar para evitar AttributeError
        self.setWindowTitle(f"Bienvenido cliente, {self.user_data.get('usuario', '')}")
        self.resize(1100, 700)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        # Barra superior
        topbar = QHBoxLayout()
        self.status_remota1 = QLabel("")
        self.status_remota2 = QLabel("")
        self.status_label1 = QLabel("")
        self.status_label2 = QLabel("")
        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.clicked.connect(self.logout)
        # Orden: remotas, usuario, id, stretch, logout
        topbar.addWidget(self.status_remota1)
        topbar.addWidget(self.status_remota2)
        topbar.addSpacing(10)
        topbar.addWidget(self.status_label1)
        topbar.addWidget(self.status_label2)
        topbar.addStretch()
        topbar.addWidget(btn_logout)
        layout.addLayout(topbar)
        # Pestañas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        # Pestaña: Mis reservas
        self.tab_reservas = QWidget()
        self.tabs.addTab(self.tab_reservas, "Mis reservas")
        self._build_tab_mis_reservas()
        # Pestaña: Crear reserva
        self.tab_crear = QWidget()
        self.tabs.addTab(self.tab_crear, "Crear reserva")
        self._build_tab_crear_reserva()
        # Pestaña: Vehículos disponibles
        self.tab_vehiculos = QWidget()
        self.tabs.addTab(self.tab_vehiculos, "Vehículos disponibles")
        self._build_tab_vehiculos()
        # Pestaña: Realizar abonos
        self.tab_abonos = QWidget()
        self.tabs.addTab(self.tab_abonos, "Realizar abonos")
        self._build_tab_abonos()
        # Pestaña: Cambiar contraseña
        self.tab_cambiar = QWidget()
        self.tabs.addTab(self.tab_cambiar, "Cambiar contraseña")
        self._build_tab_cambiar_contrasena()
        # Pestaña: Editar perfil (si aplica)
        self.tab_perfil = QWidget()
        self.tabs.addTab(self.tab_perfil, "Editar perfil")
        self._build_tab_perfil()
        self._update_status_labels()
        self._start_status_updater()

    def logout(self):
        self.close()
        if self.on_logout:
            self.on_logout()

    def _update_status_labels(self):
        # Estado de remotas
        online1 = getattr(self.db_manager, 'is_remote1_active', lambda: getattr(self.db_manager, 'remote1_active', False))()
        online2 = getattr(self.db_manager, 'is_remote2_active', lambda: getattr(self.db_manager, 'remote2_active', False))()
        emoji1 = "🟢" if online1 else "🔴"
        emoji2 = "🟢" if online2 else "🔴"
        estado1 = "ONLINE" if online1 else "OFFLINE"
        estado2 = "ONLINE" if online2 else "OFFLINE"
        self.status_remota1.setText(f"{emoji1} R1: {estado1}")
        self.status_remota2.setText(f"{emoji2} R2: {estado2}")
        # Usuario e ID
        self.status_label1.setText(f"Usuario: {self.user_data.get('usuario', '')}")
        self.status_label2.setText(f"ID Cliente: {self.user_data.get('id_cliente', '')}")

    def _start_status_updater(self):
        self.timer_status = QTimer(self)
        self.timer_status.timeout.connect(self._update_status_labels)
        self.timer_status.start(1000)

    def closeEvent(self, event):
        if hasattr(self, 'timer_status'):
            self.timer_status.stop()
        super().closeEvent(event)

    def _build_tab_mis_reservas(self):
        from datetime import datetime
        from PyQt5.QtWidgets import QGridLayout, QFrame, QSizePolicy
        layout = QVBoxLayout(self.tab_reservas)
        label = QLabel("Mis reservas")
        label.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center;")
        layout.addWidget(label)
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid_layout = QGridLayout(scroll_content)
        grid_layout.setSpacing(16)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        # Contenedores por estado (columnas)
        self.cards_pendientes = QVBoxLayout()
        self.cards_pagadas = QVBoxLayout()
        self.cards_vencidas = QVBoxLayout()
        # Columnas como QFrame para bordes y fondo, con ancho máximo
        col_pendientes = QFrame(); col_pendientes.setLayout(self.cards_pendientes)
        col_pendientes.setStyleSheet("background: #FFF8E1; border-radius: 10px;")
        col_pendientes.setMaximumWidth(420)
        col_pendientes.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        col_pagadas = QFrame(); col_pagadas.setLayout(self.cards_pagadas)
        col_pagadas.setStyleSheet("background: #E8F5E9; border-radius: 10px;")
        col_pagadas.setMaximumWidth(420)
        col_pagadas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        col_vencidas = QFrame(); col_vencidas.setLayout(self.cards_vencidas)
        col_vencidas.setStyleSheet("background: #FFEBEE; border-radius: 10px;")
        col_vencidas.setMaximumWidth(420)
        col_vencidas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        # Títulos de columnas
        t1 = QLabel("⏳ Pendientes"); t1.setStyleSheet("font-size: 15px; font-weight: bold; color: #B8860B; text-align: center;")
        t2 = QLabel("✅ Pagadas"); t2.setStyleSheet("font-size: 15px; font-weight: bold; color: #388E3C; text-align: center;")
        t3 = QLabel("❌ Vencidas/Canceladas"); t3.setStyleSheet("font-size: 15px; font-weight: bold; color: #C62828; text-align: center;")
        grid_layout.addWidget(t1, 0, 0, alignment=Qt.AlignHCenter)
        grid_layout.addWidget(t2, 0, 1, alignment=Qt.AlignHCenter)
        grid_layout.addWidget(t3, 0, 2, alignment=Qt.AlignHCenter)
        grid_layout.addWidget(col_pendientes, 1, 0)
        grid_layout.addWidget(col_pagadas, 1, 1)
        grid_layout.addWidget(col_vencidas, 1, 2)
        # Ajustar stretch para que el grid no se expanda demasiado
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 0)
        grid_layout.setColumnStretch(2, 0)
        self._cargar_reservas_cliente()
        # Después de agregar las tarjetas, igualar la altura de las columnas
        max_height = max(col_pendientes.sizeHint().height(), col_pagadas.sizeHint().height(), col_vencidas.sizeHint().height())
        col_pendientes.setMinimumHeight(max_height)
        col_pagadas.setMinimumHeight(max_height)
        col_vencidas.setMinimumHeight(max_height)

    def _cargar_reservas_cliente(self):
        from datetime import datetime
        from PyQt5.QtGui import QColor
        # Limpiar layouts
        for layout in [self.cards_pendientes, self.cards_pagadas, self.cards_vencidas]:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        # Volver a poner los títulos (no necesario, ya están en el grid)
        id_cliente = self.user_data.get("id_cliente")
        query = '''
            SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, a.valor, ra.saldo_pendiente, ra.abono, es.descripcion, s.descripcion, s.costo, d.descripcion, d.valor, d.fecha_inicio, d.fecha_fin
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
        if not reservas:
            t = QLabel("No tienes reservas registradas")
            t.setStyleSheet("font-size: 12px; margin: 10px;")
            self.cards_pendientes.addWidget(t)
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
                badge_color = "#FFD54F"
                text_color = "#B8860B"
                fondo = "#FFFDE7"
            elif estado and "confirm" in estado.lower():
                estado_str = "✅ Pagada"
                card_parent = self.cards_pagadas
                badge_color = "#A5D6A7"
                text_color = "#388E3C"
                fondo = "#E8F5E9"
            elif estado and ("cancel" in estado.lower() or "venc" in estado.lower()):
                estado_str = "❌ Cancelada/Vencida"
                card_parent = self.cards_vencidas
                badge_color = "#FFCDD2"
                text_color = "#C62828"
                fondo = "#FFEBEE"
            else:
                estado_str = estado or "Desconocido"
                card_parent = self.cards_vencidas
                badge_color = "#E0E0E0"
                text_color = "#616161"
                fondo = "#F5F5F5"
            # Tarjeta visual
            card = QWidget()
            card.setStyleSheet(f"background: {fondo}; border-radius: 12px; margin: 8px; padding: 8px;")
            card.setMinimumHeight(350)
            card_layout = QVBoxLayout(card)
            # Encabezado
            header = QHBoxLayout()
            l_modelo = QLabel(f"{modelo} ({placa})")
            l_modelo.setStyleSheet("font-size: 14px; font-weight: bold; color: #222831;")
            l_estado = QLabel(estado_str)
            l_estado.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {text_color}; background: {badge_color}; border-radius: 8px; padding: 2px 8px;")
            header.addWidget(l_modelo)
            header.addStretch()
            header.addWidget(l_estado)
            card_layout.addLayout(header)
            # Fechas
            fechas = QHBoxLayout()
            salida_fmt = salida.strftime('%Y-%m-%d %H:%M') if isinstance(salida, datetime) else str(salida)
            entrada_fmt = entrada.strftime('%Y-%m-%d %H:%M') if isinstance(entrada, datetime) else str(entrada)
            l_salida = QLabel(f"Salida: {salida_fmt}"); l_salida.setStyleSheet("color: #222831;")
            l_entrada = QLabel(f"Entrada: {entrada_fmt}"); l_entrada.setStyleSheet("color: #222831;")
            fechas.addWidget(l_salida)
            fechas.addWidget(l_entrada)
            card_layout.addLayout(fechas)
            # Montos
            l_total = QLabel(f"Total: ${valor:,.0f}"); l_total.setStyleSheet("color: #1976D2; font-size: 13px; margin-bottom: 2px;")
            l_abonado = QLabel(f"Abonado: ${abono:,.0f}"); l_abonado.setStyleSheet("color: #388E3C; font-size: 13px; margin-bottom: 2px;")
            l_saldo = QLabel(f"Saldo: ${saldo:,.0f}"); l_saldo.setStyleSheet("color: #C62828; font-size: 13px; margin-bottom: 2px;")
            card_layout.addWidget(l_total)
            card_layout.addWidget(l_abonado)
            card_layout.addWidget(l_saldo)
            # Seguro y descuento
            if seguro and costo_seguro:
                l_seguro = QLabel(f"Seguro: {seguro} (${costo_seguro:,.0f})")
                l_seguro.setStyleSheet("color: #1976D2;")
                card_layout.addWidget(l_seguro)
            if desc and val_desc:
                l_desc = QLabel(f"Descuento: {desc} (-${val_desc:,.0f})")
                l_desc.setStyleSheet("color: #388E3C;")
                card_layout.addWidget(l_desc)
            # Botones de acción solo para pendientes
            if "pendiente" in estado_str.lower():
                btns = QHBoxLayout()
                btn_cancelar = QPushButton("Cancelar reserva")
                btn_cancelar.setStyleSheet("background-color: #FF7043; color: white; font-weight: bold; border-radius: 6px; padding: 4px 12px;")
                btn_cancelar.clicked.connect(lambda _, rid=id_reserva: self._cancelar_reserva_card(rid))
                btn_editar = QPushButton("Editar fechas")
                btn_editar.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold; border-radius: 6px; padding: 4px 12px;")
                btn_editar.clicked.connect(lambda _, rid=id_reserva: self._editar_reserva_card(rid))
                btns.addWidget(btn_cancelar)
                btns.addWidget(btn_editar)
                card_layout.addLayout(btns)
            card_parent.addWidget(card)

    def _build_tab_crear_reserva(self):
        from PyQt5.QtWidgets import QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox, QHBoxLayout, QWidget
        from PyQt5.QtCore import QDate
        import datetime
        layout = QVBoxLayout(self.tab_crear)
        label = QLabel("Crear nueva reserva")
        label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(label)
        # Agrupar campos principales en un QGroupBox con QFormLayout
        form_group = QGroupBox()
        form_layout = QFormLayout(form_group)
        # Vehículo
        self.cb_vehiculo = QComboBox()
        vehiculos = self.db_manager.execute_query(
            "SELECT v.placa, v.modelo, m.nombre_marca FROM Vehiculo v JOIN Marca_vehiculo m ON v.id_marca = m.id_marca WHERE v.id_estado_vehiculo = 1"
        )
        self.vehiculo_map = {f"{v[0]} - {v[1]} {v[2]}": v[0] for v in (vehiculos or [])}
        self.cb_vehiculo.addItems(list(self.vehiculo_map.keys()))
        form_layout.addRow("Vehículo", self.cb_vehiculo)
        # Fecha y hora salida (fecha a la izquierda, hora/min/ampm juntos a la derecha)
        salida_row = QHBoxLayout()
        self.date_salida = QDateEdit(); self.date_salida.setCalendarPopup(True)
        self.date_salida.setDate(QDate.currentDate())
        salida_row.addWidget(self.date_salida)
        hora_widget = QWidget(); hora_layout = QHBoxLayout(hora_widget); hora_layout.setContentsMargins(0,0,0,0)
        self.cb_hora_salida = QComboBox(); self.cb_min_salida = QComboBox(); self.cb_ampm_salida = QComboBox()
        self.cb_hora_salida.addItems([f"{h:02d}" for h in range(1, 13)])
        self.cb_min_salida.addItems(["00", "15", "30", "45"])
        self.cb_ampm_salida.addItems(["AM", "PM"])
        self.cb_hora_salida.setCurrentText("08")
        self.cb_min_salida.setCurrentText("00")
        self.cb_ampm_salida.setCurrentText("AM")
        for cb in [self.cb_hora_salida, self.cb_min_salida, self.cb_ampm_salida]:
            cb.setFixedWidth(50)
            cb.setStyleSheet("margin-right:0px; margin-left:0px;")
        hora_layout.addWidget(self.cb_hora_salida)
        hora_layout.addWidget(QLabel(":"))
        hora_layout.addWidget(self.cb_min_salida)
        hora_layout.addWidget(self.cb_ampm_salida)
        salida_row.addSpacing(10)
        salida_row.addWidget(hora_widget)
        form_layout.addRow("Fecha y hora salida", salida_row)
        # Fecha y hora entrada (fecha a la izquierda, hora/min/ampm juntos a la derecha)
        entrada_row = QHBoxLayout()
        self.date_entrada = QDateEdit(); self.date_entrada.setCalendarPopup(True)
        self.date_entrada.setDate(QDate.currentDate())
        entrada_row.addWidget(self.date_entrada)
        hora_widget_e = QWidget(); hora_layout_e = QHBoxLayout(hora_widget_e); hora_layout_e.setContentsMargins(0,0,0,0)
        self.cb_hora_entrada = QComboBox(); self.cb_min_entrada = QComboBox(); self.cb_ampm_entrada = QComboBox()
        self.cb_hora_entrada.addItems([f"{h:02d}" for h in range(1, 13)])
        self.cb_min_entrada.addItems(["00", "15", "30", "45"])
        self.cb_ampm_entrada.addItems(["AM", "PM"])
        self.cb_hora_entrada.setCurrentText("09")
        self.cb_min_entrada.setCurrentText("00")
        self.cb_ampm_entrada.setCurrentText("AM")
        for cb in [self.cb_hora_entrada, self.cb_min_entrada, self.cb_ampm_entrada]:
            cb.setFixedWidth(50)
            cb.setStyleSheet("margin-right:0px; margin-left:0px;")
        hora_layout_e.addWidget(self.cb_hora_entrada)
        hora_layout_e.addWidget(QLabel(":"))
        hora_layout_e.addWidget(self.cb_min_entrada)
        hora_layout_e.addWidget(self.cb_ampm_entrada)
        entrada_row.addSpacing(10)
        entrada_row.addWidget(hora_widget_e)
        form_layout.addRow("Fecha y hora entrada", entrada_row)
        # Validación de fechas: no permitir entrada < salida
        def validar_fechas():
            salida = self.date_salida.date().toPyDate()
            entrada = self.date_entrada.date().toPyDate()
            if entrada < salida:
                self.date_entrada.setDate(self.date_salida.date())
                QMessageBox.warning(self, "Fecha inválida", "La fecha de entrada no puede ser anterior a la de salida.")
        self.date_entrada.dateChanged.connect(validar_fechas)
        self.date_salida.dateChanged.connect(validar_fechas)
        # Seguro
        self.cb_seguro = QComboBox()
        seguros = self.db_manager.execute_query(
            "SELECT id_seguro, descripcion, costo FROM Seguro_alquiler"
        )
        self.seguro_map = {f"{s[1]} (${s[2]})": (s[0], float(s[2])) for s in (seguros or [])}
        self.cb_seguro.addItems(list(self.seguro_map.keys()))
        form_layout.addRow("Seguro", self.cb_seguro)
        # Método de pago
        self.cb_metodo_pago = QComboBox()
        self.cb_metodo_pago.addItems(["Efectivo", "Tarjeta", "Transferencia"])
        form_layout.addRow("Método de pago", self.cb_metodo_pago)
        # Total y abono
        self.label_total = QLabel("Total: $0")
        self.label_abono_min = QLabel("Abono mínimo (30%): $0")
        self.input_abono_reserva = QDoubleSpinBox();
        self.input_abono_reserva.setMaximum(99999999)
        self.input_abono_reserva.setDecimals(2)
        self.input_abono_reserva.setSingleStep(1000)
        self.input_abono_reserva.setLocale(QLocale.c())
        self.input_abono_reserva.setSuffix("")
        self.input_abono_reserva.setButtonSymbols(QDoubleSpinBox.NoButtons)
        form_layout.addRow(self.label_total)
        form_layout.addRow(self.label_abono_min)
        form_layout.addRow("Abono inicial ($)", self.input_abono_reserva)
        layout.addWidget(form_group)
        # Botón crear reserva
        self.btn_crear_reserva = QPushButton("Crear reserva")
        self.btn_crear_reserva.clicked.connect(self._crear_reserva)
        layout.addWidget(self.btn_crear_reserva)
        # Descuentos disponibles (al final)
        self.label_descuentos = QLabel("Descuentos disponibles")
        self.label_descuentos.setStyleSheet("margin-top: 10px; font-size: 13px;")
        layout.addWidget(self.label_descuentos)
        self.lista_descuentos = QLabel("")
        self.lista_descuentos.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(self.lista_descuentos)
        layout.addStretch()
        # Conectar eventos para actualizar totales en tiempo real
        self.cb_vehiculo.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self.date_salida.dateChanged.connect(self._actualizar_descuentos_y_total)
        self.cb_hora_salida.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self.cb_min_salida.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self.cb_ampm_salida.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self.date_entrada.dateChanged.connect(self._actualizar_descuentos_y_total)
        self.cb_hora_entrada.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self.cb_min_entrada.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self.cb_ampm_entrada.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self.cb_seguro.currentIndexChanged.connect(self._actualizar_descuentos_y_total)
        self._actualizar_descuentos_y_total()

    def _actualizar_descuentos_y_total(self):
        from datetime import datetime, date
        # Limpiar labels de descuentos
        for lbl in self.descuento_labels:
            lbl.deleteLater()
        self.descuento_labels.clear()
        # Fechas
        fecha_salida = self.date_salida.date().toPyDate()
        fecha_entrada = self.date_entrada.date().toPyDate()
        # Descuentos
        lista_desc = self.db_manager.execute_query(
            "SELECT id_descuento, descripcion, valor, fecha_inicio, fecha_fin FROM Descuento_alquiler"
        )
        self.descuento_id = None
        self.descuento_valor = 0.0
        descuentos_text = ""
        for d in lista_desc:
            d_id, desc, val, ini, fin = d
            # Convertir ini y fin a date si son string o datetime
            if isinstance(ini, str):
                try:
                    ini_dt = datetime.strptime(ini, "%Y-%m-%d %H:%M:%S").date()
                except Exception:
                    ini_dt = datetime.strptime(ini, "%Y-%m-%d").date()
            elif isinstance(ini, datetime):
                ini_dt = ini.date()
            elif isinstance(ini, date):
                ini_dt = ini
            else:
                continue
            if isinstance(fin, str):
                try:
                    fin_dt = datetime.strptime(fin, "%Y-%m-%d %H:%M:%S").date()
                except Exception:
                    fin_dt = datetime.strptime(fin, "%Y-%m-%d").date()
            elif isinstance(fin, datetime):
                fin_dt = fin.date()
            elif isinstance(fin, date):
                fin_dt = fin
            else:
                continue
            aplica = ini_dt <= fecha_entrada and fin_dt >= fecha_salida
            texto = f"- {desc} ({str(ini_dt)} a {str(fin_dt)})"
            if not aplica:
                texto += " - No aplica para las fechas seleccionadas"
            else:
                if self.descuento_id is None:
                    self.descuento_id = d_id
                    self.descuento_valor = float(val)
            descuentos_text += texto + "\n"
            lbl = QLabel(texto)
            self.descuento_labels.append(lbl)
        self.lista_descuentos.setText(descuentos_text)
        # Calcular total y abono
        if self.cb_vehiculo.count() == 0:
            self.label_total.setText("Total: $0")
            self.label_abono_min.setText("Abono mínimo (30%): $0")
            return
        placa = self.vehiculo_map[self.cb_vehiculo.currentText()]
        vehiculo_query = """
            SELECT t.tarifa_dia FROM Vehiculo v JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo WHERE v.placa = %s
        """
        tarifa = self.db_manager.execute_query(vehiculo_query, (placa,))
        if not tarifa:
            self.label_total.setText("Total: $0")
            self.label_abono_min.setText("Abono mínimo (30%): $0")
            return
        tarifa_dia = float(tarifa[0][0])
        dias = (self.date_entrada.date().toPyDate() - self.date_salida.date().toPyDate()).days or 1
        total = tarifa_dia * dias
        if self.descuento_valor:
            total -= self.descuento_valor
        # Sumar costo del seguro seleccionado
        seguro_costo = 0.0
        if self.cb_seguro.count() > 0 and self.cb_seguro.currentText() in self.seguro_map:
            seguro_costo = self.seguro_map[self.cb_seguro.currentText()][1]
        total += seguro_costo
        self.label_total.setText(f"Total: ${total:.2f}")
        abono_min = total * 0.3
        self.label_abono_min.setText(f"Abono mínimo (30%): ${abono_min:.2f}")

    def _crear_reserva(self):
        from PyQt5.QtWidgets import QMessageBox
        from datetime import datetime
        # Validar campos obligatorios
        if self.cb_vehiculo.count() == 0 or not self.cb_vehiculo.currentText():
            QMessageBox.warning(self, "Error", "Debe seleccionar un vehículo")
            return
        if self.cb_seguro.count() == 0 or not self.cb_seguro.currentText():
            QMessageBox.warning(self, "Error", "Debe seleccionar un seguro")
            return
        if self.cb_metodo_pago.count() == 0 or not self.cb_metodo_pago.currentText():
            QMessageBox.warning(self, "Error", "Debe seleccionar un método de pago")
            return
        if not self.date_salida.date().isValid() or not self.date_entrada.date().isValid():
            QMessageBox.warning(self, "Error", "Debe seleccionar fechas válidas")
            return
        if self.input_abono_reserva.value() <= 0:
            QMessageBox.warning(self, "Error", "Debe ingresar un abono inicial mayor a 0")
            return
        placa = self.vehiculo_map[self.cb_vehiculo.currentText()]
        id_cliente = self.user_data.get("id_cliente")
        id_seguro = self.seguro_map[self.cb_seguro.currentText()][0] if self.cb_seguro.count() > 0 else None
        id_descuento = self.descuento_id
        metodo = self.cb_metodo_pago.currentText()
        # Fechas y horas
        def get_24h(date, hora_cb, min_cb, ampm_cb):
            h = int(hora_cb.currentText())
            m = int(min_cb.currentText())
            ampm = ampm_cb.currentText()
            if ampm == "PM" and h != 12:
                h += 12
            if ampm == "AM" and h == 12:
                h = 0
            return f"{date.date().toString('yyyy-MM-dd')} {h:02d}:{m:02d}"
        salida = get_24h(self.date_salida, self.cb_hora_salida, self.cb_min_salida, self.cb_ampm_salida)
        entrada = get_24h(self.date_entrada, self.cb_hora_entrada, self.cb_min_entrada, self.cb_ampm_entrada)
        fmt = "%Y-%m-%d %H:%M"
        try:
            salida_dt = datetime.strptime(salida, fmt)
            entrada_dt = datetime.strptime(entrada, fmt)
        except Exception:
            QMessageBox.warning(self, "Error", "Fechas u horas inválidas")
            return
        if entrada_dt <= salida_dt:
            QMessageBox.warning(self, "Error", "La fecha/hora de entrada debe ser posterior a la de salida")
            return
        # Calcular valores
        vehiculo_query = """
            SELECT t.tarifa_dia FROM Vehiculo v JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo WHERE v.placa = %s
        """
        tarifa = self.db_manager.execute_query(vehiculo_query, (placa,))
        if not tarifa:
            QMessageBox.warning(self, "Error", "No se pudo obtener la tarifa del vehículo")
            return
        tarifa_dia = float(tarifa[0][0])
        dias = (entrada_dt.date() - salida_dt.date()).days or 1
        total = tarifa_dia * dias
        if self.descuento_valor:
            total -= self.descuento_valor
        seguro_costo = 0.0
        if self.cb_seguro.count() > 0 and self.cb_seguro.currentText() in self.seguro_map:
            seguro_costo = self.seguro_map[self.cb_seguro.currentText()][1]
        total += seguro_costo
        abono_min = total * 0.3
        # Leer abono y reemplazar coma por punto si el usuario la escribe
        abono = self.input_abono_reserva.text().replace(",", ".")
        try:
            abono = float(abono)
        except Exception:
            QMessageBox.warning(self, "Error", "El abono inicial debe ser un número válido (usa punto decimal)")
            return
        if abono < abono_min:
            QMessageBox.warning(self, "Error", f"El abono inicial debe ser al menos el 30%: ${abono_min:.2f}")
            return
        # Insertar reserva en estado pendiente
        try:
            # Insertar en Alquiler
            insert_alquiler = """
                INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_seguro, id_descuento, valor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.db_manager.execute_query(insert_alquiler, (salida, entrada, placa, id_cliente, id_seguro, id_descuento, total))
            # Obtener id_alquiler recién insertado
            id_alquiler = self.db_manager.get_last_insert_id()
            # Insertar en Reserva_alquiler
            insert_reserva = """
                INSERT INTO Reserva_alquiler (id_alquiler, saldo_pendiente, abono, id_estado_reserva)
                VALUES (%s, %s, %s, %s)
            """
            saldo_pendiente = total - abono
            abono_val = abono
            id_estado_pendiente = 1  # Ajusta según tu base de datos
            self.db_manager.execute_query(insert_reserva, (id_alquiler, saldo_pendiente, abono_val, id_estado_pendiente))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar la reserva: {e}")
            return
        # Mostrar mensaje o pasarela según método de pago
        if metodo == "Efectivo":
            QMessageBox.information(self, "Reserva registrada", "Reserva creada en estado pendiente. Debe acercarse a la sede más cercana para llevar el efectivo.")
        else:
            self._mostrar_pasarela_pago(total, metodo)
        self._cargar_reservas_cliente()  # Refrescar pestaña de reservas
        QMessageBox.information(self, "Reserva registrada", "Reserva creada exitosamente en estado pendiente.")

    def _mostrar_pasarela_pago(self, total, metodo):
        from PyQt5.QtWidgets import QMessageBox
        # Aquí puedes implementar la lógica real de la pasarela de pago
        QMessageBox.information(self, "Pasarela de pago", f"Simulación de pasarela de pago para {metodo}. Total a pagar: ${total:,.0f}")

    def _build_tab_vehiculos(self):
        from PyQt5.QtWidgets import (
            QVBoxLayout,
            QLabel,
            QScrollArea,
            QWidget,
            QHBoxLayout,
            QPushButton,
        )
        from PyQt5.QtCore import Qt
        layout = QVBoxLayout(self.tab_vehiculos)
        label = QLabel("Vehículos disponibles")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        # Consulta de vehículos disponibles
        placeholder = "%s" if not getattr(self.db_manager, 'offline', False) else "?"
        id_sucursal = self.user_data.get("id_sucursal")
        query = f'''
            SELECT v.placa, v.modelo, v.kilometraje, v.n_chasis,
                   m.nombre_marca, t.descripcion as tipo_vehiculo, t.tarifa_dia, t.capacidad, t.combustible,
                   c.nombre_color, tr.descripcion as transmision, ci.descripcion as cilindraje,
                   b.descripcion as blindaje, s.estado as seguro_estado, s.descripcion as seguro_desc,
                   su.nombre as sucursal, su.direccion as sucursal_dir, su.telefono as sucursal_tel, su.gerente as sucursal_mgr
            FROM Vehiculo v
            JOIN Marca_vehiculo m ON v.id_marca = m.id_marca
            JOIN Tipo_vehiculo t ON v.id_tipo_vehiculo = t.id_tipo
            LEFT JOIN Color_vehiculo c ON v.id_color = c.id_color
            LEFT JOIN Transmision_vehiculo tr ON v.id_transmision = tr.id_transmision
            LEFT JOIN Cilindraje_vehiculo ci ON v.id_cilindraje = ci.id_cilindraje
            LEFT JOIN Blindaje_vehiculo b ON v.id_blindaje = b.id_blindaje
            LEFT JOIN Seguro_vehiculo s ON v.id_seguro_vehiculo = s.id_seguro
            LEFT JOIN Sucursal su ON v.id_sucursal = su.id_sucursal
            WHERE v.id_estado_vehiculo = 1'''
        params = ()
        if id_sucursal is not None:
            query += f" AND v.id_sucursal = {placeholder}"
            params = (id_sucursal,)
        vehiculos = self.db_manager.execute_query(query, params)
        if not vehiculos:
            t = QLabel("No hay vehículos disponibles")
            t.setStyleSheet("font-size: 14px; margin: 20px;")
            scroll_layout.addWidget(t)
            return
        for vehiculo in vehiculos:
            (
                placa,
                modelo,
                kilometraje,
                n_chasis,
                marca,
                tipo_vehiculo,
                tarifa_dia,
                capacidad,
                combustible,
                color,
                transmision,
                cilindraje,
                blindaje,
                seguro_estado,
                seguro_desc,
                sucursal,
                sucursal_dir,
                sucursal_tel,
                sucursal_mgr,
            ) = vehiculo
            # Card visual
            card = QWidget()
            card.setStyleSheet(
                "background: #f5f5f5; border-radius: 15px; margin: 10px; padding: 10px; color: black;"
            )
            # Limitar la altura de las tarjetas para mantener el tamaño uniforme
            card.setMinimumHeight(280)
            card_layout = QVBoxLayout(card)
            # Header
            header = QWidget()
            header.setStyleSheet("background: #2196F3; border-radius: 10px;")
            header_layout = QVBoxLayout(header)
            l_modelo = QLabel(f"{marca} {modelo}")
            l_modelo.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
            l_placa = QLabel(f"Placa: {placa}")
            l_placa.setStyleSheet("font-size: 12px; color: white;")
            header_layout.addWidget(l_modelo)
            header_layout.addWidget(l_placa)
            header.setLayout(header_layout)
            card_layout.addWidget(header)
            # Info principal
            info = QWidget()
            info_layout = QVBoxLayout(info)
            info_layout.addWidget(QLabel(f"💰 Tarifa: ${tarifa_dia:,.0f}/día"))
            info_layout.addWidget(QLabel(f"👥 Capacidad: {capacidad} personas"))
            info_layout.addWidget(QLabel(f"⛽ Combustible: {combustible}"))
            info_layout.addWidget(QLabel(f"🎨 Color: {color or 'No especificado'}"))
            info_layout.addWidget(QLabel(f"⚙️ Transmisión: {transmision or 'No especificado'}"))
            info_layout.addWidget(QLabel(f"🔧 Cilindraje: {cilindraje or 'No especificado'}"))
            info_layout.addWidget(QLabel(f"🛡️ Blindaje: {blindaje or 'No especificado'}"))
            info_layout.addWidget(QLabel(f"📊 Kilometraje: {kilometraje:,} km"))
            info_layout.addWidget(QLabel(f"🔒 Seguro: {seguro_estado or 'No especificado'}"))
            info.setLayout(info_layout)
            card_layout.addWidget(info)
            # Info sucursal
            if sucursal:
                sucursal_info = QWidget()
                sucursal_layout = QVBoxLayout(sucursal_info)
                l_sucursal = QLabel(f"🏢 Sucursal: {sucursal}")
                l_sucursal.setStyleSheet("color: #1976D2; font-weight: bold;")
                sucursal_layout.addWidget(l_sucursal)
                if sucursal_dir:
                    sucursal_layout.addWidget(QLabel(f"📍 {sucursal_dir}"))
                if sucursal_tel:
                    sucursal_layout.addWidget(QLabel(f"📞 {sucursal_tel}"))
                if sucursal_mgr:
                    sucursal_layout.addWidget(QLabel(f"👤 Gerente: {sucursal_mgr}"))
                sucursal_info.setLayout(sucursal_layout)
                card_layout.addWidget(sucursal_info)
            # Botón seleccionar
            btn_sel = QPushButton("Seleccionar")
            btn_sel.setStyleSheet(
                "background-color: #1976D2; color: white; border-radius: 6px; padding: 4px 12px;"
            )
            vehiculo_text = f"{placa} - {modelo} {marca}"
            btn_sel.clicked.connect(
                lambda _, text=vehiculo_text, pl=placa: self._seleccionar_vehiculo(text, pl)
            )
            card_layout.addWidget(btn_sel, alignment=Qt.AlignRight)
            scroll_layout.addWidget(card)

    def _seleccionar_vehiculo(self, texto: str, placa: str):
        """Seleccionar vehículo desde la pestaña de vehículos disponibles."""
        # Asegurar que la opción exista en el combobox
        idx = self.cb_vehiculo.findText(texto)
        if idx == -1:
            self.cb_vehiculo.addItem(texto)
            self.vehiculo_map[texto] = placa
            idx = self.cb_vehiculo.findText(texto)
        if idx >= 0:
            self.cb_vehiculo.setCurrentIndex(idx)
        # Cambiar a la pestaña de creación de reservas
        self.tabs.setCurrentWidget(self.tab_crear)

    def _build_tab_abonos(self):
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QScrollArea, QWidget, QHBoxLayout, QLineEdit, QPushButton, QComboBox, QMessageBox
        from PyQt5.QtCore import Qt
        layout = QVBoxLayout(self.tab_abonos)
        label = QLabel("Realizar Abonos")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        # Info importante
        info = QVBoxLayout()
        info_label = QLabel("ℹ️ Información importante:")
        info_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        info.addWidget(info_label)
        info.addWidget(QLabel("• El primer abono debe ser al menos el 30% del valor total"))
        info.addWidget(QLabel("• Los siguientes abonos pueden ser de cualquier valor"))
        info.addWidget(QLabel("• Seleccione una reserva y complete los campos para abonar"))
        layout.addLayout(info)
        # Scroll area para reservas pendientes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.abonos_scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        # Formulario de abono
        form = QHBoxLayout()
        form.addWidget(QLabel("Monto a abonar ($):"))
        self.input_abono_abono = QLineEdit(); self.input_abono_abono.setPlaceholderText("Ej: 50000"); self.input_abono_abono.setEnabled(False)
        form.addWidget(self.input_abono_abono)
        form.addWidget(QLabel("Método de pago:"))
        self.metodo_cb = QComboBox(); self.metodo_cb.addItems(["Efectivo", "Tarjeta", "Transferencia"]); self.metodo_cb.setEnabled(False)
        form.addWidget(self.metodo_cb)
        self.btn_abonar = QPushButton("💳 Realizar Abono"); self.btn_abonar.setEnabled(False)
        self.btn_abonar.clicked.connect(self._realizar_abono)
        layout.addLayout(form)
        layout.addWidget(self.btn_abonar)
        self._abono_seleccionado = None
        self._abono_cards = {}
        self._cargar_reservas_pendientes()

    def _cargar_reservas_pendientes(self):
        from PyQt5.QtWidgets import QLabel
        id_cliente = self.user_data.get("id_cliente")
        # Limpiar tarjetas
        for i in reversed(range(self.abonos_scroll_layout.count())):
            widget = self.abonos_scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        placeholder = "%s" if not getattr(self.db_manager, 'offline', False) else "?"
        query = (
            f"SELECT ra.id_reserva, a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, v.modelo, v.placa, ra.saldo_pendiente, a.valor "
            f"FROM Reserva_alquiler ra "
            f"JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler "
            f"JOIN Vehiculo v ON a.id_vehiculo = v.placa "
            f"WHERE a.id_cliente = {placeholder} AND ra.saldo_pendiente > 0 AND ra.id_estado_reserva = 2 "
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
                saldo_real = saldo_pendiente
                if saldo_real > 0:
                    porcentaje_abonado = (
                        (float(abonado) / float(valor_total)) * 100 if valor_total > 0 else 0
                    )
                    es_primer_abono = abonado == 0
                    monto_minimo = float(valor_total) * 0.30 if es_primer_abono else 0
                    # Tarjeta visual
                    card = QWidget()
                    card.setStyleSheet(
                        "background: white; border-radius: 12px; margin: 8px; padding: 8px;"
                    )
                    card.setMinimumHeight(280)
                    card_layout = QVBoxLayout(card)
                    l_modelo = QLabel(f"{modelo} ({placa})"); l_modelo.setStyleSheet("font-weight: bold;")
                    l_saldo = QLabel(f"Saldo pendiente: ${saldo_real:,.0f}"); l_saldo.setStyleSheet("color: #B8860B;")
                    l_abonado = QLabel(f"Abonado: ${abonado:,.0f} ({porcentaje_abonado:.1f}%)")
                    card_layout.addWidget(l_modelo)
                    card_layout.addWidget(l_saldo)
                    card_layout.addWidget(l_abonado)
                    if es_primer_abono:
                        l_min = QLabel(f"Mínimo 1er abono: ${monto_minimo:,.0f}"); l_min.setStyleSheet("color: #C62828;")
                        card_layout.addWidget(l_min)
                    card.mousePressEvent = lambda e, rid=id_reserva: self._seleccionar_abono_card(rid)
                    self._abono_cards[id_reserva] = card
                    self.abonos_scroll_layout.addWidget(card)
            if len(self._abono_cards) == 0:
                t = QLabel("No tienes reservas pendientes de pago.")
                t.setStyleSheet("color: #C62828; font-size: 13px;")
                self.abonos_scroll_layout.addWidget(t)
        else:
            t = QLabel("No tienes reservas pendientes de pago.")
            t.setStyleSheet("color: #C62828; font-size: 13px;")
            self.abonos_scroll_layout.addWidget(t)
        # Reset selección
        self._abono_seleccionado = None
        self.input_abono_abono.setEnabled(False)
        self.metodo_cb.setEnabled(False)
        self.btn_abonar.setEnabled(False)

    def _seleccionar_abono_card(self, id_reserva):
        for rid, card in self._abono_cards.items():
            if rid == id_reserva:
                card.setStyleSheet("background: #FFF59D; border-radius: 12px; margin: 8px; padding: 8px;")
            else:
                card.setStyleSheet("background: white; border-radius: 12px; margin: 8px; padding: 8px;")
        self._abono_seleccionado = id_reserva
        self.input_abono_abono.setEnabled(True)
        self.metodo_cb.setEnabled(True)
        self.btn_abonar.setEnabled(True)

    def _realizar_abono(self):
        from PyQt5.QtWidgets import QMessageBox
        id_reserva = self._abono_seleccionado
        if not id_reserva:
            QMessageBox.warning(self, "Aviso", "Seleccione una reserva para abonar")
            return
        monto = self.input_abono_abono.text().strip()
        metodo = self.metodo_cb.currentText()
        if not monto:
            QMessageBox.warning(self, "Error", "Ingrese un monto")
            return
        try:
            monto_float = float(monto)
        except ValueError:
            QMessageBox.warning(self, "Error", "El monto debe ser un número válido")
            return
        if monto_float <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
            return
        placeholder = "%s" if not getattr(self.db_manager, 'offline', False) else "?"
        valor_query = f'''
            SELECT ra.id_estado_reserva, a.valor, ra.saldo_pendiente
            FROM Reserva_alquiler ra
            JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler
            WHERE ra.id_reserva = {placeholder}
        '''
        valor_result = self.db_manager.execute_query(valor_query, (id_reserva,))
        if not valor_result:
            QMessageBox.critical(self, "Error", "No se pudo obtener información de la reserva")
            return
        estado_reserva = valor_result[0][0]
        valor_total = valor_result[0][1]
        saldo_pendiente = valor_result[0][2]
        if estado_reserva != 2:
            QMessageBox.warning(self, "Aviso", "La reserva debe estar aprobada para registrar un abono")
            return
        abonos_query = f"SELECT COALESCE(SUM(valor), 0) FROM Abono_reserva WHERE id_reserva = {placeholder}"
        abonos_result = self.db_manager.execute_query(abonos_query, (id_reserva,))
        abonado_anterior = abonos_result[0][0] if abonos_result and abonos_result[0] else 0
        if abonado_anterior == 0:
            monto_minimo = float(valor_total) * 0.30
            if monto_float < monto_minimo:
                QMessageBox.warning(self, "Error", f"El primer abono debe ser al menos el 30% del valor total (${monto_minimo:,.0f})")
                return
        saldo_pendiente_float = float(saldo_pendiente)
        if monto_float > saldo_pendiente_float:
            QMessageBox.warning(self, "Error", f"El monto excede el saldo pendiente (${saldo_pendiente_float:,.0f})")
            return
        # Registrar abono
        try:
            insert_abono = '''INSERT INTO Abono_reserva (id_reserva, valor, metodo_pago, fecha_abono) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)'''
            self.db_manager.execute_query(insert_abono, (id_reserva, monto_float, metodo), fetch=False)
            # Actualizar saldo pendiente en Reserva_alquiler
            update_saldo = '''UPDATE Reserva_alquiler SET saldo_pendiente = saldo_pendiente - %s WHERE id_reserva = %s'''
            self.db_manager.execute_query(update_saldo, (monto_float, id_reserva), fetch=False)
            if metodo == "Efectivo":
                QMessageBox.information(
                    self,
                    "Aviso",
                    "Abono registrado. Debe acercarse a la sucursal para realizar el pago en efectivo.",
                )
            else:
                self._mostrar_pasarela_pago(monto_float, metodo)
                QMessageBox.information(self, "Éxito", "Abono registrado correctamente")
            self._cargar_reservas_pendientes()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el abono: {exc}")

    def _build_tab_cambiar_contrasena(self):
        from PyQt5.QtWidgets import QFormLayout, QLineEdit, QPushButton, QMessageBox
        layout = QFormLayout(self.tab_cambiar)
        self.input_actual = QLineEdit(); self.input_actual.setEchoMode(QLineEdit.Password)
        self.input_nueva = QLineEdit(); self.input_nueva.setEchoMode(QLineEdit.Password)
        self.input_confirmar = QLineEdit(); self.input_confirmar.setEchoMode(QLineEdit.Password)
        btn_cambiar = QPushButton("Cambiar")
        btn_cambiar.clicked.connect(self._cambiar_contrasena)
        layout.addRow("Contraseña actual:", self.input_actual)
        layout.addRow("Nueva contraseña:", self.input_nueva)
        layout.addRow("Confirmar nueva contraseña:", self.input_confirmar)
        layout.addRow(btn_cambiar)

    def _cambiar_contrasena(self):
        from PyQt5.QtWidgets import QMessageBox
        actual = self.input_actual.text()
        nueva = self.input_nueva.text()
        confirmar = self.input_confirmar.text()
        if not actual or not nueva or not confirmar:
            QMessageBox.warning(self, "Error", "Complete todos los campos")
            return
        if nueva != confirmar:
            QMessageBox.warning(self, "Error", "La nueva contraseña y la confirmación no coinciden")
            return
        from src.auth import AuthManager
        auth = AuthManager(self.db_manager)
        usuario = self.user_data.get("usuario")
        resultado = auth.cambiar_contrasena(usuario, actual, nueva)
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente")
            self.input_actual.clear()
            self.input_nueva.clear()
            self.input_confirmar.clear()
        else:
            QMessageBox.warning(self, "Error", str(resultado))

    def _build_tab_perfil(self):
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout
        id_cliente = self.user_data.get("id_cliente")
        layout = QVBoxLayout(self.tab_perfil)
        label = QLabel("Editar perfil")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)
        # Obtener datos actuales
        placeholder = "%s" if not getattr(self.db_manager, 'offline', False) else "?"
        datos = self.db_manager.execute_query(
            f"SELECT nombre, telefono, direccion, correo FROM Cliente WHERE id_cliente = {placeholder}",
            (id_cliente,),
        )
        nombre = datos[0][0] if datos else ""
        telefono = datos[0][1] if datos else ""
        direccion = datos[0][2] if datos else ""
        correo = datos[0][3] if datos else ""
        form = QFormLayout()
        self.entry_nombre = QLineEdit(nombre)
        self.entry_telefono = QLineEdit(telefono)
        self.entry_direccion = QLineEdit(direccion)
        self.entry_correo = QLineEdit(correo)
        form.addRow("Nombre:", self.entry_nombre)
        form.addRow("Teléfono:", self.entry_telefono)
        form.addRow("Dirección:", self.entry_direccion)
        form.addRow("Correo:", self.entry_correo)
        layout.addLayout(form)
        btn_guardar = QPushButton("Guardar cambios")
        def guardar():
            try:
                ok = self.db_manager.update_cliente_info_both(
                    id_cliente,
                    self.entry_nombre.text(),
                    self.entry_telefono.text(),
                    self.entry_direccion.text(),
                    self.entry_correo.text(),
                )
                if ok:
                    QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente (ambas bases)")
                else:
                    QMessageBox.critical(self, "Error", "No se pudo actualizar el perfil en ambas bases")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el perfil: {exc}")
        btn_guardar.clicked.connect(guardar)
        layout.addWidget(btn_guardar)

    def _cancelar_reserva_card(self, id_reserva):
        from PyQt5.QtWidgets import QMessageBox
        placeholder = "%s" if not getattr(self.db_manager, 'offline', False) else "?"
        estado_query = f"SELECT id_estado_reserva FROM Reserva_alquiler WHERE id_reserva = {placeholder}"
        estado = self.db_manager.execute_query(estado_query, (id_reserva,))
        if estado and estado[0][0] != 1:  # Solo permite cancelar si está 'Pendiente'
            QMessageBox.warning(self, "Aviso", "Solo puedes cancelar reservas en estado 'Pendiente'.")
            return
        query = f"UPDATE Reserva_alquiler SET id_estado_reserva = 3 WHERE id_reserva = {placeholder}"
        try:
            self.db_manager.execute_query(query, (id_reserva,), fetch=False)
            QMessageBox.information(self, "Éxito", "Reserva cancelada")
            self._cargar_reservas_cliente()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo cancelar la reserva: {exc}")

    def _editar_reserva_card(self, id_reserva):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QDateEdit, QMessageBox
        from PyQt5.QtCore import QDate, Qt
        from datetime import datetime
        placeholder = "%s" if not getattr(self.db_manager, 'offline', False) else "?"
        reserva_query = '''
            SELECT a.fecha_hora_salida, a.fecha_hora_entrada, a.id_vehiculo, a.id_seguro, a.id_descuento, a.valor
            FROM Reserva_alquiler ra 
            JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler 
            WHERE ra.id_reserva = %s
        '''
        reserva_data = self.db_manager.execute_query(reserva_query, (id_reserva,))
        if not reserva_data:
            QMessageBox.critical(self, "Error", "No se pudo obtener la información de la reserva.")
            return
        (
            salida_actual,
            entrada_actual,
            id_vehiculo,
            id_seguro,
            id_descuento,
            valor_actual,
        ) = reserva_data[0]
        def formatear_fecha(fecha):
            if isinstance(fecha, str):
                try:
                    return datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    return datetime.strptime(fecha, "%Y-%m-%d %H:%M")
            return fecha
        salida_dt = formatear_fecha(salida_actual)
        entrada_dt = formatear_fecha(entrada_actual)
        dlg = QDialog(self)
        dlg.setWindowTitle("Editar fechas de reserva")
        dlg.setModal(True)
        dlg.resize(400, 300)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Editar Fechas de Reserva"))
        # Fecha y hora salida
        layout.addWidget(QLabel("Nueva fecha y hora salida:"))
        salida_row = QHBoxLayout()
        salida_date = QDateEdit()
        salida_date.setCalendarPopup(True)
        salida_date.setDate(QDate(salida_dt.year, salida_dt.month, salida_dt.day))
        salida_row.addWidget(salida_date)
        horas_12 = [f"{h:02d}" for h in range(1, 13)]
        minutos = ["00", "15", "30", "45"]
        ampm = ["AM", "PM"]
        salida_hora_cb = QComboBox(); salida_hora_cb.addItems(horas_12)
        salida_min_cb = QComboBox(); salida_min_cb.addItems(minutos)
        salida_ampm_cb = QComboBox(); salida_ampm_cb.addItems(ampm)
        # Set default hour/min/ampm
        hora_salida = salida_dt.hour
        if hora_salida == 0:
            salida_hora_cb.setCurrentText("12"); salida_ampm_cb.setCurrentText("AM")
        elif hora_salida < 12:
            salida_hora_cb.setCurrentText(f"{hora_salida:02d}"); salida_ampm_cb.setCurrentText("AM")
        elif hora_salida == 12:
            salida_hora_cb.setCurrentText("12"); salida_ampm_cb.setCurrentText("PM")
        else:
            salida_hora_cb.setCurrentText(f"{hora_salida-12:02d}"); salida_ampm_cb.setCurrentText("PM")
        salida_min_cb.setCurrentText(f"{salida_dt.minute:02d}")
        salida_row.addWidget(salida_hora_cb)
        salida_row.addWidget(QLabel(":"))
        salida_row.addWidget(salida_min_cb)
        salida_row.addWidget(salida_ampm_cb)
        layout.addLayout(salida_row)
        # Fecha y hora entrada
        layout.addWidget(QLabel("Nueva fecha y hora entrada:"))
        entrada_row = QHBoxLayout()
        entrada_date = QDateEdit()
        entrada_date.setCalendarPopup(True)
        entrada_date.setDate(QDate(entrada_dt.year, entrada_dt.month, entrada_dt.day))
        entrada_row.addWidget(entrada_date)
        entrada_hora_cb = QComboBox(); entrada_hora_cb.addItems(horas_12)
        entrada_min_cb = QComboBox(); entrada_min_cb.addItems(minutos)
        entrada_ampm_cb = QComboBox(); entrada_ampm_cb.addItems(ampm)
        hora_entrada = entrada_dt.hour
        if hora_entrada == 0:
            entrada_hora_cb.setCurrentText("12"); entrada_ampm_cb.setCurrentText("AM")
        elif hora_entrada < 12:
            entrada_hora_cb.setCurrentText(f"{hora_entrada:02d}"); entrada_ampm_cb.setCurrentText("AM")
        elif hora_entrada == 12:
            entrada_hora_cb.setCurrentText("12"); entrada_ampm_cb.setCurrentText("PM")
        else:
            entrada_hora_cb.setCurrentText(f"{hora_entrada-12:02d}"); entrada_ampm_cb.setCurrentText("PM")
        entrada_min_cb.setCurrentText(f"{entrada_dt.minute:02d}")
        entrada_row.addWidget(entrada_hora_cb)
        entrada_row.addWidget(QLabel(":"))
        entrada_row.addWidget(entrada_min_cb)
        entrada_row.addWidget(entrada_ampm_cb)
        layout.addLayout(entrada_row)
        # Etiqueta valor actual
        valor_label = QLabel(f"Valor actual: ${valor_actual:,.0f}")
        valor_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        layout.addWidget(valor_label)
        # Botón guardar
        btn_guardar = QPushButton("Guardar cambios")
        def get_24h(date, hora_cb, min_cb, ampm_cb):
            h = int(hora_cb.currentText())
            m = int(min_cb.currentText())
            ampm = ampm_cb.currentText()
            if ampm == "PM" and h != 12:
                h += 12
            if ampm == "AM" and h == 12:
                h = 0
            return f"{date.date().toString('yyyy-MM-dd')} {h:02d}:{m:02d}"
        def guardar():
            try:
                nueva_salida = get_24h(salida_date, salida_hora_cb, salida_min_cb, salida_ampm_cb)
                nueva_entrada = get_24h(entrada_date, entrada_hora_cb, entrada_min_cb, entrada_ampm_cb)
                fmt = "%Y-%m-%d %H:%M"
                fecha_salida_dt = datetime.strptime(nueva_salida, fmt)
                fecha_entrada_dt = datetime.strptime(nueva_entrada, fmt)
                if fecha_entrada_dt <= fecha_salida_dt:
                    QMessageBox.warning(dlg, "Error", "La fecha de entrada debe ser posterior a la de salida.")
                    return
                # Actualizar en la base de datos
                update_query = f"""
                    UPDATE Alquiler SET fecha_hora_salida = %s, fecha_hora_entrada = %s WHERE id_vehiculo = %s
                """
                self.db_manager.execute_query(update_query, (nueva_salida, nueva_entrada, id_vehiculo), fetch=False)
                QMessageBox.information(dlg, "Éxito", "Fechas actualizadas correctamente.")
                dlg.accept()
                self._cargar_reservas_cliente()
            except Exception as exc:
                QMessageBox.critical(dlg, "Error", f"No se pudo actualizar la reserva: {exc}")
        btn_guardar.clicked.connect(guardar)
        layout.addWidget(btn_guardar)
        dlg.exec_() 