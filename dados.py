# === DADOS MESTRE DO MOH ===
HABILIDADES = {
    'S1': {'Nome': 'Programação Básica (Python)', 'Tempo': 80, 'Valor': 3, 'Complexidade': 4, 'Pre_Reqs': [], 'Demanda': 0.9},
    'S2': {'Nome': 'Modelagem de Dados (SQL)', 'Tempo': 60, 'Valor': 4, 'Complexidade': 3, 'Pre_Reqs': [], 'Demanda': 0.8},
    'S3': {'Nome': 'Algoritmos Avançados', 'Tempo': 100, 'Valor': 7, 'Complexidade': 8, 'Pre_Reqs': ['S1'], 'Demanda': 0.7},
    'S4': {'Nome': 'Fundamentos de ML', 'Tempo': 120, 'Valor': 8, 'Complexidade': 9, 'Pre_Reqs': ['S1', 'S3'], 'Demanda': 0.85},
    'S5': {'Nome': 'Visualização de Dados (BI)', 'Tempo': 40, 'Valor': 6, 'Complexidade': 5, 'Pre_Reqs': ['S2'], 'Demanda': 0.75},
    'S6': {'Nome': 'IA Generativa Ética', 'Tempo': 150, 'Valor': 10, 'Complexidade': 10, 'Pre_Reqs': ['S4'], 'Demanda': 0.95},
    'S7': {'Nome': 'Estruturas em Nuvem', 'Tempo': 70, 'Valor': 5, 'Complexidade': 7, 'Pre_Reqs': [], 'Demanda': 0.8},
    'S8': {'Nome': 'APIs e Microsserviços', 'Tempo': 90, 'Valor': 6, 'Complexidade': 6, 'Pre_Reqs': ['S1'], 'Demanda': 0.7},
    'S9': {'Nome': 'DevOps & CI/CD', 'Tempo': 110, 'Valor': 9, 'Complexidade': 8, 'Pre_Reqs': ['S7', 'S8'], 'Demanda': 0.85},
    'H10': {'Nome': 'Segurança de Dados', 'Tempo': 60, 'Valor': 5, 'Complexidade': 6, 'Pre_Reqs': [], 'Demanda': 0.9},
    'H11': {'Nome': 'Análise de Big Data', 'Tempo': 90, 'Valor': 8, 'Complexidade': 8, 'Pre_Reqs': ['S4'], 'Demanda': 0.75},
    'H12': {'Nome': 'Introdução a IoT', 'Tempo': 30, 'Valor': 3, 'Complexidade': 3, 'Pre_Reqs': [], 'Demanda': 0.6}
}

HABILIDADES_CRITICAS = ['S3', 'S5', 'S7', 'S8', 'S9']

CENARIOS_MERCADO = {
    'IA_Dominante': {
        'probabilidade': 0.4,
        'bonus_habilidades': ['S4', 'S6', 'H11'],
        'penalidade_habilidades': ['S2', 'S5'],
        'fator_bonus': 1.3,
        'descricao': 'Crescimento acelerado em IA e Machine Learning'
    },
    'Cloud_Predominante': {
        'probabilidade': 0.35,
        'bonus_habilidades': ['S7', 'S9', 'H10'],
        'penalidade_habilidades': ['S1', 'S3'],
        'fator_bonus': 1.25,
        'descricao': 'Expansão massiva de computação em nuvem'
    },
    'FullStack_Equilibrado': {
        'probabilidade': 0.25,
        'bonus_habilidades': ['S1', 'S8', 'S5'],
        'penalidade_habilidades': [],
        'fator_bonus': 1.15,
        'descricao': 'Demanda equilibrada por habilidades full-stack'
    }
}