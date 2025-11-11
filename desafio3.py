import logging
import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import combinations
import pandas as pd
from collections import defaultdict

class AnalisadorPivoRapido:
    def __init__(self, grafo):
        self.grafo = grafo
        self.habilidades_basicas = self._identificar_habilidades_basicas()
        self.resultados_guloso = {}
        self.resultados_otimos = {}
        self.contraexemplos = []
    
    def _identificar_habilidades_basicas(self):
        """Identifica habilidades de nível básico (sem pré-requisitos)"""
        habilidades_basicas = []
        for habilidade_id, dados in self.grafo.items():
            if not dados['Pre_Reqs']:  # Sem pré-requisitos
                habilidades_basicas.append({
                    'id': habilidade_id,
                    'nome': dados['Nome'],
                    'tempo': dados['Tempo'],
                    'valor': dados['Valor'],
                    'complexidade': dados['Complexidade'],
                    'razao_vt': dados['Valor'] / dados['Tempo'] if dados['Tempo'] > 0 else 0
                })
        
        # Ordenar por razão valor/tempo para referência
        habilidades_basicas.sort(key=lambda x: x['razao_vt'], reverse=True)
        return habilidades_basicas
    
    def estrategia_gulosa(self, meta_adaptabilidade=15, criterio='razao_vt'):
        """
        Implementação da estratégia gulosa para habilidades básicas
        """
        logging.info(f"Executando estratégia gulosa com meta S ≥ {meta_adaptabilidade}, critério: {criterio}")
        
        if criterio == 'razao_vt':
            # Ordenar por V/T (razão valor/tempo) - critério principal
            habilidades_ordenadas = sorted(
                self.habilidades_basicas,
                key=lambda h: h['razao_vt'],
                reverse=True
            )
        elif criterio == 'valor':
            # Ordenar por valor absoluto
            habilidades_ordenadas = sorted(
                self.habilidades_basicas,
                key=lambda h: h['valor'],
                reverse=True
            )
        elif criterio == 'tempo':
            # Ordenar por tempo (mais rápidas primeiro)
            habilidades_ordenadas = sorted(
                self.habilidades_basicas,
                key=lambda h: h['tempo']
            )
        else:
            raise ValueError(f"Critério não suportado: {criterio}")
        
        adaptabilidade_total = 0
        tempo_total = 0
        complexidade_total = 0
        habilidades_escolhidas = []
        historico = []
        
        for habilidade in habilidades_ordenadas:
            if adaptabilidade_total >= meta_adaptabilidade:
                break
                
            # Adicionar habilidade
            habilidades_escolhidas.append(habilidade['id'])
            adaptabilidade_total += habilidade['valor']
            tempo_total += habilidade['tempo']
            complexidade_total += habilidade['complexidade']
            
            historico.append({
                'habilidade': habilidade['id'],
                'valor_acumulado': adaptabilidade_total,
                'tempo_acumulado': tempo_total,
                'razao_vt': habilidade['razao_vt'],
                'criterio': criterio
            })
        
        resultado = {
            'adaptabilidade_final': adaptabilidade_total,
            'tempo_total': tempo_total,
            'complexidade_total': complexidade_total,
            'habilidades_escolhidas': habilidades_escolhidas,
            'meta_atingida': adaptabilidade_total >= meta_adaptabilidade,
            'historico': historico,
            'criterio_utilizado': criterio,
            'excesso_adaptabilidade': max(0, adaptabilidade_total - meta_adaptabilidade),
            'eficiencia': adaptabilidade_total / tempo_total if tempo_total > 0 else 0
        }
        
        logging.info(f"Estratégia gulosa: S = {adaptabilidade_total}, T = {tempo_total}h, "
                    f"Habilidades: {habilidades_escolhidas}")
        
        return resultado
    
    def busca_exaustiva_otima(self, meta_adaptabilidade=15, limite_tempo=200):
        """
        Busca exaustiva para encontrar solução ótima
        Considera todas as combinações possíveis de habilidades básicas
        """
        logging.info(f"Executando busca exaustiva com meta S ≥ {meta_adaptabilidade}")
        start_time = time.time()
        
        n_habilidades = len(self.habilidades_basicas)
        melhor_valor = float('inf')  # Queremos o mínimo que atinja a meta
        melhor_combinacao = []
        melhor_tempo = 0
        melhor_complexidade = 0
        total_combinacoes = 0
        combinacoes_validas = 0
        
        # Gerar todas as combinações possíveis
        for r in range(1, n_habilidades + 1):
            for combinacao in combinations(self.habilidades_basicas, r):
                total_combinacoes += 1
                
                # Calcular métricas da combinação
                valor_total = sum(h['valor'] for h in combinacao)
                tempo_total = sum(h['tempo'] for h in combinacao)
                complexidade_total = sum(h['complexidade'] for h in combinacao)
                
                # Verificar se atinge a meta e é melhor que a atual
                if (valor_total >= meta_adaptabilidade and 
                    (valor_total < melhor_valor or 
                    (valor_total == melhor_valor and tempo_total < melhor_tempo))):
                    
                    melhor_valor = valor_total
                    melhor_combinacao = [h['id'] for h in combinacao]
                    melhor_tempo = tempo_total
                    melhor_complexidade = complexidade_total
                    combinacoes_validas += 1
                
                # Verificar timeout
                if time.time() - start_time > limite_tempo:
                    logging.warning(f"Timeout após {limite_tempo}s. Combinações testadas: {total_combinacoes}")
                    break
        
        end_time = time.time()
        
        if melhor_combinacao:
            resultado = {
                'adaptabilidade_final': melhor_valor,
                'tempo_total': melhor_tempo,
                'complexidade_total': melhor_complexidade,
                'habilidades_escolhidas': melhor_combinacao,
                'meta_atingida': True,
                'tempo_execucao': end_time - start_time,
                'total_combinacoes': total_combinacoes,
                'combinacoes_validas': combinacoes_validas,
                'eficiencia': melhor_valor / melhor_tempo if melhor_tempo > 0 else 0
            }
        else:
            resultado = {
                'adaptabilidade_final': 0,
                'tempo_total': 0,
                'complexidade_total': 0,
                'habilidades_escolhidas': [],
                'meta_atingida': False,
                'tempo_execucao': end_time - start_time,
                'total_combinacoes': total_combinacoes,
                'combinacoes_validas': combinacoes_validas,
                'eficiencia': 0
            }
        
        logging.info(f"Busca exaustiva: S = {melhor_valor}, T = {melhor_tempo}h, "
                    f"Habilidades: {melhor_combinacao}, Tempo: {resultado['tempo_execucao']:.2f}s")
        
        return resultado
    
    def encontrar_contraexemplo(self, meta_adaptabilidade=15):
        """
        Encontra um contraexemplo onde a estratégia gulosa não é ótima
        """
        logging.info("Procurando contraexemplo para estratégia gulosa...")
        
        # Executar ambas as estratégias
        resultado_guloso = self.estrategia_gulosa(meta_adaptabilidade, 'razao_vt')
        resultado_otimo = self.busca_exaustiva_otima(meta_adaptabilidade)
        
        contraexemplo = None
        
        if (resultado_guloso['meta_atingida'] and resultado_otimo['meta_atingida'] and
            resultado_guloso['adaptabilidade_final'] > resultado_otimo['adaptabilidade_final']):
            # Guloso produz valor maior (pior) que ótimo - contraexemplo!
            contraexemplo = {
                'meta': meta_adaptabilidade,
                'guloso': resultado_guloso,
                'otimo': resultado_otimo,
                'diferenca_adaptabilidade': resultado_guloso['adaptabilidade_final'] - resultado_otimo['adaptabilidade_final'],
                'diferenca_tempo': resultado_guloso['tempo_total'] - resultado_otimo['tempo_total'],
                'tipo': 'super_adaptabilidade'
            }
        
        elif (resultado_guloso['meta_atingida'] and resultado_otimo['meta_atingida'] and
            resultado_guloso['tempo_total'] > resultado_otimo['tempo_total'] and
            resultado_guloso['adaptabilidade_final'] == resultado_otimo['adaptabilidade_final']):
            # Mesma adaptabilidade, mas guloso leva mais tempo
            contraexemplo = {
                'meta': meta_adaptabilidade,
                'guloso': resultado_guloso,
                'otimo': resultado_otimo,
                'diferenca_adaptabilidade': 0,
                'diferenca_tempo': resultado_guloso['tempo_total'] - resultado_otimo['tempo_total'],
                'tipo': 'mais_tempo'
            }
        
        elif (not resultado_guloso['meta_atingida'] and resultado_otimo['meta_atingida']):
            # Guloso não atinge meta, mas ótimo atinge
            contraexemplo = {
                'meta': meta_adaptabilidade,
                'guloso': resultado_guloso,
                'otimo': resultado_otimo,
                'diferenca_adaptabilidade': resultado_otimo['adaptabilidade_final'],
                'diferenca_tempo': resultado_otimo['tempo_total'],
                'tipo': 'falha_meta'
            }
        
        if contraexemplo:
            logging.info(f"Contraexemplo encontrado! Tipo: {contraexemplo['tipo']}")
            self.contraexemplos.append(contraexemplo)
        
        return contraexemplo
    
    def comparar_criterios_gulosos(self, meta_adaptabilidade=15):
        """
        Compara diferentes critérios para a estratégia gulosa
        """
        criterios = ['razao_vt', 'valor', 'tempo']
        resultados = {}
        
        for criterio in criterios:
            resultados[criterio] = self.estrategia_gulosa(meta_adaptabilidade, criterio)
        
        return resultados
    
    def analisar_complexidade(self):
        """
        Analisa complexidade computacional das abordagens
        """
        n = len(self.habilidades_basicas)
        
        analise = {
            'n_habilidades_basicas': n,
            'guloso': {
                'complexidade_temporal': 'O(n log n)',
                'complexidade_espacial': 'O(n)',
                'explicacao': 'Ordenação das habilidades + seleção gulosa'
            },
            'exaustiva': {
                'complexidade_temporal': 'O(2^n)',
                'complexidade_espacial': 'O(n)',
                'explicacao': 'Geração de todas as combinações possíveis',
                'combinacoes_totais': 2**n - 1
            },
            'viabilidade': {
                'n_limite_pratico': 20,
                'n_atual': n,
                'viavel_exaustiva': n <= 20
            }
        }
        
        return analise
    
    def executar_analise_completa(self, metas_adaptabilidade=None):
        """
        Executa análise completa para múltiplas metas de adaptabilidade
        """
        if metas_adaptabilidade is None:
            metas_adaptabilidade = [12, 14, 15, 16, 18]
        
        resultados_guloso = {}
        resultados_otimo = {}
        contraexemplos = []
        
        logging.info(f"Iniciando análise completa para metas: {metas_adaptabilidade}")
        
        for meta in metas_adaptabilidade:
            logging.info(f"Analisando meta S ≥ {meta}")
            
            # Estratégia gulosa com diferentes critérios
            resultados_guloso[meta] = self.comparar_criterios_gulosos(meta)
            
            # Busca ótima
            resultados_otimo[meta] = self.busca_exaustiva_otima(meta)
            
            # Procurar contraexemplo
            contraexemplo = self.encontrar_contraexemplo(meta)
            if contraexemplo:
                contraexemplos.append(contraexemplo)
        
        self.resultados_guloso = resultados_guloso
        self.resultados_otimos = resultados_otimo
        self.contraexemplos = contraexemplos
        
        return {
            'guloso': resultados_guloso,
            'otimo': resultados_otimo,
            'contraexemplos': contraexemplos
        }
    
    def gerar_relatorio_detalhado(self, analise_completa):
        """
        Gera relatório detalhado do Desafio 3
        """
        print("=" * 80)
        print("DESAFIO 3 — PIVÔ MAIS RÁPIDO - RELATÓRIO DETALHADO")
        print("=" * 80)
        print("🎯 OBJETIVO: Alcançar adaptabilidade mínima S ≥ 15 usando habilidades básicas")
        print(f"📊 HABILIDADES BÁSICAS DISPONÍVEIS: {len(self.habilidades_basicas)}")
        print("   " + ", ".join([f"{h['id']} (V:{h['valor']}, T:{h['tempo']}h, V/T:{h['razao_vt']:.3f})" 
                            for h in self.habilidades_basicas]))
        print()
        
        # Análise de complexidade
        analise_complexidade = self.analisar_complexidade()
        print("⚡ ANÁLISE DE COMPLEXIDADE COMPUTACIONAL:")
        print("-" * 45)
        print(f"  Abordagem Gulosa: {analise_complexidade['guloso']['complexidade_temporal']}")
        print(f"    {analise_complexidade['guloso']['explicacao']}")
        print(f"  Busca Exaustiva: {analise_complexidade['exaustiva']['complexidade_temporal']}")
        print(f"    {analise_complexidade['exaustiva']['explicacao']}")
        print(f"  Combinações totais: {analise_complexidade['exaustiva']['combinacoes_totais']}")
        print(f"  Viabilidade busca exaustiva: {'✅ SIM' if analise_complexidade['viabilidade']['viavel_exaustiva'] else '❌ NÃO'}")
        print()
        
        # Resultados para meta principal S ≥ 15
        meta_principal = 15
        print(f"🎯 RESULTADOS PARA META S ≥ {meta_principal}:")
        print("-" * 35)
        
        # Estratégia Gulosa
        guloso_vt = analise_completa['guloso'][meta_principal]['razao_vt']
        guloso_valor = analise_completa['guloso'][meta_principal]['valor']
        guloso_tempo = analise_completa['guloso'][meta_principal]['tempo']
        otimo = analise_completa['otimo'][meta_principal]
        
        print("🤖 ESTRATÉGIA GULOSA (Razão V/T):")
        print(f"   Adaptabilidade: S = {guloso_vt['adaptabilidade_final']}")
        print(f"   Tempo Total: {guloso_vt['tempo_total']}h")
        print(f"   Habilidades: {' → '.join(guloso_vt['habilidades_escolhidas'])}")
        print(f"   Eficiência: {guloso_vt['eficiencia']:.4f} pontos/hora")
        print(f"   Meta Atingida: {'✅ SIM' if guloso_vt['meta_atingida'] else '❌ NÃO'}")
        print()
        
        print("🤖 ESTRATÉGIA GULOSA (Maior Valor):")
        print(f"   Adaptabilidade: S = {guloso_valor['adaptabilidade_final']}")
        print(f"   Tempo Total: {guloso_valor['tempo_total']}h")
        print(f"   Habilidades: {' → '.join(guloso_valor['habilidades_escolhidas'])}")
        print(f"   Meta Atingida: {'✅ SIM' if guloso_valor['meta_atingida'] else '❌ NÃO'}")
        print()
        
        print("🤖 ESTRATÉGIA GULOSA (Menor Tempo):")
        print(f"   Adaptabilidade: S = {guloso_tempo['adaptabilidade_final']}")
        print(f"   Tempo Total: {guloso_tempo['tempo_total']}h")
        print(f"   Habilidades: {' → '.join(guloso_tempo['habilidades_escolhidas'])}")
        print(f"   Meta Atingida: {'✅ SIM' if guloso_tempo['meta_atingida'] else '❌ NÃO'}")
        print()
        
        print("⭐ SOLUÇÃO ÓTIMA (BUSCA EXAUSTIVA):")
        print(f"   Adaptabilidade: S = {otimo['adaptabilidade_final']}")
        print(f"   Tempo Total: {otimo['tempo_total']}h")
        print(f"   Habilidades: {' → '.join(otimo['habilidades_escolhidas'])}")
        print(f"   Eficiência: {otimo['eficiencia']:.4f} pontos/hora")
        print(f"   Tempo de Execução: {otimo['tempo_execucao']:.2f}s")
        print(f"   Combinações Testadas: {otimo['total_combinacoes']}")
        print(f"   Meta Atingida: {'✅ SIM' if otimo['meta_atingida'] else '❌ NÃO'}")
        print()
        
        # Comparação de critérios gulosos
        print("📊 COMPARAÇÃO DE CRITÉRIOS GULOSOS:")
        print("-" * 35)
        criterios_comparacao = []
        
        for criterio, resultado in analise_completa['guloso'][meta_principal].items():
            criterios_comparacao.append({
                'critério': criterio.upper(),
                'adaptabilidade': resultado['adaptabilidade_final'],
                'tempo': resultado['tempo_total'],
                'eficiencia': resultado['eficiencia'],
                'meta_atingida': resultado['meta_atingida']
            })
        
        for comp in criterios_comparacao:
            status = "✅" if comp['meta_atingida'] else "❌"
            print(f"   {comp['critério']}: S={comp['adaptabilidade']}, T={comp['tempo']}h, ")
            print(f"Eff={comp['eficiencia']:.4f} {status}")
        print()
        
        # Análise de contraexemplos
        print("🔍 ANÁLISE DE CONTRAEXEMPLOS:")
        print("-" * 30)
        
        contraexemplos_meta = [ce for ce in analise_completa['contraexemplos'] if ce['meta'] == meta_principal]
        
        if contraexemplos_meta:
            for ce in contraexemplos_meta:
                print(f"🚨 CONTRAEXEMPLO ENCONTRADO (Meta S ≥ {ce['meta']}):")
                print(f"   Tipo: {ce['tipo'].replace('_', ' ').title()}")
                print(f"   Guloso: S={ce['guloso']['adaptabilidade_final']}, T={ce['guloso']['tempo_total']}h")
                print(f"   Ótimo: S={ce['otimo']['adaptabilidade_final']}, T={ce['otimo']['tempo_total']}h")
                
                if ce['tipo'] == 'super_adaptabilidade':
                    print(f"   Problema: Guloso super-otimiza adaptabilidade ")
                    print(f"(+{ce['diferenca_adaptabilidade']} pontos além do necessário)")
                elif ce['tipo'] == 'mais_tempo':
                    print(f"   Problema: Guloso gasta {ce['diferenca_tempo']}h a mais para mesma adaptabilidade")
                elif ce['tipo'] == 'falha_meta':
                    print(f"   Problema: Guloso não atinge meta, ótimo atinge com S={ce['otimo']['adaptabilidade_final']}")
                print()
        else:
            print("   ✅ Nenhum contraexemplo encontrado para esta meta")
            print("   💡 A estratégia gulosa (V/T) é ótima para este cenário")
        print()
        
        # Análise de quando a heurística é aceitável
        print("💡 QUANDO A HEURÍSTICA GULOSA É ACEITÁVEL:")
        print("-" * 45)
        
        metas_analisadas = list(analise_completa['guloso'].keys())
        desempenho_guloso = []
        
        for meta in metas_analisadas:
            guloso = analise_completa['guloso'][meta]['razao_vt']
            otimo = analise_completa['otimo'][meta]
            
            if guloso['meta_atingida'] and otimo['meta_atingida']:
                # Calcular proximidade do ótimo
                diferenca_adaptabilidade = abs(guloso['adaptabilidade_final'] - otimo['adaptabilidade_final'])
                diferenca_tempo = abs(guloso['tempo_total'] - otimo['tempo_total'])
                
                desempenho_guloso.append({
                    'meta': meta,
                    'diferenca_adaptabilidade': diferenca_adaptabilidade,
                    'diferenca_tempo': diferenca_tempo,
                    'eficiencia_guloso': guloso['eficiencia'],
                    'eficiencia_otimo': otimo['eficiencia']
                })
        
        if desempenho_guloso:
            avg_diff_adapt = np.mean([d['diferenca_adaptabilidade'] for d in desempenho_guloso])
            avg_diff_tempo = np.mean([d['diferenca_tempo'] for d in desempenho_guloso])
            
            print(f"  Média diferença adaptabilidade: {avg_diff_adapt:.2f} pontos")
            print(f"  Média diferença tempo: {avg_diff_tempo:.2f} horas")
            
            if avg_diff_adapt < 1 and avg_diff_tempo < 10:
                print("  ✅ Heurística gulosa é ALTAMENTE ACEITÁVEL")
                print("     (Próxima do ótimo na maioria dos cenários)")
            elif avg_diff_adapt < 2 and avg_diff_tempo < 20:
                print("  ⚠️  Heurística gulosa é MODERADAMENTE ACEITÁVEL")
                print("     (Pequenas diferenças em relação ao ótimo)")
            else:
                print("  ❌ Heurística gulosa é POUCO ACEITÁVEL")
                print("     (Diferenças significativas em relação ao ótimo)")
        else:
            print("  📊 Dados insuficientes para análise de aceitabilidade")
        
        return {
            'analise_completa': analise_completa,
            'contraexemplos': analise_completa['contraexemplos'],
            'desempenho_guloso': desempenho_guloso
        }
    
    def gerar_visualizacao_completa(self, analise_completa):
        """Gera visualização completa para o Desafio 3"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Desafio 3 — Análise: Estratégia Gulosa vs Solução Ótima\n(Pivô Mais Rápido - Habilidades Básicas)', 
                    fontsize=16, weight='bold')
        
        # Gráfico 1: Comparação para Meta S ≥ 15
        meta_principal = 15
        guloso_vt = analise_completa['guloso'][meta_principal]['razao_vt']
        guloso_valor = analise_completa['guloso'][meta_principal]['valor']
        guloso_tempo = analise_completa['guloso'][meta_principal]['tempo']
        otimo = analise_completa['otimo'][meta_principal]
        
        estrategias = ['Guloso (V/T)', 'Guloso (Valor)', 'Guloso (Tempo)', 'Ótimo']
        adaptabilidades = [guloso_vt['adaptabilidade_final'], guloso_valor['adaptabilidade_final'], 
                        guloso_tempo['adaptabilidade_final'], otimo['adaptabilidade_final']]
        tempos = [guloso_vt['tempo_total'], guloso_valor['tempo_total'], 
                guloso_tempo['tempo_total'], otimo['tempo_total']]
        
        x = np.arange(len(estrategias))
        largura = 0.35
        
        bars1 = ax1.bar(x - largura/2, adaptabilidades, largura, label='Adaptabilidade (S)', 
                    color='lightgreen', edgecolor='darkgreen')
        bars2 = ax1.bar(x + largura/2, tempos, largura, label='Tempo Total (h)', 
                    color='lightblue', edgecolor='darkblue')
        
        ax1.set_title(f'Comparação de Estratégias - Meta S ≥ {meta_principal}')
        ax1.set_xlabel('Estratégia')
        ax1.set_ylabel('Valor / Tempo (h)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(estrategias, rotation=15)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Adicionar valores e linha da meta
        for i, (adapt, tempo) in enumerate(zip(adaptabilidades, tempos)):
            ax1.text(i - largura/2, adapt + 0.1, f'S={adapt}', ha='center', va='bottom', fontsize=9)
            ax1.text(i + largura/2, tempo + 0.1, f'T={tempo}h', ha='center', va='bottom', fontsize=9)
        
        ax1.axhline(meta_principal, color='red', linestyle='--', alpha=0.7, label=f'Meta S ≥ {meta_principal}')
        ax1.legend()
        
        # Gráfico 2: Análise de Múltiplas Metas
        metas = list(analise_completa['guloso'].keys())
        tempos_guloso = [analise_completa['guloso'][m]['razao_vt']['tempo_total'] for m in metas]
        tempos_otimo = [analise_completa['otimo'][m]['tempo_total'] for m in metas]
        
        ax2.plot(metas, tempos_guloso, marker='o', linewidth=2, label='Guloso (V/T)', color='blue')
        ax2.plot(metas, tempos_otimo, marker='s', linewidth=2, label='Ótimo', color='green')
        
        ax2.set_title('Tempo Necessário vs Meta de Adaptabilidade')
        ax2.set_xlabel('Meta de Adaptabilidade (S)')
        ax2.set_ylabel('Tempo Total (horas)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Destacar meta principal
        ax2.axvline(meta_principal, color='red', linestyle='--', alpha=0.5, label='Meta Principal')
        
        # Gráfico 3: Eficiência das Estratégias
        eficiencias_guloso = [analise_completa['guloso'][m]['razao_vt']['eficiencia'] for m in metas]
        eficiencias_otimo = [analise_completa['otimo'][m]['eficiencia'] for m in metas]
        
        ax3.plot(metas, eficiencias_guloso, marker='o', linewidth=2, label='Guloso (V/T)', color='purple')
        ax3.plot(metas, eficiencias_otimo, marker='s', linewidth=2, label='Ótimo', color='orange')
        
        ax3.set_title('Eficiência (Pontos/Hora) vs Meta de Adaptabilidade')
        ax3.set_xlabel('Meta de Adaptabilidade (S)')
        ax3.set_ylabel('Eficiência (Pontos/Hora)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.axvline(meta_principal, color='red', linestyle='--', alpha=0.5)
        
        # Gráfico 4: Análise de Contraexemplos
        contraexemplos_por_meta = defaultdict(list)
        for ce in analise_completa['contraexemplos']:
            contraexemplos_por_meta[ce['meta']].append(ce)
        
        metas_contra = list(contraexemplos_por_meta.keys())
        num_contraexemplos = [len(contraexemplos_por_meta[m]) for m in metas_contra]
        
        if metas_contra:
            bars = ax4.bar(metas_contra, num_contraexemplos, color='red', alpha=0.7, edgecolor='darkred')
            ax4.set_title('Contraexemplos por Meta de Adaptabilidade')
            ax4.set_xlabel('Meta de Adaptabilidade (S)')
            ax4.set_ylabel('Número de Contraexemplos')
            ax4.grid(axis='y', alpha=0.3)
            
            for bar, num in zip(bars, num_contraexemplos):
                ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1, 
                        f'{num}', ha='center', va='bottom', fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'NENHUM CONTRAEXEMPLO\nENCONTRADO', 
                    ha='center', va='center', transform=ax4.transAxes, 
                    fontsize=16, weight='bold', color='green')
            ax4.set_title('Contraexemplos por Meta de Adaptabilidade')
        
        plt.tight_layout()
        return fig

def executar_desafio3(grafo, metas_adaptabilidade=None):
    """
    Função principal do Desafio 3
    """
    logging.info("=" * 60)
    logging.info("INICIANDO DESAFIO 3 - PIVÔ MAIS RÁPIDO")
    logging.info("=" * 60)
    
    try:
        # Criar analisador
        analisador = AnalisadorPivoRapido(grafo)
        
        # Executar análise completa
        print("🔍 Executando análise completa...")
        analise_completa = analisador.executar_analise_completa(metas_adaptabilidade)
        
        # Gerar relatório
        relatorio = analisador.gerar_relatorio_detalhado(analise_completa)
        
        # Gerar visualização
        print("📊 Gerando visualizações...")
        fig = analisador.gerar_visualizacao_completa(analise_completa)
        
        logging.info("Desafio 3 executado com sucesso")
        
        return {
            'sucesso': True,
            'analise_completa': analise_completa,
            'relatorio': relatorio,
            'figura': fig,
            'contraexemplos': analisador.contraexemplos
        }
        
    except Exception as e:
        logging.error(f"Erro no Desafio 3: {e}")
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
    resultado = executar_desafio3(HABILIDADES)
    
    if resultado['sucesso']:
        print("\n🎉 Desafio 3 concluído com sucesso!")
        plt.show()  # Mostrar gráficos
    else:
        print(f"❌ Erro: {resultado['erro']}")