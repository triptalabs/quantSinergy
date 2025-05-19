# app.py

import streamlit as st
import pandas as pd
from datetime import datetime

from db.init_db import init_db, load_all_trades, get_connection
from models.trade import Trade
from services.binance_client import client, get_balances, get_price

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Trading",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Funciones de Trade ---
def insert_trade(trade: Trade):
    conn = get_connection()
    data = trade.to_dict()
    keys = ",".join(data.keys())
    placeholders = ",".join("?" for _ in data)
    sql = f"INSERT INTO trades ({keys}) VALUES ({placeholders})"
    conn.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()

# --- Funciones Binance ---
def get_assets_df():
    spot = get_balances()
    spot_df = pd.DataFrame(spot)
    spot_df["free"] = spot_df["free"].astype(float)
    spot_df["locked"] = spot_df["locked"].astype(float)
    spot_df["total"] = spot_df["free"] + spot_df["locked"]
    spot_df["origin"] = "spot"

    futures = client.futures_account_balance()
    fut_df = pd.DataFrame(futures).rename(columns={"balance": "total"})
    fut_df["total"] = fut_df["total"].astype(float)
    fut_df["free"] = fut_df["total"]
    fut_df["locked"] = 0.0
    fut_df["origin"] = "futures"

    assets_df = pd.concat([
        spot_df[["asset","free","locked","total","origin"]],
        fut_df[["asset","free","locked","total","origin"]]
    ], ignore_index=True)

    def compute_value(row):
        asset = row["asset"].upper()
        qty = row["total"]
        if asset == "USDT":
            return qty
        try:
            price = get_price(f"{asset}USDT")
            return qty * price
        except:
            return None

    assets_df["value_usdt"] = assets_df.apply(compute_value, axis=1)
    return spot_df, fut_df, assets_df

# --- Página Inicio ---
def pagina_inicio():
    st.header("Inicio")
    if st.button("Conectar Binance" if not st.session_state.get("binance_connected", False) else "Desconectar Binance"):
        st.session_state.binance_connected = not st.session_state.get("binance_connected", False)
        st.session_state.show_form = False

    if st.session_state.get("binance_connected", False):
        try:
            spot_df, fut_df, assets_df = get_assets_df()
            total = assets_df["value_usdt"].dropna().sum()

            st.metric("Saldo Total (USDT)", f"{total:,.2f}")

            detalle = st.selectbox("Detalles de:", ["Spot", "Futuros"])
            if detalle == "Spot":
                st.dataframe(
                    spot_df[["asset","free","locked","total","value_usdt"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.dataframe(
                    fut_df[["asset","free","locked","total","value_usdt"]],
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Error al obtener datos de Binance: {e}")
    else:
        st.info("Presiona el botón para conectar a Binance")

# --- Página Trades ---
def pagina_trades():
    st.header("Trades")
    df = load_all_trades()

    if st.button("➕ Nueva operación"):
        st.session_state.show_form = True

    if st.session_state.get("show_form", False):
        with st.expander("Agregar Operación", expanded=True):
            with st.form("trade_form", clear_on_submit=True):
                pair           = st.text_input("Par (p. ej. BTC/USDT)", value="BTC/USDT")
                leverage       = st.number_input("Apalancamiento", min_value=1, value=1, step=1)
                qty            = st.number_input("Cantidad", min_value=0.0, step=0.0001)
                entry_price    = st.number_input("Precio de entrada", min_value=0.0, step=0.0001)
                entry_value    = st.number_input("Valor de entrada (opcional)", min_value=0.0, step=0.0001)
                exit_price     = st.number_input("Precio de salida", min_value=0.0, step=0.0001)
                exit_value     = st.number_input("Valor de salida (opcional)", min_value=0.0, step=0.0001)
                commission_pct = st.number_input("Comisión (%)", min_value=0.0, value=0.1, step=0.01)

                roi_str = st.text_input("ROI (%) (opcional)", value="")
                pnl_str = st.text_input("PNL (valor) (opcional)", value="")

                submitted = st.form_submit_button("Guardar")
                if submitted:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trade = Trade(
                        timestamp=timestamp,
                        pair=pair,
                        leverage=leverage,
                        qty=qty,
                        entry_price=entry_price or None,
                        entry_value=entry_value or None,
                        exit_price=exit_price or None,
                        exit_value=exit_value or None,
                        commission_pct=commission_pct,
                    )
                    trade.calculate_prices_values()
                    if roi_str:
                        trade.set_roi(float(roi_str))
                    elif pnl_str:
                        trade.set_pnl(float(pnl_str))
                    else:
                        trade.calculate_commission()
                        trade.calculate_pnl_roi()
                    insert_trade(trade)
                    st.success("✅ Operación guardada")
                    st.session_state.show_form = False
                    df = load_all_trades()

    if not df.empty:
        st.dataframe(
            df.drop(columns=["id"]),
            use_container_width=True,
            height=600,
            hide_index=True
        )
    else:
        st.info("No hay trades registrados aún.")

# --- Función principal ---
def main():
    init_db()
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    tabs = st.tabs(["Inicio", "Trades"])
    with tabs[0]:
        pagina_inicio()
    with tabs[1]:
        pagina_trades()

if __name__ == "__main__":
    main()
