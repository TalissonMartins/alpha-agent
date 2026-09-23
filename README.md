# AlphaAgent 🚀
Plataforma B2B modular de análise fundamentalista e valuation automatizado para ativos da B3 (Bolsa de Valores do Brasil).

## 📊 Sobre o Projeto
O **AlphaAgent** é uma solução de engenharia de software desenvolvida em Python com foco em performance, arquitetura limpa (padrão MVC) e resiliência defensiva (`try/except` e tratamento avançado de nulos). O sistema automatiza a extração de dados fundamentalistas do mercado brasileiro e aplica modelos clássicos de valuation de forma estruturada.

## 🛠️ Stack Tecnológica
* **Linguagem:** Python 3.14
* **Bibliotecas Principais:** `pandas`, `numpy`, `yfinance` (extração de dados)
* **Arquitetura:** Modular orientada a serviços (`src/data/`, `src/finance/`, `src/main.py`)
* **Gestão de Versão:** Git & GitHub

## ▶️ Instalação e execução

Instale as dependências do projeto em um ambiente virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -e ".[test]"
```

Execute o orquestrador como módulo a partir da raiz do repositório:

```bash
python -m src.main
```

Para iniciar o PostgreSQL local:

```bash
docker compose up -d postgres
```

Copie `.env.example` para `.env`, defina `PERSIST_DATABASE=true` e execute
`python -m src.main` para salvar cada coleta como um snapshot histórico.
O fluxo continua funcionando sem banco quando `PERSIST_DATABASE=false`.

Para testar a integração opcional com o Gemini, defina `GEMINI_API_KEY`
no arquivo `.env` e execute:

```bash
python ai_agent.py
```

Os percentuais recebidos do `yfinance` são tratados como frações decimais
(por exemplo, `0.06` representa `6%`) e convertidos para a representação
percentual exibida nos relatórios.

## ⚠️ Limitações do MVP

- Os dados dependem do Yahoo Finance e podem estar atrasados, incompletos ou
  indisponíveis temporariamente.
- A coleta faz novas tentativas limitadas para falhas transitórias, mas não
  garante disponibilidade nem substitui uma fonte financeira licenciada.
- Graham, Gordon e DCF são modelos simplificados, com premissas fixas no
  código; não constituem recomendação de investimento.
- O DCF só é calculado quando a fonte fornece fluxo de caixa livre e ações em
  circulação. Ele não ajusta dívida, caixa ou opções.
- O resultado deve ser revisado por um analista antes de qualquer decisão
  financeira ou uso institucional.

## 🗄️ Persistência

O Marco 2.5 usa SQLAlchemy 2.x com PostgreSQL. A tabela `assets` mantém o
cadastro dos ativos e `asset_snapshots` guarda os dados coletados e os
resultados de valuation com timestamp, permitindo histórico sem sobrescrever
coletas anteriores.

## 📈 Funcionalidades do Motor Financeiro (Fase 2)
O motor de cálculo (`engine.py`) processa os dados brutos e gera indicadores institucionais avançados:
* **Preço Justo de Graham:** Cálculo do valor intrínseco baseado no Lucro por Ação (LPA) e Valor Patrimonial por Ação (VPA).
* **Margem de Segurança (%):** Avaliação quantitativa do potencial de valorização ou descolamento de preço em relação ao teto de Graham e Gordon.
* **Modelo de Gordon (Versão Simplificada):** Projeção de valuation orientada ao rendimento de dividendos.
* **Earnings Yield (%):** Retorno de lucros para análise comparativa de rentabilidade.
* **DCF (Versão Simplificada):** Valor presente de cinco anos de fluxo de caixa livre projetado e valor terminal, por ação.

## 📂 Estrutura do Repositório
```text
AlphaAgent/
│
├── docs/                # Documentação oficial e Plano Mestre
├── src/
│   ├── data/            # Módulo de extração e consumo de dados da B3
│   ├── db/              # Modelos SQLAlchemy e persistência histórica
│   ├── finance/         # Motor de cálculo, valuation e indicadores
│   ├── config.py        # Configuração por variáveis de ambiente
│   └── main.py          # Orquestrador central (Maestro) da pipeline
│
├── .env                 # Variáveis de ambiente
├── .gitignore           # Exclusões de controlo de versão
└── README.md            # Documentação do projeto
