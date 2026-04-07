import pandas as pd
import random

# -----------------------------
# CONFIGURAÇÕES
# -----------------------------
TOTAL_PARTICIPANTES = 480
PERCENTUAL_STRESS = 0.7  # 70% querem GT1 como primeira opção
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

def gerar_prioridades_stress():
    prioridades = {}

    if random.random() <= PERCENTUAL_STRESS:
        # Força GT1 como prioridade 1
        prioridades['GT1'] = 1
        
        restantes = [2,3,4,5,6]
        outros_gts = ['GT2','GT3','GT4','GT5','GT6']
        random.shuffle(restantes)
        
        for gt, prio in zip(outros_gts, restantes):
            prioridades[gt] = prio
    else:
        # Distribuição normal
        prios = list(range(1,7))
        random.shuffle(prios)
        prioridades = dict(zip(gts, prios))
    
    return prioridades

# -----------------------------
# GERAÇÃO DOS DADOS
# -----------------------------
dados = []

for i in range(TOTAL_PARTICIPANTES):
    regiao = gerar_regiao()
    uf = gerar_uf(regiao)
    segmento = gerar_segmento()
    prioridades = gerar_prioridades_stress()
    
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
arquivo = "base_stress_gt1_70.csv"
df.to_csv(arquivo, index=False, encoding='utf-8-sig')

# -----------------------------
# VERIFICAÇÃO DO STRESS
# -----------------------------
qtde_gt1_prioridade1 = sum(df['GT1'] == 1)
percentual_real = qtde_gt1_prioridade1 / TOTAL_PARTICIPANTES * 100

print(f"Arquivo gerado: {arquivo}")
print(f"Participantes que escolheram GT1 como 1ª opção: {qtde_gt1_prioridade1} ({percentual_real:.2f}%)")
print(df.head())
