# APP_RANSHARING — Monitoreo RanSharing Entel

## 🚀 Cómo ejecutar la aplicación

### 1. Instalar dependencias
```powershell
cd c:\Users\pledesma\Desktop\Proyecto_WOM\APP_RANSHARING
pip install -r requirements.txt
```

### 2. Configurar Google Sheets
Edita el archivo `.streamlit/secrets.toml` y agrega las credenciales de tu
**Service Account** de Google Cloud. Instrucciones completas en el archivo.

### 3. Ejecutar la app
```powershell
streamlit run app.py
```

---

## 📁 Estructura del Proyecto

```
APP_RANSHARING/
├── app.py                    ← Aplicación principal Streamlit
├── requirements.txt          ← Dependencias Python
├── .streamlit/
│   ├── config.toml           ← Tema WOM/Entel (púrpura/magenta)
│   └── secrets.toml          ← Credenciales Google Sheets (NO subir a Git)
├── config/
│   └── settings.py           ← DB config, paleta de colores, constantes
├── queries/
│   └── sql_queries.py        ← Queries SQL modularizadas por KPI
├── utils/
│   ├── db.py                 ← Conexión PostgreSQL (psycopg2)
│   └── kpis.py               ← Lógica de auditoría y cruce de datos
└── components/
    ├── cards.py              ← Tarjetas HTML estilo WOM/Entel
    └── charts.py             ← Gráficos Plotly (8 módulos KPI + mapa)
```

---

## 📊 Módulos KPI disponibles

| Módulo       | Métricas                                                     |
|--------------|--------------------------------------------------------------|
| Accesibilidad| E_RAB_Setup_SR, E_RAB_Setup_SR_QCI5, RRC_Setup_SR, S1_Sig   |
| Downtime     | Cell_Availability (%), Unavailability_Minutes                |
| DROP         | E_RAB_Drop_Rate, E_RAB_Drop_QCI5_Excl, RRC_Drop_Rate        |
| Velocidad    | DL_Throughput_Mbps, UL_Throughput_Mbps                       |
| Usuarios     | RRC_Conn_Max, RRC_Conn_Avg                                   |
| PRB          | DL_PRB_Utilization (%), UL_PRB_Utilization (%)               |
| Tráfico      | DL_Traffic_GB, UL_Traffic_GB                                 |
| VoLTE        | VoLTE_E_RAB_Setup_SR, VoLTE_Traffic_Erl, VoLTE_Users         |

---

## ⚠️ Notas importantes

### Nombres de columnas SQL
Las queries asumen **nomenclatura Ericsson estándar LTE**. Si tu tabla
`counters_hourly_entel` usa nombres distintos, edita `queries/sql_queries.py`.

Columnas clave asumidas:
- `datetime_id` → timestamp
- `eutrancell` → nombre de celda
- `e_rab_setup_sr`, `cell_availability`, etc.

### Google Sheet esperada (RANSHARING_CELLS)
Columnas mínimas: `SITE`, `CELLNAME`, `OPERATOR`, `LAT`, `LON`

---

## 🎨 Diseño
- **Paleta**: Púrpura `#7B2D8B` · Magenta `#E91E8C` · Fondo `#F2EDF9`
- **Fuente**: Inter (Google Fonts)
- **Sidebar**: Gradiente oscuro con módulos KPI navegables
- **Tarjetas**: Estilo PowerBI con borde de color de acuerdo al estado
