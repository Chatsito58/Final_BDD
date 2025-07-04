import pytest

try:  # Skip tests if customtkinter is not available
    import customtkinter  # noqa: F401
except Exception:  # pragma: no cover - dependency missing
    pytest.skip("customtkinter not installed", allow_module_level=True)

from src.db_manager import DBManager
from src.views.registro_ctk import RegistroCTk

def test_load_options_offline():
    db = DBManager()
    db.offline = True
    reg = RegistroCTk.__new__(RegistroCTk)
    reg.db = db
    reg._load_options()
    assert len(reg.tipo_doc_opts) > 0
    assert len(reg.cod_post_opts) > 0
