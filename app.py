# app.py

import streamlit as st
import pandas as pd
from datetime import datetime

from db.init_db import init_db, load_all_trades, get_connection
from models.trade import Trade

def insert_trade(trade: Trade):
    """
    Inserta un Trade en la tabla 'trades' de SQLite.
    """
    conn = get_connection()
    data = trade.to_dict()
    keys = ",".join(data.keys())
    placeholders = ",".join("?" for _ in data)
    sql = f"INSERT INTO trades ({keys}) VALUES ({placeholders})"
    conn.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()

def main():
    st.title("📈 Control de Trading (Persistente)")

    # Inicializa DB y carga operaciones existentes
    init_db()
    df = load_all_trades()

    # Formulario de nueva operación
    with st.form("trade_form", clear_on_submit=True):
        pair           = st.text_input("Par (ej. BTC/USDT)", value="BTC/USDT")
        leverage       = st.number_input("Apalancamiento", min_value=1, value=1, step=1)
        qty            = st.number_input("Cantidad", min_value=0.0, step=0.0001)
        entry_price    = st.number_input("Precio de entrada", min_value=0.0, step=0.0001)
        entry_value    = st.number_input("Valor de entrada (opcional)", min_value=0.0, step=0.0001)
        exit_price     = st.number_input("Precio de salida", min_value=0.0, step=0.0001)
        exit_value     = st.number_input("Valor de salida (opcional)", min_value=0.0, step=0.0001)
        commission_pct = st.number_input("Comisión (%)", min_value=0.0, value=0.1, step=0.01)

        # Campos opcionales para bidireccionalidad PNL/ROI
        roi_str = st.text_input("ROI (%) (opcional)", value="")
        pnl_str = st.text_input("PNL (valor absoluto) (opcional)", value="")

        submitted = st.form_submit_button("➕ Agregar operación")
        if submitted:
            # Timestamp automático
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Crear instancia Trade
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

            # Lógica de cálculo
            # 1. Siempre calculamos price ↔ value para asegurar entry values
            trade.calculate_prices_values()

            # 2. Si el usuario definió ROI, recalculamos salida a partir de ROI
            if roi_str:
                trade.set_roi(float(roi_str))
            # 3. Si definió PNL, recalculamos salida a partir de PNL
            elif pnl_str:
                trade.set_pnl(float(pnl_str))
            # 4. Si no, hacemos el flujo estándar
            else:
                trade.calculate_commission()
                trade.calculate_pnl_roi()

            # Guardar en BD y refrescar tabla
            insert_trade(trade)
            st.success("✅ Operación guardada")
            df = load_all_trades()

    # Mostrar tabla de operaciones
    if not df.empty:
        st.dataframe(df.drop(columns=["id"]), use_container_width=True)

if __name__ == "__main__":
    main()
