import os
from config import KEYBOARDS, KEYBOARDS_DIR, HANDLERS, LANGUAGES, CONTEXT_FILE, HANDLERS_DIR
from utils.keyboards import _get_keyboards_obj

def test_get_keyboards_obj():
    result = _get_keyboards_obj()
    assert isinstance(result, dict)


def test_keyboards_loaded():
    assert len(KEYBOARDS) > 0

def test_keyboards_files_loaded():
    assert os.path.isdir(KEYBOARDS_DIR), "KEYBOARDS_DIR is not a valid directory"
    assert len(os.listdir(KEYBOARDS_DIR)) > 0, "No keyboard files found in KEYBOARDS_DIR"

def test_keyboards_files_format():
    keyboard_files = os.listdir(KEYBOARDS_DIR)
    for file in keyboard_files:
        if file.endswith('.py'):
            assert file != '__pycache__', f"Invalid file format for keyboard: {file}"

def test_handlers_exist():
    for handler in HANDLERS:
        handler_file = os.path.join(HANDLERS_DIR, handler + '.py')
        assert os.path.isfile(handler_file), f"Handler file '{handler}.py' not found"
