"""Limpeza reprodutivel: data/raw/*.csv -> data/processed/earthquakes.csv

Decisoes de limpeza (tambem documentadas no README):
1. Concatena todos os snapshots diarios e remove duplicatas por `id`, mantendo a versao
   com `updated` mais recente (o USGS revisa eventos).
2. Mantem apenas type == 'earthquake' (descarta explosoes, minas etc.).
3. Converte `time`/`updated` para datetime UTC; descarta linhas sem tempo, coordenadas ou magnitude.
4. Valida faixas: latitude [-90,90], longitude [-180,180], magnitude [-1,10]; profundidade negativa vira 0.
5. Deriva `region` (ultimo trecho de `place` apos a virgula), `mag_class`, `depth_class`, `date`, `hour`.
6. Mantem so as colunas uteis e ordena por tempo.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "earthquakes.csv"

KEEP = ["id", "time", "date", "hour", "latitude", "longitude", "depth", "mag", "magType",
        "mag_class", "depth_class", "place", "region", "status", "updated"]


def load_raw() -> pd.DataFrame:
    files = sorted(RAW_DIR.glob("quakes_*.csv"))
    if not files:
        raise SystemExit("Nenhum arquivo em data/raw. Rode src/collect.py primeiro.")
    return pd.concat((pd.read_csv(f) for f in files), ignore_index=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df["updated"] = pd.to_datetime(df["updated"], utc=True, errors="coerce")
    df = df.sort_values("updated").drop_duplicates("id", keep="last")
    df = df[df["type"] == "earthquake"]
    df = df.dropna(subset=["time", "latitude", "longitude", "mag"])
    df = df[df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)
            & df["mag"].between(-1, 10)]
    df["depth"] = df["depth"].clip(lower=0)
    df["place"] = df["place"].fillna("Desconhecido").str.strip()
    df["region"] = df["place"].str.rsplit(",", n=1).str[-1].str.strip()
    df["mag_class"] = pd.cut(df["mag"], [-1, 3, 4, 5, 6, 10],
                             labels=["<3", "3-4", "4-5", "5-6", "6+"], right=False).astype(str)
    df["depth_class"] = pd.cut(df["depth"], [0, 70, 300, 1000],
                               labels=["rasa (<70 km)", "intermediaria (70-300 km)", "profunda (>300 km)"],
                               include_lowest=True).astype(str)
    df["date"] = df["time"].dt.date.astype(str)
    df["hour"] = df["time"].dt.hour
    return df[KEEP].sort_values("time").reset_index(drop=True)


def main() -> None:
    out = clean(load_raw())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"{len(out)} eventos limpos -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
