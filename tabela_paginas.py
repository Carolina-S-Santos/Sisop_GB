from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import TOTAL_PAGINAS_VIRTUAIS


@dataclass
class EntradaTabelaPaginas:
    pagina: int
    presente: bool = False
    frame: Optional[int] = None
    ultimo_acesso: int = 0


class TabelaDePaginas:
    def __init__(self, paginas_validas: int):
        if not 1 <= paginas_validas <= TOTAL_PAGINAS_VIRTUAIS:
            raise ValueError(
                f"Quantidade de paginas deve ficar entre 1 e {TOTAL_PAGINAS_VIRTUAIS}."
            )

        self.paginas_validas = paginas_validas
        self._entradas = [
            EntradaTabelaPaginas(pagina)
            for pagina in range(TOTAL_PAGINAS_VIRTUAIS)
        ]

    def obter(self, pagina: int) -> EntradaTabelaPaginas:
        if not 0 <= pagina < self.paginas_validas:
            raise ValueError(
                f"Pagina virtual {pagina} fora do espaco do processo "
                f"(0 a {self.paginas_validas - 1})."
            )
        return self._entradas[pagina]

    def marcar_presente(self, pagina: int, frame: int, tempo: int) -> None:
        entrada = self.obter(pagina)
        entrada.presente = True
        entrada.frame = frame
        entrada.ultimo_acesso = tempo

    def marcar_ausente(self, pagina: int) -> None:
        entrada = self.obter(pagina)
        entrada.presente = False
        entrada.frame = None

    def registrar_acesso(self, pagina: int, tempo: int) -> None:
        self.obter(pagina).ultimo_acesso = tempo
