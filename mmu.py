from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from config import BYTES_CONTEUDO_EXIBIDOS, TAMANHO_PAGINA_BYTES, TOTAL_FRAMES
from memoria import MemoriaPrincipal, MemoriaVirtual, PaginaResidente
from processo import Processo


@dataclass
class ResultadoAcesso:
    processo: Processo
    endereco_virtual: int
    pagina_virtual: int
    deslocamento: int
    page_fault: bool
    frame: int
    endereco_fisico: int
    conteudo: str
    acao: str
    vitima: Optional[PaginaResidente] = None


class MMU:
    def __init__(
        self,
        memoria_principal: MemoriaPrincipal,
        memoria_virtual: MemoriaVirtual,
    ) -> None:
        self.memoria_principal = memoria_principal
        self.memoria_virtual = memoria_virtual
        self._tempo = 0
        self._ultimo_uso_por_frame: Dict[int, int] = {}

    def acessar(self, pid: int, endereco_virtual: int) -> ResultadoAcesso:
        processo = self.memoria_virtual.obter_processo(pid)
        processo.validar_endereco(endereco_virtual)

        pagina_virtual, deslocamento = divmod(
            endereco_virtual,
            TAMANHO_PAGINA_BYTES,
        )
        entrada = processo.tabela_paginas.obter(pagina_virtual)

        self._tempo += 1
        page_fault = not entrada.presente
        vitima = None

        if entrada.presente:
            if entrada.frame is None:
                raise RuntimeError("Entrada presente sem frame associado.")
            frame = entrada.frame
            acao = "hit: pagina ja estava carregada"
        else:
            frame_livre = self.memoria_principal.frame_livre()

            if frame_livre is not None:
                frame = frame_livre
                acao = "page fault: pagina carregada em frame livre"
            else:
                frame, vitima = self._selecionar_vitima_lru()
                processo_vitima = self.memoria_virtual.obter_processo(vitima.pid)
                processo_vitima.tabela_paginas.marcar_ausente(vitima.pagina)
                acao = (
                    "page fault: substituiu "
                    f"P{vitima.pid} pagina {vitima.pagina} por "
                    f"P{pid} pagina {pagina_virtual}, pois era a pagina menos "
                    "recentemente usada (LRU)"
                )

            dados = self.memoria_virtual.ler_pagina(pid, pagina_virtual)
            self.memoria_principal.carregar(
                frame,
                dados,
                PaginaResidente(pid, pagina_virtual),
            )
            processo.tabela_paginas.marcar_presente(pagina_virtual, frame, self._tempo)

        self._ultimo_uso_por_frame[frame] = self._tempo
        processo.tabela_paginas.registrar_acesso(pagina_virtual, self._tempo)

        endereco_fisico = frame * TAMANHO_PAGINA_BYTES + deslocamento
        quantidade = min(
            BYTES_CONTEUDO_EXIBIDOS,
            TAMANHO_PAGINA_BYTES - deslocamento,
            processo.tamanho_bytes - endereco_virtual,
        )
        conteudo = self._formatar_conteudo(
            self.memoria_principal.ler(frame, deslocamento, quantidade)
        )

        return ResultadoAcesso(
            processo=processo,
            endereco_virtual=endereco_virtual,
            pagina_virtual=pagina_virtual,
            deslocamento=deslocamento,
            page_fault=page_fault,
            frame=frame,
            endereco_fisico=endereco_fisico,
            conteudo=conteudo,
            acao=acao,
            vitima=vitima,
        )

    def _selecionar_vitima_lru(self) -> Tuple[int, PaginaResidente]:
        if len(self._ultimo_uso_por_frame) < TOTAL_FRAMES:
            raise RuntimeError("LRU chamado antes de preencher todos os frames.")

        frame = min(self._ultimo_uso_por_frame, key=self._ultimo_uso_por_frame.get)
        vitima = self.memoria_principal.ocupante(frame)
        if vitima is None:
            raise RuntimeError("Frame selecionado pelo LRU esta vazio.")

        return frame, vitima

    @staticmethod
    def _formatar_conteudo(dados: bytes) -> str:
        partes = []
        for byte in dados:
            if byte == 0:
                partes.append("\\0")
            elif 32 <= byte <= 126:
                partes.append(chr(byte))
            else:
                partes.append(f"\\x{byte:02x}")
        return "".join(partes)
