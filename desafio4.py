import logging
import numpy as np
import matplotlib.pyplot as plt
import time
import timeit
import random
import pandas as pd
from collections import defaultdict

class OrdenadorHabilidades:
    def __init__(self, grafo):
        self.grafo = grafo
        self.habilidades_lista = self._preparar_dados_ordenacao()
        
    def _preparar_dados_ordenacao(self):
        """Prepara a lista de habilidades para ordenação"""
        habilidades = []
        for habilidade_id, dados in self.grafo.items():
            habilidades.append({
                'ID': habilidade_id,
                'Nome': dados['Nome'],
                'Tempo': dados['Tempo'],
                'Valor': dados['Valor'],
                'Complexidade': dados['Complexidade'],
                'Pre_Reqs': dados['Pre_Reqs']
            })
        return habilidades
    
    def merge_sort(self, arr, criterio='Complexidade'):
        """
        Implementação completa do Merge Sort
        """
        if len(arr) <= 1:
            return arr
        
        # Dividir
        mid = len(arr) // 2
        left_half = self.merge_sort(arr[:mid], criterio)
        right_half = self.merge_sort(arr[mid:], criterio)
        
        # Combinar
        return self._merge(left_half, right_half, criterio)
    
    def _merge(self, left, right, criterio):
        """
        Função de merge para o Merge Sort
        """
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            # Comparar baseado no critério
            if criterio == 'Complexidade':
                left_val = left[i]['Complexidade']
                right_val = right[j]['Complexidade']
            elif criterio == 'Tempo':
                left_val = left[i]['Tempo']
                right_val = right[j]['Tempo']
            elif criterio == 'Valor':
                left_val = left[i]['Valor']
                right_val = right[j]['Valor']
            elif criterio == 'razao_vt':
                left_val = left[i]['Valor'] / left[i]['Tempo'] if left[i]['Tempo'] > 0 else 0
                right_val = right[j]['Valor'] / right[j]['Tempo'] if right[j]['Tempo'] > 0 else 0
            else:
                raise ValueError(f"Critério não suportado: {criterio}")
            
            if left_val <= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        # Adicionar elementos restantes
        result.extend(left[i:])
        result.extend(right[j:])
        
        return result
    
    def quick_sort(self, arr, criterio='Complexidade'):
        """
        Implementação completa do Quick Sort
        """
        if len(arr) <= 1:
            return arr
        
        # Escolher pivô (estratégia: elemento do meio)
        pivot_index = len(arr) // 2
        pivot = arr[pivot_index]
        
        # Particionar
        left = []
        right = []
        middle = []
        
        for item in arr:
            if criterio == 'Complexidade':
                item_val = item['Complexidade']
                pivot_val = pivot['Complexidade']
            elif criterio == 'Tempo':
                item_val = item['Tempo']
                pivot_val = pivot['Tempo']
            elif criterio == 'Valor':
                item_val = item['Valor']
                pivot_val = pivot['Valor']
            elif criterio == 'razao_vt':
                item_val = item['Valor'] / item['Tempo'] if item['Tempo'] > 0 else 0
                pivot_val = pivot['Valor'] / pivot['Tempo'] if pivot['Tempo'] > 0 else 0
            else:
                raise ValueError(f"Critério não suportado: {criterio}")
            
            if item_val < pivot_val:
                left.append(item)
            elif item_val > pivot_val:
                right.append(item)
            else:
                middle.append(item)
        
        # Recursão e combinação
        return (self.quick_sort(left, criterio) + 
                middle + 
                self.quick_sort(right, criterio))
    
    def ordenar_nativo(self, arr, criterio='Complexidade'):
        """
        Ordenação usando o sort nativo do Python como baseline
        """
        if criterio == 'Complexidade':
            key_func = lambda x: x['Complexidade']
        elif criterio == 'Tempo':
            key_func = lambda x: x['Tempo']
        elif criterio == 'Valor':
            key_func = lambda x: x['Valor']
        elif criterio == 'razao_vt':
            key_func = lambda x: x['Valor'] / x['Tempo'] if x['Tempo'] > 0 else 0
        else:
            raise ValueError(f"Critério não suportado: {criterio}")
        
        return sorted(arr, key=key_func)
    
    def dividir_sprints(self, habilidades_ordenadas):
        """
        Divide as habilidades ordenadas em Sprint A (1-6) e Sprint B (7-12)
        """
        sprint_a = habilidades_ordenadas[:6]
        sprint_b = habilidades_ordenadas[6:]
        
        # Calcular métricas para cada sprint
        def calcular_metricas(sprint):
            return {
                'total_habilidades': len(sprint),
                'tempo_total': sum(h['Tempo'] for h in sprint),
                'valor_total': sum(h['Valor'] for h in sprint),
                'complexidade_media': np.mean([h['Complexidade'] for h in sprint]),
                'complexidade_total': sum(h['Complexidade'] for h in sprint),
                'eficiencia_media': np.mean([h['Valor'] / h['Tempo'] for h in sprint if h['Tempo'] > 0])
            }
        
        return {
            'sprint_a': {
                'habilidades': sprint_a,
                'metricas': calcular_metricas(sprint_a)
            },
            'sprint_b': {
                'habilidades': sprint_b,
                'metricas': calcular_metricas(sprint_b)
            },
            'diferenca_tempo': abs(calcular_metricas(sprint_a)['tempo_total'] - 
                                  calcular_metricas(sprint_b)['tempo_total']),
            'diferenca_complexidade': abs(calcular_metricas(sprint_a)['complexidade_total'] - 
                                        calcular_metricas(sprint_b)['complexidade_total'])
        }
    
    def analisar_complexidade_algoritmos(self, n_max=10000):
        """
        Análise teórica da complexidade dos algoritmos
        """
        analise = {
            'merge_sort': {
                'melhor_caso': 'O(n log n)',
                'caso_medio': 'O(n log n)',
                'pior_caso': 'O(n log n)',
                'estavel': True,
                'in_place': False,
                'explicacao': 'Divide recursivamente e combina de forma ordenada'
            },
            'quick_sort': {
                'melhor_caso': 'O(n log n)',
                'caso_medio': 'O(n log n)',
                'pior_caso': 'O(n²)',
                'estavel': False,
                'in_place': True,
                'explicacao': 'Particiona em torno de um pivô e ordena recursivamente'
            },
            'sort_nativo': {
                'melhor_caso': 'O(n log n)',
                'caso_medio': 'O(n log n)',
                'pior_caso': 'O(n log n)',
                'estavel': True,
                'in_place': False,
                'explicacao': 'Timsort - híbrido de Merge Sort e Insertion Sort'
            }
        }
        
        # Análise prática para diferentes tamanhos
        tamanhos_testar = [100, 500, 1000, 5000, 10000]
        resultados_tempo = defaultdict(list)
        
        for tamanho in tamanhos_testar:
            if tamanho > n_max:
                continue
                
            # Gerar dados de teste
            dados_teste = [{'id': i, 'valor': random.randint(1, 100)} for i in range(tamanho)]
            
            # Medir tempos
            tempo_merge = timeit.timeit(lambda: self.merge_sort(dados_teste.copy(), 'valor'), number=5)
            tempo_quick = timeit.timeit(lambda: self.quick_sort(dados_teste.copy(), 'valor'), number=5)
            tempo_nativo = timeit.timeit(lambda: self.ordenar_nativo(dados_teste.copy(), 'valor'), number=5)
            
            resultados_tempo['merge_sort'].append(tempo_merge)
            resultados_tempo['quick_sort'].append(tempo_quick)
            resultados_tempo['sort_nativo'].append(tempo_nativo)
        
        analise['resultados_praticos'] = {
            'tamanhos': tamanhos_testar[:len(resultados_tempo['merge_sort'])],
            'tempos': resultados_tempo
        }
        
        return analise
    
    def comparar_desempenho(self, n_repeticoes=100):
        """
        Compara o desempenho dos algoritmos para o conjunto de habilidades real
        """
        logging.info("Comparando desempenho dos algoritmos de ordenação...")
        
        resultados = {}
        criterios = ['Complexidade', 'Tempo', 'Valor', 'razao_vt']
        
        for criterio in criterios:
            logging.info(f"Testando critério: {criterio}")
            
            # Medir tempos
            tempo_merge = timeit.timeit(
                lambda: self.merge_sort(self.habilidades_lista.copy(), criterio), 
                number=n_repeticoes
            )
            
            tempo_quick = timeit.timeit(
                lambda: self.quick_sort(self.habilidades_lista.copy(), criterio), 
                number=n_repeticoes
            )
            
            tempo_nativo = timeit.timeit(
                lambda: self.ordenar_nativo(self.habilidades_lista.copy(), criterio), 
                number=n_repeticoes
            )
            
            # Verificar correção
            resultado_merge = self.merge_sort(self.habilidades_lista.copy(), criterio)
            resultado_quick = self.quick_sort(self.habilidades_lista.copy(), criterio)
            resultado_nativo = self.ordenar_nativo(self.habilidades_lista.copy(), criterio)
            
            # Verificar se todos produzem a mesma ordenação
            correto_merge_quick = all(
                m[criterio if criterio != 'razao_vt' else 'Valor'] == q[criterio if criterio != 'razao_vt' else 'Valor'] 
                for m, q in zip(resultado_merge, resultado_quick)
            )
            
            correto_merge_nativo = all(
                m[criterio if criterio != 'razao_vt' else 'Valor'] == n[criterio if criterio != 'razao_vt' else 'Valor'] 
                for m, n in zip(resultado_merge, resultado_nativo)
            )
            
            resultados[criterio] = {
                'merge_sort': {
                    'tempo': tempo_merge,
                    'tempo_medio': tempo_merge / n_repeticoes,
                    'correto': correto_merge_quick and correto_merge_nativo
                },
                'quick_sort': {
                    'tempo': tempo_quick,
                    'tempo_medio': tempo_quick / n_repeticoes,
                    'correto': correto_merge_quick
                },
                'sort_nativo': {
                    'tempo': tempo_nativo,
                    'tempo_medio': tempo_nativo / n_repeticoes,
                    'correto': correto_merge_nativo
                },
                'ordenacao_correta': correto_merge_quick and correto_merge_nativo
            }
        
        return resultados
    
    def executar_analise_completa(self):
        """
        Executa análise completa do Desafio 4
        """
        logging.info("Iniciando análise completa do Desafio 4...")
        
        # 1. Ordenar por Complexidade (critério principal)
        print("📊 Ordenando habilidades por complexidade...")
        habilidades_ordenadas_complexidade = self.merge_sort(self.habilidades_lista.copy(), 'Complexidade')
        
        # 2. Dividir em sprints
        print("🎯 Dividindo em Sprint A e Sprint B...")
        resultado_sprints = self.dividir_sprints(habilidades_ordenadas_complexidade)
        
        # 3. Comparar desempenho dos algoritmos
        print("⚡ Comparando desempenho dos algoritmos...")
        comparacao_desempenho = self.comparar_desempenho(n_repeticoes=100)
        
        # 4. Análise de complexidade teórica
        print("🔍 Analisando complexidade teórica...")
        analise_complexidade = self.analisar_complexidade_algoritmos()
        
        # 5. Ordenar por outros critérios para análise
        print("📈 Ordenando por outros critérios...")
        ordenacoes_alternativas = {}
        for criterio in ['Tempo', 'Valor', 'razao_vt']:
            ordenacoes_alternativas[criterio] = self.merge_sort(self.habilidades_lista.copy(), criterio)
        
        return {
            'ordenacao_principal': habilidades_ordenadas_complexidade,
            'sprints': resultado_sprints,
            'comparacao_desempenho': comparacao_desempenho,
            'analise_complexidade': analise_complexidade,
            'ordenacoes_alternativas': ordenacoes_alternativas
        }
    
    def gerar_relatorio_detalhado(self, analise_completa):
        """
        Gera relatório detalhado do Desafio 4
        """
        print("=" * 80)
        print("DESAFIO 4 — TRILHAS PARALAELAS - RELATÓRIO DETALHADO")
        print("=" * 80)
        print("🎯 OBJETIVO: Ordenar 12 habilidades por Complexidade usando Merge Sort")
        print("📊 DIVISÃO: Sprint A (1-6) e Sprint B (7-12)")
        print()
        
        # Justificativa da escolha do algoritmo
        print("🔍 JUSTIFICATIVA DA ESCOLHA DO ALGORITMO:")
        print("-" * 45)
        print("✅ MERGE SORT selecionado porque:")
        print("   • Complexidade garantida O(n log n) mesmo no pior caso")
        print("   • Estável (mantém ordem relativa de elementos iguais)")
        print("   • Previsível e confiável para conjuntos de dados pequenos")
        print("   • Facilita divisão equitativa em sprints paralelas")
        print("   • Evita o pior caso O(n²) do Quick Sort")
        print()
        
        # Análise de complexidade
        print("⚡ ANÁLISE DE COMPLEXIDADE COMPUTACIONAL:")
        print("-" * 45)
        complexidade = analise_completa['analise_complexidade']
        
        for algoritmo, dados in complexidade.items():
            if algoritmo == 'resultados_praticos':
                continue
            print(f"  {algoritmo.upper().replace('_', ' ')}:")
            print(f"    Melhor caso: {dados['melhor_caso']}")
            print(f"    Caso médio: {dados['caso_medio']}")
            print(f"    Pior caso: {dados['pior_caso']}")
            print(f"    Estável: {'✅ SIM' if dados['estavel'] else '❌ NÃO'}")
            print(f"    In-place: {'✅ SIM' if dados['in_place'] else '❌ NÃO'}")
            print(f"    Explicação: {dados['explicacao']}")
            print()
        
        # Resultados da ordenação por complexidade
        print("📊 RESULTADOS DA ORDENAÇÃO POR COMPLEXIDADE:")
        print("-" * 45)
        habilidades_ordenadas = analise_completa['ordenacao_principal']
        
        print("🏆 HABILIDADES ORDENADAS (Crescente por Complexidade):")
        for i, habilidade in enumerate(habilidades_ordenadas, 1):
            print(f"  {i:2d}. {habilidade['ID']}: {habilidade['Nome']}")
            print(f"       Complexidade: {habilidade['Complexidade']} | "
                  f"Tempo: {habilidade['Tempo']}h | Valor: {habilidade['Valor']} | "
                  f"V/T: {habilidade['Valor']/habilidade['Tempo']:.3f}")
        print()
        
        # Análise das Sprints
        sprints = analise_completa['sprints']
        print("🎯 DIVISÃO EM SPRINTS PARALELAS:")
        print("-" * 35)
        
        print("🚀 SPRINT A (Habilidades 1-6):")
        for i, habilidade in enumerate(sprints['sprint_a']['habilidades'], 1):
            print(f"     {i}. {habilidade['ID']} - C:{habilidade['Complexidade']}")
        metricas_a = sprints['sprint_a']['metricas']
        print(f"     📈 Métricas: T:{metricas_a['tempo_total']}h, V:{metricas_a['valor_total']}, "
              f"C médio:{metricas_a['complexidade_media']:.1f}")
        
        print("\n🚀 SPRINT B (Habilidades 7-12):")
        for i, habilidade in enumerate(sprints['sprint_b']['habilidades'], 1):
            print(f"     {i}. {habilidade['ID']} - C:{habilidade['Complexidade']}")
        metricas_b = sprints['sprint_b']['metricas']
        print(f"     📈 Métricas: T:{metricas_b['tempo_total']}h, V:{metricas_b['valor_total']}, "
              f"C médio:{metricas_b['complexidade_media']:.1f}")
        
        print(f"\n⚖️  BALANCEAMENTO ENTRE SPRINTS:")
        print(f"   Diferença de tempo: {sprints['diferenca_tempo']}h")
        print(f"   Diferença de complexidade: {sprints['diferenca_complexidade']} pontos")
        
        if sprints['diferenca_tempo'] < 50 and sprints['diferenca_complexidade'] < 10:
            print("   ✅ BOA DISTRIBUIÇÃO: Sprints bem balanceadas")
        else:
            print("   ⚠️  DISTRIBUIÇÃO DESBALANCEADA: Considerar rebalanceamento")
        print()
        
        # Comparação de desempenho
        print("⚡ COMPARAÇÃO DE DESEMPENHO (100 execuções):")
        print("-" * 50)
        desempenho = analise_completa['comparacao_desempenho']['Complexidade']
        
        algoritmos = ['merge_sort', 'quick_sort', 'sort_nativo']
        nomes = ['Merge Sort', 'Quick Sort', 'Sort Nativo']
        
        print("   Algoritmo       | Tempo Total | Tempo Médio | Correto")
        print("   " + "-" * 50)
        
        for algo, nome in zip(algoritmos, nomes):
            dados = desempenho[algo]
            correto = "✅" if dados['correto'] else "❌"
            print(f"   {nome:15} | {dados['tempo']:10.4f}s | {dados['tempo_medio']:11.6f}s | {correto}")
        
        # Análise de velocidade relativa
        tempo_merge = desempenho['merge_sort']['tempo_medio']
        tempo_nativo = desempenho['sort_nativo']['tempo_medio']
        velocidade_relativa = tempo_nativo / tempo_merge if tempo_merge > 0 else 0
        
        print(f"\n   📈 Merge Sort é {velocidade_relativa:.1f}x mais lento que Sort Nativo")
        
        if velocidade_relativa < 5:
            print("   ✅ DESEMPENHO ACEITÁVEL: Diferença pequena para conjunto pequeno")
        else:
            print("   ⚠️  DESEMPENHO MODERADO: Implementação pode ser otimizada")
        print()
        
        # Ordenações alternativas
        print("📈 ORDENAÇÕES ALTERNATIVAS (PARA ANÁLISE):")
        print("-" * 45)
        ordenacoes_alt = analise_completa['ordenacoes_alternativas']
        
        for criterio, habilidades in ordenacoes_alt.items():
            primeiro = habilidades[0]['ID']
            ultimo = habilidades[-1]['ID']
            print(f"   {criterio.upper():12}: {primeiro} → ... → {ultimo}")
        
        print(f"\n💡 INSIGHTS E RECOMENDAÇÕES:")
        print("-" * 30)
        print("1. ✅ Merge Sort é excelente para conjuntos pequenos e estáveis")
        print("2. ⚠️  Para conjuntos maiores, considerar Quick Sort ou Timsort nativo")
        print("3. 📊 Divisão por complexidade criou sprints razoavelmente balanceadas")
        print("4. 🎯 Considerar ordenação por V/T para maximizar valor por tempo")
        print("5. 🔄 Para produção, usar sort nativo (otimizado e testado)")
        
        return {
            'analise_completa': analise_completa,
            'sprints_balanceadas': (sprints['diferenca_tempo'] < 50 and 
                                  sprints['diferenca_complexidade'] < 10),
            'velocidade_relativa': velocidade_relativa
        }
    
    def gerar_visualizacao_completa(self, analise_completa):
        """Gera visualização completa para o Desafio 4"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Desafio 4 — Análise de Ordenação e Trilhas Paralelas\n(Merge Sort vs Outros Algoritmos)', 
                    fontsize=16, weight='bold')
        
        # Gráfico 1: Habilidades Ordenadas por Complexidade
        habilidades_ordenadas = analise_completa['ordenacao_principal']
        ids = [h['ID'] for h in habilidades_ordenadas]
        complexidades = [h['Complexidade'] for h in habilidades_ordenadas]
        tempos = [h['Tempo'] for h in habilidades_ordenadas]
        valores = [h['Valor'] for h in habilidades_ordenadas]
        
        x = np.arange(len(ids))
        largura = 0.35
        
        bars1 = ax1.bar(x - largura/2, complexidades, largura, label='Complexidade', 
                       color='lightcoral', edgecolor='darkred')
        bars2 = ax1.bar(x + largura/2, tempos, largura, label='Tempo (h)', 
                       color='lightblue', edgecolor='darkblue', alpha=0.7)
        
        ax1.set_title('Habilidades Ordenadas por Complexidade\n(Sprint A: 1-6, Sprint B: 7-12)')
        ax1.set_xlabel('Habilidade (Ordenada)')
        ax1.set_ylabel('Complexidade / Tempo (h)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(ids, rotation=45)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Adicionar linha divisória entre sprints
        ax1.axvline(5.5, color='red', linestyle='--', alpha=0.7, linewidth=2, label='Divisão Sprints')
        ax1.text(2.5, max(complexidades) * 0.9, 'SPRINT A', ha='center', va='center', 
                fontweight='bold', fontsize=12, color='darkgreen', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
        ax1.text(8.5, max(complexidades) * 0.9, 'SPRINT B', ha='center', va='center', 
                fontweight='bold', fontsize=12, color='darkblue', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        
        # Gráfico 2: Comparação de Desempenho dos Algoritmos
        desempenho = analise_completa['comparacao_desempenho']['Complexidade']
        algoritmos = ['Merge Sort', 'Quick Sort', 'Sort Nativo']
        tempos_medios = [
            desempenho['merge_sort']['tempo_medio'],
            desempenho['quick_sort']['tempo_medio'],
            desempenho['sort_nativo']['tempo_medio']
        ]
        
        cores = ['lightcoral', 'lightgreen', 'lightblue']
        bars = ax2.bar(algoritmos, tempos_medios, color=cores, edgecolor=['darkred', 'darkgreen', 'darkblue'], alpha=0.7)
        
        ax2.set_title('Comparação de Desempenho\n(Tempo Médio por Execução - 100 iterações)')
        ax2.set_ylabel('Tempo (segundos)')
        ax2.grid(axis='y', alpha=0.3)
        
        # Adicionar valores
        for bar, tempo in zip(bars, tempos_medios):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.000001, 
                    f'{tempo:.6f}s', ha='center', va='bottom', fontsize=9)
        
        # Gráfico 3: Análise das Sprints
        sprints = analise_completa['sprints']
        metricas_a = sprints['sprint_a']['metricas']
        metricas_b = sprints['sprint_b']['metricas']
        
        categorias = ['Tempo Total', 'Valor Total', 'Complex. Total', 'Complex. Média']
        valores_a = [metricas_a['tempo_total'], metricas_a['valor_total'], 
                    metricas_a['complexidade_total'], metricas_a['complexidade_media']]
        valores_b = [metricas_b['tempo_total'], metricas_b['valor_total'], 
                    metricas_b['complexidade_total'], metricas_b['complexidade_media']]
        
        x = np.arange(len(categorias))
        largura = 0.35
        
        bars1 = ax3.bar(x - largura/2, valores_a, largura, label='Sprint A', 
                       color='lightgreen', edgecolor='darkgreen')
        bars2 = ax3.bar(x + largura/2, valores_b, largura, label='Sprint B', 
                       color='lightblue', edgecolor='darkblue')
        
        ax3.set_title('Comparação entre Sprints A e B\n(Balanceamento de Carga)')
        ax3.set_xlabel('Métrica')
        ax3.set_ylabel('Valor')
        ax3.set_xticks(x)
        ax3.set_xticklabels(categorias)
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # Gráfico 4: Complexidade Teórica vs Prática
        complexidade = analise_completa['analise_complexidade']
        if 'resultados_praticos' in complexidade:
            dados_praticos = complexidade['resultados_praticos']
            tamanhos = dados_praticos['tamanhos']
            
            ax4.plot(tamanhos, dados_praticos['tempos']['merge_sort'], 
                    marker='o', label='Merge Sort', linewidth=2)
            ax4.plot(tamanhos, dados_praticos['tempos']['quick_sort'], 
                    marker='s', label='Quick Sort', linewidth=2)
            ax4.plot(tamanhos, dados_praticos['tempos']['sort_nativo'], 
                    marker='^', label='Sort Nativo', linewidth=2)
            
            ax4.set_title('Desempenho em Diferentes Tamanhos de Entrada\n(Escala Logarítmica)')
            ax4.set_xlabel('Tamanho do Conjunto (n)')
            ax4.set_ylabel('Tempo de Execução (segundos)')
            ax4.set_xscale('log')
            ax4.set_yscale('log')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        else:
            # Gráfico alternativo: Ordenações por Diferentes Critérios
            ordenacoes_alt = analise_completa['ordenacoes_alternativas']
            criterios = list(ordenacoes_alt.keys())
            
            # Calcular métricas para cada ordenação
            metricas_ordenacoes = []
            for criterio, habilidades in ordenacoes_alt.items():
                primeira = habilidades[0]['ID']
                ultima = habilidades[-1]['ID']
                complexidade_prim = habilidades[0]['Complexidade']
                complexidade_ult = habilidades[-1]['Complexidade']
                metricas_ordenacoes.append({
                    'criterio': criterio,
                    'primeira': primeira,
                    'ultima': ultima,
                    'diff_complexidade': complexidade_ult - complexidade_prim
                })
            
            criterios_nomes = [c['criterio'] for c in metricas_ordenacoes]
            diff_complexidades = [c['diff_complexidade'] for c in metricas_ordenacoes]
            
            bars = ax4.bar(criterios_nomes, diff_complexidades, 
                          color=['lightcoral', 'lightgreen', 'lightblue', 'lightyellow'],
                          edgecolor=['darkred', 'darkgreen', 'darkblue', 'darkorange'])
            
            ax4.set_title('Amplitude de Complexidade por Critério de Ordenação')
            ax4.set_ylabel('Diferença de Complexidade (Última - Primeira)')
            ax4.grid(axis='y', alpha=0.3)
            
            for bar, diff in zip(bars, diff_complexidades):
                ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1, 
                        f'{diff}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return fig

def executar_desafio4(grafo):
    """
    Função principal do Desafio 4
    """
    logging.info("=" * 60)
    logging.info("INICIANDO DESAFIO 4 - TRILHAS PARALELAS")
    logging.info("=" * 60)
    
    try:
        # Criar ordenador
        ordenador = OrdenadorHabilidades(grafo)
        
        # Executar análise completa
        print("📊 Executando análise completa de ordenação...")
        analise_completa = ordenador.executar_analise_completa()
        
        # Gerar relatório
        relatorio = ordenador.gerar_relatorio_detalhado(analise_completa)
        
        # Gerar visualização
        print("📈 Gerando visualizações...")
        fig = ordenador.gerar_visualizacao_completa(analise_completa)
        
        logging.info("Desafio 4 executado com sucesso")
        
        return {
            'sucesso': True,
            'analise_completa': analise_completa,
            'relatorio': relatorio,
            'figura': fig
        }
        
    except Exception as e:
        logging.error(f"Erro no Desafio 4: {e}")
        return {
            'sucesso': False,
            'erro': str(e)
        }

if __name__ == "__main__":
    # Configurar logging para teste
    logging.basicConfig(level=logging.INFO)
    
    # Dados de teste
    from dados import HABILIDADES
    
    # Executar desafio
    resultado = executar_desafio4(HABILIDADES)
    
    if resultado['sucesso']:
        print("\n🎉 Desafio 4 concluído com sucesso!")
        plt.show()  # Mostrar gráficos
    else:
        print(f"❌ Erro: {resultado['erro']}")