
# ───────────────────────────────────────────────────────────────────────────────
# CBD_MDE_2025 — Data Cleaning & Preprocessing Pipeline
#
# Research question:
#   What are the specific logistics needs within CBDs, and how can alignment
#   of supply and demand inform UCC implementation in LEZs?
#
# This script cleans and preprocesses the survey data for downstream FAMD,
# clustering, correspondence analysis, and visualization.
# ───────────────────────────────────────────────────────────────────────────────

# 1. Initial Setup
#    1.1 Import libraries
import pandas as pd
import numpy as np
import unicodedata
import re
from pathlib import Path
from pandas.api.types import CategoricalDtype
from sklearn.preprocessing import MultiLabelBinarizer
# (prince, KMeans, silhouette_score, matplotlib will be used later)

#    1.2 Locate project root & raw data
project_root = Path.cwd().resolve().parents[1]
data_file    = project_root / "data" / "raw" / "03. Resultados_encuesta_logistica_ZUAP_20220927_v1.xlsx"
print("Project root:", project_root)
print("Data file:", data_file)

# load the actual responses
df_raw = pd.read_excel(data_file, sheet_name="Respuestas")
print("Raw shape:", df_raw.shape)
print(df_raw.columns.tolist())
print(df_raw.head())

# 2. Load & Rename Raw Survey
#    2.1 Read Excel, strip whitespace, lowercase headers, parse timestamps
def dataframe_cleaning(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower()
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

    if 'marca temporal' in df.columns:
        df['marca temporal'] = pd.to_datetime(df['marca temporal'], errors='coerce')
    df = df.drop_duplicates()

    #    2.2 Drop non‐informative Spanish‐named columns
    drop_cols = [
        # Database flag
        'db',
        # “Go to end of survey.”
        'ir al fin de la encuesta.',
        
        # “By type of load, select up to 3”
        'de acuerdo con el tipo de carga que distribuye su empresa, indique máximo 3 tipos en el siguiente listado:',
        # Origin in Valle de Aburrá?
        '¿el origen de la mercancía que transporta es el valle de aburrá?',
        # Municipality of origin
        'por favor, indique el municipio:',
        # Daily deliveries to downtown Medellín
        'por favor, indique cuántas entregas hace en el centro de medellín al día:',
        # Daily number of establishments served downtown
        'por favor, indique el número de establecimientos que surte en el centro de medellín a diario:',
        # Daily orders received for downtown
        '¿cuántos pedidos recibe su empresa diariamente que tienen como destino el centro de medellín?',
        # Fleet composition by fuel type
        'por favor indique la cantidad de vehículos con combustión a diésel (acpm) con los que cuenta su empresa:',
        'por favor indique la cantidad de vehículos con combustión a gasolina con los que cuenta su empresa:',
        'por favor indique la cantidad de vehículos con combustión a gas natural vehicular (gnv) con los que cuenta su empresa:',
        'por favor indique la cantidad de vehículos con motor eléctrico con los que cuenta su empresa:',
        # Vehicle age ranges
        'por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos anteriores a 1990]',
        'por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos entre 1991 y 2000]',
        'por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos entre 2001 y 2010]',
        'por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos entre 2011 y 2015]',
        'por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos del 2016 en adelante]',
        # Fuel/energy economy metrics
        '¿cuánto es el rendimiento en galones/kilómetro, de sus vehículos a acpm?',
        '¿cuánto es el rendimiento en galones/kilómetro, de sus vehículos a gasolina?',
        '¿cuánto es el rendimiento en metros cúbicos/kilómetro, de sus vehículos a gnv?',
        '¿cuánto es el rendimiento kilowatt-hora, de sus vehículos eléctricos?',
        # Cost and driver-hours metrics
        '¿cuánto es el costo total por movilizar un camión cargado hacia el centro de medellín?',
        '¿cuántas horas al volante permanece durante un turno de reparto una/un conductora/or en su empresa?',
        # Driver‐road‐user relationship (1=very complex…5=very adequate)
        'de acuerdo con la siguiente escala, donde 1 es "muy compleja" y 5 es "muy adecuada" ¿cómo considera la relación de sus conductores con los demás actores viales (peatones, ciclistas, conductores, transporte público) en el espacio público de la zuap?',
        # In‐company physical‐activity programs
        '¿al interior de su empresa se realizan actividades que promuevan la actividad física entre sus calaboradoras/es?',
        '¿qué actividades se realizan?',
        '¿cuántas veces por semana se realizan actividades para promover la actividad física?',
        # Awareness of Yellow Zone decree
        '¿conoce usted el decreto no 1790 de noviembre 20 de 2012 (decreto de zona amarilla o de cargue y descargue en el centro de la ciudad)?'
    ]
    df = df.drop(columns=drop_cols, errors='ignore')

    #    2.3 Rename remaining to concise English
    rename_map = {
        'marca temporal': 'timestamp',
        'nombre de la empresa': 'company_name',
        'correo electrónico': 'email',
        'dirección de la empresa': 'est_address',
        'teléfono de contacto': 'contact_phone',
        'por favor indique el número de colaboradores que tiene su empresa o comercio': 'employees',
        '¿en su empresa o comercio cuentan con colaboradoras mujeres?': 'has_female_employees',
        'por favor indique el número de mujeres que trabajan en su empresa o comercio': 'female_employees',
        'porcentaje mujeres': 'female_percentage',
        'de sus empleadas mujeres, ¿cuántas hacen parte de la cadena de distribución del negocio (conducen, reparten domicilios, acompañan las entregas, etc.)?': 'female_in_distribution',
        '% mujeres en la distribución': 'pct_female_in_distribution',
        'de las mujeres vinculadas a la cadena logística de su empresa o comercio ¿cuántas están vinculadas por contrato laboral?': 'female_with_contract',
        '% mujeres vinculadas': 'pct_female_with_contract',
        'entre sus colaboradoras mujeres, alguna(s) se identifica(n) con los siguientes grupos poblacionales:': 'female_population_groups',
        '¿acompañan y/o apoyan el proceso formativo de las mujeres que hacen parte de la cadena logística?': 'female_support_roles',
        'por favor, indique dentro de la siguientes categorías, cuál se relaciona con la actividad realizada en su comercio:': 'economic_activity',
        'de acuerdo al listado señale en orden de importancia las 3 principales actividades comerciales que se desarrollan en su establecimiento:': 'top_3_activities',
        'productos principales': 'main_products',
        '¿su establecimiento cuenta con espacio de bodega o almacenamiento de mercancías o productos?': 'has_warehouse_space',
        '¿con cuántos espacios de bodega cuenta?': 'warehouse_count',
        '¿en qué piso se ubica(n) la(s) bodegas que sirven a su empresa o comercio?': 'warehouse_floor',
        'por favor, indique el área de la bodega que sirve a su comercio en metros cuadrados:': 'warehouse_area_m2',
        'por favor, indique la altura en metros de la bodega que sirve a su comercio:': 'warehouse_height_m',
        '¿el(los) espacio(s) de bodega están ubicados al interior de la zuap?': 'warehouse_within_zuap',
        '¿en qué municipio se encuentra ubicada la bodega que sirve a su comercio?': 'warehouse_municipality',
        'por favor, indique el tipo de bodega con la que cuenta:': 'warehouse_type',
        'por favor, seleccione los días en los cuales recibe materiales, materias primas o productos:': 'supply_day',
        '¿cuántas veces por semana abastece su establecimiento?': 'supply_frequency_per_week',
        'por favor, indique los horarios durante los cuales realiza las actividades de cargue y descargue de las mercancías:': 'loading_schedule',
        'por favor, indique la forma en la que ingresa la mercancía a su comercio o área de bodega:': 'unloading_method',
        'en una escala de 1 a 5, donde 1 es "muy inseguro" y 5 "muy seguro", ¿considera usted que el proceso de cargue y descargue de mercancías en camión, carro o motocicleta es?': 'safety_perception_motorized',
        'en una escala de 1 a 5, donde 1 es "muy inseguro" y 5 "muy seguro", ¿considera usted que el proceso de cargue y descargue de mercancías en bicicleta es?': 'safety_perception_bicycle',
        '¿el establecimiento o bodega posee alguno de los siguientes elementos para el cargue y descargue de mercancías?': 'loading_equipment',
        '¿qué medio realiza para el envío de sus artículos a domicilio?': 'delivery_modes',
        '¿cuántos domicilios realiza a diario su establecimiento?': 'daily_delivery_count',
        '¿qué medio realiza para el envío de sus ventas por internet?': 'online_delivery_modes',
        '¿cuántos envíos de artículos vendidos por internet realiza a diario su establecimiento?': 'daily_online_delivery_count'
    }
    return df.rename(columns=rename_map)

df_clean = dataframe_cleaning(data_file)
print("df_clean shape:", df_clean.shape)
print(df_clean.columns.tolist())
print(df_clean.head())
print("original info:", df_clean.info())

#check repeated results in columns
print("Checking unique values in each column:")
for col in df_clean.columns[6:]:
    if col in df_clean.columns:
        uniques = df_clean[col].unique()
        print(f"{col} ({len(uniques)} unique):")
        print(uniques)
        print("-" * 40)
    else:
        print(f"{col}: [Column not found in df_clean]")
        print("-" * 40)

# 3. Initial Type Adjustment
#    3.1 Single‐label categorical → category
categorical__nominal_cols = [
    "main_products", "has_warehouse_space", "warehouse_within_zuap",
    "warehouse_municipality", "warehouse_type", "economic_activity","female_support_roles"
]
for col in categorical__nominal_cols:
    df_clean[col] = df_clean[col].astype("category")

#    3.2 Multi‐label text fields → string (to explode later)
multi_col_text = ["top_3_activities","supply_day","loading_schedule",
              "unloading_method","loading_equipment",
              "delivery_modes","online_delivery_modes","female_population_groups"]
for col in multi_col_text:
    df_clean[col] = df_clean[col].astype(str)

#    3.3 Ordinal factors
#        3.3.1 Floors as ordered categories
floor_cats = sorted(df_clean["warehouse_floor"].dropna().unique(), key=float)
df_clean["warehouse_floor"] = df_clean["warehouse_floor"]\
    .astype(CategoricalDtype(categories=floor_cats, ordered=True))
#        3.3.2 Likert scales 1–5
likert = CategoricalDtype(categories=[1,2,3,4,5], ordered=True)
for col in ["safety_perception_motorized","safety_perception_bicycle"]:
    df_clean[col] = df_clean[col].astype(likert)

#    3.4 Numeric counts & measures
num_cols = ["warehouse_count","warehouse_area_m2","warehouse_height_m",
            "daily_delivery_count","daily_online_delivery_count",
            "employees","female_employees",
            "female_in_distribution","female_with_contract"]
for col in num_cols:
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

#    3.5 Percentages → float
for col in ["female_percentage","pct_female_in_distribution","pct_female_with_contract"]:
    df_clean[col] = df_clean[col].astype(float)

#    3.6 Supply frequency → extract numeric & ordered
freq_map = {
    "1 vez por semana":1, "2":2, "5":5, "6 o más":6,
    "La periodicidad es quincenal":2, "La periodicidad es mensual":1
}
df_clean["supply_frequency_num"] = (
    df_clean["supply_frequency_per_week"]
      .map(freq_map).fillna(0).astype(int)
      .astype(CategoricalDtype(categories=[1,2,5,6], ordered=True))
)

#    3.7 Remaining text as category
descriptive_cols = ["email", "company_name", "est_address", "contact_phone"]

for col in descriptive_cols:
    df_clean[col] = df_clean[col].astype("category")

print("df_clean shape:", df_clean.shape)
print(df_clean.columns.tolist())
print(df_clean.head())
print("New df info:", df_clean.info())


# Check new unique values in each column from the 6th column onward
print("\nUnique values in each column (from index 6):")
for col in df_clean.columns[6:]:
    uniques = df_clean[col].dropna().unique()
    print(f"{col} ({len(uniques)} unique):")
    print(uniques)
    print("-" * 40)


# 4. Normalize & Translate Text
#    4.1 Helper: lowercase, strip accents
def normalize_text(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # strip accents
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s

#    4.2 warehouse_within_zuap
YESNO = {"sí":"yes","si":"yes","no":"no","no aplica":pd.NA}

# Normalize and map warehouse_within_zuap values
df_clean["warehouse_within_zuap"] = (
    df_clean["warehouse_within_zuap"]
      .map(normalize_text)
      .replace(YESNO)
      .astype("category")
)
# Show unique values for verification
print("warehouse_within_zuap (unique):", df_clean["warehouse_within_zuap"].unique())

# 4.3 Clean main_products without collapsing to top-N: preserve each row’s unique value
df_clean["main_products"] = (
    df_clean["main_products"]
      .map(normalize_text)          # normalize case, remove accents, trim
      .astype("category")           # cast to categorical, retaining all unique levels
)

print("Normalized main_products (unique):", df_clean["main_products"].unique())

# 4.4 Main categories exactly as they appear in original data
main_cats = ["Venta al detalle", "Fabricante", "Proveedor", "Ventas por internet"]

def split_econ_preserve_caps(x):
    if pd.isna(x):
        return pd.Series([pd.NA, pd.NA, pd.NA])
    
    # Step 1: Find matching main category (case-sensitive match)
    main = next((m for m in main_cats if x.startswith(m)), None)
    if main is None:
        return pd.Series([x, pd.NA, pd.NA])  # fallback
    
    # Step 2: Strip out main part and work with the rest
    rest = x[len(main):].strip()
    if not rest:
        return pd.Series([main, pd.NA, pd.NA])
    
    # Step 3: Use regex to find segments that start with uppercase (incl. accents)
    parts = re.findall(r'([A-ZÁÉÍÓÚÑ][^A-ZÁÉÍÓÚÑ]*)', rest)
    sub1 = parts[0].strip() if len(parts) >= 1 else pd.NA
    sub2 = parts[1].strip() if len(parts) >= 2 else pd.NA
    
    return pd.Series([main, sub1, sub2])

# Apply the split (no normalization!)

# ensure economic_activity is treated as plain strings for the split
econ_split = df_clean["economic_activity"].astype(str).apply(split_econ_preserve_caps)

df_clean[["econ_main", "econ_sub1", "econ_sub2"]] = econ_split

for col in ["econ_main", "econ_sub1", "econ_sub2"]:
    df_clean[col] = df_clean[col].astype("category")

# Verify outcome
print("Last df_clean",df_clean[["economic_activity", "econ_main", "econ_sub1", "econ_sub2"]].head())

# add step to 
    #Translate the df_clean DataFrame
# add step to 
    #Translate the df_clean DataFrame

# 7. (Stub) FAMD in R — export df_clean for factor analysis

# 8. (Stub) Clustering on FAMD coordinates

# 9. (Stub) Build contingency & perform CA

# 10. (Stub) Visualize & interpret

# ───────────────────────────────────────────────────────────────────────────────
# End of preprocessing pipeline — df_clean is now ready for analysis.
# ───────────────────────────────────────────────────────────────────────────────
