

https://github.com/user-attachments/assets/50a855eb-d34d-452a-beaa-21f46049d5f7

Entiende tu Préstamo: Advanced Argentine Loan Simulator:
Descripción GeneralEntiende tu Préstamo es una aplicación analítica de grado experto desarrollada en Python (Streamlit) para modelar,
proyectar y auditar estructuras de financiamiento en el mercado argentino.
El ecosistema financiero en Argentina presenta un alto grado de complejidad debido a la alta inflación, la multiplicidad de regímenes tributarios provinciales y la pronunciada brecha entre la Tasa Nominal Anual (TNA) publicitaria y el Costo Financiero Total (CFT)  real.
Esta herramienta resuelve dicha asimetría de información procesando flujos de caja reales.
Utiliza el sistema de amortización francés e incorpora un motor fiscal que mapea las 24 jurisdicciones del país.
Stack TecnológicoFrontend & UI: streamlit (Renderizado reactivo y gestión del estado).
Data Processing: pandas (Estructuración de cronogramas de pago y tablas comparativas). Financial Mathematics: numpy-financial (Cálculo de cuotas base con pmt y derivación de tasas efectivas mediante la TIR de flujos de caja con irr).
Data Visualization: plotly.graph_objects (Gráficos interactivos, Waterfall charts y barras apiladas).
Arquitectura Financiera y Features Principales1. Motor de Cálculo del CFT (Costo Financiero Total)A diferencia de calculadoras básicas que solo aplican multiplicadores sobre la TNA, este proyecto construye un array de flujos de caja descontados (Cash Flows).
1. Desembolso Neto: Calcula el capital real recibido en mano deduciendo gastos iniciales (Comisiones de otorgamiento e Impuesto a los Sellos). Egresos Mensuales: Proyecta la cuota pura (Capital + Interés) y le adiciona de forma iterativa el IVA (21% sobre intereses) y el Seguro de Vida (sobre el saldo deudor pendiente).  
Derivación de la Tasa: Aplica la función npf.irr() sobre estos flujos para obtener la Tasa Interna de Retorno mensual, anualizándola luego para exponer el CFT Efectivo Anual exacto.  
2. Motor Tributario y Regulatorio FederalEl simulador cuenta con un diccionario de configuración (JURISDICCIONES_CONFIG) que parametriza las alícuotas impositivas de las 23 provincias y CABA.
Impuesto a los Sellos: Deducción porcentual automática sobre el capital inicial según la provincia seleccionada.  Ingresos Brutos (IIBB): Cálculo informativo de la carga impositiva que absorbe el banco (impactando indirectamente en la tasa).  
Compliance BCRA (Cancelación Anticipada): El sistema alerta automáticamente al usuario sobre la normativa del Banco Central de la República Argentina, indicando el mes exacto (a partir del 25% del plazo original o 180 días) donde la penalidad por pre-cancelación se vuelve del 0%.
3. Simulador de Riesgo Inflacionario (Tasa Fija vs. UVA)Para abordar el contexto macroeconómico argentino, la aplicación incluye un módulo de Stress Testing inflacionario.  Toma la inflación anual esperada (input del usuario) y la convierte en inflación mensual efectiva.  Proyecta una curva de amortización indexada por inflación (UVA), mostrando cómo una cuota inicial baja escala exponencialmente frente a un escenario de cuotas nominales fijas.  Analiza la sostenibilidad de la deuda descontando la inflación, comparando el monto nominal total pagado contra su valor real presente.  
4. Visualización de Datos AvanzadaThe TNA Trap (Gráfico de Cascada): Utiliza un Waterfall chart de Plotly para mostrar el puente entre la TNA y el CFT. El gráfico desglosa visualmente cómo la capitalización mensual (TEA), los impuestos (IVA/Sellos) y los seguros inflan el costo del crédito.  
Composición de Cuota: Gráfico de barras apiladas (Stacked Bar Chart) que ilustra el comportamiento del Sistema Francés: alta carga de intereses en las primeras cuotas que decrece a favor de la amortización de capital en las cuotas finales.  
5. Comparador Multientidad (Benchmarking)Permite instanciar un DataFrame comparativo con hasta 3 alternativas de crédito diferentes (Bancos vs. Fintechs). Homologa las variables (TNA, comisiones, plazos, impuestos locales) para rankear las opciones en base al CFT Efectivo Anual y el capital neto recibido.  
Estructura del Código: El script principal (1_main-base.py) está dividido en las siguientes capas lógicas:  Configuración de Constantes: Diccionarios de tasas provinciales y setup de la página.  Core Functions: Funciones puras para matemática financiera (tasa_mensual_desde_tna, calcular_cuota, ratio_endeudamiento_total).  Engine de Costos (configurar_costo, calcular_importe_costo): Sistema modular que permite encender, apagar o modificar la base imponible de cualquier cargo (ej. cobrar sobre saldo deudor vs. capital inicial).
UI & Sidebar: Recolección de variables macroeconómicas e inputs del usuario.  Main Loop de Amortización: Generación de la tabla mes a mes y los flujos de caja.  Módulos de Visualización (Plotly) y Exportación (CSV).  
Instalación y Despliegue LocalClonar el repositorio:Bashgit clone [https://github.com/tu-usuario/entiende-tu-prestamo.git](https://github.com/wgekko/app_analisis_prestamos.git)
cd app_analisis_prestamos

Crear un entorno virtual (Recomendado):Bashpython -m venv venv

source venv/bin/activate  # En Windows: venv\Scripts\activate

Instalar dependencias:Bashpip install streamlit pandas numpy-financial plotly

Ejecutar la aplicación:Bashstreamlit run main.py

La aplicación se abrirá automáticamente en tu navegador por defecto en http://localhost:8501.

si desean personal colores, estilos y tipo de letra. 

se debe crear una carpeta .streamlit y adjunto el una carpeta con el mismo nombre con dos archivos alternativos


⚠️ Disclaimer FinancieroE ste proyecto es de código abierto y tiene fines estrictamente educativos y de análisis de datos. Los cálculos impositivos y regulatorios son estimaciones basadas en alícuotas estándar y no constituyen asesoramiento financiero, legal ni contable profesional. Las tasas y normativas del BCRA o entidades provinciales están sujetas a modificaciones sin previo aviso.

video demo 

https://github.com/user-attachments/assets/f48eed73-e1a2-4414-b9d1-12647f6ac809



