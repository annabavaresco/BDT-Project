#from Pazienti import Coda
import mysql.connector 
from Ospedali import Hospital
from Pazienti import Paziente
import json
from pprint import pprint

with open("Code_ps.json", "r") as f:
    cd = json.load(f)

cd[0]["arancio"].append("ciao")

with open("Code_ps.json", "w") as f:
    json.dump(cd, f)

def from_patient_to_dict(pat: Paziente):
    ret = {
        "id_paziente" : pat.id_paziente, #da definire meglio,
        "ospedale" : pat.ospedale,
        "colore" : pat.colore,
        "altri" : pat.altri,
        "più_gravi" : pat.più_gravi,
        "meno_gravi" : pat.meno_gravi,
        "t_inizio" : pat.t_inizio,
        "t_fine" : pat.t_fine,
        "durata": pat.durata
    }

    return ret

def from_dict_to_patient(d: dict):
    pat = Paziente(d["id_paziente"], #da definire meglio,
        d["ospedale"],
        d["colore"],
        d["altri"],
        d["più_gravi"],
        d["meno_gravi"],
        d["t_inizio"],
        d["t_fine"],
        d["durata"])
    
    return pat
    
def add_patient(pat, code, color):
    with open("Code_ps.json", "r") as f:
        hospitals = json.load(f)
    p = from_patient_to_dict(pat)
    hospitals[code][color].append(p)

    with open("Code_ps.json", "w") as f:
        json.dump(hospitals, f)
       
    
def remove_patient(num: int, end_timestamp, code, color):
    with open("Code_ps.json", "r") as f:
        hospitals = json.load(f)
    if num > len(hospitals[code][color]):
        raise Exception('Stai cercando di rimuovere più pazienti di quanti ce ne sono\
                in attesa!')
    if len(hospitals[code][color]) == 0:
        raise Exception('La coda è vuota, non è possibile rimuovere pazienti!')
    for i in range(num):
        p = hospitals[code][color].pop()
        p.t_fine = end_timestamp

        p.durata = p.t_fine - p.t_inizio
        connection = mysql.connector.connect(
            host = 'emergencyroom.ci8zphg60wmc.us-east-2.rds.amazonaws.com',
            port =  3306,
            user = 'admin',
            database = 'prova',
            password = 'emr00mtr3nt036'
            )

        connection.autocommit = True
        cursor = connection.cursor()

        query = "insert into pazienti_prova (id, colore, ospedale, inizio, fine, durata,\
            altri, più_gravi, meno_gravi)\
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(query, [p.id_paziente, p.colore, p.ospedale, p.t_inizio, p.t_fine, \
                        p.durata, p.altri,p.più_gravi, p.meno_gravi])
        connection.close()
        
    with open("Code_ps.json", "w") as f:
        json.dump(hospitals, f)
            
# fantastica_lista = ['mela', 'pera', 'pesca', 'banana']


        # "bianco" : [{"id" :  "P",
        #     "ospedale": "",
        #     "colore": "bianco",
        #     "altri": 2,
        #     "più gravi" : 1,
        #     "meno gravi": 0,
        #     "tstp inizio": ,
        #     "tstp fine": ,
        #     "durata" : }],