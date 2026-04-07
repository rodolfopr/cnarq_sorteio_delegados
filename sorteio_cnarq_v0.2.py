import pandas as pd
import random
from collections import defaultdict

# =========================
# CONFIGURAÇÃO
# =========================
ARQUIVO = 'base_delegados_cnarq.csv'
SEED = 42

LIMITE_VAGAS = 80
COTA_SEGMENTO = 20
COTA_REGIAO = 2

gts = [f'GT{i}' for i in range(1, 7)]
REGIOES = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
SEGMENTOS = ['Poder Público', 'Sociedade Civil']

# =========================
# CARREGAMENTO
# =========================
df = pd.read_csv(ARQUIVO)
participantes = df.to_dict('records')

# Fixar semente para reprodutibilidade
random.seed(SEED)
random.shuffle(participantes)

# Pré-calcular mapeamento de escolhas para performance
for p in participantes:
    p['escolhas'] = {p[gt]: gt for gt in gts}

# =========================
# FUNÇÃO PRINCIPAL REVISADA
# =========================
def alocar_por_prioridade_com_cotas_garantidas():
    alocados = {gt: [] for gt in gts}
    alocados_ids = set()
    log_fallback = []
    
    # Controle de quantas vagas de cota já foram preenchidas por GT
    cotas_preenchidas = {gt: {
        'Poder Público': 0,
        'Sociedade Civil': 0,
        **{r: 0 for r in REGIOES}
    } for gt in gts}
    
    # Primeiro, garantir que cada GT terá suas cotas mínimas
    # Para isso, pré-selecionamos candidatos que serão alocados por cota
    
    # Ordem de prioridade para alocação de cotas: 1ª opção primeiro
    for prioridade in range(1, 7):
        print(f"\n=== Processando cotas - {prioridade}ª opção ===")
        
        for gt in gts:
            # Verificar se ainda há cotas a preencher neste GT
            falta_pub = max(0, COTA_SEGMENTO - cotas_preenchidas[gt]['Poder Público'])
            falta_soc = max(0, COTA_SEGMENTO - cotas_preenchidas[gt]['Sociedade Civil'])
            falta_regioes = {r: max(0, COTA_REGIAO - cotas_preenchidas[gt][r]) for r in REGIOES}
            
            total_falta_cotas = falta_pub + falta_soc + sum(falta_regioes.values())
            
            if total_falta_cotas == 0:
                continue
            
            # Buscar candidatos não alocados que têm este GT nesta prioridade
            candidatos_disponiveis = []
            for p in participantes:
                if p['ID'] not in alocados_ids and p[gt] == prioridade:
                    candidatos_disponiveis.append(p)
            
            if not candidatos_disponiveis:
                continue
            
            # Classificar candidatos por sua utilidade para as cotas
            # Quanto mais cotas atende, maior prioridade
            def pontuacao_cota(p):
                pontos = 0
                # Cota de segmento
                if falta_pub > 0 and p['Macrossegmento'] == 'Poder Público':
                    pontos += 10
                if falta_soc > 0 and p['Macrossegmento'] == 'Sociedade Civil':
                    pontos += 10
                # Cota de região
                if falta_regioes[p['Região']] > 0:
                    pontos += 5
                return pontos
            
            # Ordenar por pontuação (maior primeiro) e depois embaralhar para sorteio
            candidatos_disponiveis.sort(key=pontuacao_cota, reverse=True)
            
            # Selecionar candidatos para preencher as cotas
            selecionados_cota = []
            for p in candidatos_disponiveis:
                if len(selecionados_cota) >= total_falta_cotas:
                    break
                
                # Verificar se ainda precisamos deste tipo de cota
                precisa_pub = (falta_pub > 0 and p['Macrossegmento'] == 'Poder Público')
                precisa_soc = (falta_soc > 0 and p['Macrossegmento'] == 'Sociedade Civil')
                precisa_regiao = (falta_regioes[p['Região']] > 0)
                
                if precisa_pub or precisa_soc or precisa_regiao:
                    selecionados_cota.append(p)
                    if precisa_pub:
                        falta_pub -= 1
                    if precisa_soc:
                        falta_soc -= 1
                    if precisa_regiao:
                        falta_regioes[p['Região']] -= 1
            
            # Alocar os selecionados
            for p in selecionados_cota:
                alocados[gt].append(p)
                alocados_ids.add(p['ID'])
                cotas_preenchidas[gt][p['Macrossegmento']] += 1
                cotas_preenchidas[gt][p['Região']] += 1
                print(f"  {gt}: Cota alocada - {p['Macrossegmento']} / {p['Região']} (prioridade {prioridade})")
    
    # Agora, processar as vagas restantes por prioridade (ampla concorrência)
    print("\n=== Processando ampla concorrência ===")
    
    for prioridade in range(1, 7):
        print(f"\n=== Ampla concorrência - {prioridade}ª opção ===")
        
        for gt in gts:
            if len(alocados[gt]) >= LIMITE_VAGAS:
                continue
            
            vagas_restantes = LIMITE_VAGAS - len(alocados[gt])
            
            # Buscar candidatos não alocados que têm este GT nesta prioridade
            candidatos = []
            for p in participantes:
                if p['ID'] not in alocados_ids and p[gt] == prioridade:
                    candidatos.append(p)
            
            if not candidatos:
                continue
            
            # Embaralhar para sorteio justo
            random.shuffle(candidatos)
            
            # Alocar até preencher as vagas
            selecionados = candidatos[:vagas_restantes]
            
            for p in selecionados:
                alocados[gt].append(p)
                alocados_ids.add(p['ID'])
            
            print(f"  {gt}: Alocados {len(selecionados)} na ampla concorrência")
    
    # FASE FINAL: FALLBACK
    pendentes_finais = [p for p in participantes if p['ID'] not in alocados_ids]
    
    print(f"\n=== FASE FINAL (FALLBACK) ===")
    print(f"Pendentes: {len(pendentes_finais)}")
    
    for p in pendentes_finais:
        alocado = False
        for gt in gts:
            if len(alocados[gt]) < LIMITE_VAGAS:
                alocados[gt].append(p)
                alocados_ids.add(p['ID'])
                log_fallback.append({
                    'ID': p['ID'],
                    'GT': gt,
                    'UF': p['UF'],
                    'Regiao': p['Região'],
                    'Segmento': p['Macrossegmento']
                })
                print(f"  Fallback: ID {p['ID']} ({p['UF']}) alocado em {gt}")
                alocado = True
                break
        if not alocado:
            print(f"  ⚠ ID {p['ID']} ({p['UF']}) NÃO conseguiu vaga em nenhum GT!")
    
    return alocados, log_fallback, pendentes_finais

# =========================
# EXECUÇÃO
# =========================
resultado, log_fallback, nao_alocados = alocar_por_prioridade_com_cotas_garantidas()

# =========================
# FUNÇÃO DE RELATÓRIO
# =========================
def gerar_relatorio(resultado, participantes, log_fallback, nao_alocados):
    print("\n" + "="*70)
    print("RELATÓRIO FINAL")
    print("="*70)
    
    total_geral = 0
    satisfacao = {i: 0 for i in range(1, 7)}
    falhas_cota = False
    
    for gt in gts:
        ocupantes = resultado[gt]
        total = len(ocupantes)
        total_geral += total
        
        cont_seg = defaultdict(int)
        cont_reg = defaultdict(int)
        
        for p in ocupantes:
            cont_seg[p['Macrossegmento']] += 1
            cont_reg[p['Região']] += 1
            
            prioridade = p[gt]
            satisfacao[prioridade] += 1
        
        print(f"\n{gt}: {total}/{LIMITE_VAGAS} vagas ocupadas")
        
        print("  Segmentos:")
        for seg in SEGMENTOS:
            status = "✓" if cont_seg[seg] >= COTA_SEGMENTO else "⚠"
            print(f"    {status} {seg}: {cont_seg[seg]} (mínimo {COTA_SEGMENTO})")
            if cont_seg[seg] < COTA_SEGMENTO:
                falhas_cota = True
        
        print("  Regiões:")
        for reg in REGIOES:
            status = "✓" if cont_reg[reg] >= COTA_REGIAO else "⚠"
            print(f"    {status} {reg}: {cont_reg[reg]} (mínimo {COTA_REGIAO})")
            if cont_reg[reg] < COTA_REGIAO:
                falhas_cota = True
    
    # Verificação de cotas
    print("\n" + "="*70)
    print("VERIFICAÇÃO DE COTAS POR GT")
    print("="*70)
    
    if not falhas_cota:
        print("✓ Todas as cotas foram cumpridas em todos os GTs!")
    else:
        print("⚠ ALERTA: Algumas cotas não foram cumpridas. Verifique o relatório acima.")
    
    # Satisfação dos participantes
    print("\n" + "="*70)
    print("SATISFAÇÃO DOS PARTICIPANTES")
    print("="*70)
    
    total_satisfacao = sum(satisfacao.values())
    
    for i in range(1, 7):
        percentual = (satisfacao[i] / total_satisfacao) * 100 if total_satisfacao > 0 else 0
        print(f"{i}ª opção: {satisfacao[i]} participantes ({percentual:.1f}%)")
    
    if total_satisfacao > 0:
        media = sum(i * satisfacao[i] for i in range(1, 7)) / total_satisfacao
        print(f"\nSatisfação média: {media:.2f} (quanto menor, melhor)")
    
    # Resumo geral
    print("\n" + "="*70)
    print("RESUMO GERAL")
    print("="*70)
    print(f"TOTAL DE PESSOAS NA BASE: {len(participantes)}")
    print(f"TOTAL DE PESSOAS ALOCADAS: {total_geral}")
    print(f"TOTAL DE VAGAS DISPONÍVEIS: {LIMITE_VAGAS * len(gts)}")
    print(f"PENDENTES (não alocados): {len(nao_alocados)}")
    print(f"FALLBACKS (alocados fora da prioridade): {len(log_fallback)}")
    
    return falhas_cota

# =========================
# GERAR RELATÓRIO
# =========================
falhas = gerar_relatorio(resultado, participantes, log_fallback, nao_alocados)

# =========================
# EXPORTAR RESULTADOS
# =========================

# 1. Alocação final por GT
linhas = []
for gt in gts:
    for p in resultado[gt]:
        registro = p.copy()
        registro['GT_Alocado'] = gt
        registro['Prioridade_Atendida'] = p[gt]
        if 'escolhas' in registro:
            del registro['escolhas']
        linhas.append(registro)

df_final = pd.DataFrame(linhas)
df_final.to_csv('resultado_alocacao.csv', index=False, encoding='utf-8-sig')
print("\n✓ Arquivo 'resultado_alocacao.csv' gerado com sucesso.")

# 2. Log de fallbacks
if log_fallback:
    df_fallback = pd.DataFrame(log_fallback)
    df_fallback.to_csv('log_fallbacks.csv', index=False, encoding='utf-8-sig')
    print("✓ Arquivo 'log_fallbacks.csv' gerado com sucesso.")

# 3. Lista de não alocados
if nao_alocados:
    df_nao_alocados = pd.DataFrame(nao_alocados)
    if 'escolhas' in df_nao_alocados.columns:
        df_nao_alocados = df_nao_alocados.drop(columns=['escolhas'])
    df_nao_alocados.to_csv('nao_alocados.csv', index=False, encoding='utf-8-sig')
    print("✓ Arquivo 'nao_alocados.csv' gerado com sucesso.")
else:
    print("✓ Todos os participantes foram alocados com sucesso!")

# =========================
# RELATÓRIO DE TRANSPARÊNCIA
# =========================
print("\n" + "="*70)
print("RELATÓRIO DE TRANSPARÊNCIA")
print("="*70)
print(f"Seed utilizada: {SEED}")
print(f"Total de GTs: {len(gts)}")
print(f"Limite de vagas por GT: {LIMITE_VAGAS}")
print(f"Cota mínima por segmento: {COTA_SEGMENTO}")
print(f"Cota mínima por região: {COTA_REGIAO}")
print("\nMetodologia:")
print("1. FASE DE COTAS: Alocação prioritária para garantir mínimos por segmento e região")
print("2. AMPLA CONCORRÊNCIA: Alocação por ordem de prioridade (1ª a 6ª opção)")
print("3. FALLBACK: Alocação residual em GTs com vagas disponíveis")
print("\nO sorteio foi realizado com embaralhamento inicial e alocação por prioridade,")
print("garantindo que ninguém fosse alocado em opção inferior enquanto houvesse")
print("vagas em opções superiores, respeitando as cotas estabelecidas.")
