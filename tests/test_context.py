import pytest
from unittest.mock import MagicMock, patch
from utils.context import _Context, _NoneModule, _NotDefinedModule, _get_context_obj

# Тест для проверки получения атрибута из контекста
def test_context_get_attribute():
    context_obj = MagicMock()
    context_obj.some_attribute = "some_value"

    context = _Context(context_obj)

    assert context.some_attribute == "some_value"

# Тест для проверки получения отформатированной строки из контекста
def test_context_format_string():
    context_obj = MagicMock()
    context_obj.some_string = "Hello, {name}!"

    caller_locals = {'name': 'World'}
    context_obj.some_string = context_obj.some_string.format_map(caller_locals)

    assert context_obj.some_string == "Hello, World!"

test_context_format_string()

# Тест для проверки выброса исключения при попытке доступа к неопределенному модулю
def test_none_module_access():
    none_module = _NoneModule("test_module", "some_attribute")
    with pytest.raises(_NotDefinedModule):
        none_module.some_attribute

# Тест для проверки получения объекта контекста
@patch("utils.context.CONTEXT_FILE", new="test_module")
@patch("utils.context.importlib.import_module")
def test_get_context_obj(mock_import_module):
    context_module = MagicMock()
    context_module.some_attribute = "some_value"

    mock_import_module.return_value = context_module

    context = _get_context_obj()

    assert isinstance(context, _Context)
    assert context.some_attribute == "some_value"
