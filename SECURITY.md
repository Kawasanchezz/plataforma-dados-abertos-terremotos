# Política de segurança

## Versões suportadas
Projeto acadêmico: somente a branch `main` recebe correções.

## Como reportar uma vulnerabilidade
Use **Security → Report a vulnerability** (GitHub Private Vulnerability Reporting) neste
repositório. Não abra issue pública com detalhes de exploração.

## Escopo e modelo de ameaça
- O projeto não tem autenticação, banco de dados, upload nem API própria, e não usa segredos.
- Dados vêm da API pública do USGS (não confiável): são validados/filtrados em `src/clean.py`
  e exibidos pelo Streamlit sem HTML bruto.
- O workflow de coleta (`contents: write`) só roda por agendamento ou por quem já tem
  permissão de escrita; a entrada `days` é passada por variável de ambiente e validada (1–90).

## Controles existentes
Dependências fixadas e auditadas com `pip-audit` no CI, Dependabot (pip e GitHub Actions),
actions fixadas por SHA, permissões mínimas no CI, testes automatizados.

## Limitações conhecidas
- Dependências transitivas não estão em lockfile com hashes.
- O dashboard hospedado no Streamlit Community Cloud não tem rate limiting próprio.
- O README/dados dependem da disponibilidade e integridade da fonte USGS.
- Nenhuma auditoria externa foi feita; o projeto não é garantidamente livre de vulnerabilidades.
