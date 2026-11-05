"""Coletor: baixa terremotos (M>=2.5) da API FDSN do USGS e salva um CSV bruto por dia (UTC).

Uso:
    python src/collect.py              # ultimos 3 dias (rodada agendada; reescreve dias revisados)
    python src/collect.py --days 60    # backfill inicial (maximo 90)
"""
import argparse
import datetime as dt
from pathlib import Path

import requests

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
MAX_DAYS = 90
MAX_BYTES = 5 * 1024 * 1024  # limite de resposta por dia
TIMEOUT = (10, 60)  # (conexao, leitura) em segundos


def days_arg(value: str) -> int:
    n = int(value)
    if not 1 <= n <= MAX_DAYS:
        raise argparse.ArgumentTypeError(f"--days deve estar entre 1 e {MAX_DAYS}")
    return n


def fetch_day(day: dt.date, min_mag: float = 2.5) -> str:
    params = {
        "format": "csv",
        "starttime": day.isoformat(),
        "endtime": (day + dt.timedelta(days=1)).isoformat(),
        "minmagnitude": min_mag,
        "orderby": "time-asc",
    }
    with requests.get(URL, params=params, timeout=TIMEOUT, stream=True) as r:
        r.raise_for_status()
        body = b""
        for chunk in r.iter_content(65536):
            body += chunk
            if len(body) > MAX_BYTES:
                raise RuntimeError(f"Resposta maior que {MAX_BYTES} bytes para {day}")
    return body.decode("utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=days_arg, default=3)
    args = ap.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.datetime.now(dt.timezone.utc).date()
    for i in range(args.days):
        day = today - dt.timedelta(days=i)
        text = fetch_day(day)
        # nome derivado so de uma data validada: sem path traversal
        (RAW_DIR / f"quakes_{day.isoformat()}.csv").write_text(text, encoding="utf-8", newline="")
        print(f"{day}: {max(text.count(chr(10)) - 1, 0)} eventos")


if __name__ == "__main__":
    main()
