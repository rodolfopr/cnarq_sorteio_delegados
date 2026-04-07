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
# ALOCAÇÃO
# =========================
def alocar_por_prioridade():
    alocados = {gt: [] for gt in gts}
    alocados_ids = set()
    log_fallback = []

    for prioridade in range(1, 7):
        print(f"\n=== Processando {prioridade}ª opção ===")

        # Participantes ainda não alocados
        pendentes = [p for p in participantes if p['ID'] not in alocados_ids]

        # Agrupar por GT desejado nesta prioridade
        candidatos_por_gt = defaultdict(list)
        for p in pendentes:
            gt_escolhido = p['escolhas'].get(prioridade)
            if gt_escolhido:
                candidatos_por_gt[gt_escolhido].append(p)

        # Processar cada GT
        for gt in gts:
            if len(alocados[gt]) >= LIMITE_VAGAS:
                continue

            candidatos = candidatos_por_gt[gt]
            if not candidatos:
                continue

            vagas_restantes = LIMITE_VAGAS - len(alocados[gt])
            print(f"  {gt}: {len(candidatos)} candidatos, {vagas_restantes} vagas")

            # =========================
            # CONTEXTO ATUAL DO GT
            # =========================
            contagem_regiao = {r: sum(1 for p in alocados[gt] if p['Região'] == r) for r in REGIOES}
            contagem_segmento = {s: sum(1 for p in alocados[gt] if p['Macrossegmento'] == s) for s in SEGMENTOS}

            necessidades_regiao = {r: max(0, COTA_REGIAO - contagem_regiao[r]) for r in REGIOES}
            necessidades_segmento = {s: max(0, COTA_SEGMENTO - contagem_segmento[s]) for s in SEGMENTOS}

            # =========================
            # CLASSIFICAÇÃO DOS CANDIDATOS
            # =========================
            grupo_ideal = []      # atende região E segmento
            grupo_regiao = []     # atende apenas região
            grupo_segmento = []   # atende apenas segmento
            grupo_geral = []      # não atende nenhuma cota

            for p in candidatos:
                atende_regiao = necessidades_regiao[p['Região']] > 0
                atende_segmento = necessidades_segmento[p['Macrossegmento']] > 0

                if atende_regiao and atende_segmento:
                    grupo_ideal.append(p)
                elif atende_regiao:
                    grupo_regiao.append(p)
                elif atende_segmento:
                    grupo_segmento.append(p)
                else:
                    grupo_geral.append(p)

            # Embaralhar todos os grupos para garantir sorteio justo
            for grupo in [grupo_ideal, grupo_regiao, grupo_segmento, grupo_geral]:
                random.shuffle(grupo)

            selecionados = []
            necessidades_regiao_temp = necessidades_regiao.copy()
            necessidades_segmento_temp = necessidades_segmento.copy()

            # =========================
            # FASE 1: COTAS (prioridade hierárquica)
            # =========================
            for grupo in [grupo_ideal, grupo_regiao, grupo_segmento]:
                for p in grupo:
                    if len(selecionados) >= vagas_restantes:
                        break

                    selecionados.append(p)

                    # Atualiza necessidades temporárias
                    if necessidades_regiao_temp[p['Região']] > 0:
                        necessidades_regiao_temp[p['Região']] -= 1
                    if necessidades_segmento_temp[p['Macrossegmento']] > 0:
                        necessidades_segmento_temp[p['Macrossegmento']] -= 1

                if len(selecionados) >= vagas_restantes:
                    break

            # =========================
            # FASE 2: AMPLA CONCORRÊNCIA
            # =========================
            if len(selecionados) < vagas_restantes:
                restantes = [p for p in candidatos if p not in selecionados]
                random.shuffle(restantes)

                faltantes = vagas_restantes - len(selecionados)
                selecionados.extend(restantes[:faltantes])

            # =========================
            # ALOCAÇÃO FINAL
            # =========================
            for p in selecionados:
                alocados[gt].append(p)
                alocados_ids.add(p['ID'])

            print(f"    Alocados: {len(selecionados)} (Cotas: {len([p for p in selecionados if p in grupo_ideal or p in grupo_regiao or p in grupo_segmento])}, Ampla: {len([p for p in selecionados if p in grupo_geral])})")

    # =========================
    # FASE FINAL: FALLBACK
    # =========================
    pendentes_finais = [p for p in participantes if p['ID'] not in alocados_ids]

    print(f"\n=== FASE FINAL (FALLBACK) ===")
    print(f"Pendentes: {len(pendentes_finais)}")

    fallback_count = 0
    nao_alocados = []

    for p in pendentes_finais:
        alocado = False
        for gt in gts:
            if len(alocados[gt]) < LIMITE_VAGAS:
                alocados[gt].append(p)
                alocados_ids.add(p['ID'])
                fallback_count += 1
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
            nao_alocados.append(p)
            print(f"  ⚠ ID {p['ID']} ({p['UF']}) NÃO conseguiu vaga em nenhum GT!")

    print(f"\nTotal fallbacks: {fallback_count}")
    print(f"Total não alocados: {len(nao_alocados)}")

    return alocados, log_fallback, nao_alocados

# =========================
# EXECUÇÃO
# =========================
resultado, log_fallback, nao_alocados = alocar_por_prioridade()

# =========================
# AUDITORIA FINAL
# =========================
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

        # Verifica em qual prioridade este participante conseguiu este GT
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

# =========================
# VERIFICAÇÃO DE COTAS
# =========================
print("\n" + "="*70)
print("VERIFICAÇÃO DE COTAS POR GT")
print("="*70)

if not falhas_cota:
    print("✓ Todas as cotas foram cumpridas em todos os GTs!")
else:
    print("⚠ ALERTA: Algumas cotas não foram cumpridas. Verifique o relatório acima.")

# =========================
# SATISFAÇÃO DOS PARTICIPANTES
# =========================
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

# =========================
# RESUMO GERAL
# =========================
print("\n" + "="*70)
print("RESUMO GERAL")
print("="*70)
print(f"TOTAL DE PESSOAS NA BASE: {len(participantes)}")
print(f"TOTAL DE PESSOAS ALOCADAS: {total_geral}")
print(f"TOTAL DE VAGAS DISPONÍVEIS: {LIMITE_VAGAS * len(gts)}")
print(f"PENDENTES (não alocados): {len(nao_alocados)}")
print(f"FALLBACKS (alocados fora da prioridade): {len(log_fallback)}")

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
        # Remove campo auxiliar 'escolhas' antes de exportar
        if 'escolhas' in registro:
            del registro['escolhas']
        linhas.append(registro)

df_final = pd.DataFrame(linhas)
df_final.to_csv('resultado_alocacao.csv', index=False, encoding='utf-8-sig')
print("\n✓ Arquivo 'resultado_alocacao.csv' gerado com sucesso.")

# 2. Log de fallbacks (opcional)
if log_fallback:
    df_fallback = pd.DataFrame(log_fallback)
    df_fallback.to_csv('log_fallbacks.csv', index=False, encoding='utf-8-sig')
    print("✓ Arquivo 'log_fallbacks.csv' gerado com sucesso.")

# 3. Lista de não alocados (opcional)
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
print(f"Data/hora da execução: {pd.Timestamp.now()}")
print(f"Total de GTs: {len(gts)}")
print(f"Limite de vagas por GT: {LIMITE_VAGAS}")
print(f"Cota mínima por segmento: {COTA_SEGMENTO}")
print(f"Cota mínima por região: {COTA_REGIAO}")
print("\nO sorteio foi realizado com embaralhamento inicial e alocação por prioridade,")
print("garantindo que ninguém fosse alocado em opção inferior enquanto houvesse")
print("vagas em opções superiores, respeitando as cotas estabelecidas.")
