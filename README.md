# Simulador de Memoria Virtual

Projeto em Python 3 para simular traducao de enderecos virtuais, page faults,
carregamento de paginas em frames livres e substituicao de paginas em memoria
principal.

## Como executar

```bash
python main.py
```

Para rodar os testes simples:

```bash
python -m unittest
```

Nao ha dependencias externas.

## Tamanhos usados

- Memoria principal: 64 KB.
- Memoria virtual: 1 MB, com enderecamento virtual por processo.
- Tamanho de pagina/frame: 8 KB.
- Paginas virtuais por processo: 128.
- Frames na memoria principal: 8.

Cada processo possui seu proprio espaco de enderecamento virtual, limitado a
1 MB. A demonstracao cria dois processos leves:

- P1 `Editor`, com 96 KB.
- P2 `Navegador`, com 80 KB.

Os dados dos processos sao preenchidos com um padrao textual por pagina, por
exemplo `Editor-P1-pagina-003|`. Assim, o simulador consegue mostrar o conteudo
realmente acessado apos a traducao de endereco.

## Organizacao do codigo

- `config.py`: constantes de tamanho de memoria, pagina e frames.
- `processo.py`: representa o processo leve e seus dados virtuais.
- `tabela_paginas.py`: tabela de paginas de cada processo.
- `memoria.py`: memoria principal e armazenamento virtual simulado.
- `mmu.py`: unidade de gerenciamento de memoria.
- `main.py`: demonstracao deterministica por linha de comando.
- `test_simulador.py`: testes unitarios simples.

## Funcionamento da MMU

A MMU recebe um PID e um endereco virtual. A cada acesso ela:

1. Valida se o endereco pertence ao processo.
2. Divide o endereco virtual em pagina virtual e deslocamento.
3. Consulta a tabela de paginas do processo.
4. Se a pagina esta presente, ocorre hit.
5. Se a pagina nao esta presente, ocorre page fault.
6. Em page fault, carrega a pagina em um frame livre quando ha espaco.
7. Se todos os frames estao ocupados, substitui uma pagina usando LRU.
8. Atualiza a tabela de paginas e calcula o endereco fisico final.
9. Le o conteudo na memoria principal e imprime o resultado.

## Algoritmo de substituicao: LRU

O algoritmo escolhido foi LRU, sigla para `Least Recently Used`.

Cada acesso recebe um contador de tempo crescente. Para cada frame, a MMU
guarda o instante do ultimo uso. Quando ocorre page fault e nao ha frame livre,
a MMU escolhe o frame com o menor instante de uso, ou seja, a pagina que ficou
mais tempo sem ser acessada.

Esse criterio torna a demonstracao facil de acompanhar: paginas acessadas
recentemente permanecem na memoria principal; paginas antigas sao substituidas.

## Exemplo de saida

Trecho da demonstracao:

```text
[01] Processo P1 (Editor) | VA=0 | pagina=0 | deslocamento=0 | PAGE FAULT
     acao=page fault: pagina carregada em frame livre | frame=0 | PA=0 | conteudo="Editor-P1-pagina-000|Edi"
[02] Processo P1 (Editor) | VA=12 | pagina=0 | deslocamento=12 | HIT
     acao=hit: pagina ja estava carregada | frame=0 | PA=12 | conteudo="agina-000|Editor-P1-pag"
[11] Processo P2 (Navegador) | VA=32992 | pagina=4 | deslocamento=224 | PAGE FAULT
     acao=page fault: substituiu P1 pagina 0 por P2 pagina 4, pois era a pagina menos recentemente usada (LRU) | frame=0 | PA=224 | conteudo="r-P2-pagina-004|Navegado"

RESUMO:
Total de acessos: 14
Hits: 3
Page faults: 11
Substituicoes por LRU: 3
Frames usados: 8/8
```

Durante a execucao completa, as primeiras instrucoes mostram carregamento em
frames livres. Depois que os 8 frames ficam ocupados, novas paginas provocam
substituicao pelo criterio LRU. Ao final, o simulador tambem exibe um resumo
com total de acessos, hits, page faults, substituicoes por LRU e frames usados.

## Pontos atendidos dos criterios de avaliacao

- Simula memoria principal de 64 KB.
- Simula memoria virtual de 1 MB, com enderecamento virtual por processo.
- Usa paginas e frames de 8 KB.
- Usa 128 paginas virtuais e 8 frames fisicos.
- Simula dois processos leves.
- Cada processo tem conteudo associado e exibido na saida.
- Mantem tabela de paginas por processo.
- Traduz endereco virtual para endereco fisico.
- Detecta hit e page fault.
- Carrega paginas em frames livres.
- Substitui paginas quando a memoria principal esta cheia.
- Implementa e documenta LRU.
- Exibe processo, endereco virtual, pagina, deslocamento, status, frame,
  endereco fisico e conteudo acessado a cada instrucao.
- Possui demonstracao deterministica e testes simples.
