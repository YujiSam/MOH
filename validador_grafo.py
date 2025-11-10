import logging
from collections import deque

class ValidadorGrafo:
    def __init__(self, grafo):
        self.grafo = grafo
        self.ciclos_encontrados = []
        self.nos_orfaos = []
        self.pre_requisitos_inexistentes = []
    
    def detectar_ciclos_dfs(self):
        """Detecta ciclos no grafo usando DFS"""
        visitados = set()
        no_caminho = set()
        ciclos = []
        
        def dfs(no, caminho_atual):
            if no in no_caminho:
                inicio_ciclo = caminho_atual.index(no)
                ciclo = caminho_atual[inicio_ciclo:]
                ciclo.append(no)
                ciclos.append(ciclo)
                return True
            
            if no in visitados:
                return False
            
            visitados.add(no)
            no_caminho.add(no)
            caminho_atual.append(no)
            
            for prereq in self.grafo.get(no, {}).get('Pre_Reqs', []):
                if prereq in self.grafo:
                    dfs(prereq, caminho_atual.copy())
            
            no_caminho.remove(no)
            caminho_atual.pop()
            return False
        
        for no in self.grafo:
            if no not in visitados:
                dfs(no, [])
        
        self.ciclos_encontrados = ciclos
        return ciclos
    
    def verificar_pre_requisitos_inexistentes(self):
        """Verifica pré-requisitos que não são nós do grafo"""
        pre_requisitos_inexistentes = []
        
        for no, dados in self.grafo.items():
            for prereq in dados.get('Pre_Reqs', []):
                if prereq not in self.grafo:
                    pre_requisitos_inexistentes.append((no, prereq))
        
        self.pre_requisitos_inexistentes = pre_requisitos_inexistentes
        return pre_requisitos_inexistentes
    
    def verificar_nos_orfaos(self):
        """Verifica nós inalcançáveis"""
        raizes = [no for no, dados in self.grafo.items() if not dados.get('Pre_Reqs', [])]
        
        visitados = set()
        fila = deque(raizes)
        
        while fila:
            no_atual = fila.popleft()
            if no_atual in visitados:
                continue
            visitados.add(no_atual)
            
            for no, dados in self.grafo.items():
                if no_atual in dados.get('Pre_Reqs', []) and no not in visitados:
                    fila.append(no)
        
        nos_orfaos = [no for no in self.grafo if no not in visitados]
        self.nos_orfaos = nos_orfaos
        return nos_orfaos
    
    def validar_grafo_completo(self):
        """Executa todas as validações"""
        logging.info("Iniciando validação completa do grafo...")
        
        ciclos = self.detectar_ciclos_dfs()
        pre_requisitos_inexistentes = self.verificar_pre_requisitos_inexistentes()
        nos_orfaos = self.verificar_nos_orfaos()
        
        valido = not (ciclos or pre_requisitos_inexistentes)
        
        relatorio = {
            'valido': valido,
            'ciclos': ciclos,
            'pre_requisitos_inexistentes': pre_requisitos_inexistentes,
            'nos_orfaos': nos_orfaos
        }
        
        if not valido:
            logging.error("Grafo inválido detectado")
        else:
            logging.info("Grafo validado com sucesso")
        
        return relatorio