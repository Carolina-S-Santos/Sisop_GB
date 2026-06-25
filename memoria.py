from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from config import TAMANHO_PAGINA_BYTES, TOTAL_FRAMES
from processo import Processo


@dataclass(frozen=True)
class PaginaResidente:
    pid: int
    pagina: int


class MemoriaVirtual:
    def __init__(self) -> None:
        self._processos: Dict[int, Processo] = {}

    def registrar_processo(self, processo: Processo) -> None:
        if processo.pid in self._processos:
            raise ValueError(f"Ja existe processo com PID {processo.pid}.")
        self._processos[processo.pid] = processo

    def obter_processo(self, pid: int) -> Processo:
        try:
            return self._processos[pid]
        except KeyError as exc:
            raise ValueError(f"Processo P{pid} nao existe.") from exc

    def ler_pagina(self, pid: int, pagina: int) -> bytes:
        return self.obter_processo(pid).ler_pagina(pagina)

    @property
    def processos(self) -> List[Processo]:
        return list(self._processos.values())


class MemoriaPrincipal:
    def __init__(self) -> None:
        self._frames = [bytearray(TAMANHO_PAGINA_BYTES) for _ in range(TOTAL_FRAMES)]
        self._ocupantes: List[Optional[PaginaResidente]] = [None] * TOTAL_FRAMES

    def frame_livre(self) -> Optional[int]:
        for indice, ocupante in enumerate(self._ocupantes):
            if ocupante is None:
                return indice
        return None

    def carregar(self, frame: int, dados: bytes, ocupante: PaginaResidente) -> None:
        self._validar_frame(frame)
        if len(dados) != TAMANHO_PAGINA_BYTES:
            raise ValueError(
                f"Pagina deve ter exatamente {TAMANHO_PAGINA_BYTES} bytes."
            )

        self._frames[frame][:] = dados
        self._ocupantes[frame] = ocupante

    def ler(self, frame: int, deslocamento: int, quantidade: int) -> bytes:
        self._validar_frame(frame)
        if not 0 <= deslocamento < TAMANHO_PAGINA_BYTES:
            raise ValueError("Deslocamento fora do frame.")
        if quantidade < 0 or deslocamento + quantidade > TAMANHO_PAGINA_BYTES:
            raise ValueError("Leitura ultrapassa o limite do frame.")

        return bytes(self._frames[frame][deslocamento : deslocamento + quantidade])

    def ocupante(self, frame: int) -> Optional[PaginaResidente]:
        self._validar_frame(frame)
        return self._ocupantes[frame]

    @property
    def frames_usados(self) -> int:
        return sum(ocupante is not None for ocupante in self._ocupantes)

    def _validar_frame(self, frame: int) -> None:
        if not 0 <= frame < TOTAL_FRAMES:
            raise ValueError(f"Frame {frame} fora da memoria principal.")
