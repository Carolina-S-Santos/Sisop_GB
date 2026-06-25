from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil

from config import MEMORIA_VIRTUAL_BYTES, TAMANHO_PAGINA_BYTES
from tabela_paginas import TabelaDePaginas


@dataclass
class Processo:
    pid: int
    nome: str
    tamanho_bytes: int
    tabela_paginas: TabelaDePaginas = field(init=False)
    _dados: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.pid <= 0:
            raise ValueError("PID deve ser positivo.")
        if not 1 <= self.tamanho_bytes <= MEMORIA_VIRTUAL_BYTES:
            raise ValueError(
                "Tamanho do processo deve ficar entre 1 byte e 1 MB."
            )

        self.tabela_paginas = TabelaDePaginas(self.quantidade_paginas)
        self._dados = self._gerar_dados()

    @property
    def quantidade_paginas(self) -> int:
        return ceil(self.tamanho_bytes / TAMANHO_PAGINA_BYTES)

    def validar_endereco(self, endereco_virtual: int) -> None:
        if not 0 <= endereco_virtual < self.tamanho_bytes:
            raise ValueError(
                f"Endereco virtual {endereco_virtual} fora do processo P{self.pid} "
                f"(0 a {self.tamanho_bytes - 1})."
            )

    def ler_pagina(self, pagina: int) -> bytes:
        self.tabela_paginas.obter(pagina)
        inicio = pagina * TAMANHO_PAGINA_BYTES
        fim = min(inicio + TAMANHO_PAGINA_BYTES, self.tamanho_bytes)

        bloco = bytearray(TAMANHO_PAGINA_BYTES)
        bloco[: fim - inicio] = self._dados[inicio:fim]
        return bytes(bloco)

    def _gerar_dados(self) -> bytes:
        dados = bytearray(self.tamanho_bytes)

        for pagina in range(self.quantidade_paginas):
            inicio = pagina * TAMANHO_PAGINA_BYTES
            fim = min(inicio + TAMANHO_PAGINA_BYTES, self.tamanho_bytes)
            padrao = f"{self.nome}-P{self.pid}-pagina-{pagina:03d}|".encode("utf-8")

            for posicao in range(inicio, fim):
                dados[posicao] = padrao[(posicao - inicio) % len(padrao)]

        return bytes(dados)
