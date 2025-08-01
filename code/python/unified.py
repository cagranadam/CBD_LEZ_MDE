#!/usr/bin/env python
# coding: utf-8
"""
CBD_MDE_2025 — Unified Data-Cleaning Pipeline
-------------------------------------------------
This script merges **survey_cleaning.py** and **plots_and_analysis.py** into a
single, reproducible pipeline that outputs one tidy DataFrame (`df_clean`) that
works both for statistical analysis and for the plotting utilities written by
Mario.

Key design choices
------------------
* **One source of truth** for drop-lists & rename-maps (union of both scripts).
* Column names follow the shorter identifiers already expected by the plotting
  helpers (`supply_unloading`, `supply_week`, …).
* Explicit data-typing for counts, percentages & ordered factors (Likert 1-5,
  floors, supply frequency).
* Non-destructive: raw data are never mutated in-place; `clean_survey()`
  returns a *new* DataFrame.
* Saving helper writes the CSV to `data/intermediate/df_clean.csv` so that
  downstream notebooks can `%run` this module or just read the file.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

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

# 1.1 Columns to drop (union of both scripts — all lower-case for matching)
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

###############################################################################
# 4.  CLI HELPER                                                             ##
###############################################################################

def main() -> None:  # pragma: no cover ┆ noqa: D401
    """Run cleaning and write CSV."""
    df_clean = clean_survey(RAW_FILE)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Cleaned data written to: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
