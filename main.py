import logging
from datetime import datetime
import matplotlib.pyplot as plt

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
    format='%(asctime)s - %(levelname)s - %(message)s'
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
        else:
            print(f"❌ ERRO: {resultado['erro']}")
    
    def executar_desafio2(self):
        """Executa o Desafio 2"""
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 2 - VERIFICAÇÃO CRÍTICA")
        print("="*60)
        print("⚠️  Implementação pendente")
        # resultado = executar_desafio2(HABILIDADES, HABILIDADES_CRITICAS)
        # self.resultados['desafio2'] = resultado
    
    def executar_desafio3(self):
        """Executa o Desafio 3"""
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 3 - PIVÔ MAIS RÁPIDO")
        print("="*60)
        print("⚠️  Implementação pendente")
        # resultado = executar_desafio3(HABILIDADES)
        # self.resultados['desafio3'] = resultado
    
    def executar_desafio4(self):
        """Executa o Desafio 4"""
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 4 - TRILHAS PARALELAS")
        print("="*60)
        print("⚠️  Implementação pendente")
        # resultado = executar_desafio4(HABILIDADES)
        # self.resultados['desafio4'] = resultado
    
    def executar_desafio5(self):
        """Executa o Desafio 5"""
        print("\n" + "="*60)
        print("🎯 EXECUTANDO DESAFIO 5 - RECOMENDAR HABILIDADES")
        print("="*60)
        print("⚠️  Implementação pendente")
        # resultado = executar_desafio5(HABILIDADES, CENARIOS_MERCADO)
        # self.resultados['desafio5'] = resultado
    
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
        self.executar_desafio2() 
        self.executar_desafio3()
        self.executar_desafio4()
        self.executar_desafio5()
        
        # 3. Relatório final
        self.gerar_relatorio_final()
    
    def gerar_relatorio_final(self):
        """Gera relatório consolidado"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL - MOH")
        print("="*70)
        
        desafios_executados = [k for k in self.resultados.keys()]
        print(f"✅ Desafios executados com sucesso: {len(desafios_executados)}/5")
        
        for desafio in desafios_executados:
            print(f"   - {desafio.upper()}")
        
        if not desafios_executados:
            print("❌ Nenhum desafio foi executado com sucesso")
        else:
            print(f"\n🎉 Execução concluída em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

def main():
    """Função principal"""
    try:
        orchestrator = OrchestradorMOH()
        orchestrator.executar_todos_desafios()
    except Exception as e:
        logging.error(f"Erro na execução: {e}")
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    main()