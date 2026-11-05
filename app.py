import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Terremotos no mundo", layout="wide")
st.title("🌍 Terremotos no mundo (M ≥ 2.5)")
st.caption("Fonte: USGS Earthquake Catalog · atualizado diariamente via GitHub Actions")


@st.cache_data(ttl=3600)
def load() -> pd.DataFrame:
    d = pd.read_csv("data/processed/earthquakes.csv")
    d["time"] = pd.to_datetime(d["time"], utc=True, format="ISO8601")
    return d


try:
    df = load()
except FileNotFoundError:
    st.error("Dados ainda não gerados. Rode `python src/collect.py` e `python src/clean.py`.")
    st.stop()
if df.empty:
    st.warning("O arquivo de dados está vazio.")
    st.stop()
lo, hi = float(df["mag"].min()), float(df["mag"].max())
mag = st.sidebar.slider("Magnitude", lo, hi, (lo, hi))
dmin, dmax = df["time"].dt.date.min(), df["time"].dt.date.max()
periodo = st.sidebar.date_input("Período", (dmin, dmax), min_value=dmin, max_value=dmax)
d0, d1 = (periodo[0], periodo[-1]) if len(periodo) else (dmin, dmax)  # tupla parcial durante a seleção
f = df[df["mag"].between(*mag) & (df["time"].dt.date >= d0) & (df["time"].dt.date <= d1)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Eventos", f"{len(f):,}")
c2.metric("Magnitude máxima", f"{f['mag'].max():.1f}" if len(f) else "–")
c3.metric("Magnitude média", f"{f['mag'].mean():.2f}" if len(f) else "–")
c4.metric("Eventos M ≥ 5", f"{(f['mag'] >= 5).sum():,}")

st.plotly_chart(px.scatter_geo(f, lat="latitude", lon="longitude", color="mag", size="mag",
                               hover_name="place", projection="natural earth",
                               color_continuous_scale="YlOrRd"), use_container_width=True)
a, b = st.columns(2)
daily = f.groupby("date").size().reset_index(name="eventos")
a.plotly_chart(px.bar(daily, x="date", y="eventos", title="Eventos por dia"), use_container_width=True)
top = f["region"].value_counts().head(10).reset_index()
b.plotly_chart(px.bar(top, x="count", y="region", orientation="h", title="Top 10 regiões")
               .update_yaxes(autorange="reversed"), use_container_width=True)
st.dataframe(f.sort_values("time", ascending=False).head(200), use_container_width=True)
