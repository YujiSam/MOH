import logging
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import combinations
from collections import defaultdict, deque
import time
import random

class RecomendadorHabilidades:
    def __init__(self, grafo, cenarios_mercado, horizonte_anos=5, horas_por_ano=200):
        self.grafo = grafo
        self.cenarios_mercado = cenarios_mercado
        self.horizonte_anos = horizonte_anos
        self.horas_por_ano = horas_por_ano
        self.ordenacao_topologica = self._calcular_ordenacao_topologica()
        self.habilidades_basicas = self._identificar_habilidades_basicas()
        
    def _calcular_ordenacao_topologica(self):
        """Calcula ordenação topológica do grafo"""
        graus_entrada = {no: 0 for no in self.grafo}
        arestas_saida = defaultdict(list)
        
        for no, dados in self.grafo.items():
            for prereq in dados['Pre_Reqs']:
                graus_entrada[no] += 1
                arestas_saida[prereq].append(no)
        
        fila = deque([no for no in self.grafo if graus_entrada[no] == 0])
        ordenacao = []
        
        while fila:
            no = fila.popleft()
            ordenacao.append(no)
            
            for vizinho in arestas_saida[no]:
                graus_entrada[vizinho] -= 1
                if graus_entrada[vizinho] == 0:
                    fila.append(vizinho)
        
        if len(ordenacao) != len(self.grafo):
            raise ValueError("Grafo contém ciclos - não é possível ordenação topológica")
        
        return ordenacao
    
    def _identificar_habilidades_basicas(self):
        """Identifica habilidades sem pré-requisitos"""
        return [hab for hab in self.grafo if not self.grafo[hab]['Pre_Reqs']]
    
    def _calcular_valor_esperado(self, habilidade, ano_futuro=1):
        """
        Calcula valor esperado considerando cenários de mercado e horizonte temporal
        """
        valor_base = self.grafo[habilidade]['Valor']
        demanda_base = self.grafo[habilidade].get('Demanda', 0.7)
        
        valor_esperado_total = 0
        
        for cenario_nome, cenario in self.cenarios_mercado.items():
            probabilidade = cenario['probabilidade']
            valor_cenario = valor_base
            
            # Aplicar bônus/penalidade baseado no cenário
            if habilidade in cenario['bonus_habilidades']:
                valor_cenario *= cenario['fator_bonus']
                logging.debug(f"  {habilidade} recebe bônus no cenário {cenario_nome}")
            elif habilidade in cenario['penalidade_habilidades']:
                valor_cenario *= 0.8  # Penalidade de 20%
                logging.debug(f"  {habilidade} recebe penalidade no cenário {cenario_nome}")
            
            # Ajustar pela demanda e crescimento temporal
            fator_crescimento = 1 + (ano_futuro * 0.08)  # 8% de crescimento por ano
            fator_demanda = demanda_base * fator_crescimento
            
            valor_cenario_ajustado = valor_cenario * fator_demanda
            valor_esperado_total += valor_cenario_ajustado * probabilidade
        
        return valor_esperado_total
    
    def _obter_habilidades_disponiveis(self, habilidades_adquiridas):
        """Retorna habilidades que podem ser aprendidas (pré-requisitos satisfeitos)"""
        disponiveis = []
        for habilidade in self.grafo:
            if (habilidade not in habilidades_adquiridas and
                all(req in habilidades_adquiridas for req in self.grafo[habilidade]['Pre_Reqs'])):
                disponiveis.append(habilidade)
        return disponiveis
    
    def dp_horizonte_finito(self, habilidades_atuais, anos_look_ahead=3, max_habilidades=3):
        """
        Programação Dinâmica em horizonte finito para recomendar próximas habilidades
        """
        logging.info(f"Executando DP horizonte finito: {len(habilidades_atuais)} habilidades atuais, {anos_look_ahead} anos look-ahead")
        
        estado_inicial = {
            'habilidades': frozenset(habilidades_atuais),
            'tempo_disponivel': self.horas_por_ano * anos_look_ahead,
            'valor_acumulado': 0,
            'caminho': tuple(),
            'ano_atual': 0
        }
        
        # DP table: ano -> estado -> (valor_maximo, caminho)
        dp = {0: {estado_inicial['habilidades']: (0, tuple(), estado_inicial['tempo_disponivel'])}}
        melhor_global = (0, tuple(), estado_inicial['tempo_disponivel'])
        
        for ano in range(1, anos_look_ahead + 1):
            dp[ano] = {}
            logging.debug(f"Processando ano {ano}, estados no ano anterior: {len(dp[ano-1])}")
            
            for estado_hash in dp[ano-1]:
                valor_anterior, caminho_anterior, tempo_anterior = dp[ano-1][estado_hash]
                habilidades_atuais_set = set(estado_hash)
                
                # Opção 1: Não aprender nada neste ano (manter estado)
                if estado_hash not in dp[ano] or valor_anterior > dp[ano][estado_hash][0]:
                    dp[ano][estado_hash] = (valor_anterior, caminho_anterior, tempo_anterior)
                
                # Opção 2: Aprender habilidades disponíveis
                habilidades_disponiveis = self._obter_habilidades_disponiveis(habilidades_atuais_set)
                
                for habilidade in habilidades_disponiveis:
                    dados_habilidade = self.grafo[habilidade]
                    tempo_necessario = dados_habilidade['Tempo']
                    
                    if tempo_anterior >= tempo_necessario:
                        # Calcular valor esperado considerando o ano futuro
                        valor_esperado = self._calcular_valor_esperado(habilidade, ano)
                        
                        # Novo estado
                        novas_habilidades = habilidades_atuais_set | {habilidade}
                        novo_tempo = tempo_anterior - tempo_necessario
                        novo_valor = valor_anterior + valor_esperado
                        novo_caminho = caminho_anterior + (habilidade,)
                        
                        estado_hash_novo = frozenset(novas_habilidades)
                        
                        # Atualizar DP se for melhor
                        if (estado_hash_novo not in dp[ano] or 
                            novo_valor > dp[ano][estado_hash_novo][0] or
                            (novo_valor == dp[ano][estado_hash_novo][0] and novo_tempo > dp[ano][estado_hash_novo][2])):
                            
                            dp[ano][estado_hash_novo] = (novo_valor, novo_caminho, novo_tempo)
                            
                            # Atualizar melhor global
                            if novo_valor > melhor_global[0]:
                                melhor_global = (novo_valor, novo_caminho, novo_tempo)
                
                # Limitar número de estados para evitar explosão combinatória
                if len(dp[ano]) > 1000:
                    # Manter apenas os melhores estados
                    estados_ordenados = sorted(dp[ano].items(), key=lambda x: x[1][0], reverse=True)
                    dp[ano] = dict(estados_ordenados[:500])
        
        # Encontrar melhor solução
        melhor_valor, melhor_caminho, tempo_restante = melhor_global
        
        # Garantir que não recomendamos mais que max_habilidades
        habilidades_recomendadas = list(melhor_caminho)[:max_habilidades]
        
        resultado = {
            'valor_esperado': melhor_valor,
            'proximas_habilidades': habilidades_recomendadas,
            'caminho_completo': list(melhor_caminho),
            'tempo_utilizado': (self.horas_por_ano * anos_look_ahead) - tempo_restante,
            'tempo_restante': tempo_restante,
            'horizonte_considerado': anos_look_ahead,
            'anos_otimizados': anos_look_ahead,
            'estados_explorados': sum(len(estados) for estados in dp.values())
        }
        
        logging.info(f"DP concluída: Valor esperado = {melhor_valor:.2f}, "
                    f"Habilidades recomendadas = {habilidades_recomendadas}")
        
        return resultado
    
    def busca_look_ahead(self, habilidades_atuais, profundidade=2, max_habilidades=3):
        """
        Busca com look ahead considerando transições de mercado
        """
        logging.info(f"Executando busca look-ahead: profundidade={profundidade}")
        
        melhor_sequencia = []
        melhor_valor = -1
        
        # Habilidades disponíveis imediatamente
        habilidades_disponiveis = self._obter_habilidades_disponiveis(habilidades_atuais)
        
        # Gerar e avaliar sequências
        for seq in self._gerar_sequencias_limitadas(habilidades_disponiveis, profundidade, max_habilidades):
            valor_sequencia = self._avaliar_sequencia_look_ahead(seq, habilidades_atuais, profundidade)
            
            if valor_sequencia > melhor_valor:
                melhor_valor = valor_sequencia
                melhor_sequencia = seq
        
        return {
            'proximas_habilidades': melhor_sequencia[:max_habilidades],
            'valor_esperado': melhor_valor,
            'profundidade_considerada': profundidade,
            'metodo': 'busca_look_ahead'
        }
    
    def _gerar_sequencias_limitadas(self, habilidades, profundidade, max_por_nivel=2):
        """Gera sequências de habilidades limitadas para evitar explosão combinatória"""
        if profundidade == 0 or not habilidades:
            return [[]]
        
        sequencias = []
        
        # Considerar diferentes tamanhos de sequência neste nível
        for tamanho_seq in range(1, min(len(habilidades), max_por_nivel) + 1):
            for comb in combinations(habilidades, tamanho_seq):
                seq_atual = list(comb)
                
                # Obter novas habilidades disponíveis após esta sequência
                novas_habs_disponiveis = set(seq_atual)
                for hab in seq_atual:
                    novas_habs_disponiveis.update(self._obter_habilidades_disponiveis([hab]))
                
                # Remover habilidades já incluídas
                novas_habs_disponiveis = [h for h in novas_habs_disponiveis if h not in seq_atual]
                
                # Recursão para próxima profundidade
                for sub_seq in self._gerar_sequencias_limitadas(novas_habs_disponiveis, profundidade-1, max_por_nivel):
                    sequencias.append(seq_atual + sub_seq)
        
        return sequencias if sequencias else [[]]
    
    def _avaliar_sequencia_look_ahead(self, sequencia, habilidades_atuais, profundidade):
        """Avalia uma sequência considerando cenários futuros"""
        habilidades_temp = set(habilidades_atuais)
        valor_total = 0
        tempo_total = 0
        
        for i, habilidade in enumerate(sequencia):
            if tempo_total > self.horas_por_ano * profundidade:
                break
                
            if all(req in habilidades_temp for req in self.grafo[habilidade]['Pre_Reqs']):
                # Calcular valor considerando o ano futuro
                ano_futuro = min(i + 1, profundidade)
                valor_esperado = self._calcular_valor_esperado(habilidade, ano_futuro)
                valor_total += valor_esperado
                tempo_total += self.grafo[habilidade]['Tempo']
                habilidades_temp.add(habilidade)
        
        return valor_total
    
    def analisar_tendencias_mercado(self):
        """Analisa tendências de mercado para recomendações estratégicas"""
        analise = {}
        
        for cenario_nome, cenario in self.cenarios_mercado.items():
            habilidades_prioritarias = []
            
            for habilidade in cenario['bonus_habilidades']:
                if habilidade in self.grafo:
                    valor_potencial = self._calcular_valor_esperado(habilidade, 2)  # 2 anos no futuro
                    habilidades_prioritarias.append({
                        'habilidade': habilidade,
                        'valor_potencial': valor_potencial,
                        'nome': self.grafo[habilidade]['Nome'],
                        'tempo': self.grafo[habilidade]['Tempo'],
                        'alinhamento': 'ALTO'
                    })
            
            # Ordenar por valor potencial
            habilidades_prioritarias.sort(key=lambda x: x['valor_potencial'], reverse=True)
            
            analise[cenario_nome] = {
                'probabilidade': cenario['probabilidade'],
                'descricao': cenario['descricao'],
                'habilidades_prioritarias': habilidades_prioritarias[:5],  # Top 5
                'impacto_esperado': sum(h['valor_potencial'] for h in habilidades_prioritarias[:3]) / 3
            }
        
        return analise
    
    def _calcular_alinhamento_tendencias(self, habilidade):
        """Calcula alinhamento da habilidade com tendências de mercado"""
        alinhamento = 0
        for cenario_nome, cenario in self.cenarios_mercado.items():
            if habilidade in cenario['bonus_habilidades']:
                alinhamento += cenario['probabilidade'] * 0.9  # Alto alinhamento
            elif habilidade not in cenario['penalidade_habilidades']:
                alinhamento += cenario['probabilidade'] * 0.4  # Alinhamento neutro
            else:
                alinhamento += cenario['probabilidade'] * 0.1  # Baixo alinhamento
        
        return alinhamento
    
    def _identificar_gaps_estratégicos(self, perfil_atual):
        """Identifica gaps estratégicos no perfil atual"""
        areas = {
            'Programação': ['S1', 'S3', 'S8'],
            'Dados/ML': ['S2', 'S4', 'S5', 'S6', 'H11'],
            'Cloud/DevOps': ['S7', 'S9'],
            'Segurança': ['H10'],
            'IoT/Emergentes': ['H12']
        }
        
        gaps = {}
        for area, habilidades_area in areas.items():
            habilidades_possuidas = [h for h in habilidades_area if h in perfil_atual]
            cobertura = len(habilidades_possuidas) / len(habilidades_area) if habilidades_area else 0
            
            if cobertura < 0.5:  # Menos de 50% de cobertura
                gaps[area] = {
                    'cobertura': cobertura,
                    'habilidades_faltantes': [h for h in habilidades_area if h not in perfil_atual],
                    'prioridade': 'ALTA' if cobertura < 0.2 else 'MÉDIA'
                }
        
        return gaps
    
    def _calcular_roi_esperado(self, habilidades):
        """Calcula ROI esperado para conjunto de habilidades"""
        if not habilidades:
            return 0
        
        tempo_total = sum(self.grafo[h]['Tempo'] for h in habilidades)
        valor_total = sum(self._calcular_valor_esperado(h, 1) for h in habilidades)
        
        return valor_total / tempo_total if tempo_total > 0 else 0
    
    def gerar_recomendacao_inteligente(self, perfil_atual, metodo='auto'):
        """
        Gera recomendação inteligente baseada no perfil e cenários futuros
        """
        logging.info(f"Gerando recomendação para perfil: {perfil_atual}")
        
        # Análise do perfil atual
        gaps_estrategicos = self._identificar_gaps_estratégicos(perfil_atual)
        tendencias_mercado = self.analisar_tendencias_mercado()
        
        # Escolher método baseado na complexidade
        if metodo == 'auto':
            if len(perfil_atual) <= 3:  # Perfil simples
                metodo = 'dp'
            else:  # Perfil complexo
                metodo = 'look_ahead'
        
        # Executar algoritmo de recomendação
        if metodo == 'dp':
            resultado = self.dp_horizonte_finito(perfil_atual, anos_look_ahead=3, max_habilidades=3)
        else:
            resultado = self.busca_look_ahead(perfil_atual, profundidade=2, max_habilidades=3)
        
        # Enriquecer resultado com análise estratégica
        habilidades_recomendadas = resultado['proximas_habilidades']
        
        analise_estrategica = {
            'alinhamento_medio': np.mean([self._calcular_alinhamento_tendencias(h) for h in habilidades_recomendadas]),
            'roi_esperado': self._calcular_roi_esperado(habilidades_recomendadas),
            'gaps_cobertos': [area for area, gap in gaps_estrategicos.items() 
                             if any(h in gap['habilidades_faltantes'] for h in habilidades_recomendadas)],
            'cenario_mais_favoravel': max(tendencias_mercado.items(), 
                                         key=lambda x: x[1]['impacto_esperado'])[0]
        }
        
        resultado.update({
            'analise_estrategica': analise_estrategica,
            'gaps_identificados': gaps_estrategicos,
            'tendencias_mercado': tendencias_mercado,
            'metodo_utilizado': metodo
        })
        
        return resultado
    
    def executar_analise_completa(self, perfis_teste=None):
        """
        Executa análise completa para múltiplos perfis
        """
        if perfis_teste is None:
            perfis_teste = {
                'Iniciante': [],
                'Programador Junior': ['S1'],
                'Analista de Dados': ['S1', 'S2', 'S5'],
                'Desenvolvedor Backend': ['S1', 'S3', 'S8'],
                'Especialista Cloud': ['S1', 'S7', 'S8']
            }
        
        resultados = {}
        
        for perfil_nome, habilidades in perfis_teste.items():
            logging.info(f"Analisando perfil: {perfil_nome}")
            
            resultado = self.gerar_recomendacao_inteligente(habilidades)
            resultados[perfil_nome] = resultado
        
        return resultados
    
    def gerar_relatorio_detalhado(self, analise_completa):
        """
        Gera relatório detalhado do Desafio 5
        """
        print("=" * 80)
        print("DESAFIO 5 — RECOMENDAR PRÓXIMAS HABILIDADES - RELATÓRIO DETALHADO")
        print("=" * 80)
        print("🎯 OBJETIVO: Sugerir 2-3 próximas habilidades maximizando valor esperado")
        print(f"📅 HORIZONTE: {self.horizonte_anos} anos | ⏰ HORAS/ANO: {self.horas_por_ano}h")
        print()
        
        # Análise de Cenários de Mercado
        print("📊 CENÁRIOS DE MERCADO (5 ANOS):")
        print("-" * 40)
        tendencias = analise_completa[list(analise_completa.keys())[0]]['tendencias_mercado']
        
        for cenario, dados in tendencias.items():
            print(f"\n🔮 {cenario} ({dados['probabilidade']:.0%} probabilidade):")
            print(f"   {dados['descricao']}")
            print(f"   🎯 Habilidades Prioritárias:")
            for hab in dados['habilidades_prioritarias'][:3]:
                print(f"      ✓ {hab['habilidade']}: {hab['nome']}")
                print(f"          Valor Potencial: {hab['valor_potencial']:.1f} | "
                      f"Tempo: {hab['tempo']}h")
        print()
        
        # Recomendações por Perfil
        print("👥 RECOMENDAÇÕES POR PERFIL:")
        print("-" * 30)
        
        for perfil_nome, resultado in analise_completa.items():
            print(f"\n🎯 PERFIL: {perfil_nome}")
            print(f"   Habilidades Atuais: {', '.join(resultado.get('habilidades_atuais', [])) or 'Nenhuma'}")
            
            if resultado['proximas_habilidades']:
                print(f"   🏆 PRÓXIMAS HABILIDADES RECOMENDADAS:")
                for i, habilidade in enumerate(resultado['proximas_habilidades'], 1):
                    dados = self.grafo[habilidade]
                    valor_esperado = self._calcular_valor_esperado(habilidade, 1)
                    alinhamento = self._calcular_alinhamento_tendencias(habilidade)
                    
                    print(f"      {i}. {habilidade} - {dados['Nome']}")
                    print(f"          ⏱️  {dados['Tempo']}h | 💰 Valor: {dados['Valor']} | "
                          f"🎯 Valor Esperado: {valor_esperado:.1f}")
                    print(f"          📊 Alinhamento: {alinhamento:.0%} | "
                          f"📚 Pré-reqs: {', '.join(dados['Pre_Reqs']) or 'Nenhum'}")
                
                # Métricas da recomendação
                analise = resultado['analise_estrategica']
                print(f"   📈 MÉTRICAS DA RECOMENDAÇÃO:")
                print(f"      Valor Esperado Total: {resultado['valor_esperado']:.1f}")
                print(f"      Alinhamento Médio: {analise['alinhamento_medio']:.0%}")
                print(f"      ROI Esperado: {analise['roi_esperado']:.3f} pontos/hora")
                print(f"      Cenário Mais Favorável: {analise['cenario_mais_favoravel']}")
                
                if analise['gaps_cobertos']:
                    print(f"      🎯 Gaps Cobertos: {', '.join(analise['gaps_cobertos'])}")
                
                print(f"   🔧 MÉTODO: {resultado['metodo_utilizado'].upper()} | "
                      f"Horizonte: {resultado.get('horizonte_considerado', resultado.get('profundidade_considerada', 'N/A'))} anos")
            else:
                print("   ❌ Nenhuma recomendação possível com o perfil atual")
        
        # Análise Comparativa
        print("\n📊 ANÁLISE COMPARATIVA ENTRE PERFIS:")
        print("-" * 45)
        
        comparacao = []
        for perfil_nome, resultado in analise_completa.items():
            if resultado['proximas_habilidades']:
                comparacao.append({
                    'Perfil': perfil_nome,
                    'Habilidades_Recomendadas': ', '.join(resultado['proximas_habilidades']),
                    'Valor_Esperado': resultado['valor_esperado'],
                    'ROI': resultado['analise_estrategica']['roi_esperado'],
                    'Alinhamento': resultado['analise_estrategica']['alinhamento_medio']
                })
        
        if comparacao:
            df_comparacao = pd.DataFrame(comparacao)
            print(df_comparacao.to_string(index=False))
        
        # Insights Estratégicos
        print("\n💡 INSIGHTS ESTRATÉGICOS:")
        print("-" * 30)
        
        # Habilidade mais recomendada
        todas_recomendacoes = []
        for resultado in analise_completa.values():
            todas_recomendacoes.extend(resultado['proximas_habilidades'])
        
        if todas_recomendacoes:
            hab_mais_recomendada = max(set(todas_recomendacoes), key=todas_recomendacoes.count)
            freq = todas_recomendacoes.count(hab_mais_recomendada)
            print(f"   🎯 Habilidade Mais Recomendada: {hab_mais_recomendada} "
                  f"({freq} de {len(analise_completa)} perfis)")
        
        # Tendências identificadas
        print("   📈 Tendências Identificadas:")
        cenario_dominante = max(tendencias.items(), key=lambda x: x[1]['probabilidade'])
        print(f"      • Cenário mais provável: {cenario_dominante[0]} ({cenario_dominante[1]['probabilidade']:.0%})")
        
        # Recomendações gerais
        print("   🚀 Recomendações Gerais:")
        print("      • Focar em habilidades com alto alinhamento a múltiplos cenários")
        print("      • Considerar ROI (Valor/Tempo) além do valor absoluto")
        print("      • Desenvolver habilidades básicas antes de especializações")
        print("      • Manter diversificação para mitigar riscos de mercado")
        
        return {
            'analise_completa': analise_completa,
            'tendencias_mercado': tendencias,
            'comparacao_perfis': comparacao
        }
    
    def gerar_visualizacao_completa(self, analise_completa):
        """Gera visualização completa para o Desafio 5"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Desafio 5 — Sistema de Recomendação de Habilidades\n(DP Horizonte Finito + Análise de Mercado)', 
                    fontsize=16, weight='bold')
        
        # Gráfico 1: Recomendações por Perfil
        perfis = list(analise_completa.keys())
        valores_esperados = [analise_completa[p]['valor_esperado'] for p in perfis]
        num_recomendacoes = [len(analise_completa[p]['proximas_habilidades']) for p in perfis]
        
        x = np.arange(len(perfis))
        largura = 0.35
        
        bars1 = ax1.bar(x - largura/2, valores_esperados, largura, label='Valor Esperado', 
                       color='lightgreen', edgecolor='darkgreen')
        bars2 = ax1.bar(x + largura/2, num_recomendacoes, largura, label='Nº Habilidades Recomendadas', 
                       color='lightblue', edgecolor='darkblue')
        
        ax1.set_title('Recomendações por Perfil - Valor Esperado vs Quantidade')
        ax1.set_xlabel('Perfil')
        ax1.set_ylabel('Valor Esperado / Quantidade')
        ax1.set_xticks(x)
        ax1.set_xticklabels(perfis, rotation=15)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Adicionar valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.1f}' if bars == bars1 else f'{height:.0f}', 
                        ha='center', va='bottom', fontsize=9)
        
        # Gráfico 2: Análise de Cenários de Mercado
        tendencias = analise_completa[perfis[0]]['tendencias_mercado']
        cenarios = list(tendencias.keys())
        probabilidades = [tendencias[c]['probabilidade'] for c in cenarios]
        impactos = [tendencias[c]['impacto_esperado'] for c in cenarios]
        
        x = np.arange(len(cenarios))
        largura = 0.35
        
        bars1 = ax2.bar(x - largura/2, probabilidades, largura, label='Probabilidade', 
                       color='gold', edgecolor='darkorange')
        bars2 = ax2.bar(x + largura/2, impactos, largura, label='Impacto Esperado', 
                       color='lightcoral', edgecolor='darkred')
        
        ax2.set_title('Cenários de Mercado - Probabilidade vs Impacto')
        ax2.set_xlabel('Cenário')
        ax2.set_ylabel('Probabilidade / Impacto')
        ax2.set_xticks(x)
        ax2.set_xticklabels(cenarios, rotation=15)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # Gráfico 3: ROI e Alinhamento das Recomendações
        rois = []
        alinhamentos = []
        perfis_validos = []
        
        for perfil in perfis:
            resultado = analise_completa[perfil]
            if resultado['proximas_habilidades']:
                rois.append(resultado['analise_estrategica']['roi_esperado'])
                alinhamentos.append(resultado['analise_estrategica']['alinhamento_medio'])
                perfis_validos.append(perfil)
        
        if perfis_validos:
            x = np.arange(len(perfis_validos))
            largura = 0.35
            
            bars1 = ax3.bar(x - largura/2, rois, largura, label='ROI Esperado (Pontos/Hora)', 
                           color='lightseagreen', edgecolor='darkcyan')
            bars2 = ax3.bar(x + largura/2, alinhamentos, largura, label='Alinhamento com Tendências', 
                           color='mediumpurple', edgecolor='darkviolet', alpha=0.7)
            
            ax3.set_title('ROI e Alinhamento das Recomendações')
            ax3.set_xlabel('Perfil')
            ax3.set_ylabel('ROI / Alinhamento')
            ax3.set_xticks(x)
            ax3.set_xticklabels(perfis_validos, rotation=15)
            ax3.legend()
            ax3.grid(axis='y', alpha=0.3)
            
            # Adicionar valores
            for i, (roi, alinh) in enumerate(zip(rois, alinhamentos)):
                ax3.text(i - largura/2, roi + 0.01, f'{roi:.3f}', ha='center', va='bottom', fontsize=8)
                ax3.text(i + largura/2, alinh + 0.01, f'{alinh:.0%}', ha='center', va='bottom', fontsize=8)
        
        # Gráfico 4: Frequência das Habilidades Recomendadas
        todas_recomendacoes = []
        for resultado in analise_completa.values():
            todas_recomendacoes.extend(resultado['proximas_habilidades'])
        
        if todas_recomendacoes:
            freq_series = pd.Series(todas_recomendacoes).value_counts()
            
            habilidades = freq_series.index.tolist()
            frequencias = freq_series.values.tolist()
            
            bars = ax4.bar(habilidades, frequencias, color='lightcoral', edgecolor='darkred', alpha=0.7)
            
            ax4.set_title('Frequência das Habilidades nas Recomendações')
            ax4.set_xlabel('Habilidade')
            ax4.set_ylabel('Frequência de Recomendação')
            ax4.grid(axis='y', alpha=0.3)
            
            # Adicionar valores
            for bar, freq in zip(bars, frequencias):
                ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                        f'{freq}', ha='center', va='bottom', fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'NENHUMA RECOMENDAÇÃO\nGERADA', 
                    ha='center', va='center', transform=ax4.transAxes, 
                    fontsize=16, weight='bold', color='red')
            ax4.set_title('Frequência das Habilidades nas Recomendações')
        
        plt.tight_layout()
        return fig

def executar_desafio5(grafo, cenarios_mercado):
    """
    Função principal do Desafio 5
    """
    logging.info("=" * 60)
    logging.info("INICIANDO DESAFIO 5 - RECOMENDAR PRÓXIMAS HABILIDADES")
    logging.info("=" * 60)
    
    try:
        # Criar recomendador
        recomendador = RecomendadorHabilidades(grafo, cenarios_mercado)
        
        # Executar análise completa
        print("🔍 Executando análise completa de recomendações...")
        analise_completa = recomendador.executar_analise_completa()
        
        # Gerar relatório
        relatorio = recomendador.gerar_relatorio_detalhado(analise_completa)
        
        # Gerar visualização
        print("📊 Gerando visualizações...")
        fig = recomendador.gerar_visualizacao_completa(analise_completa)
        
        logging.info("Desafio 5 executado com sucesso")
        
        return {
            'sucesso': True,
            'analise_completa': analise_completa,
            'relatorio': relatorio,
            'figura': fig
        }
        
    except Exception as e:
        logging.error(f"Erro no Desafio 5: {e}")
        return {
            'sucesso': False,
            'erro': str(e)
        }

if __name__ == "__main__":
    # Configurar logging para teste
    logging.basicConfig(level=logging.INFO)
    
    # Dados de teste
    from dados import HABILIDADES, CENARIOS_MERCADO
    
    # Executar desafio
    resultado = executar_desafio5(HABILIDADES, CENARIOS_MERCADO)
    
    if resultado['sucesso']:
        print("\n🎉 Desafio 5 concluído com sucesso!")
        plt.show()  # Mostrar gráficos
    else:
        print(f"❌ Erro: {resultado['erro']}")