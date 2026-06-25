import unittest

from config import TAMANHO_PAGINA_BYTES
from memoria import MemoriaPrincipal, MemoriaVirtual
from mmu import MMU
from processo import Processo


class SimuladorMemoriaVirtualTest(unittest.TestCase):
    def criar_mmu_com_processo(self) -> MMU:
        memoria_virtual = MemoriaVirtual()
        memoria_virtual.registrar_processo(Processo(1, "Teste", 10 * TAMANHO_PAGINA_BYTES))
        return MMU(MemoriaPrincipal(), memoria_virtual)

    def test_primeiro_acesso_falha_e_segundo_acesso_hit(self) -> None:
        mmu = self.criar_mmu_com_processo()

        primeiro = mmu.acessar(1, 0)
        segundo = mmu.acessar(1, 15)

        self.assertTrue(primeiro.page_fault)
        self.assertFalse(segundo.page_fault)
        self.assertEqual(primeiro.frame, segundo.frame)
        self.assertIn("Teste-P1-pagina-000", primeiro.conteudo)

    def test_lru_substitui_pagina_menos_recente(self) -> None:
        mmu = self.criar_mmu_com_processo()

        for pagina in range(8):
            mmu.acessar(1, pagina * TAMANHO_PAGINA_BYTES)

        mmu.acessar(1, 0)
        resultado = mmu.acessar(1, 8 * TAMANHO_PAGINA_BYTES)

        self.assertTrue(resultado.page_fault)
        self.assertIsNotNone(resultado.vitima)
        self.assertEqual(resultado.vitima.pagina, 1)
        self.assertIn(
            "substituiu P1 pagina 1 por P1 pagina 8",
            resultado.acao,
        )
        self.assertIn("menos recentemente usada (LRU)", resultado.acao)


if __name__ == "__main__":
    unittest.main()
