import logging
import numpy as np
import random
from collections import deque, defaultdict
import matplotlib.pyplot as plt
import time

class OtimizadorCaminhoDP:
    def __init__(self, grafo, tempo_max=350, complexidade_max=30, objetivo='S6'):
        self.grafo = grafo
        self.tempo_max = tempo_max
        self.complexidade_max = complexidade_max
        self.objetivo = objetivo
        self.ordenacao_topologica = self._calcular_ordenacao_topologica()
        
    def _calcular_ordenacao_topologica(self):
        """Calcula ordenação topológica do grafo para processamento em ordem correta"""
        graus_entrada = {no: 0 for no in self.grafo}
        arestas_saida = defaultdict(list)
        
        # Construir grafo de dependências
        for no, dados in self.grafo.items():
            for prereq in dados['Pre_Reqs']:
                graus_entrada[no] += 1
                arestas_saida[prereq].append(no)
        
        # Encontrar nós sem dependências (grau de entrada 0)
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
            ciclos = [no for no in self.grafo if no not in ordenacao]
            raise ValueError(f"Grafo contém ciclos - nós não ordenados: {ciclos}")
        
        logging.info(f"Ordenação topológica calculada: {ordenacao}")
        return ordenacao
    
    def knapsack_multidimensional_dp(self):
        """
        Implementação completa da Programação Dinâmica multidimensional
        DP[no][tempo][complexidade] = valor máximo
        """
        logging.info("Iniciando Programação Dinâmica multidimensional...")
        start_time = time.time()
        
        # Inicializar estruturas DP
        dp = {}  # dp[no][t][c] = valor máximo
        caminho = {}  # caminho[no][t][c] = sequência de habilidades
        pre_requisitos_map = {}  # Mapeamento de pré-requisitos
        
        # Inicializar para todos os nós
        for no in self.ordenacao_topologica:
            dp[no] = np.zeros((self.tempo_max + 1, self.complexidade_max + 1))
            caminho[no] = [[[] for _ in range(self.complexidade_max + 1)] 
                          for _ in range(self.tempo_max + 1)]
            pre_requisitos_map[no] = self.grafo[no]['Pre_Reqs']
        
        # Processar cada nó na ordem topológica
        for no in self.ordenacao_topologica:
            dados_no = self.grafo[no]
            tempo_no = dados_no['Tempo']
            valor_no = dados_no['Valor']
            complexidade_no = dados_no['Complexidade']
            
            logging.debug(f"Processando nó {no}: T={tempo_no}, V={valor_no}, C={complexidade_no}")
            
            for tempo in range(self.tempo_max + 1):
                for comp in range(self.complexidade_max + 1):
                    # Valor máximo herdado do nó anterior na ordenação
                    valor_herdado = 0
                    caminho_herdado = []
                    
                    if self.ordenacao_topologica.index(no) > 0:
                        no_anterior = self.ordenacao_topologica[self.ordenacao_topologica.index(no) - 1]
                        valor_herdado = dp[no_anterior][tempo][comp]
                        caminho_herdado = caminho[no_anterior][tempo][comp]
                    
                    # Verificar se podemos incluir o nó atual
                    valor_com_no = 0
                    caminho_com_no = []
                    
                    if (tempo >= tempo_no and comp >= complexidade_no and
                        self._verificar_pre_requisitos_satisfeitos(no, dp, tempo - tempo_no, comp - complexidade_no)):
                        
                        valor_com_no = valor_no
                        caminho_com_no = [no]
                        
                        # Adicionar valor dos pré-requisitos (se houver)
                        for prereq in pre_requisitos_map[no]:
                            if prereq in dp:
                                valor_com_no += dp[prereq][tempo - tempo_no][comp - complexidade_no]
                                caminho_prereq = caminho[prereq][tempo - tempo_no][comp - complexidade_no]
                                if caminho_prereq:
                                    # Combinar caminhos mantendo a ordem
                                    caminho_com_no = caminho_prereq + caminho_com_no
                    
                    # Escolher o melhor entre incluir ou não o nó
                    if valor_com_no > valor_herdado:
                        dp[no][tempo][comp] = valor_com_no
                        caminho[no][tempo][comp] = caminho_com_no
                    else:
                        dp[no][tempo][comp] = valor_herdado
                        caminho[no][tempo][comp] = caminho_herdado
        
        # Encontrar a melhor solução que inclui o nó objetivo
        melhor_valor_total = 0
        melhor_caminho_total = []
        melhor_tempo_usado = 0
        melhor_complexidade_usada = 0
        
        for tempo in range(self.tempo_max + 1):
            for comp in range(self.complexidade_max + 1):
                if self.objetivo in caminho[self.objetivo][tempo][comp]:
                    if dp[self.objetivo][tempo][comp] > melhor_valor_total:
                        melhor_valor_total = dp[self.objetivo][tempo][comp]
                        melhor_caminho_total = caminho[self.objetivo][tempo][comp]
                        melhor_tempo_usado = tempo
                        melhor_complexidade_usada = comp
        
        end_time = time.time()
        logging.info(f"DP concluída em {end_time - start_time:.2f} segundos")
        
        if melhor_valor_total == 0:
            raise ValueError(f"Não foi possível encontrar caminho válido para {self.objetivo} com as restrições fornecidas")
        
        return {
            'valor_maximo': melhor_valor_total,
            'caminho_otimo': melhor_caminho_total,
            'tempo_utilizado': melhor_tempo_usado,
            'complexidade_utilizada': melhor_complexidade_usada,
            'eficiencia_tempo': melhor_valor_total / melhor_tempo_usado if melhor_tempo_usado > 0 else 0,
            'eficiencia_complexidade': melhor_valor_total / melhor_complexidade_usada if melhor_complexidade_usada > 0 else 0,
            'recursos_restantes': {
                'tempo': self.tempo_max - melhor_tempo_usado,
                'complexidade': self.complexidade_max - melhor_complexidade_usada
            }
        }
    
    def _verificar_pre_requisitos_satisfeitos(self, no, dp, tempo, complexidade):
        """Verifica se todos os pré-requisitos podem ser satisfeitos com os recursos dados"""
        for prereq in self.grafo[no]['Pre_Reqs']:
            if prereq not in dp or dp[prereq][tempo][complexidade] == 0:
                return False
        return True
    
    def simulacao_monte_carlo(self, n_simulacoes=1000):
        """
        Simulação Monte Carlo com incerteza nos parâmetros
        V ~ Uniforme[V-10%, V+10%], T ~ Uniforme[T-10%, T+10%]
        """
        logging.info(f"Iniciando simulação Monte Carlo com {n_simulacoes} cenários")
        start_time = time.time()
        
        valores_totais = []
        caminhos_validos = []
        tempos_utilizados = []
        complexidades_utilizadas = []
        
        for i in range(n_simulacoes):
            if i % 100 == 0:
                logging.info(f"Simulação {i}/{n_simulacoes}")
            
            # Criar cópia do grafo com valores incertos
            grafo_incerto = {}
            for no, dados in self.grafo.items():
                valor_incerto = dados['Valor'] * random.uniform(0.9, 1.1)
                tempo_incerto = dados['Tempo'] * random.uniform(0.9, 1.1)
                
                grafo_incerto[no] = {
                    'Nome': dados['Nome'],
                    'Tempo': int(tempo_incerto),
                    'Valor': valor_incerto,
                    'Complexidade': dados['Complexidade'],
                    'Pre_Reqs': dados['Pre_Reqs']
                }
            
            # Executar DP para este cenário
            try:
                otimizador_incerto = OtimizadorCaminhoDP(
                    grafo_incerto, self.tempo_max, self.complexidade_max, self.objetivo
                )
                resultado_incerto = otimizador_incerto.knapsack_multidimensional_dp()
                
                valores_totais.append(resultado_incerto['valor_maximo'])
                caminhos_validos.append(resultado_incerto['caminho_otimo'])
                tempos_utilizados.append(resultado_incerto['tempo_utilizado'])
                complexidades_utilizadas.append(resultado_incerto['complexidade_utilizada'])
                
            except Exception as e:
                logging.warning(f"Erro na simulação {i}: {e}")
                continue
        
        # Análise estatística
        valores_array = np.array(valores_totais)
        tempos_array = np.array(tempos_utilizados)
        complexidades_array = np.array(complexidades_utilizadas)
        
        end_time = time.time()
        logging.info(f"Monte Carlo concluído em {end_time - start_time:.2f} segundos")
        
        return {
            'valores_simulados': valores_totais,
            'caminhos_simulados': caminhos_validos,
            'tempos_utilizados': tempos_utilizados,
            'complexidades_utilizadas': complexidades_utilizadas,
            'media_valor': np.mean(valores_array) if len(valores_array) > 0 else 0,
            'desvio_padrao_valor': np.std(valores_array) if len(valores_array) > 0 else 0,
            'media_tempo': np.mean(tempos_array) if len(tempos_array) > 0 else 0,
            'media_complexidade': np.mean(complexidades_array) if len(complexidades_array) > 0 else 0,
            'valor_minimo': np.min(valores_array) if len(valores_array) > 0 else 0,
            'valor_maximo': np.max(valores_array) if len(valores_array) > 0 else 0,
            'coef_variacao': (np.std(valores_array) / np.mean(valores_array)) if len(valores_array) > 0 and np.mean(valores_array) > 0 else 0,
            'intervalo_confianca_95': (
                np.mean(valores_array) - 1.96 * np.std(valores_array) / np.sqrt(len(valores_array)),
                np.mean(valores_array) + 1.96 * np.std(valores_array) / np.sqrt(len(valores_array))
            ) if len(valores_array) > 0 else (0, 0),
            'cenarios_validos': len(valores_totais),
            'taxa_sucesso': len(valores_totais) / n_simulacoes
        }
    
    def comparar_solucoes_deterministica_estocastica(self, resultado_deterministico, resultado_monte_carlo):
        """Compara a solução determinística com a análise estocástica"""
        valor_det = resultado_deterministico['valor_maximo']
        valor_est = resultado_monte_carlo['media_valor']
        
        diferenca_absoluta = valor_est - valor_det
        diferenca_relativa = (diferenca_absoluta / valor_det * 100) if valor_det > 0 else 0
        
        # Classificar robustez
        coef_variacao = resultado_monte_carlo['coef_variacao']
        if coef_variacao < 0.05:
            robustez = "MUITO ALTA"
        elif coef_variacao < 0.1:
            robustez = "ALTA"
        elif coef_variacao < 0.2:
            robustez = "MODERADA"
        else:
            robustez = "BAIXA"
        
        return {
            'deterministico': {
                'valor': valor_det,
                'caminho': resultado_deterministico['caminho_otimo'],
                'tempo': resultado_deterministico['tempo_utilizado'],
                'complexidade': resultado_deterministico['complexidade_utilizada'],
                'eficiencia_tempo': resultado_deterministico['eficiencia_tempo'],
                'eficiencia_complexidade': resultado_deterministico['eficiencia_complexidade']
            },
            'estocastico': {
                'valor_medio': valor_est,
                'desvio_padrao': resultado_monte_carlo['desvio_padrao_valor'],
                'coef_variacao': coef_variacao,
                'intervalo_confianca_95': resultado_monte_carlo['intervalo_confianca_95'],
                'valor_minimo': resultado_monte_carlo['valor_minimo'],
                'valor_maximo': resultado_monte_carlo['valor_maximo']
            },
            'comparacao': {
                'diferenca_absoluta': diferenca_absoluta,
                'diferenca_relativa': diferenca_relativa,
                'robustez': robustez,
                'taxa_sucesso_simulacoes': resultado_monte_carlo['taxa_sucesso']
            }
        }
    
    def gerar_relatorio_detalhado(self, resultado_deterministico, resultado_monte_carlo, comparacao):
        """Gera relatório detalhado do Desafio 1"""
        print("=" * 80)
        print("DESAFIO 1 — CAMINHO DE VALOR MÁXIMO - RELATÓRIO DETALHADO")
        print("=" * 80)
        print("🎯 OBJETIVO: Encontrar sequência até S6 que maximize valor")
        print(f"📊 RESTRIÇÕES: T ≤ {self.tempo_max}h, C ≤ {self.complexidade_max}")
        print()
        
        print("✅ SOLUÇÃO DETERMINÍSTICA (PROGRAMAÇÃO DINÂMICA):")
        print("-" * 55)
        print(f"Valor Máximo: {resultado_deterministico['valor_maximo']:.2f}")
        print(f"Caminho Ótimo: {' → '.join(resultado_deterministico['caminho_otimo'])}")
        print(f"Tempo Utilizado: {resultado_deterministico['tempo_utilizado']:.1f}h")
        print(f"Complexidade Utilizada: {resultado_deterministico['complexidade_utilizada']:.1f}")
        print(f"Recursos Restantes: T={resultado_deterministico['recursos_restantes']['tempo']}h, "
              f"C={resultado_deterministico['recursos_restantes']['complexidade']}")
        print(f"Eficiência (V/T): {resultado_deterministico['eficiencia_tempo']:.4f}")
        print(f"Eficiência (V/C): {resultado_deterministico['eficiencia_complexidade']:.4f}")
        print()
        
        # Detalhamento do caminho
        print("📝 DETALHAMENTO DO CAMINHO ÓTIMO:")
        print("-" * 35)
        tempo_acumulado = 0
        complexidade_acumulada = 0
        valor_acumulado = 0
        
        for i, habilidade in enumerate(resultado_deterministico['caminho_otimo'], 1):
            dados = self.grafo[habilidade]
            tempo_acumulado += dados['Tempo']
            complexidade_acumulada += dados['Complexidade']
            valor_acumulado += dados['Valor']
            
            print(f"  {i}. {habilidade} - {dados['Nome']}")
            print(f"     ⏱️  {dados['Tempo']}h (Acum: {tempo_acumulado}h) | "
                  f"💰 {dados['Valor']} (Acum: {valor_acumulado}) | "
                  f"🎯 C: {dados['Complexidade']} (Acum: {complexidade_acumulada})")
        print()
        
        print("🎲 ANÁLISE ESTOCÁSTICA (MONTE CARLO):")
        print("-" * 40)
        print(f"Cenários Simulados: {resultado_monte_carlo['cenarios_validos']}")
        print(f"Taxa de Sucesso: {resultado_monte_carlo['taxa_sucesso']:.1%}")
        print(f"Valor Esperado (E[V]): {resultado_monte_carlo['media_valor']:.2f}")
        print(f"Desvio Padrão (σ): {resultado_monte_carlo['desvio_padrao_valor']:.2f}")
        print(f"Coeficiente de Variação: {resultado_monte_carlo['coef_variacao']:.2%}")
        print(f"Intervalo 95% Confiança: [{comparacao['estocastico']['intervalo_confianca_95'][0]:.2f}, "
              f"{comparacao['estocastico']['intervalo_confianca_95'][1]:.2f}]")
        print(f"Valor Mínimo Simulado: {resultado_monte_carlo['valor_minimo']:.2f}")
        print(f"Valor Máximo Simulado: {resultado_monte_carlo['valor_maximo']:.2f}")
        print(f"Tempo Médio Utilizado: {resultado_monte_carlo['media_tempo']:.1f}h")
        print(f"Complexidade Média: {resultado_monte_carlo['media_complexidade']:.1f}")
        print()
        
        print("📈 COMPARAÇÃO E ANÁLISE DE ROBUSTEZ:")
        print("-" * 45)
        diferenca = comparacao['comparacao']['diferenca_relativa']
        if abs(diferenca) < 2:
            status = "CONVERGENTE"
            emoji = "🟢"
        elif abs(diferenca) < 5:
            status = "PRÓXIMO"
            emoji = "🟡"
        elif abs(diferenca) < 10:
            status = "MODERADO"
            emoji = "🟠"
        else:
            status = "DIVERGENTE"
            emoji = "🔴"
        
        print(f"Diferença Relativa: {diferenca:+.2f}% {emoji} ({status})")
        print(f"Robustez da Solução: {comparacao['comparacao']['robustez']} "
              f"(CV = {comparacao['estocastico']['coef_variacao']:.2%})")
        print(f"Confiança na Solução: {'ALTA' if comparacao['comparacao']['taxa_sucesso_simulacoes'] > 0.9 else 'MÉDIA' if comparacao['comparacao']['taxa_sucesso_simulacoes'] > 0.7 else 'BAIXA'}")
        
        return {
            'deterministico': resultado_deterministico,
            'estocastico': resultado_monte_carlo,
            'comparacao': comparacao
        }
    
    def gerar_visualizacao_completa(self, resultado_deterministico, resultado_monte_carlo, comparacao):
        """Gera visualização completa para o Desafio 1"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Desafio 1 — Análise de Caminho de Valor Máximo\n(Programação Dinâmica Multidimensional + Monte Carlo)', 
                    fontsize=16, weight='bold')
        
        # Gráfico 1: Distribuição Monte Carlo
        valores = resultado_monte_carlo['valores_simulados']
        n, bins, patches = ax1.hist(valores, bins=30, color='steelblue', 
                                   edgecolor='black', alpha=0.7, density=True)
        
        media = resultado_monte_carlo['media_valor']
        std = resultado_monte_carlo['desvio_padrao_valor']
        deterministico = resultado_deterministico['valor_maximo']
        
        ax1.axvline(media, color='red', linestyle='-', linewidth=2, 
                   label=f'Média Estocástica = {media:.2f}')
        ax1.axvline(deterministico, color='green', linestyle='--', linewidth=2, 
                   label=f'Determinístico = {deterministico:.2f}')
        ax1.axvline(media + std, color='orange', linestyle=':', linewidth=1.5, 
                   label=f'+1σ = {media + std:.2f}')
        ax1.axvline(media - std, color='orange', linestyle=':', linewidth=1.5, 
                   label=f'-1σ = {media - std:.2f}')
        
        ax1.set_title('Distribuição do Valor Total - Simulação Monte Carlo\n(1000 cenários com incerteza ±10%)')
        ax1.set_xlabel('Valor Total do Caminho')
        ax1.set_ylabel('Densidade de Probabilidade')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.6)
        
        # Gráfico 2: Caminho Ótimo e Recursos
        caminho = resultado_deterministico['caminho_otimo']
        tempos = [self.grafo[h]['Tempo'] for h in caminho]
        valores = [self.grafo[h]['Valor'] for h in caminho]
        complexidades = [self.grafo[h]['Complexidade'] for h in caminho]
        
        x = np.arange(len(caminho))
        largura = 0.25
        
        bars1 = ax2.bar(x - largura, tempos, largura, label='Tempo (h)', color='lightblue', edgecolor='navy')
        bars2 = ax2.bar(x, valores, largura, label='Valor', color='lightgreen', edgecolor='darkgreen')
        bars3 = ax2.bar(x + largura, complexidades, largura, label='Complexidade', color='lightcoral', edgecolor='darkred')
        
        ax2.set_title('Caminho Ótimo - Composição por Habilidade')
        ax2.set_xlabel('Sequência no Caminho')
        ax2.set_ylabel('Valores')
        ax2.set_xticks(x)
        ax2.set_xticklabels(caminho, rotation=45)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # Adicionar valores nas barras
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=8)
        
        # Gráfico 3: Utilização de Recursos
        recursos = ['Tempo', 'Complexidade']
        utilizados = [resultado_deterministico['tempo_utilizado'], 
                     resultado_deterministico['complexidade_utilizada']]
        limites = [self.tempo_max, self.complexidade_max]
        utilizacao_percent = [u/l*100 for u, l in zip(utilizados, limites)]
        
        colors = ['lightblue', 'lightcoral']
        bars = ax3.bar(recursos, utilizados, color=colors, edgecolor=['blue', 'red'], alpha=0.7)
        ax3.axhline(self.tempo_max, color='blue', linestyle='--', alpha=0.5, label=f'Limite Tempo ({self.tempo_max}h)')
        ax3.axhline(self.complexidade_max, color='red', linestyle='--', alpha=0.5, label=f'Limite Complex. ({self.complexidade_max})')
        
        ax3.set_title('Utilização de Recursos no Caminho Ótimo')
        ax3.set_ylabel('Valor Utilizado')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # Adicionar porcentagens
        for i, (bar, perc) in enumerate(zip(bars, utilizacao_percent)):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 2, 
                    f'{perc:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico 4: Análise de Sensibilidade
        diferenca = comparacao['comparacao']['diferenca_relativa']
        coef_variacao = resultado_monte_carlo['coef_variacao'] * 100
        taxa_sucesso = resultado_monte_carlo['taxa_sucesso'] * 100
        
        metrics = ['Diferença\nRelativa', 'Coeficiente\nde Variação', 'Taxa de\nSucesso']
        values = [abs(diferenca), coef_variacao, taxa_sucesso]
        
        # Cores baseadas nos valores
        colors = []
        for val in values:
            if val < 5:
                colors.append('lightgreen')
            elif val < 10:
                colors.append('lightyellow')
            else:
                colors.append('lightcoral')
        
        bars = ax4.bar(metrics, values, color=colors, edgecolor='black', alpha=0.7)
        ax4.set_title('Análise de Sensibilidade e Robustez')
        ax4.set_ylabel('Valor (%)')
        ax4.grid(axis='y', alpha=0.3)
        
        # Adicionar valores
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1, 
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax4.axhline(5, color='green', linestyle='--', alpha=0.5, label='Limite Ideal')
        ax4.axhline(10, color='orange', linestyle='--', alpha=0.5, label='Limite Aceitável')
        ax4.legend()
        
        plt.tight_layout()
        return fig

def executar_desafio1(grafo, tempo_max=350, complexidade_max=30, n_simulacoes=1000):
    """
    Função principal do Desafio 1
    """
    logging.info("=" * 60)
    logging.info("INICIANDO DESAFIO 1 - CAMINHO DE VALOR MÁXIMO")
    logging.info("=" * 60)
    
    try:
        # Criar otimizador
        otimizador = OtimizadorCaminhoDP(
            grafo=grafo,
            tempo_max=tempo_max,
            complexidade_max=complexidade_max,
            objetivo='S6'
        )
        
        # Executar Programação Dinâmica
        print("🧮 Executando Programação Dinâmica...")
        resultado_dp = otimizador.knapsack_multidimensional_dp()
        
        # Executar Monte Carlo
        print("🎲 Executando simulação Monte Carlo...")
        resultado_mc = otimizador.simulacao_monte_carlo(n_simulacoes=n_simulacoes)
        
        # Comparar resultados
        comparacao = otimizador.comparar_solucoes_deterministica_estocastica(resultado_dp, resultado_mc)
        
        # Gerar relatório
        relatorio = otimizador.gerar_relatorio_detalhado(resultado_dp, resultado_mc, comparacao)
        
        # Gerar visualização
        print("📊 Gerando visualizações...")
        fig = otimizador.gerar_visualizacao_completa(resultado_dp, resultado_mc, comparacao)
        
        logging.info("Desafio 1 executado com sucesso")
        
        return {
            'sucesso': True,
            'deterministico': resultado_dp,
            'monte_carlo': resultado_mc,
            'comparacao': comparacao,
            'figura': fig
        }
        
    except Exception as e:
        logging.error(f"Erro no Desafio 1: {e}")
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
    resultado = executar_desafio1(HABILIDADES)
    
    if resultado['sucesso']:
        print("\n🎉 Desafio 1 concluído com sucesso!")
        plt.show()  # Mostrar gráficos
    else:
        print(f"❌ Erro: {resultado['erro']}")