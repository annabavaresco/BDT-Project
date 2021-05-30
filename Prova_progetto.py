import requests
import json
import time
from pprint import pprint
from Ospedali import *
import mysql.connector 

resp = requests.get('https://servizi.apss.tn.it/opendata/STATOPS001.json')
hosp = resp.json()

ospedali = from_lod_to_los(hosp)

connection = mysql.connector.connect(
    host = 'emergencyroom.ci8zphg60wmc.us-east-2.rds.amazonaws.com',
    port =  3306,
    user = 'admin',
    database = 'prova',
    password = 'emr00mtr3nt036'
)

connection.autocommit = True
cursor = connection.cursor()

query = "insert into ers2 (timestamp, codice_ospedale, bianco_attesa,\
    bianco_gestione, verde_attesa,\
        verde_gestione, azzurro_attesa, azzurro_gestione, arancio_attesa,\
            arancio_gestione, rosso_attesa, rosso_gestione)\
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

for ospedale in ospedali:
    cursor.execute(query, [ospedale.timestamp, ospedale.codice, ospedale.in_attesa['bianco'],\
        ospedale.in_gestione['bianco'],\
             ospedale.in_attesa['verde'], ospedale.in_gestione['verde'], ospedale.in_attesa['azzurro'],\
                 ospedale.in_gestione['azzurro'], ospedale.in_attesa['arancio'], ospedale.in_gestione['arancio'],\
                     ospedale.in_attesa['rosso'], ospedale.in_gestione['rosso']])
connection.close()


