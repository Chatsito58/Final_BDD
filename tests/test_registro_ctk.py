import pytest
import unittest
import tempfile
import os
import sys

try:  # Skip tests if customtkinter is not available
    import customtkinter  # noqa: F401
except Exception:  # pragma: no cover - dependency missing
    pytest.skip("customtkinter not installed", allow_module_level=True)

from src.triple_db_manager import TripleDBManager
from src.views.registro_ctk import RegistroCTk

def test_load_options_offline():
    db = TripleDBManager()
    db.offline = True
    reg = RegistroCTk.__new__(RegistroCTk)
    reg.db = db
    reg._load_options()
    assert len(reg.tipo_doc_opts) > 0
    assert len(reg.cod_post_opts) > 0
