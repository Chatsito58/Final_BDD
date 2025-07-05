import types
import sys

# Create minimal customtkinter stub before importing RegistroCTk
class _Base:
    def __init__(self, *a, **k):
        pass
    def pack(self, *a, **k):
        pass
    def configure(self, *a, **k):
        pass

class CTk(_Base):
    def title(self, *a, **k):
        pass
    def geometry(self, *a, **k):
        pass
    def protocol(self, *a, **k):
        pass
    def after(self, *a, **k):
        pass
    def focus_force(self, *a, **k):
        pass
    def wm_state(self, *a, **k):
        pass
    def destroy(self):
        pass

class CTkEntry(_Base):
    def __init__(self, *a, **k):
        self.value = ""
    def get(self):
        return self.value
    def insert(self, index, text):
        self.value = text

class CTkLabel(_Base):
    pass

class CTkOptionMenu(_Base):
    def __init__(self, *a, variable=None, values=None, **k):
        self.variable = variable

class CTkButton(_Base):
    def __init__(self, *a, command=None, **k):
        self.command = command

class StringVar:
    def __init__(self, value=""):
        self._val = value
    def get(self):
        return self._val
    def set(self, val):
        self._val = val

dummy = types.SimpleNamespace(
    CTk=CTk,
    CTkEntry=CTkEntry,
    CTkLabel=CTkLabel,
    CTkOptionMenu=CTkOptionMenu,
    CTkButton=CTkButton,
    StringVar=StringVar,
)
sys.modules.setdefault("customtkinter", dummy)

from src.views.registro_ctk import RegistroCTk, messagebox
from src.auth import AuthManager

# Silence message boxes during tests
messagebox.showinfo = lambda *a, **k: None
messagebox.showwarning = lambda *a, **k: None
messagebox.showerror = lambda *a, **k: None


class DummyEntry:
    def __init__(self, value=""):
        self._value = value
    def get(self):
        return self._value


class DummyVar:
    def __init__(self, value=""):
        self._value = value
    def get(self):
        return self._value


def test_registro_and_login(triple_db_manager):
    # Build RegistroCTk instance without calling its __init__
    form = RegistroCTk.__new__(RegistroCTk)
    form.db = triple_db_manager
    form.on_back = None
    form.is_sqlite = getattr(triple_db_manager, "offline", False)
    form.tipo_doc_opts = [(1, "Cédula de Ciudadanía")]
    form.cod_post_opts = [("11001", "Bogotá (11001)")]
    form.licencia_opts = [1]
    form.cuenta_opts = []
    form.doc_entry = DummyEntry("123456789")
    form.nom_entry = DummyEntry("Juan Perez")
    form.tel_entry = DummyEntry("1234567")
    form.dir_entry = DummyEntry("Calle 1")
    form.correo_entry = DummyEntry("juan@example.com")
    form.infra_entry = DummyEntry("0")
    form.licencia_var = DummyVar("1")
    form.cuenta_var = None
    form.tipo_doc_var = DummyVar("Cédula de Ciudadanía")
    form.cod_post_var = DummyVar("Bogotá (11001)")
    form.volver = lambda *a, **k: None
    form.destroy = lambda *a, **k: None
    form._stop_status = False

    form.registrar()

    rows = triple_db_manager.execute_query(
        "SELECT id_cliente FROM Cliente WHERE correo = ?",
        ("juan@example.com",),
    )
    assert rows and len(rows) == 1
    cliente_id = rows[0][0]

    auth = AuthManager(triple_db_manager)
    user = auth.login("juan@example.com", "123456789")
    assert isinstance(user, dict)
    assert user["rol"] == "cliente"
    assert user["id_cliente"] == cliente_id
