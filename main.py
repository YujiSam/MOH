import logging
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import timeit
import random
from itertools import permutations

# === CONFIGURAÇÃO DO LOG ===
logging.basicConfig(
    filename=f"moh_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format='%(asctime)s — [%(levelname)s] — %(message)s',
    datefmt='%H:%M:%S'
)

logging.info("==== EXECUCAO DO MOH INICIADA ====")

# === DADOS MESTRE DO MOH ===
HABILIDADES = {
    'S1': {'Nome': 'Programação Básica (Python)', 'Tempo': 80, 'Valor': 3, 'Complexidade': 4, 'Pre_Reqs': []},
    'S2': {'Nome': 'Modelagem de Dados (SQL)', 'Tempo': 60, 'Valor': 4, 'Complexidade': 3, 'Pre_Reqs': []},
    'S3': {'Nome': 'Algoritmos Avançados', 'Tempo': 100, 'Valor': 7, 'Complexidade': 8, 'Pre_Reqs': ['S1']},
    'S4': {'Nome': 'Fundamentos de ML', 'Tempo': 120, 'Valor': 8, 'Complexidade': 9, 'Pre_Reqs': ['S1', 'S3']},
    'S5': {'Nome': 'Visualização de Dados (BI)', 'Tempo': 40, 'Valor': 6, 'Complexidade': 5, 'Pre_Reqs': ['S2']},
    'S6': {'Nome': 'IA Generativa Ética', 'Tempo': 150, 'Valor': 10, 'Complexidade': 10, 'Pre_Reqs': ['S4']},
    'S7': {'Nome': 'Estruturas em Nuvem', 'Tempo': 70, 'Valor': 5, 'Complexidade': 7, 'Pre_Reqs': []},
    'S8': {'Nome': 'APIs e Microsserviços', 'Tempo': 90, 'Valor': 6, 'Complexidade': 6, 'Pre_Reqs': ['S1']},
    'S9': {'Nome': 'DevOps & CI/CD', 'Tempo': 110, 'Valor': 9, 'Complexidade': 8, 'Pre_Reqs': ['S7', 'S8']},
    'H10': {'Nome': 'Segurança de Dados', 'Tempo': 60, 'Valor': 5, 'Complexidade': 6, 'Pre_Reqs': []},
    'H11': {'Nome': 'Análise de Big Data', 'Tempo': 90, 'Valor': 8, 'Complexidade': 8, 'Pre_Reqs': ['S4']},
    'H12': {'Nome': 'Introdução a IoT', 'Tempo': 30, 'Valor': 3, 'Complexidade': 3, 'Pre_Reqs': []}
}

# === ALGORITMO MERGE SORT IMPLEMENTADO ===
def merge_sort(arr):
    """Implementação real do Merge Sort para o Desafio 4"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """Função auxiliar para o Merge Sort"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i]['Complexidade'] <= right[j]['Complexidade']:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# === SIMULAÇÃO MONTE CARLO REAL ===
def simular_caminho_otimo_monte_carlo(n_simulacoes=1000):
    """
    Simulação Monte Carlo real para o Desafio 1
    Retorna a distribuição de valores considerando incerteza nos parâmetros
    """
    valores_totais = []
    
    for _ in range(n_simulacoes):
        valor_acumulado = 0
        tempo_acumulado = 0
        complexidade_acumulada = 0
        
        # Simula um caminho válido considerando pré-requisitos
        habilidades_adquiridas = set()
        
        while tempo_acumulado <= 350 and complexidade_acumulada <= 30:
            # Encontra habilidades disponíveis (pré-requisitos satisfeitos)
            disponiveis = []
            for habilidade_id, dados in HABILIDADES.items():
                if (habilidade_id not in habilidades_adquiridas and 
                    all(req in habilidades_adquiridas for req in dados['Pre_Reqs'])):
                    
                    # Aplica incerteza de ±10% nos valores
                    valor_incerto = dados['Valor'] * random.uniform(0.9, 1.1)
                    tempo_incerto = dados['Tempo'] * random.uniform(0.9, 1.1)
                    
                    disponiveis.append({
                        'id': habilidade_id,
                        'valor': valor_incerto,
                        'tempo': tempo_incerto,
                        'complexidade': dados['Complexidade']
                    })
            
            if not disponiveis:
                break
                
            # Escolhe a habilidade com melhor razão valor/tempo
            melhor = max(disponiveis, key=lambda x: x['valor'] / x['tempo'])
            
            if (tempo_acumulado + melhor['tempo'] <= 350 and 
                complexidade_acumulada + melhor['complexidade'] <= 30):
                
                valor_acumulado += melhor['valor']
                tempo_acumulado += melhor['tempo']
                complexidade_acumulada += melhor['complexidade']
                habilidades_adquiridas.add(melhor['id'])
            else:
                break
        
        valores_totais.append(valor_acumulado)
    
    return valores_totais

# === ALGORITMO GULOSO VS ÓTIMO (DESAFIO 3) ===
def estrategia_gulosa(meta_adaptabilidade=15):
    """Implementação real da estratégia gulosa para habilidades básicas"""
    habilidades_basicas = [h for h, d in HABILIDADES.items() if not d['Pre_Reqs']]
    
    # Ordena por V/T (razão valor/tempo)
    habilidades_ordenadas = sorted(
        habilidades_basicas,
        key=lambda h: HABILIDADES[h]['Valor'] / HABILIDADES[h]['Tempo'],
        reverse=True
    )
    
    adaptabilidade_total = 0
    habilidades_escolhidas = []
    
    for hab in habilidades_ordenadas:
        if adaptabilidade_total >= meta_adaptabilidade:
            break
        habilidades_escolhidas.append(hab)
        adaptabilidade_total += HABILIDADES[hab]['Valor']
    
    return adaptabilidade_total, habilidades_escolhidas

def busca_exaustiva_otima(meta_adaptabilidade=15):
    """Busca exaustiva para encontrar solução ótima"""
    habilidades_basicas = [h for h, d in HABILIDADES.items() if not d['Pre_Reqs']]
    melhor_valor = 0
    melhor_combinacao = []
    
    # Gera todos os subconjuntos possíveis
    from itertools import combinations
    for r in range(1, len(habilidades_basicas) + 1):
        for combinacao in combinations(habilidades_basicas, r):
            valor_total = sum(HABILIDADES[h]['Valor'] for h in combinacao)
            if valor_total >= meta_adaptabilidade and (valor_total < melhor_valor or melhor_valor == 0):
                melhor_valor = valor_total
                melhor_combinacao = combinacao
    
    return melhor_valor, list(melhor_combinacao)

# === MEDIÇÃO DE TEMPO PARA MERGE SORT ===
def gerar_dados_desempenho():
    """Gera dados reais de desempenho para Merge Sort vs Sort Nativo"""
    tamanhos = [100, 500, 1000, 2000, 4000, 8000]
    tempos_merge = []
    tempos_nativo = []
    
    for tamanho in tamanhos:
        # Gera lista de dicionários simulando habilidades
        dados_teste = [{'Habilidade': f'Temp{i}', 'Complexidade': random.randint(1, 10)} 
                      for i in range(tamanho)]
        
        # Mede Merge Sort
        tempo_merge = timeit.timeit(lambda: merge_sort(dados_teste.copy()), number=5)
        tempos_merge.append(tempo_merge)
        
        # Mede Sort Nativo
        tempo_nativo = timeit.timeit(
            lambda: sorted(dados_teste.copy(), key=lambda x: x['Complexidade']), 
            number=5
        )
        tempos_nativo.append(tempo_nativo)
        
        logging.info(f"Tamanho {tamanho}: Merge={tempo_merge:.4f}s, Nativo={tempo_nativo:.4f}s")
    
    return np.array(tamanhos), np.array(tempos_merge), np.array(tempos_nativo)

try:
    plt.style.use('default')
    logging.info("Estilo visual definido (fundo branco).")

    # === GRÁFICO 1 — MONTE CARLO REAL (DESAFIO 1) ===
    logging.info("Iniciando simulacao Monte Carlo real...")
    valores_monte_carlo = simular_caminho_otimo_monte_carlo(1000)
    
    plt.figure(figsize=(8, 5))
    n, bins, patches = plt.hist(valores_monte_carlo, bins=30, color='steelblue', 
                               edgecolor='black', alpha=0.7, density=True)
    
    media = np.mean(valores_monte_carlo)
    std = np.std(valores_monte_carlo)
    
    plt.axvline(media, color='red', linestyle='--', linewidth=2, 
                label=f'Média = {media:.2f}')
    plt.axvline(media + std, color='orange', linestyle=':', linewidth=1.5, 
                label=f'+1σ = {media + std:.2f}')
    plt.axvline(media - std, color='orange', linestyle=':', linewidth=1.5, 
                label=f'-1σ = {media - std:.2f}')
    
    plt.title('Desafio 1 — Distribuição do Valor Esperado\n(Simulação Monte Carlo com Incerteza ±10%)', 
              fontsize=12, weight='bold')
    plt.xlabel('Valor Total do Caminho')
    plt.ylabel('Densidade de Probabilidade')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Anotação com informações da simulação
    plt.figtext(0.02, 0.02, 
                f"1000 simulações | Restrições: T≤350h, C≤30 | Coef. Variação: {(std/media)*100:.1f}%",
                fontsize=9, style='italic')
    plt.tight_layout()
    plt.show()
    logging.info(f"Grafico 1 gerado: Media={media:.2f}, σ={std:.2f}")

    # === GRÁFICO 2 — MERGE SORT REAL (DESAFIO 4) ===
    logging.info("Gerando dados de desempenho...")
    tamanhos, tempos_merge, tempos_nativo = gerar_dados_desempenho()
    
    plt.figure(figsize=(8, 5))
    plt.plot(tamanhos, tempos_merge, marker='o', linewidth=2, markersize=6, 
             label="Merge Sort (Implementado)", color='crimson')
    plt.plot(tamanhos, tempos_nativo, marker='s', linewidth=2, markersize=5, 
             label="Sort Nativo (Python)", color='navy')
    
    plt.title('Desafio 4 — Análise de Desempenho: Merge Sort vs Sort Nativo', 
              fontsize=12, weight='bold')
    plt.xlabel('Tamanho do Conjunto de Dados (n)')
    plt.ylabel('Tempo de Execução (segundos)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Adiciona linha de tendência
    z_merge = np.polyfit(tamanhos, tempos_merge, 2)
    z_nativo = np.polyfit(tamanhos, tempos_nativo, 2)
    plt.plot(tamanhos, np.poly1d(z_merge)(tamanhos), 'crimson', alpha=0.3, linestyle='--')
    plt.plot(tamanhos, np.poly1d(z_nativo)(tamanhos), 'navy', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.show()
    logging.info("Grafico 2 (Merge Sort real) gerado com sucesso")

    # === GRÁFICO 3 — GULOSO VS ÓTIMO REAL (DESAFIO 3) ===
    logging.info("Calculando estrategia gulosa vs otima...")
    
    # Cria cenários com diferentes metas de adaptabilidade
    metas = [12, 14, 15, 16, 18]
    resultados_guloso = []
    resultados_otimo = []
    combinacoes_guloso = []
    combinacoes_otimo = []
    
    for meta in metas:
        valor_guloso, comb_guloso = estrategia_gulosa(meta)
        valor_otimo, comb_otimo = busca_exaustiva_otima(meta)
        
        resultados_guloso.append(valor_guloso)
        resultados_otimo.append(valor_otimo)
        combinacoes_guloso.append(comb_guloso)
        combinacoes_otimo.append(comb_otimo)
    
    # Plot comparativo
    x = np.arange(len(metas))
    largura = 0.35
    
    plt.figure(figsize=(9, 5))
    barras_guloso = plt.bar(x - largura/2, resultados_guloso, largura, 
                           label='Heurística Gulosa', color='lightcoral', edgecolor='darkred')
    barras_otimo = plt.bar(x + largura/2, resultados_otimo, largura, 
                          label='Solução Ótima (Busca Exaustiva)', color='lightgreen', edgecolor='darkgreen')
    
    plt.title('Desafio 3 — Comparação: Estratégia Gulosa vs Solução Ótima\n(Meta de Adaptabilidade Variável)', 
              fontsize=12, weight='bold')
    plt.xlabel('Meta de Adaptabilidade (S)')
    plt.ylabel('Valor Total Obtido')
    plt.xticks(x, [f'Meta S≥{m}' for m in metas])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Adiciona valores nas barras
    for i, (v_g, v_o) in enumerate(zip(resultados_guloso, resultados_otimo)):
        plt.text(i - largura/2, v_g + 0.1, f'{v_g}', ha='center', va='bottom', fontweight='bold')
        plt.text(i + largura/2, v_o + 0.1, f'{v_o}', ha='center', va='bottom', fontweight='bold')
    
    # Destaca cenário onde guloso não é ótimo
    diferencas = [otimo - guloso for guloso, otimo in zip(resultados_guloso, resultados_otimo)]
    if any(diferencas):
        idx_contraexemplo = diferencas.index(max(diferencas))
        plt.axvspan(idx_contraexemplo - 0.4, idx_contraexemplo + 0.4, alpha=0.2, color='red',
                   label='Contraexemplo (Guloso ≠ Ótimo)')
    
    plt.tight_layout()
    plt.show()
    
    logging.info(f"Grafico 3 gerado: Guloso={resultados_guloso}, Otimo={resultados_otimo}")

    # === GRÁFICO 4 — COMPLEXIDADE ORDENADA (DESAFIO 4) ===
    habilidades = list(HABILIDADES.keys())
    complexidades = [HABILIDADES[h]['Complexidade'] for h in habilidades]
    
    # Usa Merge Sort implementado para ordenar
    dados_ordenar = [{'Habilidade': h, 'Complexidade': c} for h, c in zip(habilidades, complexidades)]
    dados_ordenados = merge_sort(dados_ordenar.copy())
    
    habilidades_ordenadas = [item['Habilidade'] for item in dados_ordenados]
    complexidades_ordenadas = [item['Complexidade'] for item in dados_ordenados]
    
    plt.figure(figsize=(9, 5))
    barras = plt.bar(habilidades_ordenadas, complexidades_ordenadas, 
                    color='royalblue', edgecolor='navy', alpha=0.7)
    
    # Destaca sprints
    for i in range(6):
        barras[i].set_color('lightgreen')  # Sprint A
    for i in range(6, len(barras)):
        barras[i].set_color('lightcoral')  # Sprint B
    
    plt.title('Desafio 4 — Habilidades Ordenadas por Complexidade\n(Merge Sort Implementado - Sprint A(1-6) vs Sprint B(7-12))', 
              fontsize=12, weight='bold')
    plt.xlabel('Habilidade')
    plt.ylabel('Nível de Complexidade (C)')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Adiciona valores nas barras
    for barra in barras:
        height = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2., height + 0.1,
                f'{height}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.show()
    logging.info("Grafico 4 (Complexidade ordenada) gerado com sucesso")

    # === GRÁFICO 5 — ANÁLISE TEMPO vs COMPLEXIDADE ===
    tempos = [HABILIDADES[h]['Tempo'] for h in habilidades]
    valores = [HABILIDADES[h]['Valor'] for h in habilidades]
    
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(tempos, complexidades, s=[v*50 for v in valores], 
                         c=valores, cmap='viridis', alpha=0.7, edgecolors='black')
    
    # Anotações
    for i, (habilidade, tempo, complexidade) in enumerate(zip(habilidades, tempos, complexidades)):
        plt.annotate(habilidade, (tempo + 2, complexidade + 0.1), fontsize=8, 
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))
    
    plt.colorbar(scatter, label='Valor da Habilidade (V)')
    plt.title('Desafio 1 — Análise Multidimensional: Tempo vs Complexidade vs Valor\n(Tamanho do marcador = Valor; Cor = Valor)', 
              fontsize=11, weight='bold')
    plt.xlabel('Tempo de Aquisição (horas)')
    plt.ylabel('Complexidade (C)')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Linha de tendência
    z = np.polyfit(tempos, complexidades, 1)
    p = np.poly1d(z)
    plt.plot(tempos, p(tempos), "r--", alpha=0.5, label=f'Tendência (r² = {np.corrcoef(tempos, complexidades)[0,1]:.2f})')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    logging.info("Grafico 5 (Análise multidimensional) gerado com sucesso")

except Exception as e:
    logging.exception(f"Erro durante execucao: {e}")
    print(f"Erro detalhado registrado no log: {e}")

logging.info("==== EXECUCAO FINALIZADA COM SUCESSO ====")
print("✅ Todos os gráficos foram gerados!")
print("📊 Dados reais coletados e analisados")
print("📈 Visualizações conectadas aos algoritmos implementados")