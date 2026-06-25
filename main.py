from __future__ import annotations

from config import (
    MEMORIA_PRINCIPAL_BYTES,
    MEMORIA_VIRTUAL_BYTES,
    TAMANHO_PAGINA_BYTES,
    TOTAL_FRAMES,
    TOTAL_PAGINAS_VIRTUAIS,
    formatar_bytes,
)
from memoria import MemoriaPrincipal, MemoriaVirtual
from mmu import MMU, ResultadoAcesso
from processo import Processo


def endereco(pagina: int, deslocamento: int = 0) -> int:
    return pagina * TAMANHO_PAGINA_BYTES + deslocamento


def criar_simulador() -> MMU:
    memoria_virtual = MemoriaVirtual()
    memoria_virtual.registrar_processo(Processo(1, "Editor", 96 * 1024))
    memoria_virtual.registrar_processo(Processo(2, "Navegador", 80 * 1024))

    return MMU(MemoriaPrincipal(), memoria_virtual)


def instrucoes_demo() -> list[tuple[int, int]]:
    return [
        (1, endereco(0, 0)),
        (1, endereco(0, 12)),
        (1, endereco(1, 32)),
        (2, endereco(0, 0)),
        (2, endereco(1, 64)),
        (1, endereco(2, 96)),
        (2, endereco(2, 128)),
        (1, endereco(3, 160)),
        (2, endereco(3, 192)),
        (1, endereco(1, 256)),
        (2, endereco(4, 224)),
        (1, endereco(4, 288)),
        (2, endereco(1, 320)),
        (1, endereco(0, 24)),
    ]


def imprimir_cabecalho(mmu: MMU) -> None:
    print("SIMULADOR DE MEMORIA VIRTUAL")
    print("=" * 31)
    print(
        "Memoria principal: "
        f"{formatar_bytes(MEMORIA_PRINCIPAL_BYTES)} "
        f"({TOTAL_FRAMES} frames de {formatar_bytes(TAMANHO_PAGINA_BYTES)})"
    )
    print(
        "Memoria virtual: "
        f"{formatar_bytes(MEMORIA_VIRTUAL_BYTES)}, com enderecamento virtual "
        "por processo "
        f"({TOTAL_PAGINAS_VIRTUAIS} paginas de {formatar_bytes(TAMANHO_PAGINA_BYTES)})"
    )
    print("Algoritmo de substituicao: LRU (Least Recently Used)")
    print()
    print("Processos cadastrados:")
    for processo in mmu.memoria_virtual.processos:
        print(
            f"- P{processo.pid} {processo.nome}: "
            f"{formatar_bytes(processo.tamanho_bytes)}, "
            f"{processo.quantidade_paginas} paginas validas"
        )
    print()
    print("DEMONSTRACAO DETERMINISTICA")
    print("-" * 31)


def imprimir_resultado(numero: int, resultado: ResultadoAcesso) -> None:
    status = "PAGE FAULT" if resultado.page_fault else "HIT"
    print(
        f"[{numero:02d}] Processo P{resultado.processo.pid} "
        f"({resultado.processo.nome}) | "
        f"VA={resultado.endereco_virtual} | "
        f"pagina={resultado.pagina_virtual} | "
        f"deslocamento={resultado.deslocamento} | "
        f"{status}"
    )
    print(
        f"     acao={resultado.acao} | "
        f"frame={resultado.frame} | "
        f"PA={resultado.endereco_fisico} | "
        f'conteudo="{resultado.conteudo}"'
    )


def imprimir_resumo(resultados: list[ResultadoAcesso], mmu: MMU) -> None:
    total = len(resultados)
    page_faults = sum(resultado.page_fault for resultado in resultados)
    hits = total - page_faults
    substituicoes = sum(resultado.vitima is not None for resultado in resultados)

    print()
    print("RESUMO:")
    print(f"Total de acessos: {total}")
    print(f"Hits: {hits}")
    print(f"Page faults: {page_faults}")
    print(f"Substituicoes por LRU: {substituicoes}")
    print(f"Frames usados: {mmu.memoria_principal.frames_usados}/{TOTAL_FRAMES}")


def main() -> None:
    mmu = criar_simulador()
    imprimir_cabecalho(mmu)

    resultados = []
    for numero, (pid, endereco_virtual) in enumerate(instrucoes_demo(), start=1):
        resultado = mmu.acessar(pid, endereco_virtual)
        resultados.append(resultado)
        imprimir_resultado(numero, resultado)

    imprimir_resumo(resultados, mmu)


if __name__ == "__main__":
    main()
