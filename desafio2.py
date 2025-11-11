import logging
import itertools
from collections import deque, defaultdict
import matplotlib.pyplot as plt
import time

class VerificadorDesafio2:
    def __init__(self, habilidades, habilidades_criticas):
        self.habilidades = habilidades
        self.habilidades_criticas = habilidades_criticas
        self.ids = set(habilidades.keys())
        self.resultados = []
        self.relatorios_validacao = None

    def validar_grafo(self):
        visitados = set()
        stack = set()
        ciclos = []
        pre_reqs_inexistentes = []

        def dfs(n, caminho):
            visitados.add(n)
            stack.add(n)
            for pre in self.habilidades[n]['Pre_Reqs']:
                if pre not in self.ids:
                    pre_reqs_inexistentes.append((n, pre))
                elif pre not in visitados:
                    dfs(pre, caminho + [pre])
                elif pre in stack:
                    ciclos.append(caminho + [pre])
            stack.remove(n)
        for hab in self.habilidades:
            if hab not in visitados:
                dfs(hab, [hab])
        self.relatorios_validacao = {
            'valido': not ciclos and not pre_reqs_inexistentes,
            'ciclos': ciclos,
            'pre_requisitos_inexistentes': pre_reqs_inexistentes
        }
        return self.relatorios_validacao

    def calcular_custo_ordem(self, ordem):
        """
        Calcula o custo total para uma dada permutação, garantindo que o tempo
        de cada habilidade seja contado apenas uma vez.
        """
        tempo_total = 0
        habilidades_adquiridas = set()

        # Função auxiliar para adquirir uma habilidade e suas dependências recursivamente
        def adquirir_habilidade(hab_id):
            nonlocal tempo_total, habilidades_adquiridas
            
            # Se já foi adquirida, não há custo.
            if hab_id in habilidades_adquiridas:
                return

            # Primeiro, garante que todos os pré-requisitos sejam adquiridos
            for pre_req in self.habilidades[hab_id].get('Pre_Reqs', []):
                adquirir_habilidade(pre_req)

            # Após garantir os pré-requisitos, adquire a habilidade atual
            # (se ela ainda não tiver sido adquirida como pré-requisito de outra)
            if hab_id not in habilidades_adquiridas:
                tempo_total += self.habilidades[hab_id]['Tempo']
                habilidades_adquiridas.add(hab_id)

        # Itera sobre a ordem da permutação, adquirindo cada habilidade crítica
        for habilidade_critica in ordem:
            adquirir_habilidade(habilidade_critica)
            
        return tempo_total

    def analisar_permutacoes(self):
        permutacoes = list(itertools.permutations(self.habilidades_criticas))
        custos = []
        for perm in permutacoes:
            custo = self.calcular_custo_ordem(perm)
            custos.append({'permutacao': perm, 'custo_total': custo})
        custos.sort(key=lambda x: x['custo_total'])
        return custos

    def gerar_relatorio(self, custos):
        melhores = custos[:3]
        custo_medio = sum(x['custo_total'] for x in custos) / len(custos)
        estatisticas = {
            'total_permutacoes': len(custos),
            'custo_melhor': melhores[0]['custo_total'],
            'custo_pior': custos[-1]['custo_total'],
            'custo_medio': custo_medio
        }
        melhores_permutacoes = [
            {**m, 'eficiencia': estatisticas['custo_melhor'] / m['custo_total']} for m in melhores
        ]
        heuristica = (
            "Ordens que priorizam habilidades com menos pré-requisitos e que desbloqueiam outros rapidamente "
            "reduzem custo total. Habilidades terminais ou com múltiplos pré-requisitos no final concentram espera."
        )
        return {
            'melhores_permutacoes': melhores_permutacoes,
            'estatisticas': estatisticas,
            'heuristica': heuristica
        }

    def gerar_visualizacao(self, custos):
        fig, ax = plt.subplots(figsize=(10,6))
        perm_labels = [f"{' → '.join(list(x['permutacao']))}" for x in custos[:10]]
        perm_costs = [x['custo_total'] for x in custos[:10]]
        ax.barh(perm_labels, perm_costs, color='steelblue')
        ax.set_xlabel("Tempo Total (h)")
        ax.set_title("Top 10 Ordens das Permutações Críticas")
        plt.tight_layout()
        return fig

def executar_desafio2(habilidades, habilidades_criticas):
    logging.info("="*60)
    logging.info("INICIANDO DESAFIO 2 — VERIFICAÇÃO CRÍTICA")
    logging.info("="*60)
    try:
        verificador = VerificadorDesafio2(habilidades, habilidades_criticas)
        relatorio = verificador.validar_grafo()
        if not relatorio['valido']:
            return {
                'sucesso': False,
                'erro': f"Ciclos: {relatorio['ciclos']} / Pré-reqs inexistentes: {relatorio['pre_requisitos_inexistentes']}"
            }
        custos = verificador.analisar_permutacoes()
        report = verificador.gerar_relatorio(custos)
        fig = verificador.gerar_visualizacao(custos)
        return {
            'sucesso': True,
            'melhores_permutacoes': report['melhores_permutacoes'],
            'estatisticas': report['estatisticas'],
            'heuristica': report['heuristica'],
            'figura': fig
        }
    except Exception as e:
        logging.error(f"Erro no Desafio 2: {e}")
        return {
            'sucesso': False,
            'erro': str(e)
        }

# Exemplo de uso para testar:
if __name__ == "__main__":
    # Dados mínimos para testar (substitua pelos reais ou import dados.py)
    HABILIDADES = {
        'S3': {'Tempo':100, 'Pre_Reqs':['S1']},
        'S5': {'Tempo':40, 'Pre_Reqs':['S2']},
        'S7': {'Tempo':70, 'Pre_Reqs':[]},
        'S8': {'Tempo':90, 'Pre_Reqs':['S1']},
        'S9': {'Tempo':110, 'Pre_Reqs':['S7','S8']},
        'S1': {'Tempo':80, 'Pre_Reqs':[]},
        'S2': {'Tempo':60, 'Pre_Reqs':[]}
    }
    HABILIDADES_CRITICAS = ['S3', 'S5', 'S7', 'S8', 'S9']
    resultado = executar_desafio2(HABILIDADES, HABILIDADES_CRITICAS)
    if resultado['sucesso']:
        print(f"Total permutações: {resultado['estatisticas']['total_permutacoes']}")
        for i, perm in enumerate(resultado['melhores_permutacoes'], 1):
            print(f"{i}º ordem: {' → '.join(perm['permutacao'])} | Custo: {perm['custo_total']}h | Eficiência: {perm['eficiencia']:.3f}")
        print(f"Custo médio: {resultado['estatisticas']['custo_medio']:.2f}h")
        print(f"Heurística: {resultado['heuristica']}")
        plt.show()
    else:
        print(f"❌ Erro: {resultado['erro']}")
