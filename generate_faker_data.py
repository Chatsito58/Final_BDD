# -*- coding: utf-8 -*-
#& "C:/Users/William Diaz/Final_BDD/venv/Scripts/pip.exe" install faker

"""Generate sample data for the Alquiler_vehiculos database using Faker."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

# General configuration
Faker.seed(12345)
fake = Faker("es_CO")

OUTPUT_FILE = Path("data/data_inserts_faker.sql")

# Existing records inserted manually in ``inserts_prueba.sql``
ALQUILER_OFFSET = 7
DET_FACTURA_OFFSET = 0

# Codigos postales from inserts_prueba.sql
CODIGOS_POSTALES = [
    "110111",
    "760001",
    "050001",
    "680001",
    "190001",
    "170001",
    "200001",
    "180001",
    "440001",
    "810001",
    "520001",
    "410001",
    "230001",
    "730001",
    "630001",
    "500001",
    "880001",
    "810010",
    "540001",
    "860001",
    "270001",
    "660001",
    "850001",
    "470001",
    "760033",
    "250001",
    "150001",
    "680005",
    "730006",
    "130001",
]

# Sets to keep uniqueness
used_documents: set[str] = set()
used_emails: set[str] = set()
used_phones: set[str] = set()
used_plates: set[str] = set()


def unique_numeric(length: int, pool: set[str]) -> str:
    while True:
        number = "".join(random.choices("0123456789", k=length))
        if number not in pool:
            pool.add(number)
            return number


def unique_email() -> str:
    while True:
        email = fake.email()
        if email not in used_emails:
            used_emails.add(email)
            return email


def unique_phone() -> str:
    return "3" + unique_numeric(9, used_phones)


def unique_document() -> str:
    return unique_numeric(10, used_documents)


def unique_plate() -> str:
    while True:
        letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        digits = "".join(random.choices("0123456789", k=3))
        plate = f"{letters}{digits}"
        if plate not in used_plates:
            used_plates.add(plate)
            return plate


# Data generators --------------------------------------------------------------

def generar_sucursales(num: int) -> tuple[list[str], list[tuple[str, int]]]:
    """Return ``num`` rows for la tabla ``Sucursal`` and manager info."""
    rows = []
    managers: list[tuple[str, int]] = []
    used_names: set[str] = set()
    for idx in range(1, num + 1):
        while True:
            nombre = f"Sucursal {fake.city()}"
            if nombre not in used_names:
                used_names.add(nombre)
                break
        direccion = fake.address().replace("\n", ", ")
        telefono = unique_phone()
        gerente = fake.name()
        codigo = random.choice(CODIGOS_POSTALES)
        rows.append(
            f"('{nombre}', '{direccion}', '{telefono}', '{gerente}', '{codigo}')"
        )
        managers.append((gerente, idx))
    return rows, managers


def generar_licencias(num: int) -> list[str]:
    rows = []
    for _ in range(num):
        inicio = fake.date_between(start_date="-9y", end_date="-1y")
        fin = inicio + timedelta(days=5 * 365)
        categoria = random.randint(1, 10)
        rows.append(f"('Vigente', '{inicio}', '{fin}', {categoria})")
    return rows


def generar_clientes(num: int, licencia_offset: int) -> list[str]:
    rows = []
    for idx in range(num):
        doc_type = random.randint(1, 3)
        doc = unique_document()
        nombre = fake.name()
        telefono = unique_phone()
        direccion = fake.address().replace("\n", ", ")
        correo = unique_email()
        id_licencia = licencia_offset + idx
        codigo = random.choice(CODIGOS_POSTALES)
        rows.append(
            f"('{doc}', '{nombre}', '{telefono}', '{direccion}', '{correo}', 0, {id_licencia}, {doc_type}, '{codigo}', NULL)"
        )
    return rows


def generar_empleados(total: int, managers: list[tuple[str, int]]) -> list[str]:
    """Return rows for ``Empleado`` ensuring one gerente per sucursal."""
    cargos = {
        1: "Administrador",
        2: "Gerente",
        3: "Ventas",
        4: "Caja",
        5: "Mantenimiento",
    }

    rows: list[str] = []

    # Admin principal
    doc = unique_document()
    salario = random.randint(3000000, 6000000)
    telefono = unique_phone()
    direccion = fake.address().replace("\n", ", ")
    correo = unique_email()
    doc_type = random.randint(1, 2)
    rows.append(
        f"('{doc}', '{fake.name()}', {salario}, '{cargos[1]}', '{telefono}', '{direccion}', '{correo}', 1, {doc_type}, 1)"
    )

    # Gerentes asociados a cada sucursal
    for nombre, sucursal in managers:
        doc = unique_document()
        salario = random.randint(2500000, 5000000)
        telefono = unique_phone()
        direccion = fake.address().replace("\n", ", ")
        correo = unique_email()
        doc_type = random.randint(1, 2)
        rows.append(
            f"('{doc}', '{nombre}', {salario}, '{cargos[2]}', '{telefono}', '{direccion}', '{correo}', {sucursal}, {doc_type}, 2)"
        )

    remaining = total - len(managers) - 1
    tipos_restantes = [3, 4, 5]
    for _ in range(remaining):
        tipo = random.choice(tipos_restantes)
        doc = unique_document()
        nombre = fake.name()
        salario = random.randint(1800000, 4000000)
        telefono = unique_phone()
        direccion = fake.address().replace("\n", ", ")
        correo = unique_email()
        sucursal = random.randint(1, len(managers))
        doc_type = random.randint(1, 2)
        rows.append(
            f"('{doc}', '{nombre}', {salario}, '{cargos[tipo]}', '{telefono}', '{direccion}', '{correo}', {sucursal}, {doc_type}, {tipo})"
        )

    return rows


def generar_talleres(num: int) -> list[str]:
    rows = []
    for _ in range(num):
        nombre = fake.company()
        direccion = fake.address().replace("\n", ", ")
        telefono = unique_phone()
        rows.append(f"('{nombre}', '{direccion}', '{telefono}')")
    return rows


def generar_vehiculos(num: int, total_sucursales: int, mantenimiento_ratio: float = 0.1) -> tuple[list[str], list[str]]:
    rows = []
    disponibles = []
    for _ in range(num):
        placa = unique_plate()
        n_chasis = 'CH' + unique_numeric(8, set())
        modelo = f"{fake.word().title()} {random.randint(2015, 2024)}"
        km = random.randint(0, 100000)
        marca = random.randint(1, 12)
        color = random.randint(1, 12)
        tipo = random.randint(1, 11)
        blindaje = random.randint(1, 10)
        transmision = random.randint(1, 5)
        cilindraje = random.randint(1, 11)
        seguro = random.randint(1, 10)
        estado = 2 if random.random() < mantenimiento_ratio else 1
        proveedor = 1
        sucursal = random.randint(1, total_sucursales)
        rows.append(
            f"('{placa}', '{n_chasis}', '{modelo}', {km}, {marca}, {color}, {tipo}, {blindaje}, {transmision}, {cilindraje}, {seguro}, {estado}, {proveedor}, {sucursal})"
        )
        if estado == 1:
            disponibles.append(placa)
    return rows, disponibles


def generar_mantenimientos(num: int, placas: list[str], total_talleres: int) -> list[str]:
    rows = []
    for _ in range(num):
        descripcion = fake.sentence(nb_words=4)
        fecha = fake.date_time_between(start_date="-2y", end_date="now")
        valor = random.randint(50000, 300000)
        tipo = random.randint(1, 2)
        taller = random.randint(1, total_talleres)
        placa = random.choice(placas)
        rows.append(
            f"('{descripcion}', '{fecha}', {valor}, {tipo}, {taller}, '{placa}')"
        )
    return rows


def generar_alquileres(num: int, placas: list[str], clientes: int, empleados: int, total_sucursales: int) -> tuple[list[str], list[dict]]:
    rows = []
    info = []
    for _ in range(num):
        fecha_salida = fake.date_time_between(start_date="-2y", end_date="now")
        duracion = random.randint(1, 10)
        fecha_entrada = fecha_salida + timedelta(days=duracion)
        valor = random.randint(100000, 300000)
        placa = random.choice(placas)
        cliente = random.randint(1, clientes)
        empleado = random.randint(1, empleados)
        sucursal = random.randint(1, total_sucursales)
        medio = random.randint(1, 3)
        estado = random.randint(1, 2)
        seguro = random.randint(1, 11)
        descuento = random.randint(1, 5)
        rows.append(
            f"('{fecha_salida}', {valor}, '{fecha_entrada}', '{placa}', {cliente}, {empleado}, {sucursal}, {medio}, {estado}, {seguro}, {descuento})"
        )
        info.append({"id_cliente": cliente, "placa": placa, "valor": valor, "fecha": fecha_salida})
    return rows, info


def generar_reservas(alquiler_info: list[dict], empleados: int, extra: int) -> tuple[list[str], dict[int, datetime]]:
    rows = []
    fechas = {}
    reserva_id = 1
    for data in alquiler_info:
        fecha = data["fecha"] - timedelta(days=random.randint(1, 30))
        abono = int(data["valor"] * 0.3)
        saldo = data["valor"] - abono
        empleado = random.randint(1, empleados)
        rows.append(
            f"('{fecha}', {abono}, {saldo}, 2, {reserva_id}, {empleado})"
        )
        fechas[reserva_id] = fecha
        reserva_id += 1

    for _ in range(extra):
        fecha = fake.date_time_between(start_date="-2y", end_date="now")
        abono = random.randint(30000, 150000)
        saldo = abono
        empleado = random.randint(1, empleados)
        rows.append(f"('{fecha}', {abono}, {saldo}, 1, NULL, {empleado})")
        fechas[reserva_id] = fecha
        reserva_id += 1
    return rows, fechas


def generar_abonos(num: int, fechas: dict[int, datetime]) -> list[str]:
    ids = list(fechas.keys())
    rows = []
    for _ in range(num):
        reserva = random.choice(ids)
        fecha = fechas[reserva] + timedelta(days=random.randint(1, 30))
        valor = random.randint(20000, 120000)
        medio = random.randint(1, 3)
        rows.append(f"({valor}, '{fecha}', {reserva}, {medio})")
    return rows


def generar_det_facturas(num: int) -> list[str]:
    """Return ``num`` rows for Det_factura."""
    rows = []
    for _ in range(num):
        valor = random.randint(80000, 350000)
        impuestos = int(valor * 0.19)
        rows.append(f"(1, {valor}, {impuestos})")
    return rows


def generar_facturas(
    alquiler_info: list[dict], det_offset: int, alquiler_offset: int
) -> list[str]:
    """Return rows for ``Factura``.

    ``det_offset`` and ``alquiler_offset`` account for existing records in
    ``Det_factura`` and ``Alquiler`` tables respectively.
    """

    rows = []
    for idx, data in enumerate(alquiler_info, start=1):
        valor = data["valor"]
        rows.append(
            f"({valor}, {alquiler_offset + idx}, {data['id_cliente']}, '{data['placa']}', {det_offset + idx})"
        )
    return rows


def generar_cuentas(num: int) -> tuple[list[str], list[str], list[str]]:
    cp_rows, cc_rows, c_rows = [], [], []
    for idx in range(1, num + 1):
        fecha = fake.date_time_between(start_date="-2y", end_date="now")
        valor = random.randint(50000, 500000)
        medio = random.randint(1, 3)
        tipo = random.randint(1, 2)
        cp_rows.append(f"('{fecha}', {valor}, 'Cuenta pagar {idx}', {medio}, {tipo}, 1)")
        fecha2 = fecha + timedelta(days=5)
        valor2 = random.randint(50000, 500000)
        cc_rows.append(f"('{fecha2}', {valor2}, 'Cuenta cobrar {idx}', {medio}, {tipo}, 1)")
        c_rows.append(f"({idx}, {idx})")
    return cp_rows, cc_rows, c_rows


# Write SQL file ---------------------------------------------------------------

COLUMNAS = {
    "Licencia_conduccion": [
        "estado",
        "fecha_emision",
        "fecha_vencimiento",
        "id_categoria",
    ],
    "Cliente": [
        "documento",
        "nombre",
        "telefono",
        "direccion",
        "correo",
        "infracciones",
        "id_licencia",
        "id_tipo_documento",
        "id_codigo_postal",
        "id_cuenta",
    ],
    "Empleado": [
        "documento",
        "nombre",
        "salario",
        "cargo",
        "telefono",
        "direccion",
        "correo",
        "id_sucursal",
        "id_tipo_documento",
        "id_tipo_empleado",
    ],
    "Sucursal": [
        "nombre",
        "direccion",
        "telefono",
        "gerente",
        "id_codigo_postal",
    ],
    "Taller_mantenimiento": ["nombre", "direccion", "telefono"],
    "Vehiculo": [
        "placa",
        "n_chasis",
        "modelo",
        "kilometraje",
        "id_marca",
        "id_color",
        "id_tipo_vehiculo",
        "id_blindaje",
        "id_transmision",
        "id_cilindraje",
        "id_seguro_vehiculo",
        "id_estado_vehiculo",
        "id_proveedor",
        "id_sucursal",
    ],
    "Mantenimiento_vehiculo": [
        "descripcion",
        "fecha_hora",
        "valor",
        "id_tipo",
        "id_taller",
        "id_vehiculo",
    ],
    "Alquiler": [
        "fecha_hora_salida",
        "valor",
        "fecha_hora_entrada",
        "id_vehiculo",
        "id_cliente",
        "id_empleado",
        "id_sucursal",
        "id_medio_pago",
        "id_estado",
        "id_seguro",
        "id_descuento",
    ],
    "Reserva_alquiler": [
        "fecha_hora",
        "abono",
        "saldo_pendiente",
        "id_estado_reserva",
        "id_alquiler",
        "id_empleado",
    ],
    "Abono_reserva": ["valor", "fecha_hora", "id_reserva", "id_medio_pago"],
    "Det_factura": ["id_servicio", "valor", "impuestos"],
    "Factura": [
        "valor",
        "id_alquiler",
        "id_cliente",
        "id_vehiculo",
        "id_det_factura",
    ],
    "Cuenta_pagar": [
        "fecha_hora",
        "valor",
        "descripcion",
        "id_medio_pago",
        "id_tipo_entidad",
        "id_entidad",
    ],
    "Cuenta_cobrar": [
        "fecha_hora",
        "valor",
        "descripcion",
        "id_medio_pago",
        "id_tipo_entidad",
        "id_entidad",
    ],
    "Cuenta": ["id_cuenta_pagar", "id_cuenta_cobrar"],
}


def escribir_inserts(tabla: str, filas: list[str], file):
    file.write(f"-- Tabla: {tabla}\n")
    columnas = ", ".join(COLUMNAS[tabla])
    if filas:
        file.write(f"INSERT INTO {tabla} ({columnas}) VALUES\n    ")
        file.write(",\n    ".join(filas))
        file.write(";\n\n")


def main() -> None:
    licencias = generar_licencias(5000)
    clientes = generar_clientes(5000, licencia_offset=2)
    sucursales, gerentes = generar_sucursales(20)
    empleados = generar_empleados(1000, gerentes)
    talleres = generar_talleres(100)
    vehiculos, disponibles = generar_vehiculos(500, len(gerentes))
    mantenimientos = generar_mantenimientos(3000, disponibles, len(talleres))
    alquileres, info = generar_alquileres(4000, disponibles, 5001, 1005, len(gerentes))
    reservas, fechas = generar_reservas(info, 1005, extra=1000)
    abonos = generar_abonos(12000, fechas)
    dets = generar_det_facturas(len(info))
    facturas = generar_facturas(
        info, det_offset=DET_FACTURA_OFFSET, alquiler_offset=ALQUILER_OFFSET
    )
    cp, cc, c = generar_cuentas(1000)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        escribir_inserts("Licencia_conduccion", licencias, f)
        escribir_inserts("Cliente", clientes, f)
        escribir_inserts("Sucursal", sucursales, f)
        escribir_inserts("Empleado", empleados, f)
        escribir_inserts("Taller_mantenimiento", talleres, f)
        escribir_inserts("Vehiculo", vehiculos, f)
        escribir_inserts("Mantenimiento_vehiculo", mantenimientos, f)
        escribir_inserts("Alquiler", alquileres, f)
        escribir_inserts("Reserva_alquiler", reservas, f)
        escribir_inserts("Abono_reserva", abonos, f)
        escribir_inserts("Det_factura", dets, f)
        escribir_inserts("Factura", facturas, f)
        escribir_inserts("Cuenta_pagar", cp, f)
        escribir_inserts("Cuenta_cobrar", cc, f)
        escribir_inserts("Cuenta", c, f)


if __name__ == "__main__":
    main()