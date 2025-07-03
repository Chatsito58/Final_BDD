import customtkinter as ctk


def build_tab_vehiculos(view, parent):
    """Create the vehicles tab showing available vehicles."""
    import tkinter as tk

    frame = ctk.CTkFrame(parent)
    frame.pack(expand=True, fill="both", padx=10, pady=10)
    ctk.CTkLabel(frame, text="Vehículos disponibles", font=("Arial", 18, "bold")).pack(pady=10)

    view.cards_vehiculos = ctk.CTkFrame(frame, fg_color="#E3F2FD")  # Azul pastel
    view.cards_vehiculos.pack(fill="both", expand=True, padx=10, pady=10)

    placeholder = '%s' if not view.db_manager.offline else '?'
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
            WHERE v.id_estado_vehiculo = 1 AND v.id_sucursal = {placeholder}
    """
    vehiculos = view.db_manager.execute_query(query, (view.user_data.get('id_sucursal'),))

    if not vehiculos:
        ctk.CTkLabel(view.cards_vehiculos, text="No hay vehículos disponibles", font=("Arial", 14)).pack(pady=20)
        return

    canvas = tk.Canvas(view.cards_vehiculos, bg="#E3F2FD")
    scrollbar = tk.Scrollbar(view.cards_vehiculos, orient="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#E3F2FD")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for vehiculo in vehiculos:
        (placa, modelo, kilometraje, n_chasis, marca, tipo_vehiculo, tarifa_dia,
         capacidad, combustible, color, transmision, cilindraje, blindaje,
         seguro_estado, seguro_desc, sucursal, sucursal_dir, sucursal_tel) = vehiculo

        card = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
        card.pack(fill="x", padx=10, pady=5)

        header_frame = ctk.CTkFrame(card, fg_color="#2196F3", corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header_frame, text=f"{marca} {modelo}",
                      font=("Arial", 16, "bold"), text_color="white").pack(pady=5)
        ctk.CTkLabel(header_frame, text=f"Placa: {placa}",
                      font=("Arial", 12), text_color="white").pack()

        main_frame = ctk.CTkFrame(card, fg_color="transparent")
        main_frame.pack(fill="x", padx=10, pady=5)

        row1 = ctk.CTkFrame(main_frame, fg_color="transparent")
        row1.pack(fill="x", pady=2)

        ctk.CTkLabel(row1, text=f"💰 Tarifa: ${tarifa_dia:,.0f}/día",
                      font=("Arial", 12, "bold"), text_color="#2E7D32").pack(side="left", padx=5)
        ctk.CTkLabel(row1, text=f"👥 Capacidad: {capacidad} personas",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
        ctk.CTkLabel(row1, text=f"⛽ Combustible: {combustible}",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)

        row2 = ctk.CTkFrame(main_frame, fg_color="transparent")
        row2.pack(fill="x", pady=2)

        ctk.CTkLabel(row2, text=f"🎨 Color: {color or 'No especificado'}",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
        ctk.CTkLabel(row2, text=f"⚙️ Transmisión: {transmision or 'No especificado'}",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
        ctk.CTkLabel(row2, text=f"🔧 Cilindraje: {cilindraje or 'No especificado'}",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)

        row3 = ctk.CTkFrame(main_frame, fg_color="transparent")
        row3.pack(fill="x", pady=2)

        ctk.CTkLabel(row3, text=f"🛡️ Blindaje: {blindaje or 'No especificado'}",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
        ctk.CTkLabel(row3, text=f"📊 Kilometraje: {kilometraje:,} km",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)
        ctk.CTkLabel(row3, text=f"🔒 Seguro: {seguro_estado or 'No especificado'}",
                      font=("Arial", 12), text_color="#424242").pack(side="left", padx=5)

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

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        vehiculo_info = (placa, modelo, marca, tipo_vehiculo, tarifa_dia)
        ctk.CTkButton(
            btn_frame,
            text="🚗 Reservar este vehículo",
            command=lambda v=vehiculo_info: view._abrir_nueva_reserva_vehiculo(v),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            font=("Arial", 12, "bold"),
        ).pack(pady=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
