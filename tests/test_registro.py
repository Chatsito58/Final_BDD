import hashlib
import sys
import types
from types import SimpleNamespace

import pytest

dummy_ctk = types.ModuleType("customtkinter")

class DummyCTk:
    pass

dummy_ctk.CTk = DummyCTk
dummy_ctk.CTkEntry = object
dummy_ctk.StringVar = object
dummy_ctk.CTkOptionMenu = object
dummy_ctk.CTkLabel = object
dummy_ctk.CTkButton = object

sys.modules.setdefault("customtkinter", dummy_ctk)

from src.views import registro_ctk
from src.views.registro_ctk import RegistroCTk


class DummyEntry:
    def __init__(self, value=""):
        self.value = value

    def insert(self, index, text):
        self.value = text

    def get(self):
        return self.value


def setup_dummy_gui(monkeypatch):
    import customtkinter as ctk

    # Prevent Tk initialization
    monkeypatch.setattr(ctk.CTk, "__init__", lambda self, *a, **k: None)
    monkeypatch.setattr(ctk.CTk, "title", lambda self, *a, **k: None, raising=False)
    monkeypatch.setattr(ctk.CTk, "geometry", lambda self, *a, **k: None, raising=False)
    monkeypatch.setattr(ctk.CTk, "protocol", lambda self, *a, **k: None, raising=False)
    monkeypatch.setattr(ctk.CTk, "after", lambda self, *a, **k: None, raising=False)
    monkeypatch.setattr(RegistroCTk, "_start_status_updater", lambda self: None)
    monkeypatch.setattr(RegistroCTk, "_maximize_and_focus", lambda self: None)
    monkeypatch.setattr(RegistroCTk, "volver", lambda self, *a, **k: None)

    def fake_build(self):
        self.doc_entry = DummyEntry()
        self.nom_entry = DummyEntry()
        self.tel_entry = DummyEntry()
        self.dir_entry = DummyEntry()
        self.correo_entry = DummyEntry()
        self.infra_entry = DummyEntry("0")
        self.licencia_var = None
        self.cuenta_var = None
        self.tipo_doc_var = None
        self.cod_post_var = None
    monkeypatch.setattr(RegistroCTk, "_build_form", fake_build)


def test_registro_creates_and_checks_duplicate(triple_db_manager, monkeypatch):
    setup_dummy_gui(monkeypatch)
    messages = {"warnings": [], "infos": [], "errors": []}

    monkeypatch.setattr(
        registro_ctk,
        "messagebox",
        SimpleNamespace(
            showwarning=lambda title, msg: messages["warnings"].append(msg),
            showinfo=lambda title, msg: messages["infos"].append(msg),
            showerror=lambda title, msg: messages["errors"].append(msg),
        ),
    )

    reg = RegistroCTk(triple_db_manager)
    reg.doc_entry.insert(0, "123")
    reg.nom_entry.insert(0, "Alice")
    reg.correo_entry.insert(0, "alice@example.com")

    reg.registrar()

    clientes = triple_db_manager.execute_query(
        "SELECT id_cliente, documento, correo FROM Cliente WHERE correo = ?",
        ("alice@example.com",),
    )
    assert len(clientes) == 1
    cliente_id, documento, correo = clientes[0]
    assert documento == "123"
    assert correo == "alice@example.com"

    usuarios = triple_db_manager.execute_query(
        "SELECT usuario, contrasena, id_cliente FROM Usuario WHERE usuario = ?",
        ("alice@example.com",),
    )
    assert len(usuarios) == 1
    user, hashed_pwd, fk_cliente = usuarios[0]
    assert user == "alice@example.com"
    assert fk_cliente == cliente_id
    expected_hash = hashlib.sha256("123".encode()).hexdigest()
    assert hashed_pwd == expected_hash

    # Second attempt with same email should warn and not insert again
    reg.registrar()
    assert any("ya est\u00e1 registrado" in msg for msg in messages["warnings"])

    count_cliente = triple_db_manager.execute_query(
        "SELECT COUNT(*) FROM Cliente WHERE correo = ?", ("alice@example.com",)
    )[0][0]
    count_usuario = triple_db_manager.execute_query(
        "SELECT COUNT(*) FROM Usuario WHERE usuario = ?", ("alice@example.com",)
    )[0][0]
    assert count_cliente == 1
    assert count_usuario == 1
