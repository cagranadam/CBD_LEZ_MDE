#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
import unicodedata
import re


def _normalize_text(s):
    """Lower-case, strip accents, collapse whitespace. Blank on NaN."""
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # strip accents
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def dataframe_cleaning(path):
    """
    Clean the survey dataframe by removing non-informative columns and renaming columns
    to more descriptive English names for R analysis.
    
    Parameters:
    path (str): Path to the Excel file containing the survey data
    
    Returns:
    pd.DataFrame: Cleaned dataframe ready for analysis
    """
    
    df = pd.read_excel(path)

    # Non informative columns that won't be considered in the analysis  
    col_out = ['id', 'db', 'Marca temporal', 'Correo electrónico', 'Teléfono de contacto',
               'Ir al fin de la encuesta.', 'Nombre de la empresa', 
               'De acuerdo con el tipo de carga que distribuye su empresa, indique máximo 3 tipos en el siguiente listado:',
               '¿El origen de la mercancía que transporta es el Valle de Aburrá?',
               'Por favor, indique el municipio:',
               'Por favor, indique cuántas entregas hace en el centro de Medellín al día:',
               'Por favor, indique el número de establecimientos que surte en el centro de Medellín a diario:',
               '¿Cuántos pedidos recibe su empresa diariamente que tienen como destino el centro de Medellín?',
               'Por favor indique la cantidad de vehículos con combustión a diésel (ACPM) con los que cuenta su empresa:',
               'Por favor indique la cantidad de vehículos con combustión a gasolina con los que cuenta su empresa:',
               'Por favor indique la cantidad de vehículos con combustión a gas natural vehicular (GNV) con los que cuenta su empresa:',
               'Por favor indique la cantidad de vehículos con motor eléctrico con los que cuenta su empresa:',
               'Por favor, indique el rango de edad promedio del parque vehicular de su empresa [Modelos anteriores a 1990]',
               'Por favor, indique el rango de edad promedio del parque vehicular de su empresa [Modelos entre 1991 y 2000]',
               'Por favor, indique el rango de edad promedio del parque vehicular de su empresa [Modelos entre 2001 y 2010]',
               'Por favor, indique el rango de edad promedio del parque vehicular de su empresa [Modelos entre 2011 y 2015]',
               'Por favor, indique el rango de edad promedio del parque vehicular de su empresa [Modelos del 2016 en adelante]',
               '¿Cuánto es el rendimiento en galones/kilómetro, de sus vehículos a ACPM?',
               '¿Cuánto es el rendimiento en galones/kilómetro, de sus vehículos a gasolina?',
               '¿Cuánto es el rendimiento en metros cúbicos/kilómetro, de sus vehículos a GNV?',
               '¿Cuánto es el rendimiento kilowatt-hora, de sus vehículos eléctricos?',
               '¿Cuánto es el costo total por movilizar un camión cargado hacia el centro de Medellín?',
               '¿Cuántas horas al volante permanece durante un turno de reparto una/un conductora/or en su empresa?',
               'De acuerdo con la siguiente escala, donde 1 es "Muy compleja" y 5 es "Muy adecuada" ¿Cómo considera la relación de sus conductores con los demás actores viales (peatones, ciclistas, conductores, transporte público) en el espacio público de la ZUAP?',
               '¿Al interior de su empresa se realizan actividades que promuevan la actividad física entre sus calaboradoras/es?',
               '¿Qué actividades se realizan?',
               '¿Cuántas veces por semana se realizan actividades para promover la actividad física?',
               '¿Conoce usted el Decreto No 1790 de noviembre 20 de 2012 (Decreto de Zona Amarilla o de cargue y descargue en el centro de la ciudad)?']

    df = df.drop(col_out, axis=1)

    # Lowercase column names
    df.columns = df.columns.str.lower()

    # Change variables names for facility
    col_name = {'dirección de la empresa': 'est_address',
                'por favor indique el número de colaboradores que tiene su empresa o comercio': 'employees',
                'por favor indique el número de mujeres que trabajan en su empresa o comercio': 'female_employees',
                'de sus empleadas mujeres, ¿cuántas hacen parte de la cadena de distribución del negocio (conducen, reparten domicilios, acompañan las entregas, etc.)?': 'female_emplo_distri',
                'de las mujeres vinculadas a la cadena logística de su empresa o comercio ¿cuántas están vinculadas por contrato laboral?': 'female_distri_vincu',
                'entre sus colaboradoras mujeres, alguna(s) se identifica(n) con los siguientes grupos poblacionales:': 'female_popg',
                '¿acompañan y/o apoyan el proceso formativo de las mujeres que hacen parte de la cadena logística?': 'female_support',
                'por favor, indique dentro de la siguientes categorías, cuál se relaciona con la actividad realizada en su comercio:': 'economic_activity',
                'de acuerdo al listado señale en orden de importancia las 3 principales actividades comerciales que se desarrollan en su establecimiento:': 'specific_activity',
                'productos principales': 'main_products',
                '¿su establecimiento cuenta con espacio de bodega o almacenamiento de mercancías o productos?': 'warehouse',
                '¿con cuántos espacios de bodega cuenta?': 'number_warehouse',
                '¿en qué piso se ubica(n) la(s) bodegas que sirven a su empresa o comercio?': 'warehouse_floor',
                'por favor, indique el área de la bodega que sirve a su comercio en metros cuadrados:': 'warehouse_area',
                'por favor, indique la altura en metros de la bodega que sirve a su comercio:': 'warehouse_height',
                '¿el(los) espacio(s) de bodega están ubicados al interior de la zuap?': 'zuap_warehouse',
                '¿en qué municipio se encuentra ubicada la bodega que sirve a su comercio?': 'warehouse_municipality',
                'por favor, indique el tipo de bodega con la que cuenta:': 'warehouse_type',
                'por favor, seleccione los días en los cuales recibe materiales, materias primas o productos:': 'supply_day',
                '¿cuántas veces por semana abastece su establecimiento?': 'supply_week',
                'por favor, indique los horarios durante los cuales realiza las actividades de cargue y descargue de las mercancías:': 'supply_schedule',
                'por favor, indique la forma en la que ingresa la mercancía a su comercio o área de bodega:': 'supply_unloading',
                'en una escala de 1 a 5, donde 1 es "muy inseguro" y 5 "muy seguro", ¿considera usted que el proceso de cargue y descargue de mercancías en camión, carro o motocicleta es?': 'supply_safety_percep',
                'en una escala de 1 a 5, donde 1 es "muy inseguro" y 5 "muy seguro", ¿considera usted que el proceso de cargue y descargue de mercancías en bicicleta es?': 'supply_bic_safety_perception',
                '¿el establecimiento o bodega posee alguno de los siguientes elementos para el cargue y descargue de mercancías?': 'warehouse_equipement',
                '¿qué medio realiza para el envío de sus artículos a domicilio?': 'delivery_transp_mode',
                '¿cuántos domicilios realiza a diario su establecimiento?': 'num_deliveries',
                '¿qué medio realiza para el envío de sus ventas por internet?': 'online_trans_mode',
                '¿cuántos envíos de artículos vendidos por internet realiza a diario su establecimiento?': 'num_online_deliveries',
                '% mujeres en la distribución': 'women_distri_percentage',
                '% mujeres vinculadas': 'hired_women_percentage'}

    df = df.rename(columns=col_name)

    # Normalize main_products column
    if "main_products" in df.columns:
        df["main_products"] = df["main_products"].map(_normalize_text).astype("category")

    return df


def temporal_analysis(df):
    """
    Function to compute temporal analysis of supply schedules.
    Returns a dataframe ready for heatmap visualization in R.
    """
    # Keep relevant columns
    df = df[['supply_day', 'supply_schedule', 'employees']].copy()

    # Replace 'a' for 'to'
    df['supply_schedule'] = df['supply_schedule'].str.replace('a', 'to')

    # Explode supply days
    df['supply_day'] = df['supply_day'].str.split(',\s*')
    df = df.explode('supply_day')

    # Explode supply schedule
    df['supply_schedule'] = df['supply_schedule'].str.split(',\s*')
    df = df.explode('supply_schedule').reset_index(drop=True)

    # Groupby to compute heatmap
    df = df.groupby(['supply_day', 'supply_schedule']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df[df['supply_day'] != 'Festivos']
    df = df.pivot(index='supply_schedule', columns='supply_day', values='frequency').fillna(0)

    rename = {'Domingo': 'Sunday', 'Jueves': 'Thursday', 'Lunes': 'Monday', 'Martes': 'Tuesday',
              'Miércoles': 'Wednesday', 'Sábado': 'Saturday', 'Viernes': 'Friday'}
    df.rename(columns=rename, inplace=True)

    # Reorder columns
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    available_days = [day for day in day_order if day in df.columns]
    df = df[available_days]

    return df


def transportation_mode(df):
    """
    Type of Establishment vs Delivery Transportation Mode analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'supply_unloading', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Identify type of transportation mode
    transp_mode = ['camión', 'motocicleta', 'bicicleta', 'carreta', 'particular']
    df['transp_type'] = df['supply_unloading'].apply(lambda x: [word for word in transp_mode if word.lower() in x.lower()])

    # Explode transportation mode
    df = df.explode('transp_type').reset_index(drop=True)

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'transp_type']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='transp_type', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    rename1 = {'bicicleta': 'Bicycle', 'camión': 'Truck', 'carreta': 'Handcart', 'motocicleta': 'Motorcycle', 'particular': 'Private Vehicle'}
    df.rename(columns=rename1, inplace=True)

    return df


def unloading_location(df):
    """
    Type of Establishment vs Unloading Location analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'supply_unloading', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Identify how is the unloading
    unloading = ['sobre la vía', 'sobre el andén', 'bahía', 'internamente', 'vías aledañas', 'parqueadero']
    df['unloading_location'] = df['supply_unloading'].apply(lambda x: [word for word in unloading if word.lower() in x.lower()])

    # Explode unloading location
    df = df.explode('unloading_location').reset_index(drop=True)

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'unloading_location']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='unloading_location', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    rename1 = {'sobre la vía': 'On the road', 'sobre el andén': 'On the sidewalk', 'bahía': 'Loading/unloading zone',
               'internamente': 'Establishment facilities', 'vías aledañas': 'Nearby roads', 'parqueadero': 'Parking lot'}
    df.rename(columns=rename1, inplace=True)

    return df


def unloading_equipement(df):
    """
    Type of Establishment vs Unloading Equipment analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'warehouse_equipement', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Identify unloading equipement
    df['warehouse_equipement'] = df['warehouse_equipement'].str.strip()
    df['warehouse_equipement'] = df['warehouse_equipement'].str.replace(r".*ning.*", 'No', regex=True, case=False)

    # Explode warehouse equipement
    df['warehouse_equipement'] = df['warehouse_equipement'].str.split(',\s*')
    df = df.explode('warehouse_equipement')

    # Unify type of equipement
    to_unify = {'Caminata': 'Manual workforce', 'Na': 'No', '1': 'No', 'Camina': 'Manual workforce',
                'Parqueadero de uso interno': 'No', 'Al hombro': 'Manual workforce', 'Descargue a mano': 'Manual workforce',
                'no posee': 'No', 'Personal externo': 'Manual workforce', 'Parqueadero para clientes': 'No',
                'A mano': 'Manual workforce', 'La misma persona la carga en sus manos': 'Manual workforce',
                'No hay bodega': 'No', 'Las personas lo llevan cargados': 'Manual workforce',
                'No se requiere por el volumen': 'No', 'No aplica': 'No', 'No es necesario entra oaquete manual': 'No',
                'No se requiere lis paquetes vson pequeños sebtraen a mano': 'No', 'Caminando': 'Manual workforce',
                'Cajas': 'No', 'Carretilla entra': 'Carretilla', 'Bahía': 'No', np.nan: 'No', 'no': 'No',
                'Escaleras eléctricas': 'Other', 'Escalas': 'Other', 'Porta doble': 'Other', 'Montacargas': 'Loading Ramp',
                'Rampa mecánica': 'Loading Ramp', 'Gato hidráulico': 'Loading Ramp'}

    df['warehouse_equipement'] = df['warehouse_equipement'].replace(to_unify)

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'warehouse_equipement']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='warehouse_equipement', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    rename1 = {'Carretilla': 'Handcart', 'No': 'None', 'Elevador': 'Elevator',
                 'Rampa fija': 'Fixed Loading Ramp'}
    df.rename(columns=rename1, inplace=True)

    return df


def supply_frequency(df):
    """
    Type of Establishment vs Supply frequency analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'supply_week', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Change names
    to_unify = {'La periodicidad es quincenal': 'Other', 'La periodicidad es mensual': 'Other'}
    df['supply_week'] = df['supply_week'].replace(to_unify)

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'supply_week']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='supply_week', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    rename1 = {5: '5 times a week', '6 o más': '6 times or more a week', '1 vez por semana': '1 time a week',
               2: '2 times a week', 3: '3 times a week', 4: '4 times a week'}
    df.rename(columns=rename1, inplace=True)

    column_order = ['1 time a week', '2 times a week', '3 times a week',
                   '4 times a week', '5 times a week', '6 times or more a week', 'Other']
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]

    return df


def warehouse_ownership(df):
    """
    Warehouse ownership analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'warehouse', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'warehouse']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='warehouse', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    rename1 = {'Externo, alquilado': 'External (Rented)',
               'Externo, compartido con otros comercios': 'External (Shared)',
               'Externo, propio': 'External (Own)',
               'Interno': 'Internal',
               'No': 'None'}
    df.rename(columns=rename1, inplace=True)

    return df


def warehouse_in_zuap(df):
    """
    Warehouse location in ZUAP analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'zuap_warehouse', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'zuap_warehouse']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='zuap_warehouse', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    rename1 = {'Sí': 'Yes'}
    df.rename(columns=rename1, inplace=True)

    column_order = ['Yes', 'No']
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]

    return df


def e_commerce_deliveries(df):
    """
    E-commerce deliveries analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'online_trans_mode', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Identify unloading equipement
    df['online_trans_mode'] = df['online_trans_mode'].str.strip()
    df['online_trans_mode'] = df['online_trans_mode'].str.replace(r".*ning.*", 'No', regex=True, case=False)

    # Explode warehouse equipement
    df['online_trans_mode'] = df['online_trans_mode'].str.split(',\s*')
    df = df.explode('online_trans_mode')

    to_unify = {'Motocicleta': 'Motorcycle', 'No se realizan ventas por internet': 'No deliveries',
                'Vehículo particular': 'Van/Car', 'Furgón': 'Small truck', 'Carreta "zorrilla"': 'Handcart',
               'Si se realizan ventas por internet': 'No deliveries', 'Caminata': 'Walking',
               'Mostrador': 'No deliveries', np.nan: 'No deliveries', 'No': 'No deliveries',
               'Cliente recoje en negocio': 'No deliveries', 'No se realiza': 'No deliveries',
               'Bicicleta normal': 'Bike/Cargo Bike', 'Transportadora': 'Carrier', 'Empresa transportadora': 'Carrier',
               'Transportadoras': 'Carrier', 'Realizan venta por Internet': 'No deliveries',
               'cliente recoge': 'No deliveries', 'Servicio de mensajería': 'Carrier', 'Camioneta': 'Van/Car',
               'Bicicleta de carga': 'Bike/Cargo Bike', 'Servicios de mensajería': 'Carrier',
               'Novse hace envíos': 'No deliveries', 'Na': 'No deliveries', 'Trnasportadora': 'Carrier',
               'Rappifavor': 'Carrier', 'Mensajería contratada': 'Carrier', 'Van': 'Van/Car'}

    df['online_trans_mode'] = df['online_trans_mode'].replace(to_unify)

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'online_trans_mode']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='online_trans_mode', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    return df


def traditional_deliveries(df):
    """
    Traditional deliveries analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'delivery_transp_mode', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Identify unloading equipement
    df['delivery_transp_mode'] = df['delivery_transp_mode'].str.strip()
    df['delivery_transp_mode'] = df['delivery_transp_mode'].str.replace(r".*ning.*", 'No', regex=True, case=False)

    # Explode warehouse equipement
    df['delivery_transp_mode'] = df['delivery_transp_mode'].str.split(',\s*')
    df = df.explode('delivery_transp_mode')

    to_unify = {'Motocicleta': 'Motorcycle', 'No se realizan domicilios': 'No deliveries', 'Furgón': 'Van/Car',
               'Carreta "zorrilla"': 'Handcart', 'Caminata': 'Walking', 'Vehículo particular': 'Van/Car', np.nan: 'No deliveries',
               'Van': 'Van/Car', 'Carro particular': 'Van/Car', 'Transportadora': 'Carrier',
               'Empresa transportadora': 'Carrier', 'Servicio de mensajería': 'Carrier', 'Servicios de mensajería': 'Carrier',
               'Camioneta': 'Van/Car', 'Bicicleta normal': 'Bike/Cargo Bike', 'Bicicleta de carga': 'Bike/Cargo Bike',
               'No aplica': 'No deliveries', 'No se hacen envíos': 'No deliveries', 'Na': 'No deliveries', 'No': 'No deliveries',
               'Trasnportadora': 'Carrier', 'Transportadoras': 'Carrier', 'Mensajeria contratada': 'Carrier',
                'Motocarga gasolina': 'Threewheeler'}

    df['delivery_transp_mode'] = df['delivery_transp_mode'].replace(to_unify)

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'delivery_transp_mode']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='delivery_transp_mode', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    return df


def supply_perception(df):
    """
    Supply safety perception analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'supply_safety_percep', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'supply_safety_percep']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='supply_safety_percep', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    return df


def bike_perception(df):
    """
    Bike safety perception analysis.
    """
    # Keep relevant columns
    df = df[['economic_activity', 'supply_bic_safety_perception', 'employees']].copy()

    # Identify type of commerce
    est_types = ['Proveedor', 'Venta al detalle', 'Fabricante', 'Ventas por internet']
    df['est_type'] = df['economic_activity'].apply(lambda x: next((word for word in est_types if word.lower() in x.lower()), None))

    # Groupby to compute stacked bar plot
    df = df.groupby(['est_type', 'supply_bic_safety_perception']).count().rename(columns={'employees': 'frequency'}).reset_index()
    df = df.pivot(index='est_type', columns='supply_bic_safety_perception', values='frequency').fillna(0)
    df = df.div(df.sum(axis=1), axis=0)

    # Rename columns and indexes
    rename = {'Proveedor': 'Supplier', 'Venta al detalle': 'Retailer', 'Fabricante': 'Manufacturer', 'Ventas por internet': 'E-commerce'}
    df.rename(index=rename, inplace=True)

    return df


def create_cleaned_df_for_r():
    """
    Create and export a cleaned dataframe for R analysis.
    This function loads the raw survey data, cleans it, and exports it as CSV and Excel files.
    Also creates processed dataframes for specific analyses.
    """
    
    # Define the path to the raw data
    raw_data_path = r"C:\Users\cgranadamunoz\OneDrive - Universidad Nacional de Colombia\UCC - General\CBD_MDE_2025\data\raw\03. Resultados_encuesta_logistica_ZUAP_20220927_v1.xlsx"
    
    # Define output paths
    output_dir = r"C:\Users\cgranadamunoz\OneDrive - Universidad Nacional de Colombia\UCC - General\CBD_MDE_2025\data\intermediate"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print("Loading and cleaning survey data...")
        
        # Load and clean the data
        df_cleaned = dataframe_cleaning(raw_data_path)
        
        print(f"Data cleaned successfully!")
        print(f"Cleaned columns: {df_cleaned.shape[1]}")
        print(f"Number of observations: {df_cleaned.shape[0]}")
        
        # Export main cleaned dataset
        csv_output_path = os.path.join(output_dir, "cleaned_survey_for_r.csv")
        excel_output_path = os.path.join(output_dir, "cleaned_survey_for_r.xlsx")
        
        print(f"Exporting main dataset to CSV: {csv_output_path}")
        df_cleaned.to_csv(csv_output_path, index=False, encoding='utf-8')
        
        print(f"Exporting main dataset to Excel: {excel_output_path}")
        df_cleaned.to_excel(excel_output_path, index=False)
        
        # Create processed dataframes for analysis
        print("\nCreating processed dataframes for specific analyses...")
        
        processed_datasets = {}
        
        try:
            print("- Creating temporal analysis dataset...")
            processed_datasets['temporal_analysis'] = temporal_analysis(df_cleaned)
        except Exception as e:
            print(f"  Error in temporal analysis: {str(e)}")
        
        try:
            print("- Creating transportation mode dataset...")
            processed_datasets['transportation_mode'] = transportation_mode(df_cleaned)
        except Exception as e:
            print(f"  Error in transportation mode: {str(e)}")
        
        try:
            print("- Creating unloading location dataset...")
            processed_datasets['unloading_location'] = unloading_location(df_cleaned)
        except Exception as e:
            print(f"  Error in unloading location: {str(e)}")
        
        try:
            print("- Creating unloading equipment dataset...")
            processed_datasets['unloading_equipment'] = unloading_equipement(df_cleaned)
        except Exception as e:
            print(f"  Error in unloading equipment: {str(e)}")
        
        try:
            print("- Creating supply frequency dataset...")
            processed_datasets['supply_frequency'] = supply_frequency(df_cleaned)
        except Exception as e:
            print(f"  Error in supply frequency: {str(e)}")
        
        try:
            print("- Creating warehouse ownership dataset...")
            processed_datasets['warehouse_ownership'] = warehouse_ownership(df_cleaned)
        except Exception as e:
            print(f"  Error in warehouse ownership: {str(e)}")
        
        try:
            print("- Creating warehouse ZUAP location dataset...")
            processed_datasets['warehouse_in_zuap'] = warehouse_in_zuap(df_cleaned)
        except Exception as e:
            print(f"  Error in warehouse ZUAP location: {str(e)}")
        
        try:
            print("- Creating e-commerce deliveries dataset...")
            processed_datasets['ecommerce_deliveries'] = e_commerce_deliveries(df_cleaned)
        except Exception as e:
            print(f"  Error in e-commerce deliveries: {str(e)}")
        
        try:
            print("- Creating traditional deliveries dataset...")
            processed_datasets['traditional_deliveries'] = traditional_deliveries(df_cleaned)
        except Exception as e:
            print(f"  Error in traditional deliveries: {str(e)}")
        
        try:
            print("- Creating supply perception dataset...")
            processed_datasets['supply_perception'] = supply_perception(df_cleaned)
        except Exception as e:
            print(f"  Error in supply perception: {str(e)}")
        
        try:
            print("- Creating bike perception dataset...")
            processed_datasets['bike_perception'] = bike_perception(df_cleaned)
        except Exception as e:
            print(f"  Error in bike perception: {str(e)}")
        
        # Export processed datasets
        print("\nExporting processed datasets...")
        
        # Create a comprehensive Excel file with multiple sheets
        excel_processed_path = os.path.join(output_dir, "processed_datasets_for_r.xlsx")
        with pd.ExcelWriter(excel_processed_path, engine='openpyxl') as writer:
            # Export main cleaned dataset
            df_cleaned.to_excel(writer, sheet_name='main_cleaned_data', index=False)
            
            # Export each processed dataset
            for name, dataset in processed_datasets.items():
                if dataset is not None and not dataset.empty:
                    dataset.to_excel(writer, sheet_name=name, index=True)
                    print(f"  - Exported {name} dataset")
        
        # Also export individual CSV files for each processed dataset
        for name, dataset in processed_datasets.items():
            if dataset is not None and not dataset.empty:
                csv_path = os.path.join(output_dir, f"{name}_for_r.csv")
                dataset.to_csv(csv_path, index=True, encoding='utf-8')
        
        print("\nData summary:")
        print(f"Main dataset shape: {df_cleaned.shape}")
        print("\nColumn names:")
        for i, col in enumerate(df_cleaned.columns, 1):
            print(f"{i:2d}. {col}")
        
        print(f"\nFirst few rows of main dataset:")
        print(df_cleaned.head())
        
        print(f"\nData types:")
        print(df_cleaned.dtypes)
        
        print(f"\nMissing values per column:")
        missing_values = df_cleaned.isnull().sum()
        missing_percent = (missing_values / len(df_cleaned)) * 100
        missing_df = pd.DataFrame({
            'Missing_Count': missing_values,
            'Missing_Percent': missing_percent
        })
        missing_summary = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
        if not missing_summary.empty:
            print(missing_summary)
        else:
            print("No missing values found!")
        
        print(f"\nProcessed datasets summary:")
        for name, dataset in processed_datasets.items():
            if dataset is not None and not dataset.empty:
                print(f"- {name}: {dataset.shape}")
        
        return df_cleaned, processed_datasets
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return None, None


def main():
    """
    Main function to execute the data cleaning and export process.
    """
    print("=" * 80)
    print("ZUAP Survey Data Cleaning for R Analysis")
    print("=" * 80)
    
    # Create cleaned dataframe and export
    cleaned_df, processed_datasets = create_cleaned_df_for_r()
    
    if cleaned_df is not None:
        print("\n" + "=" * 80)
        print("Data cleaning and export completed successfully!")
        print("\nFiles ready for R analysis:")
        print("- Main dataset CSV: data/intermediate/cleaned_survey_for_r.csv")
        print("- Main dataset Excel: data/intermediate/cleaned_survey_for_r.xlsx")
        print("- Processed datasets Excel: data/intermediate/processed_datasets_for_r.xlsx")
        
        if processed_datasets:
            print("\nIndividual processed datasets (CSV):")
            for name in processed_datasets.keys():
                print(f"- data/intermediate/{name}_for_r.csv")
        
        print("\n" + "=" * 80)
        print("Usage in R:")
        print("# Load main dataset")
        print("library(readr)")
        print("df <- read_csv('data/intermediate/cleaned_survey_for_r.csv')")
        print("\n# Load specific processed datasets")
        print("temporal_data <- read_csv('data/intermediate/temporal_analysis_for_r.csv')")
        print("transport_data <- read_csv('data/intermediate/transportation_mode_for_r.csv')")
        print("# ... and so on for other datasets")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("Data cleaning failed. Please check the error messages above.")
        print("=" * 80)


if __name__ == "__main__":
    main()
