import pandas as pd
import random

# -----------------------------
# CONFIGURAÇÕES
# -----------------------------
TOTAL_PARTICIPANTES = 480
random.seed(42)

gts = [f'GT{i}' for i in range(1, 7)]

REGIOES = {
    'Norte': ['AC','AP','AM','PA','RO','RR','TO'],
    'Nordeste': ['AL','BA','CE','MA','PB','PE','PI','RN','SE'],
    'Centro-Oeste': ['DF','GO','MT','MS'],
    'Sudeste': ['SP','RJ','MG','ES'],
    'Sul': ['PR','RS','SC']
}

SEGMENTOS = ['Poder Público', 'Sociedade Civil']

# Distribuição realista (peso populacional aproximado)
PESO_REGIAO = {
    'Norte': 0.08,
    'Nordeste': 0.27,
    'Centro-Oeste': 0.10,
    'Sudeste': 0.42,
    'Sul': 0.13
}

# -----------------------------
# GERADORES AUXILIARES
# -----------------------------
nomes = [
    "Ana Silva", "Carlos Souza", "Mariana Oliveira", "João Santos",
    "Fernanda Lima", "Ricardo Pereira", "Juliana Costa", "Bruno Rocha",
    "Patrícia Alves", "Lucas Ribeiro", "Camila Martins", "Eduardo Gomes"
]

def gerar_nome():
    return random.choice(nomes) + f" {random.randint(1,9999)}"

def gerar_regiao():
    r = random.random()
    acumulado = 0
    for regiao, peso in PESO_REGIAO.items():
        acumulado += peso
        if r <= acumulado:
            return regiao
    return 'Sudeste'

def gerar_uf(regiao):
    return random.choice(REGIOES[regiao])

def gerar_segmento():
    return random.choice(SEGMENTOS)

def gerar_prioridades():
    prioridades = list(range(1,7))
    random.shuffle(prioridades)
    return dict(zip(gts, prioridades))

# -----------------------------
# GERAÇÃO DOS DADOS
# -----------------------------
dados = []

for i in range(TOTAL_PARTICIPANTES):
    regiao = gerar_regiao()
    uf = gerar_uf(regiao)
    segmento = gerar_segmento()
    prioridades = gerar_prioridades()
    
    registro = {
        'ID': i + 1,
        'Nome': gerar_nome(),
        'UF': uf,
        'Região': regiao,
        'Macrossegmento': segmento
    }
    
    registro.update(prioridades)
    dados.append(registro)

df = pd.DataFrame(dados)

# -----------------------------
# EXPORTAÇÃO
# -----------------------------
arquivo = "base_delegados_teste.csv"
df.to_csv(arquivo, index=False, encoding='utf-8-sig')

print(f"Arquivo gerado com sucesso: {arquivo}")
print(df.head())
