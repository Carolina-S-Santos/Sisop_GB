KIB = 1024
MIB = 1024 * KIB

MEMORIA_PRINCIPAL_BYTES = 64 * KIB
MEMORIA_VIRTUAL_BYTES = 1 * MIB
TAMANHO_PAGINA_BYTES = 8 * KIB

TOTAL_PAGINAS_VIRTUAIS = MEMORIA_VIRTUAL_BYTES // TAMANHO_PAGINA_BYTES
TOTAL_FRAMES = MEMORIA_PRINCIPAL_BYTES // TAMANHO_PAGINA_BYTES

BYTES_CONTEUDO_EXIBIDOS = 24


def formatar_bytes(valor: int) -> str:
    if valor % MIB == 0:
        return f"{valor // MIB} MB"
    if valor % KIB == 0:
        return f"{valor // KIB} KB"
    return f"{valor} bytes"
