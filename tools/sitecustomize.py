"""
Workaround local (Windows) para um problema de permissões ao criar diretórios temporários.

Em alguns ambientes, o `tempfile.mkdtemp()` cria pastas com ACL inválida (sem permissão
de escrita), o que quebra `venv`/`ensurepip`/`pip`.

Este patch substitui `tempfile.mkdtemp` e `tempfile.TemporaryDirectory` por versões
que criam a pasta com permissões padrão (via pathlib.mkdir) e depois fazem cleanup.

Nota: este ficheiro só é carregado quando o diretório `backend/tools` estiver no
`PYTHONPATH` (ver `backend/run.ps1`).
"""

from __future__ import annotations

import pathlib
import secrets
import shutil
import tempfile


_real_gettempdir = tempfile.gettempdir


def _safe_mkdtemp(suffix: str | None = None, prefix: str | None = None, dir: str | None = None) -> str:
    base_dir = pathlib.Path(dir or _real_gettempdir())
    base_dir.mkdir(parents=True, exist_ok=True)

    prefix = prefix or "tmp"
    suffix = suffix or ""

    for _ in range(200):
        name = f"{prefix}{secrets.token_hex(8)}{suffix}"
        path = base_dir / name
        try:
            path.mkdir(parents=False, exist_ok=False)
            return str(path)
        except FileExistsError:
            continue

    raise FileExistsError("Não foi possível criar diretório temporário.")


class _SafeTemporaryDirectory:
    def __init__(
        self,
        suffix: str | None = None,
        prefix: str | None = None,
        dir: str | None = None,
        ignore_cleanup_errors: bool = False,
    ):
        self.name = _safe_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
        self._ignore_cleanup_errors = ignore_cleanup_errors

    def __enter__(self) -> str:
        return self.name

    def __exit__(self, exc_type, exc, tb) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        shutil.rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)


tempfile.mkdtemp = _safe_mkdtemp  # type: ignore[assignment]
tempfile.TemporaryDirectory = _SafeTemporaryDirectory  # type: ignore[assignment]

