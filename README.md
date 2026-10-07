# AlphaAgent

Motor local de classificacao. Nao e corretora. Nao emite ordem de compra nem venda. Nao ha Agente 2.

Estado: Fase 4.0. O motor local esta fechado ate a Fase 3.14.

## O que roda
- Acao B3: Graham, Gordon e status.
- Renda fixa: taxa do Tesouro Transparente, com titulo, vencimento e data base.
- Exterior: cambio USD/BRL do dia, com fallback manual.
- FII: P/VP.
- Historico diario e lista do que mudou de status.

## Como rodar
```powershell
cd C:\Users\User\OneDrive\Documentos\AlphaAgent
py -m pytest tests -q
py -m src.main
```

A saida fica em `relatorios/`. Essa pasta nao vai para o GitHub.

## O que nao usar
`ai_agent.py` e `docker-compose.yml` foram retirados. Docker, FastAPI e login ainda nao entram.
