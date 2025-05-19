# 📈 Tabla-Trading: Control de Trading en Streamlit

**Tabla-Trading** es una aplicación de escritorio local desarrollada en Python y Streamlit para llevar el control de tus operaciones de trading de manera sencilla, persistente y conectada a Binance.

---

## 🔍 Descripción

Esta herramienta te permite:

* Registrar operaciones con campos obligatorios y calculados de forma bidireccional:

  * Timestamp automático
  * Par de trading (p.ej. BTC/USDT)
  * Apalancamiento
  * Cantidad (qty)
  * Precio ↔ Valor (bidireccional)
  * Comisión manual (%) y cálculo automático
  * PNL ↔ ROI (bidireccional)
* Persistir todo en **SQLite** (`trades.db`) sin depender de contenedores ni servicios externos.
* Visualizar en una interfaz **wide** optimizada para escritorio, con:

  * Tabla de operaciones (sin scroll vertical de página)
  * Botón flotante para añadir nuevas operaciones
* Conectar y desconectar tu cuenta de **Binance** vía API para:

  * Consultar balances de Spot y Futuros
  * Mostrar origen (spot/futures) y valor en USDT de cada activo
  * Consultar precio puntual de cualquier par

---

## 🚀 Características principales

1. **Interfaz limpia**: tabla principal y formulario lateral desplegable.
2. **Persistencia local**: SQLite integrado, sin servidores.
3. **Cálculos bidireccionales**:

   * Precio ↔ Valor (entrada y salida)
   * PNL ↔ ROI ↔ Precio de salida
4. **Comisión configurable**: define tu % de comisiones y el cálculo es automático.
5. **Integración Binance**:

   * Toggle conectar/desconectar
   * Spot vs. Futuros (origen)
   * Valor en USDT por activo
   * Consulta de precios en tiempo real
6. **Escalabilidad**: estructura modular (módulos `db/`, `models/`, `services/`) para futuras mejoras.

---

## 📂 Estructura de carpetas

```bash
Tabla-Trading/
├── .gitignore            # Ignora venv, __pycache__, .db, .env
├── README.md             # Documentación principal
├── requirements.txt      # Dependencias Python
├── .env                  # Variables de entorno (Binance API)
├── trades.db             # Base de datos SQLite (autogenerada)
├── app.py                # Aplicación Streamlit
├── db/
│   └── init_db.py        # Inicialización y carga de SQLite
├── models/
│   └── trade.py          # Lógica de negocio Trade (dataclass + cálculos)
└── services/
    └── binance_client.py # Cliente Binance (Spot y Futures)
```

---

## ⚙️ Instalación y configuración

1. Clona el repositorio:

   ```bash
   git clone https://github.com/triptalabs/Tabla-Trading.git
   cd Tabla-Trading
   ```

2. Crea y activa un entorno virtual (recomendado):

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   . `.\.venv\Scripts\Activate.ps1`
   # Bash (Git Bash/WSL/macOS):
   source .venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura las credenciales de Binance (opcional si usarás API):

   * Crea un archivo `.env` en la raíz:

     ```ini
     BINANCE_API_KEY=tu_api_key
     BINANCE_API_SECRET=tu_api_secret
     ```
   * Asegúrate de que `.gitignore` incluye `.env`.

---

## 🎯 Uso de la aplicación

Ejecuta la app localmente:

```bash
streamlit run app.py
```

* **Tabla principal**: visualiza todas tus operaciones.
* **➕ Nueva operación**: abre el formulario lateral para registrar trade.
* **Formulario**: completa los datos o usa inputs bidireccionales y guarda.
* **Sidebar Binance**:

  * Pulsa **Conectar Binance** para ver balances (Spot + Futures).
  * Ingresa un par (p.ej. `BTCUSDT`) y pulsa **Obtener precio**.
  * Pulsa **Desconectar Binance** para limpiar la sesión.

---

## 🤝 Contribuciones

1. Haz un fork del repositorio.
2. Crea una branch `feature/tu-descripción`.
3. Implementa tu mejora y añade tests si aplica.
4. Haz un PR describiendo los cambios con claridad.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
