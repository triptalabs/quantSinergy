# models/trade.py

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Trade:
    timestamp: str
    pair: str
    leverage: int
    qty: float

    # Valores de entrada/salida: se puede definir uno u otro
    entry_price: Optional[float] = None
    entry_value: Optional[float] = None
    exit_price: Optional[float]  = None
    exit_value: Optional[float]  = None

    # Comisión manual (%)
    commission_pct: float = 0.1

    # Campos calculados
    commission: float = field(init=False, default=0.0)
    pnl:        float = field(init=False, default=0.0)
    roi:        float = field(init=False, default=0.0)

    def calculate_prices_values(self):
        """Bidireccional: price ↔ value"""
        if self.entry_price is not None and self.entry_value is None:
            self.entry_value = self.entry_price * self.qty
        elif self.entry_value is not None and self.entry_price is None:
            self.entry_price = self.entry_value / self.qty

        if self.exit_price is not None and self.exit_value is None:
            self.exit_value = self.exit_price * self.qty
        elif self.exit_value is not None and self.exit_price is None:
            self.exit_price = self.exit_value / self.qty

    def calculate_commission(self):
        """Comisión sobre entrada + salida"""
        r = self.commission_pct / 100
        self.commission = (self.entry_value + self.exit_value) * r

    def calculate_pnl_roi(self):
        """PNL = exit − entry − commission; ROI% = PNL/entry × 100"""
        self.pnl = self.exit_value - self.entry_value - self.commission
        self.roi = (self.pnl / self.entry_value * 100) if self.entry_value else 0.0

    def calculate_all(self):
        """Ejecuta todos los cálculos en el orden correcto"""
        self.calculate_prices_values()
        self.calculate_commission()
        self.calculate_pnl_roi()

    def set_roi(self, target_roi: float):
        """
        Ajusta exit_value y exit_price para lograr target_roi (%).
        Fórmula derivada de:
        ROI = [EV*(1−r) − IV*(1+r)]/IV * 100
        """
        self.roi = target_roi
        r = self.commission_pct / 100
        roi_frac = self.roi / 100
        # Calcula exit_value para lograr ese ROI
        self.exit_value = self.entry_value * (1 + r + roi_frac) / (1 - r)
        self.exit_price = self.exit_value / self.qty
        # Recalcula commission y pnl
        self.calculate_commission()
        self.pnl = self.exit_value - self.entry_value - self.commission

    def set_pnl(self, target_pnl: float):
        """
        Ajusta exit_value y exit_price para lograr target_pnl (valor absoluto).
        """
        self.pnl = target_pnl
        r = self.commission_pct / 100
        # PNL = EV*(1−r) − IV*(1+r) → EV = (PNL + IV*(1+r))/(1−r)
        self.exit_value = (self.pnl + self.entry_value * (1 + r)) / (1 - r)
        self.exit_price = self.exit_value / self.qty
        # Recalcula commission y roi
        self.calculate_commission()
        self.roi = (self.pnl / self.entry_value * 100) if self.entry_value else 0.0

    def to_dict(self) -> dict:
        """Prepara un dict listo para insertarse en SQLite"""
        return {
            "timestamp":     self.timestamp,
            "pair":          self.pair,
            "leverage":      self.leverage,
            "qty":           self.qty,
            "entry_price":   self.entry_price,
            "entry_value":   self.entry_value,
            "exit_price":    self.exit_price,
            "exit_value":    self.exit_value,
            "commission_pct":self.commission_pct,
            "commission":    self.commission,
            "pnl":           self.pnl,
            "roi":           self.roi,
        }
