import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import permutations
from collections import deque
import time

class AnalisadorHabilidadesCriticas:
    def __init__(self, grafo, habilidades_criticas):
        self.grafo = grafo
        self.habilidades_criticas = habilidades_criticas
        self.permutacoes_validas = []
        self.resultados = []
        self.grafo_dependencias = self._construir_grafo_dependencias()
    
    def _construir_grafo_dependencias(self):
        """Constrói grafo de dependências completo incluindo pré-requisitos indiretos"""
        grafo_deps = {}
        
        for habilidade in self.habilidades_criticas:
            # Encontrar todos os pré-requisitos (diretos e indiretos)
            todos_pre_requisitos = set()
            fila = deque(self.grafo[habilidade]['Pre_Reqs'])
            
            while fila:
                prereq = fila.popleft()
                if prereq not in todos_pre_requisitos:
                    todos_pre_requisitos.add(prereq)
                    # Adicionar pré-requisitos dos pré-requisitos
                    fila.extend(self.grafo[prereq]['Pre_Reqs'])
            
            grafo_deps[habilidade] = {
                'pre_requisitos_diretos': set(self.grafo[habilidade]['Pre_Reqs']),
                'pre_requisitos_todos': todos_pre_requisitos,
                'tempo': self.grafo[habilidade]['Tempo'],
                'valor': self.grafo[habilidade]['Valor'],
                'complexidade': self.grafo[habilidade]['Complexidade']
            }
        
        return grafo_deps
    
    def _validar_permutacao_viabilidade(self, permutacao):
        """
        Valida se uma permutação é viável considerando pré-requisitos
        Retorna (é_viável, motivo_inviabilidade)
        """
        habilidades_adquiridas = set()
        
        for i, habilidade in enumerate(permutacao):
            prereqs_necessarios = self.grafo_dependencias[habilidade]['pre_requisitos_diretos']
            
            # Verificar se todos os pré-requisitos diretos foram adquiridos
            if not prereqs_necessarios.issubset(habilidades_adquiridas):
                prereqs_faltantes = prereqs_necessarios - habilidades_adquiridas
                return False, f"{habilidade} requer {prereqs_faltantes} na posição {i+1}"
            
            habilidades_adquiridas.add(habilidade)
        
        return True, ""
    
    def calcular_custo_permutacao(self, permutacao):
        """
        Calcula o custo total (Tempo de Aquisição + Espera por pré-reqs) para uma permutação
        Implementa algoritmo de scheduling com dependências
        """
        tempo_total = 0
        tempo_trabalho_efetivo = 0
        tempo_espera_total = 0
        habilidades_adquiridas = set()
        timeline = []  # Para rastrear a linha do tempo
        
        # Inicializar com habilidades básicas (sem pré-requisitos) que não estão na lista crítica
        habilidades_basicas = set()
        for hab, dados in self.grafo.items():
            if not dados['Pre_Reqs'] and hab not in self.habilidades_criticas:
                habilidades_basicas.add(hab)
        
        habilidades_disponiveis = habilidades_basicas.copy()
        cronograma = []
        
        for habilidade in permutacao:
            dados_habilidade = self.grafo_dependencias[habilidade]
            prereqs_diretos = dados_habilidade['pre_requisitos_diretos']
            tempo_habilidade = dados_habilidade['tempo']
            
            # Verificar se podemos começar imediatamente
            pode_comecar = prereqs_diretos.issubset(habilidades_adquiridas)
            
            if pode_comecar:
                # Sem tempo de espera - começar imediatamente
                tempo_inicio = tempo_total
                tempo_fim = tempo_inicio + tempo_habilidade
                tempo_trabalho_efetivo += tempo_habilidade
                
                cronograma.append({
                    'habilidade': habilidade,
                    'inicio': tempo_inicio,
                    'fim': tempo_fim,
                    'espera': 0,
                    'tipo': 'execucao'
                })
                
                tempo_total = tempo_fim
                habilidades_adquiridas.add(habilidade)
                
            else:
                # Calcular tempo de espera necessário
                prereqs_faltantes = prereqs_diretos - habilidades_adquiridas
                tempo_espera_necessario = 0
                
                # Encontrar o tempo máximo de conclusão dos pré-requisitos faltantes
                for prereq in prereqs_faltantes:
                    # Simular aquisição do pré-requisito
                    tempo_prereq = self.grafo[prereq]['Tempo']
                    tempo_espera_necessario = max(tempo_espera_necessario, tempo_prereq)
                
                tempo_espera_total += tempo_espera_necessario
                tempo_inicio = tempo_total + tempo_espera_necessario
                tempo_fim = tempo_inicio + tempo_habilidade
                tempo_trabalho_efetivo += tempo_habilidade
                
                # Adicionar período de espera ao cronograma
                if tempo_espera_necessario > 0:
                    cronograma.append({
                        'habilidade': 'ESPERA',
                        'inicio': tempo_total,
                        'fim': tempo_inicio,
                        'espera': tempo_espera_necessario,
                        'tipo': 'espera'
                    })
                
                cronograma.append({
                    'habilidade': habilidade,
                    'inicio': tempo_inicio,
                    'fim': tempo_fim,
                    'espera': tempo_espera_necessario,
                    'tipo': 'execucao'
                })
                
                tempo_total = tempo_fim
                habilidades_adquiridas.add(habilidade)
        
        custo_total = tempo_total
        
        return {
            'permutacao': permutacao,
            'custo_total': custo_total,
            'tempo_trabalho_efetivo': tempo_trabalho_efetivo,
            'tempo_espera_total': tempo_espera_total,
            'percentual_espera': (tempo_espera_total / custo_total * 100) if custo_total > 0 else 0,
            'cronograma': cronograma,
            'eficiencia': tempo_trabalho_efetivo / custo_total if custo_total > 0 else 0
        }
    
    def encontrar_todas_permutacoes_validas(self):
        """
        Encontra todas as permutações válidas das habilidades críticas
        Considerando viabilidade de pré-requisitos
        """
        logging.info("Encontrando permutações válidas...")
        
        todas_permutacoes = list(permutations(self.habilidades_criticas))
        permutacoes_validas = []
        
        for i, perm in enumerate(todas_permutacoes):
            if i % 100 == 0:  # Log progresso
                logging.info(f"Validando permutação {i}/{len(todas_permutacoes)}")
            
            viavel, motivo = self._validar_permutacao_viabilidade(perm)
            if viavel:
                permutacoes_validas.append(perm)
        
        self.permutacoes_validas = permutacoes_validas
        logging.info(f"Encontradas {len(permutacoes_validas)} permutações válidas de {len(todas_permutacoes)} totais")
        
        return permutacoes_validas
    
    def analisar_todas_permutacoes(self):
        """
        Analisa todas as permutações válidas e calcula custos
        """
        logging.info("Iniciando análise de custos de todas as permutações...")
        start_time = time.time()
        
        if not self.permutacoes_validas:
            self.encontrar_todas_permutacoes_validas()
        
        resultados = []
        
        for i, perm in enumerate(self.permutacoes_validas):
            if i % 50 == 0:  # Log progresso
                logging.info(f"Analisando permutação {i}/{len(self.permutacoes_validas)}")
            
            resultado = self.calcular_custo_permutacao(perm)
            resultados.append(resultado)
        
        # Ordenar por custo total
        resultados_ordenados = sorted(resultados, key=lambda x: x['custo_total'])
        
        self.resultados = resultados_ordenados
        
        end_time = time.time()
        logging.info(f"Análise concluída em {end_time - start_time:.2f} segundos")
        
        return resultados_ordenados
    
    def encontrar_melhores_permutacoes(self, n_melhores=3):
        """
        Encontra as N melhores permutações com menor custo total
        """
        if not self.resultados:
            self.analisar_todas_permutacoes()
        
        return self.resultados[:n_melhores]
    
    def analisar_heurísticas(self, melhores_permutacoes):
        """
        Analisa heurísticas observadas nas melhores permutações
        """
        heurísticas = {
            'primeiras_posicoes': [],
            'ultimas_posicoes': [],
            'ordem_tempo': [],
            'ordem_pre_requisitos': []
        }
        
        for resultado in melhores_permutacoes:
            sequencia = resultado['permutacao']
            
            # Análise de primeiras posições
            heurísticas['primeiras_posicoes'].append(sequencia[0])
            heurísticas['ultimas_posicoes'].append(sequencia[-1])
            
            # Análise de ordem por tempo
            tempos = [self.grafo_dependencias[h]['tempo'] for h in sequencia]
            heurísticas['ordem_tempo'].append(tempos)
            
            # Contar violações de pré-requisitos
            violacoes = 0
            habilidades_adquiridas = set()
            for habilidade in sequencia:
                prereqs = self.grafo_dependencias[habilidade]['pre_requisitos_diretos']
                if not prereqs.issubset(habilidades_adquiridas):
                    violacoes += 1
                habilidades_adquiridas.add(habilidade)
            heurísticas['ordem_pre_requisitos'].append(violacoes)
        
        # Análise de frequências
        freq_primeiras = pd.Series(heurísticas['primeiras_posicoes']).value_counts()
        freq_ultimas = pd.Series(heurísticas['ultimas_posicoes']).value_counts()
        
        # Identificar padrões de tempo
        padrao_tempo = self._identificar_padrao_tempo(heurísticas['ordem_tempo'])
        
        # Identificar heurística principal
        heuristica_principal = self._identificar_heuristica_principal(melhores_permutacoes)
        
        return {
            'frequencia_primeiras': freq_primeiras,
            'frequencia_ultimas': freq_ultimas,
            'padrao_tempo': padrao_tempo,
            'heuristica_observada': heuristica_principal,
            'violacoes_pre_requisitos_medias': np.mean(heurísticas['ordem_pre_requisitos'])
        }
    
    def _identificar_padrao_tempo(self, ordens_tempo):
        """Identifica padrões na ordem dos tempos"""
        if not ordens_tempo:
            return "Nenhum padrão identificado"
        
        # Verificar se há tendência de tempo crescente/decrescente
        primeira_ordem = ordens_tempo[0]
        if all(first <= second for first, second in zip(primeira_ordem, primeira_ordem[1:])):
            return "Tempo Crescente"
        elif all(first >= second for first, second in zip(primeira_ordem, primeira_ordem[1:])):
            return "Tempo Decrescente"
        else:
            return "Tempo Misturado"
    
    def _identificar_heuristica_principal(self, melhores_permutacoes):
        """Identifica a heurística principal usada nas melhores permutações"""
        if not melhores_permutacoes:
            return "Nenhuma heurística identificada"
        
        # Verificar respeito aos pré-requisitos
        respeito_pre_requisitos = True
        for resultado in melhores_permutacoes:
            sequencia = resultado['permutacao']
            habilidades_adquiridas = set()
            
            for habilidade in sequencia:
                prereqs = self.grafo_dependencias[habilidade]['pre_requisitos_diretos']
                if not prereqs.issubset(habilidades_adquiridas):
                    respeito_pre_requisitos = False
                    break
                habilidades_adquiridas.add(habilidade)
            
            if not respeito_pre_requisitos:
                break
        
        if respeito_pre_requisitos:
            return "Respeito Estrito à Ordem dos Pré-requisitos"
        
        # Verificar se segue ordem de tempo
        tempos_consistentes = True
        tempos_primeira = [self.grafo_dependencias[h]['tempo'] for h in melhores_permutacoes[0]['permutacao']]
        
        for resultado in melhores_permutacoes[1:]:
            tempos_atual = [self.grafo_dependencias[h]['tempo'] for h in resultado['permutacao']]
            if tempos_primeira != tempos_atual:
                tempos_consistentes = False
                break
        
        if tempos_consistentes:
            return "Ordem Consistente por Tempo"
        
        return "Combinação Complexa de Fatores"
    
    def gerar_estatisticas_completas(self):
        """Gera estatísticas completas sobre todas as permutações"""
        if not self.resultados:
            self.analisar_todas_permutacoes()
        
        custos = [r['custo_total'] for r in self.resultados]
        tempos_efetivos = [r['tempo_trabalho_efetivo'] for r in self.resultados]
        tempos_espera = [r['tempo_espera_total'] for r in self.resultados]
        eficiencias = [r['eficiencia'] for r in self.resultados]
        
        return {
            'total_permutacoes': len(self.resultados),
            'custo_medio': np.mean(custos),
            'custo_melhor': min(custos),
            'custo_pior': max(custos),
            'desvio_padrao_custo': np.std(custos),
            'tempo_efetivo_medio': np.mean(tempos_efetivos),
            'tempo_espera_medio': np.mean(tempos_espera),
            'percentual_espera_medio': np.mean([r['percentual_espera'] for r in self.resultados]),
            'eficiencia_media': np.mean(eficiencias),
            'coef_variacao_custo': np.std(custos) / np.mean(custos) if np.mean(custos) > 0 else 0,
            'amplitude_custos': max(custos) - min(custos)
        }
    
    def gerar_relatorio_detalhado(self, melhores_permutacoes, analise_heuristica, estatisticas):
        """Gera relatório detalhado do Desafio 2"""
        print("=" * 80)
        print("DESAFIO 2 — VERIFICAÇÃO CRÍTICA - RELATÓRIO DETALHADO")
        print("=" * 80)
        print(f"🎯 HABILIDADES CRÍTICAS ANALISADAS: {', '.join(self.habilidades_criticas)}")
        print(f"📊 TOTAL DE PERMUTAÇÕES: {len(list(permutations(self.habilidades_criticas)))}")
        print(f"✅ PERMUTAÇÕES VÁLIDAS: {estatisticas['total_permutacoes']}")
        print(f"📈 TAXA DE VALIDADE: {estatisticas['total_permutacoes']/len(list(permutations(self.habilidades_criticas))):.1%}")
        print()
        
        print("🏆 TRÊS MELHORES ORDENS DE AQUISIÇÃO:")
        print("-" * 55)
        
        for i, resultado in enumerate(melhores_permutacoes, 1):
            print(f"{i}º LUGAR - Custo Total: {resultado['custo_total']}h")
            print(f"   Ordem: {' → '.join(resultado['permutacao'])}")
            print(f"   ⏱️  Tempo Efetivo: {resultado['tempo_trabalho_efetivo']}h")
            print(f"   ⏳ Tempo de Espera: {resultado['tempo_espera_total']}h")
            print(f"   📊 Eficiência: {resultado['eficiencia']:.3f} "
                  f"(Espera: {resultado['percentual_espera']:.1f}%)")
            
            # Mostrar cronograma resumido
            print(f"   🗓️  Cronograma Resumido:")
            for evento in resultado['cronograma']:
                if evento['tipo'] == 'execucao':
                    print(f"      {evento['habilidade']}: {evento['inicio']}h-{evento['fim']}h")
                else:
                    print(f"      ESPERA: {evento['inicio']}h-{evento['fim']}h "
                          f"({evento['espera']}h)")
            print()
        
        print("📊 ANÁLISE DE HEURÍSTICAS E PADRÕES:")
        print("-" * 40)
        print(f"🔍 Heurística Observada: {analise_heuristica['heuristica_observada']}")
        print(f"📈 Padrão de Tempo: {analise_heuristica['padrao_tempo']}")
        print(f"⚡ Violações Médias de Pré-requisitos: {analise_heuristica['violacoes_pre_requisitos_medias']:.2f}")
        print()
        
        print("🎯 FREQUÊNCIA NAS PRIMEIRAS POSIÇÕES (Melhores Permutações):")
        for habilidade, freq in analise_heuristica['frequencia_primeiras'].items():
            percentual = freq / len(melhores_permutacoes) * 100
            dados = self.grafo_dependencias[habilidade]
            print(f"   {habilidade}: {freq} vez(es) ({percentual:.0f}%) - "
                  f"T: {dados['tempo']}h, V: {dados['valor']}, "
                  f"Pré-reqs: {len(dados['pre_requisitos_diretos'])}")
        
        print("\n🎯 FREQUÊNCIA NAS ÚLTIMAS POSIÇÕES (Melhores Permutações):")
        for habilidade, freq in analise_heuristica['frequencia_ultimas'].items():
            percentual = freq / len(melhores_permutacoes) * 100
            dados = self.grafo_dependencias[habilidade]
            print(f"   {habilidade}: {freq} vez(es) ({percentual:.0f}%) - "
                  f"T: {dados['tempo']}h, V: {dados['valor']}, "
                  f"Pré-reqs: {len(dados['pre_requisitos_diretos'])}")
        print()
        
        print("📈 ESTATÍSTICAS GERAIS DAS PERMUTAÇÕES:")
        print("-" * 45)
        print(f"  Custo Médio: {estatisticas['custo_medio']:.1f}h")
        print(f"  Melhor Custo: {estatisticas['custo_melhor']}h")
        print(f"  Pior Custo: {estatisticas['custo_pior']}h")
        print(f"  Amplitude de Custos: {estatisticas['amplitude_custos']}h")
        print(f"  Desvio Padrão: {estatisticas['desvio_padrao_custo']:.1f}h")
        print(f"  Coeficiente de Variação: {estatisticas['coef_variacao_custo']:.2%}")
        print(f"  Tempo Efetivo Médio: {estatisticas['tempo_efetivo_medio']:.1f}h")
        print(f"  Tempo de Espera Médio: {estatisticas['tempo_espera_medio']:.1f}h")
        print(f"  Percentual de Espera Médio: {estatisticas['percentual_espera_medio']:.1f}%")
        print(f"  Eficiência Média: {estatisticas['eficiencia_media']:.3f}")
        
        # Análise de impacto
        melhor_custo = estatisticas['custo_melhor']
        pior_custo = estatisticas['custo_pior']
        impacto_escolha = pior_custo - melhor_custo
        
        print(f"\n💡 IMPACTO DA ESCOLHA DA ORDEM:")
        print(f"  Diferença Melhor vs Pior: {impacto_escolha}h "
              f"({impacto_escolha/melhor_custo*100:.1f}% do melhor custo)")
        
        if impacto_escolha > 100:
            print("  🚨 ALTA SENSIBILIDADE: A ordem impacta significativamente no custo total")
        elif impacto_escolha > 50:
            print("  ⚠️  MÉDIA SENSIBILIDADE: A ordem tem impacto moderado no custo total")
        else:
            print("  ✅ BAIXA SENSIBILIDADE: A ordem tem impacto limitado no custo total")
        
        return {
            'melhores_permutacoes': melhores_permutacoes,
            'analise_heuristica': analise_heuristica,
            'estatisticas': estatisticas
        }
    
    def gerar_visualizacao_completa(self, melhores_permutacoes, estatisticas):
        """Gera visualização completa para o Desafio 2"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Desafio 2 — Análise de Permutações de Habilidades Críticas\n(120 permutações com custo de tempo + espera)', 
                    fontsize=16, weight='bold')
        
        # Gráfico 1: Comparação dos 3 Melhores Caminhos
        nomes_melhores = [f"Ordem {i+1}" for i in range(len(melhores_permutacoes))]
        custos_melhores = [perm['custo_total'] for perm in melhores_permutacoes]
        tempos_efetivos = [perm['tempo_trabalho_efetivo'] for perm in melhores_permutacoes]
        tempos_espera = [perm['tempo_espera_total'] for perm in melhores_permutacoes]
        
        x = np.arange(len(nomes_melhores))
        largura = 0.25
        
        bars1 = ax1.bar(x - largura, tempos_efetivos, largura, label='Tempo Efetivo', 
                       color='lightgreen', edgecolor='darkgreen')
        bars2 = ax1.bar(x, tempos_espera, largura, label='Tempo Espera', 
                       color='lightcoral', edgecolor='darkred')
        bars3 = ax1.bar(x + largura, custos_melhores, largura, label='Custo Total', 
                       color='lightblue', edgecolor='darkblue', alpha=0.6)
        
        ax1.set_title('Três Melhores Ordens - Composição do Custo')
        ax1.set_xlabel('Ordem de Aquisição')
        ax1.set_ylabel('Tempo (horas)')
        ax1.set_xticks(x)
        ax1.set_xticklabels([f"Top {i+1}" for i in range(len(melhores_permutacoes))])
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Adicionar valores
        for i, (tef, tesp, custo) in enumerate(zip(tempos_efetivos, tempos_espera, custos_melhores)):
            ax1.text(i - largura, tef + 5, f'{tef}h', ha='center', va='bottom', fontsize=9)
            ax1.text(i, tesp + 5, f'{tesp}h', ha='center', va='bottom', fontsize=9)
            ax1.text(i + largura, custo + 5, f'{custo}h', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # Gráfico 2: Distribuição de Todos os Custos
        todos_custos = [r['custo_total'] for r in self.resultados]
        ax2.hist(todos_custos, bins=20, color='steelblue', edgecolor='navy', alpha=0.7)
        ax2.axvline(estatisticas['custo_medio'], color='red', linestyle='--', 
                   label=f'Média: {estatisticas["custo_medio"]:.1f}h')
        ax2.axvline(estatisticas['custo_melhor'], color='green', linestyle='--', 
                   label=f'Melhor: {estatisticas["custo_melhor"]}h')
        ax2.axvline(estatisticas['custo_pior'], color='orange', linestyle='--', 
                   label=f'Pior: {estatisticas["custo_pior"]}h')
        
        ax2.set_title('Distribuição de Custos de Todas as Permutações')
        ax2.set_xlabel('Custo Total (horas)')
        ax2.set_ylabel('Frequência')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        # Gráfico 3: Análise de Eficiência vs Custo
        eficiencias = [r['eficiencia'] for r in self.resultados]
        percentuais_espera = [r['percentual_espera'] for r in self.resultados]
        
        scatter = ax3.scatter(todos_custos, eficiencias, c=percentuais_espera, 
                             cmap='RdYlGn_r', s=50, alpha=0.7, edgecolors='black')
        
        # Destacar os 3 melhores
        for i, resultado in enumerate(melhores_permutacoes):
            ax3.scatter(resultado['custo_total'], resultado['eficiencia'], 
                       color='gold', s=150, edgecolors='black', marker='*', 
                       label=f'Top {i+1}' if i == 0 else "")
        
        ax3.set_title('Relação: Custo Total vs Eficiência\n(Cor = % Tempo de Espera)')
        ax3.set_xlabel('Custo Total (horas)')
        ax3.set_ylabel('Eficiência (Trabalho/Custo)')
        ax3.grid(alpha=0.3)
        ax3.legend()
        plt.colorbar(scatter, ax=ax3, label='% Tempo de Espera')
        
        # Gráfico 4: Análise de Pré-requisitos vs Tempo
        habilidades = self.habilidades_criticas
        num_pre_requisitos = [len(self.grafo_dependencias[h]['pre_requisitos_diretos']) for h in habilidades]
        tempos = [self.grafo_dependencias[h]['tempo'] for h in habilidades]
        
        scatter = ax4.scatter(num_pre_requisitos, tempos, s=100, c=tempos, 
                             cmap='viridis', alpha=0.7, edgecolors='black')
        
        # Anotar os pontos
        for i, (habilidade, n_pre, tempo) in enumerate(zip(habilidades, num_pre_requisitos, tempos)):
            ax4.annotate(habilidade, (n_pre, tempo), xytext=(5, 5), 
                        textcoords='offset points', fontweight='bold', fontsize=9)
        
        ax4.set_title('Relação: Número de Pré-requisitos vs Tempo de Aquisição')
        ax4.set_xlabel('Número de Pré-requisitos Diretos')
        ax4.set_ylabel('Tempo de Aquisição (horas)')
        ax4.grid(alpha=0.3)
        plt.colorbar(scatter, ax=ax4, label='Tempo (horas)')
        
        plt.tight_layout()
        return fig

def executar_desafio2(grafo, habilidades_criticas):
    """
    Função principal do Desafio 2
    """
    logging.info("=" * 60)
    logging.info("INICIANDO DESAFIO 2 - VERIFICAÇÃO CRÍTICA")
    logging.info("=" * 60)
    
    try:
        # Criar analisador
        analisador = AnalisadorHabilidadesCriticas(grafo, habilidades_criticas)
        
        # Encontrar e analisar todas as permutações
        print("🔍 Encontrando permutações válidas...")
        permutacoes_validas = analisador.encontrar_todas_permutacoes_validas()
        
        print("📊 Analisando custos de todas as permutações...")
        analisador.analisar_todas_permutacoes()
        
        # Encontrar melhores
        print("🏆 Identificando melhores ordens...")
        melhores_permutacoes = analisador.encontrar_melhores_permutacoes(n_melhores=3)
        
        # Análises
        print("🎯 Analisando heurísticas...")
        analise_heuristica = analisador.analisar_heurísticas(melhores_permutacoes)
        
        print("📈 Calculando estatísticas...")
        estatisticas = analisador.gerar_estatisticas_completas()
        
        # Gerar relatório
        relatorio = analisador.gerar_relatorio_detalhado(melhores_permutacoes, analise_heuristica, estatisticas)
        
        # Gerar visualização
        print("📊 Gerando visualizações...")
        fig = analisador.gerar_visualizacao_completa(melhores_permutacoes, estatisticas)
        
        logging.info("Desafio 2 executado com sucesso")
        
        return {
            'sucesso': True,
            'melhores_permutacoes': melhores_permutacoes,
            'analise_heuristica': analise_heuristica,
            'estatisticas': estatisticas,
            'figura': fig,
            'total_permutacoes': len(permutacoes_validas)
        }
        
    except Exception as e:
        logging.error(f"Erro no Desafio 2: {e}")
        return {
            'sucesso': False,
            'erro': str(e)
        }

if __name__ == "__main__":
    # Configurar logging para teste
    logging.basicConfig(level=logging.INFO)
    
    # Dados de teste
    from dados import HABILIDADES, HABILIDADES_CRITICAS
    
    # Executar desafio
    resultado = executar_desafio2(HABILIDADES, HABILIDADES_CRITICAS)
    
    if resultado['sucesso']:
        print("\n🎉 Desafio 2 concluído com sucesso!")
        plt.show()  # Mostrar gráficos
    else:
        print(f"❌ Erro: {resultado['erro']}")