import importlib
import inspect
from typing import Union

from config import CONTEXT_FILE
from loguru import logger
from services import _NoneModule


class _Context:

    def __init__(self, _context_obj: object) -> None:
        self._context_obj = _context_obj

    def __getattr__(self, name: str) -> Union["_Context", None, str, list, dict]:
        r = getattr(self._context_obj, name, None)

        if r is None:
            return f'"{name}" is not defined.'

        if isinstance(r, str):
            frame = inspect.currentframe()
            try:
                if frame is not None and frame.f_back is not None and frame.f_back.f_locals is not None:
                    caller_locals = frame.f_back.f_locals
                    r = r.format_map(caller_locals)
            finally:
                del frame

            return r

        elif isinstance(r, (list, dict)):
            return r

        elif isinstance(r, type):
            return _Context(r)

    def __getitem__(self, name: str) -> Union["_Context", None, str, list, dict]:
        r = getattr(self._context_obj, name, None)

        if r is None:
            return f'"{name}" is not defined.'

        if isinstance(r, str):
            frame = inspect.currentframe()
            try:
                if frame is not None and frame.f_back is not None and frame.f_back.f_locals is not None:
                    caller_locals = frame.f_back.f_locals
                    r = r.format_map(caller_locals)
            finally:
                del frame

            return r

        elif isinstance(r, (list, dict)):
            return r

        elif isinstance(r, type):
            return _Context(r)


def _get_context_obj() -> _Context | _NoneModule:
    if CONTEXT_FILE is not None:
        _module = importlib.import_module(CONTEXT_FILE)
        context = _Context(_module)
    else:
        context = _NoneModule("text", "CONTEXT_FILE")

    logger.debug("Context file loaded")
    return context


context: _Context | _NoneModule = _get_context_obj()
