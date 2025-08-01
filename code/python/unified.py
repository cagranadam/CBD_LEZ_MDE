#!/usr/bin/env python
# coding: utf-8
"""
CBD_MDE_2025 — Unified Data-Cleaning Pipeline for FAMD-Clustering-CA Analysis
--------------------------------------------------------------------------------
This script creates a unified pipeline that outputs tidy DataFrames ready for:
1. Factor Analysis of Mixed Data (FAMD) in R
2. K-means Clustering analysis
3. Correspondence Analysis (CA)

Research Question:
What are the specific logistics needs within Central Business Districts (CBDs), 
and how can the alignment of supply and demand among urban establishments inform 
the strategic implementation of Urban Consolidation Centers (UCCs) in Low Emission 
Zones (ZUAP) based on survey results?

Key Outputs:
- df_clean.csv: Basic cleaned data with proper typing
- translated_survey.csv: Data with English translations
- survey_for_famd.csv: One-hot encoded data ready for FAMD
- r_ready_data.csv: R-optimized format for multivariate analysis

Design Principles:
- Preserve all variables needed for FAMD (mixed data types)
- Create proper categorical encodings for CA
- Generate dummy variables for clustering algorithms
- Maintain translation mappings for international research
- Support logistics needs assessment and UCC implementation analysis
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Optional, Union, Dict, List
import os

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype

###############################################################################
# 1.  CONFIGURATION                                                          ##
###############################################################################

# ── locate repo root (assumes script lives two levels below project root) ──
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "03. Resultados_encuesta_logistica_ZUAP_20220927_v1.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "data" / "intermediate" / "df_clean.csv"

# --- Comprehensive Translation Dictionaries ---
# Imported from v3_data_cleaning.py to ensure consistency across analysis pipeline

# Days of the week in Spanish → English
DAY_EN = {
    'Lunes': 'Monday',
    'Martes': 'Tuesday', 
    'Miércoles': 'Wednesday',
    'Jueves': 'Thursday',
    'Viernes': 'Friday',
    'Sábado': 'Saturday',
    'Domingo': 'Sunday'
}

# Delivery/transport modes in Spanish → English
DMODE_EN = {
    'Caminando / Foot': 'Walking/Foot',
    'Bicicleta / Bicycle': 'Bicycle',
    'Motocicleta / Motorcycle': 'Motorcycle',
    'Carro particular / Private car': 'Private car',
    'Camioneta / Pick-up truck': 'Pick-up truck',
    'Vehículo de carga liviana / Small delivery vehicle': 'Small delivery vehicle',
    'Vehículo de carga mediana / Medium delivery vehicle': 'Medium delivery vehicle',
    'Vehículo de carga pesada / Heavy delivery vehicle': 'Heavy delivery vehicle',
    'Diablito / Dolly': 'Dolly',
    'Carro de cargas / Cargo cart': 'Cargo cart',
    'Servicio de Transporte Público / Public transport': 'Public transport'
}

# Unloading methods in Spanish → English
UNLOAD_EN = {
    'Acera / Sidewalk': 'Sidewalk',
    'Carril de tráfico / Traffic lane': 'Traffic lane',
    'Carril de estacionamiento / Parking lane': 'Parking lane',
    'Zona de descargue / Dedicated unloading zone': 'Dedicated unloading zone',
    'Espacio privado / Private space': 'Private space',
    'Calle cerrada / Closed street': 'Closed street'
}

# Equipment types in Spanish → English
EQUIP_EN = {
    'Montacargas / Forklift': 'Forklift',
    'Carretilla / Cart': 'Cart',
    'Grúa / Crane': 'Crane',
    'Plataforma hidráulica / Hydraulic platform': 'Hydraulic platform',
    'Correas transportadoras / Conveyor belts': 'Conveyor belts',
    'Ascensor / Elevator': 'Elevator',
    'Escalera mecánica / Escalator': 'Escalator',
    'Rampa / Ramp': 'Ramp',
    'Escalera / Stairs': 'Stairs',
    'Diablito / Dolly': 'Dolly'
}

# Population groups in Spanish → English
GROUP_EN = {
    'Adulto mayor / Senior citizen': 'Senior citizen',
    'Estudiante / Student': 'Student',
    'Habitante de calle / Homeless person': 'Homeless person',
    'Persona con discapacidad / Person with disability': 'Person with disability',
    'Población LGBTI / LGBTI population': 'LGBTI population',
    'Trabajador informal / Informal worker': 'Informal worker',
    'Turista / Tourist': 'Tourist',
    'Vendedor ambulante / Street vendor': 'Street vendor'
}

# Complete column rename mapping for Spanish → English
UNIFIED_RENAME_MAP = {
    'Correo electrónico': 'email',
    'Nombre del establecimiento': 'establishment_name',
    'Dirección': 'address',
    'Barrio': 'neighborhood',
    'Teléfono': 'phone',
    'Tipo de establecimiento': 'establishment_type',
    'Descripción otros': 'establishment_type_other',
    'Pisos del establecimiento': 'floors',
    '¿Cuántos empleados?': 'employees',
    'Días de atención al público': 'service_days',
    'Horario de apertura': 'opening_hours',
    'Horario de cierre': 'closing_hours',
    '¿Recibe algún tipo de mercancía?': 'receives_goods',
    'Frecuencia de recepción de mercancías': 'supply_frequency',
    'Día de la semana de abastecimiento': 'supply_week',
    'Hora de recepción': 'supply_hour',
    'Modo de transporte utilizado para abastecimiento': 'supply_mode',
    'Lugar donde descarga la mercancía': 'supply_unloading',
    'Equipos necesarios para el manejo de mercancías': 'supply_equipment',
    '¿Realiza algún tipo de despacho/envío?': 'dispatches_goods',
    'Frecuencia de envío de mercancías': 'dispatch_frequency',
    'Día de la semana de despacho': 'dispatch_week',
    'Hora de despacho': 'dispatch_hour',
    'Modo de transporte utilizado para despacho': 'dispatch_mode',
    'Lugar donde carga la mercancía': 'dispatch_loading',
    'Equipos necesarios para el despacho de mercancías': 'dispatch_equipment',
    'Grupos poblacionales que atiende': 'served_groups',
    'Productos o servicios disponibles': 'products_services',
    'Comentarios adicionales': 'additional_comments',
    'Latitud': 'latitude',
    'Longitud': 'longitude'
}

# Multi-label field mappings for comprehensive translation
MAPS = {
    'service_days': DAY_EN,
    'supply_week': DAY_EN,
    'dispatch_week': DAY_EN,
    'supply_mode': DMODE_EN,
    'dispatch_mode': DMODE_EN,
    'supply_unloading': UNLOAD_EN,
    'dispatch_loading': UNLOAD_EN,
    'supply_equipment': EQUIP_EN,
    'dispatch_equipment': EQUIP_EN,
    'served_groups': GROUP_EN
}

# ── Analysis constants used in plotting functions (legacy support) ──
ESTABLISHMENT_TYPES = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
TRANSPORT_MODES = ['camión', 'motocicleta', 'bicicleta', 'carreta', 'particular']
UNLOADING_LOCATIONS = ['sobre la vía', 'sobre el andén', 'bahía', 'internamente', 'vías aledañas', 'parqueadero']
WEEKDAYS_ES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
WEEKDAYS_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Translation mappings for common categories
ESTABLISHMENT_TRANSLATIONS = {
    'Proveedor': 'Supplier', 
    'Venta al detalle': 'Retailer', 
    'Fabricante': 'Manufacturer', 
    'Ventas por internet': 'E-commerce'
}

TRANSPORT_TRANSLATIONS = {
    'bicicleta': 'Bicycle', 
    'camión': 'Truck', 
    'carreta': 'Handcart', 
    'motocicleta': 'Motorcycle', 
    'particular': 'Private Vehicle'
}

LOCATION_TRANSLATIONS = {
    'sobre la vía': 'On the road', 
    'sobre el andén': 'On the sidewalk', 
    'bahía': 'Loading/unloading zone',
    'internamente': 'Establishment facilities', 
    'vías aledañas': 'Nearby roads', 
    'parqueadero': 'Parking lot'
}

###############################################################################
# 2.  TRANSLATION AND MULTI-LABEL PROCESSING FUNCTIONS                      ##
###############################################################################

def translate_multi(text, mapping_dict):
    """
    Translate multi-label text fields using comprehensive mapping dictionaries.
    
    Parameters:
    -----------
    text : str or nan
        Input text containing multiple labels separated by commas/semicolons
    mapping_dict : dict
        Translation mapping for the specific field
        
    Returns:
    --------
    str or nan
        Translated text with same delimiters, or original if no mapping found
    """
    if pd.isna(text) or text == '':
        return text
    
    # Handle multiple separators (comma, semicolon)
    separators = [', ', '; ', ',', ';']
    
    for sep in separators:
        if sep in str(text):
            items = [item.strip() for item in str(text).split(sep)]
            translated_items = []
            
            for item in items:
                if item in mapping_dict:
                    translated_items.append(mapping_dict[item])
                else:
                    translated_items.append(item)  # Keep original if not found
            
            return sep.join(translated_items)
    
    # Single item case
    text_str = str(text).strip()
    return mapping_dict.get(text_str, text_str)


def translate_all_multi_labels(df):
    """
    Apply comprehensive translations to all multi-label fields in the DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with renamed columns (English names)
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with translated multi-label fields
    """
    df_translated = df.copy()
    
    # Apply translations to each multi-label field
    for column, mapping_dict in MAPS.items():
        if column in df_translated.columns:
            df_translated[column] = df_translated[column].apply(
                lambda x: translate_multi(x, mapping_dict)
            )
    
    return df_translated


def create_one_hot_encoding(df, column, mapping_dict, prefix=None):
    """
    Create one-hot encoded columns for multi-label categorical data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    column : str
        Column name to encode
    mapping_dict : dict
        Mapping dictionary for the column
    prefix : str, optional
        Prefix for new column names
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with one-hot encoded columns added
    """
    if column not in df.columns:
        return df
    
    df_encoded = df.copy()
    prefix = prefix or column
    
    # Get all possible values from mapping
    all_values = list(mapping_dict.values())
    
    # Create binary columns for each possible value
    for value in all_values:
        col_name = f"{prefix}_{value.replace(' ', '_').replace('/', '_').lower()}"
        df_encoded[col_name] = df_encoded[column].apply(
            lambda x: 1 if pd.notna(x) and value in str(x) else 0
        )
    
    return df_encoded


def prepare_famd_dataset(df):
    """
    Prepare dataset for Factor Analysis of Mixed Data (FAMD) in R.
    
    This function:
    1. Applies comprehensive translations
    2. Creates one-hot encodings for multi-label fields
    3. Ensures proper data types for mixed analysis
    4. Handles missing values appropriately
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned DataFrame with English column names
        
    Returns:
    --------
    pd.DataFrame
        FAMD-ready dataset with proper encodings
    """
    # Start with translated data
    df_famd = translate_all_multi_labels(df)
    
    # Create one-hot encodings for multi-label fields
    multi_label_fields = [
        'service_days', 'supply_week', 'dispatch_week',
        'supply_mode', 'dispatch_mode', 
        'supply_unloading', 'dispatch_loading',
        'supply_equipment', 'dispatch_equipment',
        'served_groups'
    ]
    
    for field in multi_label_fields:
        if field in MAPS and field in df_famd.columns:
            df_famd = create_one_hot_encoding(df_famd, field, MAPS[field])
    
    # Ensure proper data types
    # Numeric variables
    numeric_vars = ['floors', 'employees', 'latitude', 'longitude']
    for var in numeric_vars:
        if var in df_famd.columns:
            df_famd[var] = pd.to_numeric(df_famd[var], errors='coerce')
    
    # Categorical variables (for CA)
    categorical_vars = ['establishment_type', 'receives_goods', 'dispatches_goods',
                       'supply_frequency', 'dispatch_frequency']
    for var in categorical_vars:
        if var in df_famd.columns:
            df_famd[var] = df_famd[var].astype('category')
    
    return df_famd


###############################################################################
# 3.  LEGACY CONSTANTS AND FUNCTIONS (for backward compatibility)           ##
###############################################################################
DROP_COLS = {
    # from both scripts -------------------------------------------------------
    "id", "db", "marca temporal", "correo electrónico", "teléfono de contacto",
    "ir al fin de la encuesta.",
    # long battery of operational variables not used downstream --------------
    "de acuerdo con el tipo de carga que distribuye su empresa, indique máximo 3 tipos en el siguiente listado:",
    "¿el origen de la mercancía que transporta es el valle de aburrá?",
    "por favor, indique el municipio:",
    "por favor, indique cuántas entregas hace en el centro de medellín al día:",
    "por favor, indique el número de establecimientos que surte en el centro de medellín a diario:",
    "¿cuántos pedidos recibe su empresa diariamente que tienen como destino el centro de medellín?",
    "por favor indique la cantidad de vehículos con combustión a diésel (acpm) con los que cuenta su empresa:",
    "por favor indique la cantidad de vehículos con combustión a gasolina con los que cuenta su empresa:",
    "por favor indique la cantidad de vehículos con combustión a gas natural vehicular (gnv) con los que cuenta su empresa:",
    "por favor indique la cantidad de vehículos con motor eléctrico con los que cuenta su empresa:",
    "por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos anteriores a 1990]",
    "por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos entre 1991 y 2000]",
    "por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos entre 2001 y 2010]",
    "por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos entre 2011 y 2015]",
    "por favor, indique el rango de edad promedio del parque vehicular de su empresa [modelos del 2016 en adelante]",
    "¿cuánto es el rendimiento en galones/kilómetro, de sus vehículos a acpm?",
    "¿cuánto es el rendimiento en galones/kilómetro, de sus vehículos a gasolina?",
    "¿cuánto es el rendimiento en metros cúbicos/kilómetro, de sus vehículos a gnv?",
    "¿cuánto es el rendimiento kilowatt-hora, de sus vehículos eléctricos?",
    "¿cuánto es el costo total por movilizar un camión cargado hacia el centro de medellín?",
    "¿cuántas horas al volante permanece durante un turno de reparto una/un conductora/or en su empresa?",
    "de acuerdo con la siguiente escala, donde 1 es \"muy compleja\" y 5 es \"muy adecuada\" ¿cómo considera la relación de sus conductores con los demás actores viales (peatones, ciclistas, conductores, transporte público) en el espacio público de la zuap?",
    "¿al interior de su empresa se realizan actividades que promuevan la actividad física entre sus calaboradoras/es?",
    "¿qué actividades se realizan?",
    "¿cuántas veces por semana se realizan actividades para promover la actividad física?",
    "¿conoce usted el decreto no 1790 de noviembre 20 de 2012 (decreto de zona amarilla o de cargue y descargue en el centro de la ciudad)?",
}

# 1.2 Column-rename map (keys and values both lower-case for safer matching)
# Preference is given to the shorter identifiers used in the plotting helpers.
RENAME_MAP = {
    # identification ----------------------------------------------------------
    "nombre de la empresa": "company_name",
    "dirección de la empresa": "est_address",
    # people & gender ---------------------------------------------------------
    "por favor indique el número de colaboradores que tiene su empresa o comercio": "employees",
    "¿en su empresa o comercio cuentan con colaboradoras mujeres?": "has_female_employees",
    "por favor indique el número de mujeres que trabajan en su empresa o comercio": "female_employees",
    "de sus empleadas mujeres, ¿cuántas hacen parte de la cadena de distribución del negocio (conducen, reparten domicilios, acompañan las entregas, etc.)?": "female_emplo_distri",
    "% mujeres en la distribución": "women_distri_percentage",
    "de las mujeres vinculadas a la cadena logística de su empresa o comercio ¿cuántas están vinculadas por contrato laboral?": "female_distri_vincu",
    "% mujeres vinculadas": "hired_women_percentage",
    "entre sus colaboradoras mujeres, alguna(s) se identifica(n) con los siguientes grupos poblacionales:": "female_popg",
    "¿acompañan y/o apoyan el proceso formativo de las mujeres que hacen parte de la cadena logística?": "female_support",
    # economic activity -------------------------------------------------------
    "por favor, indique dentro de la siguientes categorías, cuál se relaciona con la actividad realizada en su comercio:": "economic_activity",
    "de acuerdo al listado señale en orden de importancia las 3 principales actividades comerciales que se desarrollan en su establecimiento:": "specific_activity",
    "productos principales": "main_products",
    # warehouse & logistics ---------------------------------------------------
    "¿su establecimiento cuenta con espacio de bodega o almacenamiento de mercancías o productos?": "warehouse",
    "¿con cuántos espacios de bodega cuenta?": "number_warehouse",
    "¿en qué piso se ubica(n) la(s) bodegas que sirven a su empresa o comercio?": "warehouse_floor",
    "por favor, indique el área de la bodega que sirve a su comercio en metros cuadrados:": "warehouse_area",
    "por favor, indique la altura en metros de la bodega que sirve a su comercio:": "warehouse_height",
    "¿el(los) espacio(s) de bodega están ubicados al interior de la zuap?": "zuap_warehouse",
    "¿en qué municipio se encuentra ubicada la bodega que sirve a su comercio?": "warehouse_municipality",
    "por favor, indique el tipo de bodega con la que cuenta:": "warehouse_type",
    "¿el establecimiento o bodega posee alguno de los siguientes elementos para el cargue y descargue de mercancías?": "warehouse_equipement",
    # supply chain flow -------------------------------------------------------
    "por favor, seleccione los días en los cuales recibe materiales, materias primas o productos:": "supply_day",
    "¿cuántas veces por semana abastece su establecimiento?": "supply_week",
    "por favor, indique los horarios durante los cuales realiza las actividades de cargue y descargue de las mercancías:": "supply_schedule",
    "por favor, indique la forma en la que ingresa la mercancía a su comercio o área de bodega:": "supply_unloading",
    "en una escala de 1 a 5, donde 1 es \"muy inseguro\" y 5 \"muy seguro\", ¿considera usted que el proceso de cargue y descargue de mercancías en camión, carro o motocicleta es?": "supply_safety_percep",
    "en una escala de 1 a 5, donde 1 es \"muy inseguro\" y 5 \"muy seguro\", ¿considera usted que el proceso de cargue y descargue de mercancías en bicicleta es?": "supply_bic_safety_perception",
    # delivery ---------------------------------------------------------------
    "¿qué medio realiza para el envío de sus artículos a domicilio?": "delivery_transp_mode",
    "¿cuántos domicilios realiza a diario su establecimiento?": "num_deliveries",
    "¿qué medio realiza para el envío de sus ventas por internet?": "online_trans_mode",
    "¿cuántos envíos de artículos vendidos por internet realiza a diario su establecimiento?": "num_online_deliveries",
}

###############################################################################
# 2.  HELPER FUNCTIONS                                                       ##
###############################################################################

def _normalize_text(s: str | float | int | None) -> str:
    """Lower-case, strip accents, collapse whitespace. Blank on NaN."""
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # strip accents
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s

###############################################################################
# 3.  MAIN CLEANING FUNCTION                                                 ##
###############################################################################

def clean_survey(path: Path | str = RAW_FILE, *, sheet: str = "Respuestas") -> pd.DataFrame:
    """Return cleaned DataFrame ready for analysis & plotting."""
    # ── 3.1 read raw --------------------------------------------------------
    df = pd.read_excel(path, sheet_name=sheet)

    # ── 3.2 standardise headers -------------------------------------------
    df.columns = df.columns.str.strip().str.lower()

    # ── 3.3 drop non-informative columns ----------------------------------
    drop_lower = {c.lower() for c in DROP_COLS}
    df = df.drop(columns=[c for c in df.columns if c in drop_lower], errors="ignore")

    # ── 3.4 rename to concise English idents ------------------------------
    rename_lower = {k.lower(): v for k, v in RENAME_MAP.items()}
    df = df.rename(columns=rename_lower)

    # ── 3.5 basic tidying --------------------------------------------------
    # strip strings
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    # parse timestamp if still present
    if "marca temporal" in df.columns:
        df["marca temporal"] = pd.to_datetime(df["marca temporal"], errors="coerce")

    df = df.drop_duplicates()

    # ── 3.6 type conversions ---------------------------------------------
    # counts & numeric measures
    NUMERIC_COLS = [
        "number_warehouse", "warehouse_area", "warehouse_height",
        "num_deliveries", "num_online_deliveries", "employees", "female_employees",
        "female_emplo_distri", "female_distri_vincu",
    ]
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # percentages
    PCT_COLS = ["women_distri_percentage", "hired_women_percentage"]
    for col in PCT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Additional derived percentage calculations (if base columns exist)
    if "female_employees" in df.columns and "employees" in df.columns:
        df["female_percentage"] = (df["female_employees"] / df["employees"] * 100).round(2)
    
    if "female_emplo_distri" in df.columns and "female_employees" in df.columns:
        df["pct_female_in_distribution"] = (
            df["female_emplo_distri"] / df["female_employees"] * 100
        ).round(2)
    
    if "female_distri_vincu" in df.columns and "female_emplo_distri" in df.columns:
        df["pct_female_with_contract"] = (
            df["female_distri_vincu"] / df["female_emplo_distri"] * 100
        ).round(2)

    # likert 1-5
    likert = CategoricalDtype(categories=[1, 2, 3, 4, 5], ordered=True)
    for col in ["supply_safety_percep", "supply_bic_safety_perception"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(likert)

    # floors as ordered categorical (keep raw text but ordered by numeric part)
    if "warehouse_floor" in df.columns:
        floors = sorted(df["warehouse_floor"].dropna().unique(), key=lambda x: float(re.sub(r"[^0-9.-]", "", str(x)) or 0))
        df["warehouse_floor"] = df["warehouse_floor"].astype(CategoricalDtype(categories=floors, ordered=True))

    # supply frequency numeric & ordered
    if "supply_week" in df.columns:
        freq_map = {
            "1 vez por semana": 1,
            "2": 2,
            "5": 5,
            "6 o más": 6,
            "la periodicidad es quincenal": 2,
            "la periodicidad es mensual": 1,
        }
        df["supply_frequency_num"] = (
            df["supply_week"].map(str).str.lower().map(freq_map).fillna(0).astype(int)
        )
        df["supply_frequency_num"] = df["supply_frequency_num"].astype(
            CategoricalDtype(categories=[1, 2, 5, 6], ordered=True)
        )

    # cast common single-label categoricals
    CAT_COLS = [
        "main_products",
        "warehouse",
        "zuap_warehouse",
        "warehouse_municipality",
        "warehouse_type",
        "economic_activity",
        "female_support",
    ]
    for col in CAT_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # multi-label text kept as strings for later explode
    MULTI_TEXT = [
        "specific_activity",
        "supply_day",
        "supply_schedule",
        "supply_unloading",
        "warehouse_equipement",
        "delivery_transp_mode",
        "online_trans_mode",
        "female_popg",
    ]
    for col in MULTI_TEXT:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # ── 3.7 basic normalisation -------------------------------------------
    YESNO = {"sí": "yes", "si": "yes", "no": "no", "no aplica": pd.NA}
    if "zuap_warehouse" in df.columns:
        df["zuap_warehouse"] = (
            df["zuap_warehouse"].map(_normalize_text).replace(YESNO).astype("category")
        )

    if "main_products" in df.columns:
        df["main_products"] = df["main_products"].map(_normalize_text).astype("category")

    # ── 3.8 economic activity split (keep original + 3 levels) -------------
    main_cats = ["Venta al detalle", "Fabricante", "Proveedor", "Ventas por internet"]

    def _split_econ(x):
        if pd.isna(x):
            return pd.Series([pd.NA, pd.NA, pd.NA])
        main = next((m for m in main_cats if x.startswith(m)), None)
        if main is None:
            return pd.Series([x, pd.NA, pd.NA])
        rest = x[len(main) :].strip()
        if not rest:
            return pd.Series([main, pd.NA, pd.NA])
        parts = re.findall(r"([A-ZÁÉÍÓÚÑ][^A-ZÁÉÍÓÚÑ]*)", rest)
        sub1 = parts[0].strip() if len(parts) >= 1 else pd.NA
        sub2 = parts[1].strip() if len(parts) >= 2 else pd.NA
        return pd.Series([main, sub1, sub2])

    if "economic_activity" in df.columns:
        econ_split = df["economic_activity"].astype(str).apply(_split_econ)
        df[["econ_main", "econ_sub1", "econ_sub2"]] = econ_split
        for col in ["econ_main", "econ_sub1", "econ_sub2"]:
            df[col] = df[col].astype("category")

    return df

def clean_survey_for_analysis(
    path: Path | str = RAW_FILE, 
    *, 
    sheet: str = "Respuestas",
    add_derived_columns: bool = True,
    return_analysis_ready: bool = False
) -> pd.DataFrame:
    """
    Extended cleaning function that prepares data specifically for Mario's analysis workflows.
    
    Args:
        path: Path to the Excel file
        sheet: Sheet name to read
        add_derived_columns: Whether to add establishment type and other derived columns
        return_analysis_ready: Whether to return data ready for immediate analysis
        
    Returns:
        Cleaned DataFrame with optional analysis-ready enhancements
    """
    # Get basic cleaned data
    df = clean_survey(path, sheet=sheet)
    
    if add_derived_columns:
        # Add establishment type categorization
        df['est_type'] = categorize_establishment_type(df)
        
        # Add translated establishment types
        df['est_type_en'] = df['est_type'].map(ESTABLISHMENT_TRANSLATIONS)
        
        # Add supply frequency categorization
        if 'supply_week' in df.columns:
            freq_map = {
                '1 vez por semana': '1/week',
                '2': '2/week', 
                '5': '5/week',
                '6 o más': '6+/week',
                'La periodicidad es quincenal': 'Biweekly',
                'La periodicidad es mensual': 'Monthly'
            }
            df['supply_frequency_clean'] = df['supply_week'].astype(str).map(freq_map)
        
        # Add yes/no normalization for warehouse location
        if 'zuap_warehouse' in df.columns:
            yesno_map = {'Sí': 'Yes', 'No': 'No', 'No aplica': 'Not applicable'}
            df['zuap_warehouse_en'] = df['zuap_warehouse'].astype(str).map(yesno_map)
    
    if return_analysis_ready:
        # Remove rows with missing establishment types for analysis
        df = df[df['est_type'].notna()].copy()
        
        # Ensure numeric columns are properly typed
        numeric_cols = ['employees', 'female_employees', 'num_deliveries', 'num_online_deliveries']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df
 
###############################################################################
# 4.  ANALYSIS UTILITY FUNCTIONS                                             ##
###############################################################################

def categorize_establishment_type(df: pd.DataFrame, column: str = None) -> pd.Series:
    """
    Extract establishment type from economic activity descriptions.
    Handles both legacy 'economic_activity' and new 'establishment_type' columns.
    
    Args:
        df: DataFrame containing the economic activity data
        column: Column name containing economic activity information
        
    Returns:
        Series with establishment type categories
    """
    # Auto-detect column name if not provided
    if column is None:
        if 'establishment_type' in df.columns:
            column = 'establishment_type'
        elif 'economic_activity' in df.columns:
            column = 'economic_activity'
        else:
            # Return None series if no suitable column found
            return pd.Series([None] * len(df), index=df.index)
    
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    return df[column].apply(
        lambda x: next((word for word in est_types if word.lower() in str(x).lower()), None)
    )

def extract_keywords_from_text(
    df: pd.DataFrame, 
    column: str, 
    keywords: List[str], 
    normalize: bool = True
) -> pd.DataFrame:
    """
    Extract and explode keywords from multi-label text fields.
    
    Args:
        df: Input DataFrame
        column: Column name to process
        keywords: List of keywords to search for
        normalize: Whether to normalize text before matching
        
    Returns:
        DataFrame with exploded keyword matches
    """
    df_copy = df.copy()
    
    if normalize:
        # Apply text normalization
        df_copy[f"{column}_normalized"] = df_copy[column].apply(
            lambda x: _normalize_text(str(x)) if pd.notna(x) else ""
        )
        search_column = f"{column}_normalized"
    else:
        search_column = column
    
    # Extract matching keywords
    df_copy[f"{column}_keywords"] = df_copy[search_column].apply(
        lambda x: [word for word in keywords if word.lower() in str(x).lower()]
    )
    
    # Explode to separate rows
    result = df_copy.explode(f"{column}_keywords").reset_index(drop=True)
    
    # Clean up temporary columns
    if normalize:
        result = result.drop(columns=[f"{column}_normalized"])
    
    return result

def compute_percentage_distributions(
    df: pd.DataFrame, 
    group_col: str, 
    value_col: str, 
    count_col: str = "employees"
) -> pd.DataFrame:
    """
    Compute percentage distributions for stacked bar plots.
    
    Args:
        df: Input DataFrame
        group_col: Column to group by (e.g., establishment type)
        value_col: Column with values to distribute
        count_col: Column to use for counting/weighting
        
    Returns:
        DataFrame with percentage distributions
    """
    # Group and count
    grouped = df.groupby([group_col, value_col])[count_col].count().reset_index()
    grouped = grouped.rename(columns={count_col: 'frequency'})
    
    # Pivot to wide format
    pivot = grouped.pivot(index=group_col, columns=value_col, values='frequency').fillna(0)
    
    # Convert to percentages
    percentages = pivot.div(pivot.sum(axis=1), axis=0)
    
    return percentages

def translate_establishment_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply standard translations for establishment categories.
    
    Args:
        df: DataFrame with Spanish establishment categories in index
        
    Returns:
        DataFrame with translated categories
    """
    translation_map = {
        'Proveedor': 'Supplier', 
        'Venta al detalle': 'Retailer', 
        'Fabricante': 'Manufacturer', 
        'Ventas por internet': 'E-commerce'
    }
    
    df_translated = df.copy()
    if hasattr(df_translated, 'index'):
        df_translated = df_translated.rename(index=translation_map)
    
    return df_translated

###############################################################################
# 5.  ENHANCED EXPORT FUNCTIONS                                              ##
###############################################################################

def save_analysis_outputs(
    df_clean: pd.DataFrame, 
    output_dir: Optional[Union[str, Path]] = None,
    formats: List[str] = ["csv"]
) -> Dict[str, Path]:
    """
    Save cleaned data in multiple formats for different analysis workflows.
    
    Args:
        df_clean: Cleaned DataFrame
        output_dir: Directory to save outputs (defaults to PROJECT_ROOT/data/intermediate)
        formats: List of formats to save ("csv", "parquet", "excel")
        
    Returns:
        Dictionary mapping format names to saved file paths
    """
    if output_dir is None:
        output_dir = PROJECT_ROOT / "data" / "intermediate"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_files = {}
    
    for fmt in formats:
        if fmt == "csv":
            file_path = output_dir / "df_clean.csv"
            df_clean.to_csv(file_path, index=False)
        elif fmt == "parquet":
            file_path = output_dir / "df_clean.parquet"
            df_clean.to_parquet(file_path, index=False)
        elif fmt == "excel":
            file_path = output_dir / "df_clean.xlsx"
            df_clean.to_excel(file_path, index=False)
        else:
            continue
            
        saved_files[fmt] = file_path
        print(f"✅ Saved {fmt.upper()} to: {file_path.relative_to(PROJECT_ROOT)}")
    
    return saved_files

###############################################################################
# 6.  CLI HELPER AND ENHANCED FUNCTIONS FOR FAMD WORKFLOW                   ##
###############################################################################

def clean_survey_comprehensive(
    path: Path | str = RAW_FILE, 
    *, 
    sheet: str = "Respuestas",
    use_unified_names: bool = True
) -> pd.DataFrame:
    """
    Comprehensive cleaning function using v3_data_cleaning.py approach.
    
    This function provides the most complete data cleaning pipeline by:
    1. Using comprehensive column renaming (UNIFIED_RENAME_MAP)
    2. Applying extensive translation dictionaries
    3. Preserving all variables needed for FAMD analysis
    4. Maintaining data integrity for statistical analysis
    
    Parameters:
    -----------
    path : Path or str
        Path to the Excel file
    sheet : str
        Sheet name to read  
    use_unified_names : bool
        Whether to use the comprehensive UNIFIED_RENAME_MAP
        
    Returns:
    --------
    pd.DataFrame
        Comprehensively cleaned DataFrame ready for FAMD analysis
    """
    # Read raw data
    df = pd.read_excel(path, sheet_name=sheet)
    
    # Standardize headers
    df.columns = df.columns.str.strip()
    
    # Apply comprehensive column renaming
    if use_unified_names:
        df = df.rename(columns=UNIFIED_RENAME_MAP)
    else:
        # Fallback to legacy rename map
        rename_lower = {k.lower(): v for k, v in RENAME_MAP.items()}
        df.columns = df.columns.str.lower()
        df = df.rename(columns=rename_lower)
    
    # Remove unwanted columns
    columns_to_drop = ['email', 'phone'] + [col for col in df.columns if 'timestamp' in col.lower()]
    df = df.drop(columns=columns_to_drop, errors='ignore')
    
    # Basic data cleaning
    for col in df.select_dtypes(include='object').columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'None', ''], pd.NA)
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Convert numeric columns
    numeric_columns = ['floors', 'employees', 'latitude', 'longitude']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert categorical columns
    categorical_columns = [
        'establishment_type', 'receives_goods', 'dispatches_goods',
        'supply_frequency', 'dispatch_frequency'
    ]
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    return df


def create_analysis_datasets(df_clean: pd.DataFrame) -> dict:
    """
    Create multiple analysis-ready datasets from cleaned data.
    
    Parameters:
    -----------
    df_clean : pd.DataFrame
        Basic cleaned DataFrame
        
    Returns:
    --------
    dict
        Dictionary containing different dataset formats:
        - 'basic': Core cleaned data
        - 'translated': Data with English translations  
        - 'famd_ready': One-hot encoded data for FAMD
        - 'r_optimized': R-optimized format with proper factors
    """
    datasets = {}
    
    # 1. Basic cleaned data
    datasets['basic'] = df_clean.copy()
    
    # 2. Translated version
    datasets['translated'] = translate_all_multi_labels(df_clean.copy())
    
    # 3. FAMD-ready dataset with one-hot encoding
    datasets['famd_ready'] = prepare_famd_dataset(df_clean.copy())
    
    # 4. R-optimized version
    df_r = datasets['translated'].copy()
    
    # Convert Yes/No columns to factors for R
    yesno_columns = ['receives_goods', 'dispatches_goods']
    for col in yesno_columns:
        if col in df_r.columns:
            df_r[col] = df_r[col].map({'Sí': 'Yes', 'No': 'No'})
            df_r[col] = df_r[col].astype('category')
    
    # Ensure proper factor levels for frequency variables
    frequency_columns = ['supply_frequency', 'dispatch_frequency']
    for col in frequency_columns:
        if col in df_r.columns:
            df_r[col] = df_r[col].astype('category')
    
    # Add establishment type categorization if not present
    if 'establishment_type_clean' not in df_r.columns:
        df_r['establishment_type_clean'] = categorize_establishment_type(df_r)
    
    datasets['r_optimized'] = df_r
    
    return datasets


def save_analysis_outputs(
    df_clean: pd.DataFrame, 
    output_dir: Path | str = None,
    formats: list = ["csv"]
) -> dict:
    """
    Save multiple analysis-ready datasets in different formats.
    
    Parameters:
    -----------
    df_clean : pd.DataFrame
        Cleaned DataFrame
    output_dir : Path or str, optional
        Output directory (default: PROJECT_ROOT/data/intermediate)
    formats : list
        List of formats to save ['csv', 'parquet', 'excel']
        
    Returns:
    --------
    dict
        Dictionary with file paths for each saved dataset
    """
    if output_dir is None:
        output_dir = PROJECT_ROOT / "data" / "intermediate"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create all analysis datasets
    datasets = create_analysis_datasets(df_clean)
    saved_files = {}
    
    for dataset_name, df in datasets.items():
        for fmt in formats:
            filename = f"{dataset_name}_survey.{fmt}"
            filepath = output_dir / filename
            
            if fmt == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8')
            elif fmt == 'parquet':
                df.to_parquet(filepath, index=False)
            elif fmt == 'excel':
                df.to_excel(filepath, index=False)
            
            saved_files[f"{dataset_name}_{fmt}"] = filepath
            print(f"✅ Saved {dataset_name} dataset as {fmt}: {filepath}")
    
    return saved_files


def main():
    """Run comprehensive cleaning and generate all analysis datasets."""
    print("🚀 Starting comprehensive CBD survey data cleaning...")
    
    # Use comprehensive cleaning approach
    df_clean = clean_survey_comprehensive(RAW_FILE)
    
    # Save in multiple formats for different workflows  
    saved_files = save_analysis_outputs(
        df_clean, 
        formats=["csv"]  # Add "parquet", "excel" if needed
    )
    
    print(f"\n✅ Comprehensive cleaning complete! Data shape: {df_clean.shape}")
    print(f"✅ Variables: {len(df_clean.columns)} total")
    
    # Show establishment type distribution
    if 'establishment_type' in df_clean.columns:
        print(f"\n🏢 Establishment Types Distribution:")
        est_counts = df_clean['establishment_type'].value_counts()
        for est_type, count in est_counts.head(5).items():
            print(f"   • {est_type}: {count} ({count/len(df_clean)*100:.1f}%)")
    
    # Multi-label field summary
    multilabel_fields = [col for col in df_clean.columns if col in MAPS.keys()]
    if multilabel_fields:
        print(f"\n🔗 Multi-label fields ready for translation: {len(multilabel_fields)}")
        print(f"     {multilabel_fields}")
    
    print(f"\n📁 Analysis datasets created:")
    print(f"   • basic_survey.csv: Core cleaned data")
    print(f"   • translated_survey.csv: English translations applied")  
    print(f"   • famd_ready_survey.csv: One-hot encoded for FAMD")
    print(f"   • r_optimized_survey.csv: R-compatible factors and types")
    
    print(f"\n🎯 Ready for R analysis pipeline:")
    print(f"   📈 Factor Analysis of Mixed Data (FAMD)")
    print(f"   🎯 K-means Clustering")  
    print(f"   📊 Correspondence Analysis (CA)")


if __name__ == "__main__":
    main()
