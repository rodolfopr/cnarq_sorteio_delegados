import pandas as pd
import random

# -----------------------------
# CONFIGURAÇÕES
# -----------------------------
TOTAL_PARTICIPANTES = 480
PERCENTUAL_STRESS = 0.7

# Dentro do grupo stress:
PESO_SUDESTE_STRESS = 0.5
PESO_PODER_PUBLICO_STRESS = 0.8

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

# Distribuição geral (fora do stress)
PESO_REGIAO_NORMAL = {
    'Norte': 0.08,
    'Nordeste': 0.27,
    'Centro-Oeste': 0.10,
    'Sudeste': 0.42,
    'Sul': 0.13
}

# -----------------------------
# FUNÇÕES AUXILIARES
# -----------------------------
nomes = [
    "Ana Silva", "Carlos Souza", "Mariana Oliveira", "João Santos",
    "Fernanda Lima", "Ricardo Pereira", "Juliana Costa", "Bruno Rocha",
    "Patrícia Alves", "Lucas Ribeiro", "Camila Martins", "Eduardo Gomes"
]

def gerar_nome():
    return random.choice(nomes) + f" {random.randint(1,9999)}"

def sortear_regiao(pesos):
    r = random.random()
    acumulado = 0
    for regiao, peso in pesos.items():
        acumulado += peso
        if r <= acumulado:
            return regiao
    return 'Sudeste'

def gerar_uf(regiao):
    return random.choice(REGIOES[regiao])

def gerar_segmento_stress():
    return 'Poder Público' if random.random() <= PESO_PODER_PUBLICO_STRESS else 'Sociedade Civil'

def gerar_segmento_normal():
    return random.choice(SEGMENTOS)

def gerar_prioridades_stress():
    prioridades = {'GT1': 1}
    
    restantes = [2,3,4,5,6]
    outros = ['GT2','GT3','GT4','GT5','GT6']
    random.shuffle(restantes)
    
    for gt, prio in zip(outros, restantes):
        prioridades[gt] = prio
    
    return prioridades

def gerar_prioridades_normal():
    prios = list(range(1,7))
    random.shuffle(prios)
    return dict(zip(gts, prios))

# -----------------------------
# GERAÇÃO DOS DADOS
# -----------------------------
dados = []

for i in range(TOTAL_PARTICIPANTES):
    
    if random.random() <= PERCENTUAL_STRESS:
        # GRUPO STRESS
        # 50% Sudeste dentro do stress
        if random.random() <= PESO_SUDESTE_STRESS:
            regiao = 'Sudeste'
        else:
            outras = ['Norte','Nordeste','Centro-Oeste','Sul']
            regiao = random.choice(outras)
        
        segmento = gerar_segmento_stress()
        prioridades = gerar_prioridades_stress()
    
    else:
        # GRUPO NORMAL
        regiao = sortear_regiao(PESO_REGIAO_NORMAL)
        segmento = gerar_segmento_normal()
        prioridades = gerar_prioridades_normal()
    
    uf = gerar_uf(regiao)
    
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
arquivo = "base_stress_extremo.csv"
df.to_csv(arquivo, index=False, encoding='utf-8-sig')

# -----------------------------
# DIAGNÓSTICO
# -----------------------------
total_gt1 = sum(df['GT1'] == 1)
total_sudeste = sum(df['Região'] == 'Sudeste')
total_pp = sum(df['Macrossegmento'] == 'Poder Público')

print(f"\nArquivo gerado: {arquivo}")
print(f"GT1 como 1ª opção: {total_gt1} ({(total_gt1/TOTAL_PARTICIPANTES)*100:.2f}%)")
print(f"Sudeste total: {total_sudeste} ({(total_sudeste/TOTAL_PARTICIPANTES)*100:.2f}%)")
print(f"Poder Público total: {total_pp} ({(total_pp/TOTAL_PARTICIPANTES)*100:.2f}%)")

print("\nAmostra:")
print(df.head())
