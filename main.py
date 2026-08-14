import streamlit as st
import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go
import math

# ============================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================
st.set_page_config(
    page_title="Entiende tu Préstamo - Argentina",
    page_icon=":material/calculate:",
    layout="wide",
)

JURISDICCIONES_CONFIG = {
    "Buenos Aires": {"iibb": 9.00, "sellos": 1.20, "base_iibb": "Interés de cada cuota"},
    "CABA": {"iibb": 8.00, "sellos": 1.20, "base_iibb": "Interés de cada cuota"},
    "Catamarca": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Chaco": {"iibb": 7.70, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Chubut": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Córdoba": {"iibb": 9.00, "sellos": 1.20, "base_iibb": "Interés de cada cuota"},
    "Corrientes": {"iibb": 4.70, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Entre Ríos": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Formosa": {"iibb": 5.50, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Jujuy": {"iibb": 8.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "La Pampa": {"iibb": 9.10, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "La Rioja": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Mendoza": {"iibb": 7.00, "sellos": 1.50, "base_iibb": "Interés de cada cuota"},
    "Misiones": {"iibb": 7.80, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Neuquén": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Río Negro": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Salta": {"iibb": 8.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "San Juan": {"iibb": 7.80, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "San Luis": {"iibb": 6.50, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Santa Cruz": {"iibb": 8.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Santa Fe": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Santiago del Estero": {"iibb": 3.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Tierra del Fuego": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
    "Tucumán": {"iibb": 9.00, "sellos": 0.00, "base_iibb": "Interés de cada cuota"},
}

def money(value):
    return f"${value:,.2f}" if value is not None else "$0.00"

def pct(value):
    return f"{value:.2f}%" if value is not None else "0.00%"

def tasa_mensual_desde_tna(tna):
    return (tna / 100.0) / 12.0

def calcular_cuota(capital, tasa_mensual, meses):
    if meses <= 0: return 0.0
    if abs(tasa_mensual) < 1e-12: return capital / meses
    return float(abs(npf.pmt(tasa_mensual, meses, capital, 0, 0)))

def ratio_endeudamiento_total(cuota, ingreso):
    return 0 if ingreso <= 0 else (cuota / ingreso) * 100

def semaforo_credito(ratio):
    if ratio == 0: return "⚪ No calculable"
    if ratio < 25: return "🟢 Bajo Riesgo"
    if ratio < 40: return "🟡 Riesgo Medio"
    return "🔴 Riesgo Alto"

def analisis_real_vs_nominal(df_amortizacion, inflacion_mensual):
    nominal = df_amortizacion["Cuota total"].sum()
    real = 0
    for _, row in df_amortizacion.iterrows():
        real += row["Cuota total"] / ((1 + inflacion_mensual) ** row["Mes"])
    return nominal, real

def configurar_costo(titulo, key, descripcion="", tasa_predeterminada=0.0, base_predeterminada="Capital inicial", activo_predeterminado=False, frecuencia_predeterminada="Único al inicio"):
    with st.expander(f":material/settings: {titulo}", expanded=False):
        if descripcion: st.caption(descripcion)
        
        activo = st.checkbox(f"¿Aplica {titulo.lower()}?", value=activo_predeterminado, key=f"{key}_activo")
        
        if not activo:
            return {"activo": False, "tipo": "Porcentaje", "tasa": 0.0, "importe": 0.0, "base": base_predeterminada, "frecuencia": "Único al inicio"}

        tipo = st.radio("Forma de cálculo", ["Porcentaje", "Importe fijo"], horizontal=True, key=f"{key}_tipo")
        
        if tipo == "Porcentaje":
            tasa = st.number_input("Alícuota / porcentaje", min_value=0.0, max_value=100.0, value=float(tasa_predeterminada), step=0.01, format="%.2f", key=f"{key}_tasa")
            importe = 0.0
        else:
            tasa = 0.0
            importe = st.number_input("Importe fijo", min_value=0.0, value=0.0, step=100.0, format="%.2f", key=f"{key}_importe")

        opciones_base = ["Capital inicial", "Saldo deudor (capital pendiente)", "Interés de cada cuota", "Capital + interés", "Cuota base"]
        idx_base = opciones_base.index(base_predeterminada) if base_predeterminada in opciones_base else 0
        base = st.selectbox("Base de cálculo", opciones_base, index=idx_base, key=f"{key}_base")
        
        frecuencia_opciones = ["Único al inicio", "Mensual"]
        frecuencia = st.selectbox("Frecuencia del cobro", frecuencia_opciones, index=frecuencia_opciones.index(frecuencia_predeterminada), key=f"{key}_frecuencia")

        return {"activo": True, "tipo": tipo, "tasa": tasa, "importe": importe, "base": base, "frecuencia": frecuencia}

def calcular_importe_costo(config, capital, interes, cuota_base, saldo_deudor):
    if not config["activo"]: return 0.0
    if config["tipo"] == "Importe fijo": return float(config["importe"])
    
    b = capital
    if config["base"] == "Saldo deudor (capital pendiente)": b = saldo_deudor
    elif config["base"] == "Interés de cada cuota": b = interes
    elif config["base"] == "Capital + interés": b = capital + interes
    elif config["base"] == "Cuota base": b = cuota_base
    
    return b * config["tasa"] / 100.0

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(":material/settings: Configuración Argentina")
    provincia = st.selectbox("Jurisdicción", ["Seleccionar manualmente"] + list(JURISDICCIONES_CONFIG.keys()), index=0)
    st.markdown("---")
    st.markdown(":material/3p: Perfil Financiero")
    ingreso_usuario = st.number_input("Ingreso mensual neto ($)", min_value=0.0, value=0.0, step=50000.0)
    inflacion_anual_esperada = st.number_input("Inflación anual esperada (%)", min_value=0.0, value=33.0, step=1.0)
    
# ============================================================
# DATOS PRINCIPALES
# ============================================================
st.subheader("Entiende tu Préstamo (Argentina)")
st.caption("Simulador con cálculo exacto de impuestos, métricas avanzadas y comparativas clave.")

st.markdown("## 1. Datos del préstamo (Tasa Fija)")
col1, col2, col3 = st.columns(3)
with col1: monto_prestamo = st.number_input("Monto en mano deseado", min_value=1.0, value=1000000.0, step=10000.0)
with col2: plazo_meses = st.number_input("Plazo (meses)", min_value=1, value=24, step=1)
with col3: tasa_ingresada = st.number_input("TNA (%)", min_value=0.0, value=50.0, step=0.1)

tasa_mensual = tasa_mensual_desde_tna(tasa_ingresada)
cuota_base_original = calcular_cuota(monto_prestamo, tasa_mensual, plazo_meses)

# ============================================================
# COSTOS Y TRIBUTOS A CARGO DEL CLIENTE
# ============================================================
st.markdown("## 2. Impuestos y costos a cargo del cliente")

tasa_iibb_def = 0.0
base_iibb_def = "Capital inicial"
tasa_sellos_def = 0.0

if provincia in JURISDICCIONES_CONFIG:
    config_prov = JURISDICCIONES_CONFIG[provincia]
    tasa_iibb_def = config_prov["iibb"]
    base_iibb_def = config_prov["base_iibb"]
    tasa_sellos_def = config_prov["sellos"]
    st.success(f":material/bookmark_check: Alícuotas cargadas para {provincia}. Sellos ({tasa_sellos_def}%). El IIBB bancario ({tasa_iibb_def}%) se calculará de forma informativa y no se sumará a tu cuota.")

sellos = configurar_costo("Impuesto de Sellos (Provincial)", "sellos", descripcion="Calculado automáticamente al % provincial sobre el capital inicial.", tasa_predeterminada=tasa_sellos_def, base_predeterminada="Capital inicial", activo_predeterminado=(tasa_sellos_def > 0), frecuencia_predeterminada="Único al inicio")
iva = configurar_costo("IVA (Nacional)", "iva", descripcion="21% sobre los intereses de cada cuota.", tasa_predeterminada=21.0, base_predeterminada="Interés de cada cuota", activo_predeterminado=True, frecuencia_predeterminada="Mensual")
seguro = configurar_costo("Seguro de Vida / Saldo Deudor", "seguro", descripcion="Cubre la deuda pendiente. Se cobra mensualmente sobre el saldo deudor.", tasa_predeterminada=0.15, base_predeterminada="Saldo deudor (capital pendiente)", activo_predeterminado=True, frecuencia_predeterminada="Mensual")
comision = configurar_costo("Comisión u Otros cargos por liquidación", "comision", descripcion="Comisión retenida por el banco al otorgar el crédito.", tasa_predeterminada=3.0, base_predeterminada="Capital inicial", activo_predeterminado=True, frecuencia_predeterminada="Único al inicio")

costos_cliente = {"Sellos": sellos, "IVA": iva, "Seguro": seguro, "Comisión": comision}

config_iibb_banco = {
    "activo": (tasa_iibb_def > 0),
    "tipo": "Porcentaje",
    "tasa": tasa_iibb_def,
    "importe": 0.0,
    "base": base_iibb_def,
    "frecuencia": "Mensual"
}

# ============================================================
# CRONOGRAMA Y CÁLCULOS
# ============================================================
monto_sellos_inicio = calcular_importe_costo(sellos, monto_prestamo, 0, cuota_base_original, monto_prestamo) if sellos["frecuencia"] == "Único al inicio" else 0.0
monto_comision_inicio = calcular_importe_costo(comision, monto_prestamo, 0, cuota_base_original, monto_prestamo) if comision["frecuencia"] == "Único al inicio" else 0.0

costos_pagados_al_inicio = monto_sellos_inicio + monto_comision_inicio
capital_financiado = monto_prestamo 
cuota_base = calcular_cuota(capital_financiado, tasa_mensual, plazo_meses)
monto_neto_recibido = monto_prestamo - costos_pagados_al_inicio

schedule = []
saldo = capital_financiado
total_iibb_banco = 0.0

# Flujos de caja para calcular el CFT (Costo Financiero Total)
flujos_caja_principal = [monto_neto_recibido]

for mes in range(1, plazo_meses + 1):
    saldo_deudor_inicio_mes = saldo
    interes = saldo * tasa_mensual
    capital = saldo if mes == plazo_meses else max(0.0, min(saldo, cuota_base - interes))
    saldo = max(0.0, saldo - capital)
    
    fila = {"Mes": mes, "Capital": capital, "Interés": interes}
    total_costos_mes_cliente = 0.0
    
    for nombre, config in costos_cliente.items():
        if config["frecuencia"] == "Mensual":
            val = calcular_importe_costo(config, capital, interes, capital + interes, saldo_deudor_inicio_mes)
            fila[nombre] = val
            total_costos_mes_cliente += val
        else:
            fila[nombre] = 0.0
        
    iibb_mes = calcular_importe_costo(config_iibb_banco, capital, interes, capital + interes, saldo_deudor_inicio_mes) if config_iibb_banco["frecuencia"] == "Mensual" else 0.0
    fila["IIBB (Info Banco)"] = iibb_mes
    total_iibb_banco += iibb_mes
        
    cuota_total = capital + interes + total_costos_mes_cliente
    fila["Cuota total"] = cuota_total
    
    flujos_caja_principal.append(-cuota_total)
    schedule.append(fila)

df = pd.DataFrame(schedule)
total_pagado_cuotas = df["Cuota total"].sum()
total_pagado_cliente = total_pagado_cuotas + costos_pagados_al_inicio

# Cálculo de CFT EA (Costo Financiero Total Efectivo Anual)
try:
    irr_mensual_prin = npf.irr(flujos_caja_principal)
    cft_ea_prin = ((1 + irr_mensual_prin) ** 12 - 1) * 100 if irr_mensual_prin is not None else 0.0
except:
    cft_ea_prin = 0.0

tea_prin = ((1 + tasa_mensual) ** 12 - 1) * 100

# ============================================================
# RESULTADOS Y ANÁLISIS
# ============================================================
st.markdown("---")
st.markdown("## 3. Resultados y Sostenibilidad Financiera")

cuota_promedio = df["Cuota total"].mean()
ratio = ratio_endeudamiento_total(cuota_promedio, ingreso_usuario)
semaforo = semaforo_credito(ratio)

inflacion_mensual_efectiva = ((1 + inflacion_anual_esperada / 100.0) ** (1 / 12)) - 1
total_nominal, total_real = analisis_real_vs_nominal(df, inflacion_mensual_efectiva)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Monto solicitado", money(monto_prestamo))
c2.metric(
    "Monto NETO a recibir en mano", 
    money(monto_neto_recibido), 
    delta=f"-{money(costos_pagados_al_inicio)} (Descuentos iniciales)",
    delta_color="inverse" if costos_pagados_al_inicio > 0 else "off"
)
c3.metric("Total pagado por el cliente", money(total_pagado_cliente))
c4.metric("Cuota promedio mensual", money(cuota_promedio))

st.markdown("---")
st.markdown(":material/problem: Evaluación de Riesgo e Inflación")
r1, r2, r3 = st.columns(3)
r1.metric("Semáforo de Endeudamiento", semaforo, f"Compromete el {pct(ratio)} de tu sueldo" if ingreso_usuario > 0 else "Ingresá tu sueldo en el menú izq.")
r2.metric("Costo Real Ajustado por Inflación", money(total_real), f"Ahorro licuado por inflación: {money(total_nominal - total_real)}")
r3.metric("Primera Cuota vs Última Cuota", f"{money(df.iloc[0]['Cuota total'])} / {money(df.iloc[-1]['Cuota total'])}")

st.markdown(":material/data_info_alert: Regulación BCRA: Cancelación Anticipada")
mes_libre_cancelacion = max(math.ceil(plazo_meses * 0.25), 6) # 25% del plazo o 180 días (6 meses)
st.info(f":material/info: **Tip de Ahorro Legal:** Si decidís adelantar pagos para cancelar el crédito completo antes de tiempo, los bancos suelen cobrarte una penalidad (aprox. 4% + IVA). Sin embargo, por norma del BCRA, si lo hacés **a partir de la cuota {mes_libre_cancelacion}**, la comisión es obligatoriamente **$0 (GRATIS)**.")

st.markdown(":material/download: Tabla de Amortización (Resumen)")
columnas_mostrar = ["Mes", "Capital", "Interés", "IVA", "Seguro", "Cuota total"]
st.dataframe(df[columnas_mostrar].head(12), width='stretch')

# Descargar CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Descargar Cronograma de Pagos Completo (CSV)",
    data=csv,
    file_name='cronograma_prestamo.csv',
    mime='text/csv',
)

# ============================================================
# 4. ESTRUCTURA COMPLETA Y TRAMPA DE LA TNA (WATERFALL)
# ============================================================
st.markdown("---")
st.markdown("## 4. Estructura Completa y Costo Real (CFT)")

total_capital = df["Capital"].sum()
total_interes = df["Interés"].sum()
total_iva = df["IVA"].sum() if "IVA" in df.columns else 0.0
total_seguro = df["Seguro"].sum() if "Seguro" in df.columns else 0.0

col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
col_a.metric("Capital Puro", money(total_capital))
col_b.metric("Intereses", money(total_interes))
col_c.metric("IVA (AFIP)", money(total_iva))
col_d.metric("Seguros", money(total_seguro))
col_e.metric("Comisión Bancaria", money(monto_comision_inicio))
col_f.metric("Sellos Provincial", money(monto_sellos_inicio))

st.markdown("---")
graf_col1, graf_col2 = st.columns(2)

with graf_col1:
    st.markdown(":material/speaker_notes: La Trampa de la TNA: Llegando al CFT")
    st.caption("Los bancos publicitan la TNA, pero tu bolsillo paga el CFT. Mirá cómo crecen los costos ocultos.")
    
    # Calcular incrementos para el gráfico de cascada
    diferencia_tea = tea_prin - tasa_ingresada
    diferencia_impuestos = cft_ea_prin - tea_prin

    fig_waterfall = go.Figure(go.Waterfall(
        name="Tasas", orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["TNA (Publicidad)", "Efecto Mensual (TEA)", "Seguros, IVA y Gastos", "CFT (Costo Real)"],
        textposition="outside",
        text=[f"{tasa_ingresada:.2f}%", f"+{diferencia_tea:.2f}%", f"+{diferencia_impuestos:.2f}%", f"{cft_ea_prin:.2f}% EA"],
        y=[tasa_ingresada, diferencia_tea, diferencia_impuestos, cft_ea_prin],
        connector={"line":{"color":"rgb(63, 63, 63)", "width":2, "dash":"dot"}},
        decreasing = {"marker":{"color":"#2eb85c"}},
        increasing = {"marker":{"color":"#e55353"}},
        totals = {"marker":{"color":"#f9b115"}}
    ))
    fig_waterfall.update_layout(showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
    st.plotly_chart(fig_waterfall, width='stretch')

with graf_col2:
    st.markdown(":material/percent: Evolución Mensual de tu Cuota")
    st.caption("Composición del pago a lo largo del tiempo (Sistema Francés)")
    
    fig_barras = go.Figure()
    fig_barras.add_trace(go.Bar(x=df["Mes"], y=df["Capital"], name="Capital", marker_color="#2eb85c"))
    fig_barras.add_trace(go.Bar(x=df["Mes"], y=df["Interés"], name="Interés", marker_color="#f9b115"))
    if total_iva > 0:
        fig_barras.add_trace(go.Bar(x=df["Mes"], y=df["IVA"], name="IVA", marker_color="#e55353"))
    if total_seguro > 0:
        fig_barras.add_trace(go.Bar(x=df["Mes"], y=df["Seguro"], name="Seguro", marker_color="#39f"))
        
    fig_barras.update_layout(barmode='stack', xaxis_title="Mes", yaxis_title="Monto ($)", margin=dict(t=30, b=20, l=20, r=20), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_barras, width='stretch')

# ============================================================
# 5. SIMULADOR UVA VS TASA FIJA
# ============================================================
st.markdown("---")
st.markdown("## 5. Análisis Avanzado: Tasa Fija vs. Préstamo UVA")
st.caption("Compará tu simulación actual a Tasa Fija contra el mismo préstamo indexado por inflación (UVA).")

col_u1, col_u2 = st.columns([1, 2])
with col_u1:
    tna_uva = st.number_input("TNA del préstamo UVA (%)", min_value=0.0, value=8.0, step=0.5)
with col_u2:
    st.info(f":material/rate_review: **Proyección de Inflación:** Se está utilizando la inflación anual del **{inflacion_anual_esperada}%** que configuraste en el menú lateral. El crédito UVA arranca con cuotas muy bajas, pero acompañan el ritmo inflacionario.")

tasa_mensual_uva = (tna_uva / 100.0) / 12.0
cuota_pura_uva_inicial = calcular_cuota(monto_prestamo, tasa_mensual_uva, plazo_meses)

evolucion_cuota_uva = []
evolucion_cuota_fija = []

for mes in range(1, plazo_meses + 1):
    # Asumimos que la cuota UVA aumenta de la mano con la inflación acumulada
    factor_ajuste_inflacion = (1 + inflacion_mensual_efectiva)**mes
    cuota_mes_uva_proyectada = cuota_pura_uva_inicial * factor_ajuste_inflacion
    evolucion_cuota_uva.append(cuota_mes_uva_proyectada)
    
    # Cuota fija de la simulación principal
    evolucion_cuota_fija.append(df.iloc[mes-1]['Cuota total'])

fig_uva = go.Figure()
fig_uva.add_trace(go.Scatter(x=list(range(1, plazo_meses + 1)), y=evolucion_cuota_fija, mode='lines', name='Cuota Tasa Fija', line=dict(color='#2eb85c', width=4)))
fig_uva.add_trace(go.Scatter(x=list(range(1, plazo_meses + 1)), y=evolucion_cuota_uva, mode='lines', name=f'Cuota UVA Ajustada', line=dict(color='#e55353', width=4, dash='dot')))

fig_uva.update_layout(
    title="Riesgo Inflacionario: Curva de Crecimiento de Cuotas",
    xaxis_title="Meses",
    yaxis_title="Monto de la Cuota ($)",
    hovermode="x unified",
    margin=dict(t=50, b=20, l=20, r=20),
    legend=dict(orientation="h", y=-0.2)
)
st.plotly_chart(fig_uva, width='stretch')

# ============================================================
# 6. MÓDULO COMPARADOR DE OTRAS ENTIDADES (EXPANDER DENTRO DEL MAIN)
# ============================================================
st.markdown("---")

with st.expander(":material/account_balance: Comparar con otras Instituciones Bancarias / Fintechs", expanded=False):
    st.markdown(":material/assured_workload: Comparador Multientidad con Regulación Argentina")
    st.caption("Compará hasta 3 alternativas aplicando exactamente la misma estructura de IVA, Sellos por provincia y Comisiones.")

    prestamos_comparativa = []
    col_bancos = st.columns(3)

    for i, col in enumerate(col_bancos, start=1):
        with col:
            st.subheader(f"Alternativa {i}")
            with st.container(border=True):
                nombre_entidad = st.text_input(f"Entidad {i}", value=f"Banco {chr(64 + i)}" if i < 3 else "Fintech C", key=f"comp_nombre_{i}")
                monto_comp = st.number_input(f"Monto Solicitado ($)", min_value=1.0, value=monto_prestamo, step=50000.0, key=f"comp_monto_{i}")
                plazo_comp = st.number_input(f"Plazo (meses)", min_value=1, max_value=240, value=int(plazo_meses), step=1, key=f"comp_plazo_{i}")
                tna_comp = st.number_input(f"TNA (%)", min_value=0.0, value=50.0 + (i-1)*5, step=0.5, key=f"comp_tna_{i}")
                
                prov_comp = st.selectbox(f"Jurisdicción", list(JURISDICCIONES_CONFIG.keys()), index=0, key=f"comp_prov_{i}")
                comision_pct_comp = st.number_input(f"Comisión Inicial (%)", min_value=0.0, max_value=20.0, value=3.0 if i==1 else 1.5, step=0.5, key=f"comp_comision_{i}")
                seguro_pct_comp = st.number_input(f"Seguro Vida Mensual (% s/saldo)", min_value=0.0, max_value=5.0, value=0.15, step=0.05, key=f"comp_seguro_{i}")
                aplica_iva_comp = st.checkbox("Aplica IVA (21% s/int)", value=True, key=f"comp_iva_{i}")

                alicuota_sellos = JURISDICCIONES_CONFIG[prov_comp]["sellos"]
                gasto_sellos = monto_comp * (alicuota_sellos / 100.0)
                gasto_comision = monto_comp * (comision_pct_comp / 100.0)
                costo_inicial_total = gasto_sellos + gasto_comision
                monto_neto_mano = monto_comp - costo_inicial_total

                t_mensual_comp = tasa_mensual_desde_tna(tna_comp)
                cuota_pura_comp = calcular_cuota(monto_comp, t_mensual_comp, plazo_comp)
                
                saldo_d = monto_comp
                total_int = 0.0
                total_cuotas_acum = 0.0
                flujos_caja = [monto_neto_mano]

                for m in range(1, plazo_comp + 1):
                    int_m = saldo_d * t_mensual_comp
                    cap_m = saldo_d if m == plazo_comp else max(0.0, min(saldo_d, cuota_pura_comp - int_m))
                    
                    iva_m = (int_m * 0.21) if aplica_iva_comp else 0.0
                    seg_m = saldo_d * (seguro_pct_comp / 100.0)
                    cuota_total_m = cap_m + int_m + iva_m + seg_m
                    
                    total_int += int_m
                    total_cuotas_acum += cuota_total_m
                    flujos_caja.append(-cuota_total_m)
                    saldo_d = max(0.0, saldo_d - cap_m)

                try:
                    irr_mensual_comp = npf.irr(flujos_caja)
                    cft_ea_comp = ((1 + irr_mensual_comp) ** 12 - 1) * 100 if irr_mensual_comp is not None else 0.0
                except:
                    cft_ea_comp = 0.0

                total_pagado_general = total_cuotas_acum + costo_inicial_total

                prestamos_comparativa.append({
                    "Entidad": nombre_entidad,
                    "En Mano (Neto)": monto_neto_mano,
                    "Gastos Iniciales": costo_inicial_total,
                    "Cuota Promedio": total_cuotas_acum / plazo_comp,
                    "Total Intereses": total_int,
                    "CFT (Efectivo Anual)": cft_ea_comp
                })

    st.markdown("---")
    st.markdown(":material/table_chart: Tabla Comparativa de Propuestas")
    df_comp = pd.DataFrame(prestamos_comparativa)

    st.dataframe(
        df_comp,
        column_config={
            "En Mano (Neto)": st.column_config.NumberColumn(format="$%,.2f"),
            "Gastos Iniciales": st.column_config.NumberColumn(format="$%,.2f"),
            "Cuota Promedio": st.column_config.NumberColumn(format="$%,.2f"),
            "Total Intereses": st.column_config.NumberColumn(format="$%,.2f"),
            "CFT (Efectivo Anual)": st.column_config.NumberColumn(format="%.2f%%"),
        },
        hide_index=True,
        width='stretch'
    )

     # RECOMENDACIÓN DE LA MEJOR OPCIÓN
    if not df_comp.empty and df_comp["CFT (Efectivo Anual)"].sum() > 0:
            mejor_opcion = df_comp.loc[df_comp["CFT (Efectivo Anual)"].idxmin()]
            st.success(
                f"🏆 **Recomendación por Costo Financiero Total (CFT):** "
                f"La opción más económica es **{mejor_opcion['Entidad']}** con un CFT de **{mejor_opcion['CFT (Efectivo Anual)']:.2f}% EA** "
                f"(Cuota promedio: **{money(mejor_opcion['Cuota Promedio'])}**)."
            )
    
            # GRÁFICO COMPARATIVO VISUAL
            fig_comp = go.Figure()
    
            fig_comp.add_trace(go.Bar(
                x=df_comp["Entidad"], 
                y=df_comp["En Mano (Neto)"], 
                name="Efectivo Recibido (Neto)",
                marker_color="#2eb85c"
            ))
            
            fig_comp.add_trace(go.Bar(
                x=df_comp["Entidad"], 
                y=df_comp["Total Intereses"], 
                name="Total Intereses Pagados",
                marker_color="#f9b115"
            ))
    
            fig_comp.add_trace(go.Bar(
                x=df_comp["Entidad"], 
                y=df_comp["Gastos Iniciales"], 
                name="Gastos e Impuestos Iniciales",
                marker_color="#e55353"
            ))
    
            fig_comp.update_layout(
                title="Comparativa Visual: Dinero Recibido vs. Intereses y Costos",
                barmode="group",
                yaxis_title="Monto ($)",
                margin=dict(t=40, b=20, l=20, r=20),
                legend=dict(orientation="h", y=-0.2)
            )
    
            st.plotly_chart(fig_comp, width='stretch') 