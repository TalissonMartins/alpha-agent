# AlphaAgent 🚀
Plataforma B2B modular de análise fundamentalista e valuation automatizado para ativos da B3 (Bolsa de Valores do Brasil).

## 📊 Sobre o Projeto
O **AlphaAgent** é uma solução de engenharia de software desenvolvida em Python com foco em performance, arquitetura limpa (padrão MVC) e resiliência defensiva (`try/except` e tratamento avançado de nulos). O sistema automatiza a extração de dados fundamentalistas do mercado brasileiro e aplica modelos clássicos de valuation de forma estruturada.

## 🛠️ Stack Tecnológica
* **Linguagem:** Python 3.14
* **Bibliotecas Principais:** `pandas`, `numpy`, `yfinance` (extração de dados)
* **Arquitetura:** Modular orientada a serviços (`src/data/`, `src/finance/`, `src/main.py`)
* **Gestão de Versão:** Git & GitHub

## 📈 Funcionalidades do Motor Financeiro (Fase 2)
O motor de cálculo (`engine.py`) processa os dados brutos e gera indicadores institucionais avançados:
* **Preço Justo de Graham:** Cálculo do valor intrínseco baseado no Lucro por Ação (LPA) e Valor Patrimonial por Ação (VPA).
* **Margem de Segurança (%):** Avaliação quantitativa do potencial de valorização ou descolamento de preço em relação ao teto de Graham e Gordon.
* **Modelo de Gordon (Versão Simplificada):** Projeção de valuation orientada ao rendimento de dividendos.
* **Earnings Yield (%):** Retorno de lucros para análise comparativa de rentabilidade.

## 📂 Estrutura do Repositório
```text
AlphaAgent/
│
├── docs/                # Documentação oficial e Plano Mestre
├── src/
│   ├── data/            # Módulo de extração e consumo de dados da B3
│   ├── finance/         # Motor de cálculo, valuation e indicadores
│   └── main.py          # Orquestrador central (Maestro) da pipeline
│
├── .env                 # Variáveis de ambiente
├── .gitignore           # Exclusões de controlo de versão
└── README.md            # Documentação do projeto
