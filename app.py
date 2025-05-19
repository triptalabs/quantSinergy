# app.py

import streamlit as st
import pandas as pd
from datetime import datetime

from db.init_db import init_db, load_all_trades, get_connection
from models.trade import Trade
from services.binance_client import client, get_balances, get_price

st.set_page_config(
    page_title="Control de Trading",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def insert_trade(trade: Trade):
    conn = get_connection()
    data = trade.to_dict()
    keys = ",".join(data.keys())
    placeholders = ",".join("?" for _ in data)
    sql = f"INSERT INTO trades ({keys}) VALUES ({placeholders})"
    conn.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()

def main():
    # --- Inicializar DB y cargar datos ---
    init_db()
    df = load_all_trades()

    # --- Sidebar: Binance API con toggle connect/disconnect ---
    if "binance_connected" not in st.session_state:
        st.session_state.binance_connected = False

    btn_label = "Conectar Binance" if not st.session_state.binance_connected else "Desconectar Binance"
    if st.sidebar.button(btn_label):
        st.session_state.binance_connected = not st.session_state.binance_connected

    if st.session_state.binance_connected:
        try:
            # Spot balances
            spot = get_balances()  # [{ asset, free, locked }, ...]
            # Futures balances
            futures = client.futures_account_balance()  # [{ asset, balance }, ...]

            # Normalizar datos spot
            spot_df = pd.DataFrame(spot)
            spot_df["free"] = spot_df["free"].astype(float)
            spot_df["locked"] = spot_df["locked"].astype(float)
            spot_df["total"] = spot_df["free"] + spot_df["locked"]
            spot_df["origin"] = "spot"

            # Normalizar datos futures
            futures_df = pd.DataFrame(futures)
            futures_df = futures_df.rename(columns={"balance": "total"})
            futures_df["total"] = futures_df["total"].astype(float)
            futures_df["free"] = futures_df["total"]  # en futures todo es libre
            futures_df["locked"] = 0.0
            futures_df["origin"] = "futures"

            # Unir
            assets_df = pd.concat([spot_df[["asset","free","locked","total","origin"]],
                                   futures_df[["asset","free","locked","total","origin"]]],
                                  ignore_index=True)

            # Calcular valor en USDT
            def compute_value(row):
                asset = row["asset"]
                qty = row["total"]
                if asset.upper() == "USDT":
                    return qty
                try:
                    price = get_price(f"{asset}USDT")
                    return qty * price
                except:
                    return None

            assets_df["value_usdt"] = assets_df.apply(compute_value, axis=1)

            st.sidebar.success("✅ Conectado a Binance")
            st.sidebar.dataframe(
                assets_df,
                use_container_width=True,
                height=400
            )
        except Exception as e:
            st.sidebar.error(f"Error al conectar: {e}")

    # --- Control de formulario ---
    if "show_form" not in st.session_state:
        st.session_state.show_form = False

    # --- Layout principal ---
    col_table, col_form = st.columns([3, 1])

    with col_table:
        st.title("📈 Control de Trading")
        if st.button("➕ Nueva operación"):
            st.session_state.show_form = True

        if not df.empty:
            st.dataframe(
                df.drop(columns=["id"]),
                use_container_width=True,
                height=600,
            )

    with col_form:
        if st.session_state.show_form:
            with st.form("trade_form", clear_on_submit=True):
                st.subheader("Agregar Operación")
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
        else:
            st.markdown("**Presiona ➕ para añadir una operación**")

if __name__ == "__main__":
    main()
