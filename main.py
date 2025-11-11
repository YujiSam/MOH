import logging
from datetime import datetime
import matplotlib.pyplot as plt
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import dos módulos
from dados import HABILIDADES, HABILIDADES_CRITICAS, CENARIOS_MERCADO
from validador_grafo import ValidadorGrafo
from desafio1 import executar_desafio1
from desafio2 import executar_desafio2
from desafio3 import executar_desafio3  
from desafio4 import executar_desafio4
from desafio5 import executar_desafio5

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"moh_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

class OrchestradorMOH:
    def __init__(self):
        self.resultados = {}
        self.grafo_validado = False
    
    def validar_grafo(self):
        """Valida o grafo antes de executar os desafios"""
        print("🔍 VALIDANDO GRAFO...")
        validador = ValidadorGrafo(HABILIDADES)
        relatorio = validador.validar_grafo_completo()
        
        if relatorio['valido']:
            print("✅ GRAFO VALIDADO COM SUCESSO")
            self.grafo_validado = True
        else:
            print("❌ GRAFO INVÁLIDO:")
            if relatorio['ciclos']:
                print(f"   Ciclos: {relatorio['ciclos']}")
            if relatorio['pre_requisitos_inexistentes']:
                print(f"   Pré-requisitos inexistentes: {relatorio['pre_requisitos_inexistentes']}")
        
        return relatorio['valido']
    
    def executar_desafio1(self):
        """Executa o Desafio 1"""
        if not self.grafo_validado:
            print("❌ Grafo não validado. Execute a validação primeiro.")
            return
        
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 1 - CAMINHO DE VALOR MÁXIMO")
        print("="*60)
        
        resultado = executar_desafio1(HABILIDADES)
        
        if resultado['sucesso']:
            det = resultado['deterministico']
            mc = resultado['monte_carlo']
            
            print(f"✅ SOLUÇÃO DETERMINÍSTICA:")
            print(f"   Caminho: {' → '.join(det['caminho_otimo'])}")
            print(f"   Valor: {det['valor_maximo']}")
            print(f"   Tempo: {det['tempo_utilizado']}h")
            print(f"   Complexidade: {det['complexidade_utilizada']}")
            
            print(f"🎲 ANÁLISE MONTE CARLO:")
            print(f"   Valor Esperado: {mc['media_valor']:.2f}")
            print(f"   Desvio Padrão: {mc['desvio_padrao_valor']:.2f}")
            print(f"   Coef. Variação: {mc['coef_variacao']:.2%}")
            
            self.resultados['desafio1'] = resultado
            
            # Mostrar gráfico
            if 'figura' in resultado:
                plt.figure(resultado['figura'].number)
                plt.show(block=False)
                print("📊 Gráfico do Desafio 1 exibido")
        else:
            print(f"❌ ERRO: {resultado['erro']}")
    
    def executar_desafio2(self):
        """Executa o Desafio 2"""
        if not self.grafo_validado:
            print("❌ Grafo não validado. Execute a validação primeiro.")
            return
            
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 2 - VERIFICAÇÃO CRÍTICA")
        print("="*60)
        
        resultado = executar_desafio2(HABILIDADES, HABILIDADES_CRITICAS)
        
        if resultado['sucesso']:
            melhores = resultado['melhores_permutacoes']
            estatisticas = resultado['estatisticas']
            
            print(f"✅ ANÁLISE DE {estatisticas['total_permutacoes']} PERMUTAÇÕES VÁLIDAS")
            print(f"🏆 MELHORES ORDENS:")
            
            for i, perm in enumerate(melhores, 1):
                print(f"{i}º: {' → '.join(perm['permutacao'])}")
                print(f"Custo: {perm['custo_total']}h | ")
                print(f"Eficiência: {perm['eficiencia']:.3f}")
            
            print(f"📊 ESTATÍSTICAS:")
            print(f"   Custo Médio: {estatisticas['custo_medio']:.1f}h")
            print(f"   Melhor Custo: {estatisticas['custo_melhor']}h")
            print(f"   Pior Custo: {estatisticas['custo_pior']}h")
            
            self.resultados['desafio2'] = resultado
            
            # Mostrar gráfico
            if 'figura' in resultado:
                plt.figure(resultado['figura'].number)
                plt.show(block=False)
                print("📊 Gráfico do Desafio 2 exibido")
        else:
            print(f"❌ ERRO: {resultado['erro']}")
    
    def executar_desafio3(self):
        """Executa o Desafio 3"""
        if not self.grafo_validado:
            print("❌ Grafo não validado. Execute a validação primeiro.")
            return
            
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 3 - PIVÔ MAIS RÁPIDO")
        print("="*60)
        
        resultado = executar_desafio3(HABILIDADES)
        
        if resultado['sucesso']:
            analise = resultado['analise_completa']
            meta_principal = 15
            
            guloso = analise['guloso'][meta_principal]['razao_vt']
            otimo = analise['otimo'][meta_principal]
            
            print(f"🤖 ESTRATÉGIA GULOSA (V/T):")
            print(f"   Adaptabilidade: S = {guloso['adaptabilidade_final']}")
            print(f"   Tempo: {guloso['tempo_total']}h")
            print(f"   Habilidades: {', '.join(guloso['habilidades_escolhidas'])}")
            
            print(f"⭐ SOLUÇÃO ÓTIMA:")
            print(f"   Adaptabilidade: S = {otimo['adaptabilidade_final']}")
            print(f"   Tempo: {otimo['tempo_total']}h") 
            print(f"   Habilidades: {', '.join(otimo['habilidades_escolhidas'])}")
            
            # Verificar contraexemplos
            contraexemplos = [ce for ce in analise['contraexemplos'] if ce['meta'] == meta_principal]
            if contraexemplos:
                print(f"🚨 CONTRAEXEMPLO ENCONTRADO!")
                for ce in contraexemplos:
                    print(f"   Tipo: {ce['tipo']}")
                    print(f"   Guloso: S={ce['guloso']['adaptabilidade_final']}, T={ce['guloso']['tempo_total']}h")
                    print(f"   Ótimo: S={ce['otimo']['adaptabilidade_final']}, T={ce['otimo']['tempo_total']}h")
            else:
                print("✅ Nenhum contraexemplo encontrado - Guloso é ótimo para este cenário")
            
            self.resultados['desafio3'] = resultado
            
            # Mostrar gráfico
            if 'figura' in resultado:
                plt.figure(resultado['figura'].number)
                plt.show(block=False)
                print("📊 Gráfico do Desafio 3 exibido")
        else:
            print(f"❌ ERRO: {resultado['erro']}")
    
    def executar_desafio4(self):
        """Executa o Desafio 4"""
        if not self.grafo_validado:
            print("❌ Grafo não validado. Execute a validação primeiro.")
            return
            
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 4 - TRILHAS PARALELAS")
        print("="*60)
        
        resultado = executar_desafio4(HABILIDADES)
        
        if resultado['sucesso']:
            analise = resultado['analise_completa']
            sprints = analise['sprints']
            
            print(f"✅ ORDENAÇÃO POR COMPLEXIDADE CONCLUÍDA")
            
            print(f"🚀 SPRINT A (1-6):")
            for i, hab in enumerate(sprints['sprint_a']['habilidades'], 1):
                print(f"   {i}. {hab['ID']} - C:{hab['Complexidade']}")
            
            print(f"🚀 SPRINT B (7-12):")
            for i, hab in enumerate(sprints['sprint_b']['habilidades'], 1):
                print(f"   {i}. {hab['ID']} - C:{hab['Complexidade']}")
            
            metricas_a = sprints['sprint_a']['metricas']
            metricas_b = sprints['sprint_b']['metricas']
            
            print(f"📊 MÉTRICAS DAS SPRINTS:")
            print(f"   Sprint A: T:{metricas_a['tempo_total']}h, V:{metricas_a['valor_total']}, ")
            print(f"C médio:{metricas_a['complexidade_media']:.1f}")
            print(f"   Sprint B: T:{metricas_b['tempo_total']}h, V:{metricas_b['valor_total']}, ")
            print(f"C médio:{metricas_b['complexidade_media']:.1f}")
            print(f"   Diferença tempo: {sprints['diferenca_tempo']}h")
            
            # Comparação de algoritmos
            desempenho = analise['comparacao_desempenho']['Complexidade']
            print(f"⚡ COMPARAÇÃO DE ALGORITMOS:")
            print(f"   Merge Sort: {desempenho['merge_sort']['tempo_medio']:.6f}s")
            print(f"   Quick Sort: {desempenho['quick_sort']['tempo_medio']:.6f}s") 
            print(f"   Sort Nativo: {desempenho['sort_nativo']['tempo_medio']:.6f}s")
            
            self.resultados['desafio4'] = resultado
            
            # Mostrar gráfico
            if 'figura' in resultado:
                plt.figure(resultado['figura'].number)
                plt.show(block=False)
                print("📊 Gráfico do Desafio 4 exibido")
        else:
            print(f"❌ ERRO: {resultado['erro']}")
    
    def executar_desafio5(self):
        """Executa o Desafio 5"""
        if not self.grafo_validado:
            print("❌ Grafo não validado. Execute a validação primeiro.")
            return
            
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 5 - RECOMENDAR HABILIDADES")
        print("="*60)
        
        resultado = executar_desafio5(HABILIDADES, CENARIOS_MERCADO)
        
        if resultado['sucesso']:
            analise = resultado['analise_completa']
            
            print(f"✅ SISTEMA DE RECOMENDAÇÃO CONCLUÍDO")
            print(f"📊 ANÁLISE DE {len(analise)} PERFIS")
            
            for perfil, dados in analise.items():
                if dados['proximas_habilidades']:
                    print(f"\n👤 {perfil.upper()}:")
                    print(f"   Habilidades atuais: {dados.get('habilidades_atuais', [])}")
                    print(f"   Recomendações: {', '.join(dados['proximas_habilidades'])}")
                    print(f"   Valor esperado: {dados['valor_esperado']:.1f}")
                    print(f"   ROI: {dados['analise_estrategica']['roi_esperado']:.3f}")
                else:
                    print(f"\n👤 {perfil.upper()}: Nenhuma recomendação possível")
            
            self.resultados['desafio5'] = resultado
            
            # Mostrar gráfico
            if 'figura' in resultado:
                plt.figure(resultado['figura'].number)
                plt.show(block=False)
                print("📊 Gráfico do Desafio 5 exibido")
        else:
            print(f"❌ ERRO: {resultado['erro']}")
    
    def executar_todos_desafios(self):
        """Executa todos os desafios em sequência"""
        print("🚀 INICIANDO EXECUÇÃO DO MAPA DE OPORTUNIDADES DE HABILIDADES")
        print("="*70)
        
        # 1. Validação do Grafo (obrigatório)
        if not self.validar_grafo():
            print("❌ Execução interrompida - Grafo inválido")
            return
        
        # 2. Executar desafios sequencialmente
        self.executar_desafio1()
        input("\n⏎ Pressione Enter para continuar para o próximo desafio...")
        
        self.executar_desafio2() 
        input("\n⏎ Pressione Enter para continuar para o próximo desafio...")
        
        self.executar_desafio3()
        input("\n⏎ Pressione Enter para continuar para o próximo desafio...")
        
        self.executar_desafio4()
        input("\n⏎ Pressione Enter para continuar para o próximo desafio...")
        
        self.executar_desafio5()
        
        # 3. Relatório final
        self.gerar_relatorio_final()
    
    def gerar_relatorio_final(self):
        """Gera relatório consolidado"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL - MOH")
        print("="*70)
        
        desafios_executados = [k for k in self.resultados.keys() if self.resultados[k]['sucesso']]
        print(f"✅ Desafios executados com sucesso: {len(desafios_executados)}/5")
        
        for desafio in ['desafio1', 'desafio2', 'desafio3', 'desafio4', 'desafio5']:
            status = "✅" if desafio in desafios_executados else "❌"
            print(f"   {status} {desafio.upper()}")
        
        if desafios_executados:
            print(f"\n🎉 Execução concluída em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            print("📈 Todos os gráficos foram gerados e exibidos")
            print("\n💡 Dica: Feche as janelas dos gráficos para finalizar o programa")
        else:
            print("❌ Nenhum desafio foi executado com sucesso")

def main():
    """Função principal"""
    try:
        # Configurar matplotlib para mostrar gráficos não-bloqueantes
        plt.ion()
        
        orchestrator = OrchestradorMOH()
        orchestrator.executar_todos_desafios()
        
        # Manter o programa aberto até que o usuário feche os gráficos
        if any('figura' in resultado for resultado in orchestrator.resultados.values()):
            print("\n🔄 Aguardando fechamento dos gráficos...")
            plt.show(block=True)
            
    except Exception as e:
        logging.error(f"Erro na execução: {e}")
        print(f"❌ Erro crítico: {e}")
    finally:
        plt.ioff()

if __name__ == "__main__":
    main()