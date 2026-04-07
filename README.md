# 🗂️ Sorteio 2ª CNArq - Alocação de Delegados por Prioridade

[![Licença](https://img.shields.io/badge/licença-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-production-brightgreen.svg)]()

Algoritmo oficial de sorteio para alocação de delegados nos Grupos de Trabalho (GTs) da **2ª Conferência Nacional de Arquivos (CNArq)**.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Metodologia](#metodologia)
- [Regras de Alocação](#regras-de-alocação)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Formato dos Dados](#formato-dos-dados)
- [Algoritmo em Detalhe](#algoritmo-em-detalhe)
- [Saídas Geradas](#saídas-geradas)
- [Auditoria e Transparência](#auditoria-e-transparência)
- [FAQ](#faq)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🎯 Sobre o Projeto

Este projeto implementa o algoritmo oficial de sorteio da 2ª Conferência Nacional de Arquivos, garantindo:

- ✅ **Isonomia** entre todos os participantes
- ✅ **Representatividade** regional e setorial
- ✅ **Respeito às preferências** individuais
- ✅ **Transparência** total do processo
- ✅ **Reprodutibilidade** dos resultados

## 📐 Metodologia

O algoritmo utiliza um processo de **alocação por prioridade em três fases**:

### Fase 1: Alocação de Cotas
Garante os mínimos obrigatórios em cada GT antes de qualquer outra alocação.

### Fase 2: Ampla Concorrência
Preenche as vagas restantes respeitando a ordem de prioridade dos participantes.

### Fase 3: Fallback
Aloca participantes remanescentes em qualquer GT com vaga disponível.

## ⚖️ Regras de Alocação

### Parâmetros Gerais

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| GTs | 6 | Grupos de Trabalho (GT1 a GT6) |
| Vagas por GT | 80 | Limite máximo de participantes |
| Total de vagas | 480 | Capacidade total do evento |

### Cotas Mínimas por GT

| Tipo | Mínimo | Descrição |
|------|--------|-----------|
| **Segmento** | 20 | "Poder Público" ou "Sociedade Civil" |
| **Região** | 2 | Norte, Nordeste, Centro-Oeste, Sudeste, Sul |

### Critérios de Desempate

1. **Pontuação de cota** (Fase 1): Atende mais cotas primeiro
2. **Sorteio aleatório**: Embaralhamento com seed fixa (42)

## 💻 Pré-requisitos

- Python 3.8 ou superior
- Pandas (biblioteca para manipulação de dados)
- Arquivo CSV com a base de delegados

## 🔧 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sorteio-2a-cnarq.git

# Entre no diretório
cd sorteio-2a-cnarq

# Instale as dependências
pip install pandas
