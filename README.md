# Plataforma de Dados Abertos de Ponta a Ponta — Terremotos (USGS)

Ciclo completo: **coleta agendada → limpeza reprodutível → análise → dashboard**.

- 📊 **Dashboard:** _cole aqui o link do Streamlit Community Cloud após o deploy_
- Fonte: [USGS Earthquake Catalog (API FDSN)](https://earthquake.usgs.gov/fdsnws/event/1/), eventos M ≥ 2.5, atualizada continuamente, sem chave de API.

## Estrutura
| Caminho | Função |
|---|---|
| `src/collect.py` | baixa CSV por dia (UTC) em `data/raw/` |
| `src/clean.py` | gera `data/processed/earthquakes.csv` |
| `notebooks/analise.ipynb` | 6 perguntas + gráficos Plotly |
| `app.py` | dashboard Streamlit |
| `.github/workflows/coleta.yml` | roda diariamente 06:15 UTC, executa tudo e faz commit dos dados |

## Reproduzir
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/collect.py --days 60     # backfill inicial
python src/clean.py
jupyter nbconvert --to notebook --execute --inplace notebooks/analise.ipynb
streamlit run app.py
```

## Dicionário de dados (`data/processed/earthquakes.csv`)
| Coluna | Descrição |
|---|---|
| id | identificador único do evento (USGS) |
| time | instante do evento (UTC) |
| date / hour | data (YYYY-MM-DD) e hora (0–23) UTC derivadas de `time` |
| latitude / longitude | epicentro, graus |
| depth | profundidade em km |
| mag / magType | magnitude e método de cálculo |
| mag_class | faixa: <3, 3-4, 4-5, 5-6, 6+ |
| depth_class | rasa (<70 km), intermediária (70–300), profunda (>300) |
| place | descrição textual do local |
| region | último trecho de `place` após a vírgula (país/estado ou oceano) |
| status | `automatic` ou `reviewed` |
| updated | última atualização do registro no USGS |

## Decisões de limpeza
1. Snapshots diários são concatenados e deduplicados por `id`, mantendo o `updated` mais recente (o USGS revisa eventos; por isso o coletor reescreve os últimos 3 dias).
2. Só `type == earthquake` (exclui explosões/mineração).
3. Descartadas linhas sem tempo, coordenadas ou magnitude, ou fora das faixas válidas.
4. Profundidades negativas (acima do nível do mar) viram 0.
5. `region` é heurística textual; locais sem vírgula usam o `place` inteiro (ex.: "Mid-Atlantic Ridge").

## Deploy
1. Crie o repositório público no GitHub e dê push; em *Actions* rode **Coleta diaria** manualmente com `days=60`.
2. Em [share.streamlit.io](https://share.streamlit.io) aponte para `app.py` e cole a URL acima.

## Segurança e qualidade
- Política e contato: [SECURITY.md](SECURITY.md). Licença: [MIT](LICENSE).
- Testes: `pip install -r requirements-dev.txt && pytest && ruff check . && pip-audit -r requirements.txt`
- Dados: © USGS, domínio público ([termos](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits)); a atribuição à fonte é mantida neste projeto.
