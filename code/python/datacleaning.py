# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 13:33:19 2023

@author: Mario
"""

import pandas as pd
import numpy as np

df = pd.read_excel("C:/Users/Mario/Documents/UN/03. Research Group/01. CBD/zuap_survey.xlsx")

#Non informative columns that won´t be considered in the analysis

col_out = ['id', 'db', 'Marca temporal', 'Correo electrónico', 'Teléfono de contacto',
           '¿En su empresa o comercio cuentan con colaboradoras mujeres?',
           'Porcentaje mujeres','% mujeres en la distribución','% mujeres vinculadas','Ir al fin de la encuesta.',
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

df = df.drop(col_out, axis = 1)

#Lowercase column names

df.columns = df.columns.str.lower()

#Change variables names for facility

c_ch = {'nombre de la empresa': 'company', 
        'dirección de la empresa': 'address',
        'por favor indique el número de colaboradores que tiene su empresa o comercio': 'employees',
        'por favor indique el número de mujeres que trabajan en su empresa o comercio': 'women_employees',
        'de sus empleadas mujeres, ¿cuántas hacen parte de la cadena de distribución del negocio (conducen, reparten domicilios, acompañan las entregas, etc.)?': 'woman_emplo_distri',
        'de las mujeres vinculadas a la cadena logística de su empresa o comercio ¿cuántas están vinculadas por contrato laboral?': 'we_distri_vincu',
        'entre sus colaboradoras mujeres, alguna(s) se identifica(n) con los siguientes grupos poblacionales:': 'we_popg',
        '¿acompañan y/o apoyan el proceso formativo de las mujeres que hacen parte de la cadena logística?': 'we_support',
        'por favor, indique dentro de la siguientes categorías, cuál se relaciona con la actividad realizada en su comercio:': 'economic_activity',
        'de acuerdo al listado señale en orden de importancia las 3 principales actividades comerciales que se desarrollan en su establecimiento:': 'spec_activity',
        'productos principales': 'main_products',
        '¿su establecimiento cuenta con espacio de bodega o almacenamiento de mercancías o productos?': 'storage_space',
        '¿con cuántos espacios de bodega cuenta?': 'storage_space_quantity',
        '¿en qué piso se ubica(n) la(s) bodegas que sirven a su empresa o comercio?': 'storage_floor',
        'por favor, indique el área de la bodega que sirve a su comercio en metros cuadrados:': 'storage_area',
        'por favor, indique la altura en metros de la bodega que sirve a su comercio:': 'storage_height',
        '¿el(los) espacio(s) de bodega están ubicados al interior de la zuap?': 'zuap_storage',
        '¿en qué municipio se encuentra ubicada la bodega que sirve a su comercio?': 'storage_muni',
        'por favor, indique el tipo de bodega con la que cuenta:': 'storage_type',
        'por favor, seleccione los días en los cuales recibe materiales, materias primas o productos:': 'supply_day',
        '¿cuántas veces por semana abastece su establecimiento?': 'supply_week',
        'por favor, indique los horarios durante los cuales realiza las actividades de cargue y descargue de las mercancías:': 'supply_schedule',
        'por favor, indique la forma en la que ingresa la mercancía a su comercio o área de bodega:': 'supply_entrance',
        'en una escala de 1 a 5, donde 1 es "muy inseguro" y 5 "muy seguro", ¿considera usted que el proceso de cargue y descargue de mercancías en camión, carro o motocicleta es?': 'supply_safety_percep',
        'en una escala de 1 a 5, donde 1 es "muy inseguro" y 5 "muy seguro", ¿considera usted que el proceso de cargue y descargue de mercancías en bicicleta es?': 'supply_bic_safety_perception',
        '¿el establecimiento o bodega posee alguno de los siguientes elementos para el cargue y descargue de mercancías?': 'storage_equipement',
        '¿qué medio realiza para el envío de sus artículos a domicilio?': 'delivery_mean',
        '¿cuántos domicilios realiza a diario su establecimiento?': 'num_delivery',
        '¿qué medio realiza para el envío de sus ventas por internet?': 'online_mean',
        '¿cuántos envíos de artículos vendidos por internet realiza a diario su establecimiento?': 'num_online'}

df = df.rename(columns = c_ch)

###############Woman category

#Keep main economic activity

values2 = ['Fabricante', 'Proveedor', 'Venta al detalle', 'Ventas por internet', 'Transportador']

conditions2 = list(map(df['economic_activity'].str.contains, values2))

df['economic_activity2'] = np.select(conditions2, values2, None)

#Storage type

df['storage_type'] = df['storage_type'].replace({'Otro ¿cuál?': np.nan})

#Create a column to identify the supply on typical days

cond1 = df['supply_day'].str.contains('Martes')
cond2 = df['supply_day'].str.contains('Miércoles')
cond3 = df['supply_day'].str.contains('Jueves')

df['typday_supply'] = np.where(cond1, 1, np.where(cond2, 1, np.where(cond3, 1, 0)))

#Determine the typical schedules within ZUAP

df['supply_schedule'] = df['supply_schedule'].str.replace(':00', '')

##########Revisar los horarios con más detalle

#Typical vehicle used on the supply

cond4 = df['supply_entrance'].str.contains('camión')
cond5 = df['supply_entrance'].str.contains('motocicleta')
cond6 = df['supply_entrance'].str.contains('bicicleta')
cond7 = df['supply_entrance'].str.contains('carreta')
cond8 = df['supply_entrance'].str.contains('particular')

df['truck_supply'] = np.where(cond4, 1, 0)
df['moto_supply'] = np.where(cond5, 1, 0)
df['bike_supply'] = np.where(cond6, 1, 0)
df['wagon_supply'] = np.where(cond7, 1, 0)
df['auto_supply'] = np.where(cond8, 1, 0)

#Truck's unloading in the ZUAP zone

cond9 = df['supply_entrance'].str.contains('internamente')
cond10 = df['supply_entrance'].str.contains('transportadora')
cond11 = df['supply_entrance'].str.contains('empresa')
cond12 = df['supply_entrance'].str.contains('vía')
cond13 = df['supply_entrance'].str.contains('andén')
cond14 = df['supply_entrance'].str.contains('aledañas')
cond15 = df['supply_entrance'].str.contains('propiedad')

df['internal_truck_un'] = np.where(cond9, 1, 0)
df['bay_truck_un'] = np.where(cond10, 1, 0)
df['bay_personal_truck_un'] = np.where(cond11, 1, 0)
df['road_truck_un'] = np.where(cond12, 1, 0)
df['sidewalk_truck_un'] = np.where(cond13, 1, 0)
df['near_road_truck_un'] = np.where(cond14, 1, 0)
df['parklot_truck_un'] = np.where(cond15, 1, 0)

#Equipement to load/unload in the establishment or in the storage area

cond16 = df['storage_equipement'].str.contains('Carretilla')
cond17 = df['storage_equipement'].str.contains('Elevador')
cond18 = df['storage_equipement'].str.contains('Rampa mecánica')
cond19 = df['storage_equipement'].str.contains('Rampa fija')
cond20 = df['storage_equipement'].str.contains('Porta doble')
cond21 = df['storage_equipement'].str.contains('interno')
cond22 = df['storage_equipement'].str.contains('clientes')

df['wagon_storage'] = np.where(cond16, 1, 0)
df['elevator_storage'] = np.where(cond17, 1, 0)
df['mecramp_storage'] = np.where(cond18, 1, 0)
df['fixramp_storage'] = np.where(cond19, 1, 0)
df['intparking_storage'] = np.where(cond21, 1, 0)
df['custparking_storage'] = np.where(cond22, 1, 0)

#Correct the number of delivery based on the establishment answer

cond23 = df['delivery_mean'].str.contains('No se realizan')

df['delivery_mean_correct'] = np.where(cond23, 1, 0)

df['num_delivery_corrected'] = df['delivery_mean_correct'].map(lambda x: 0 if x == 1 else x)

df.to_csv('clean_survey.csv')