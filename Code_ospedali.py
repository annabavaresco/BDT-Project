#from Pazienti import Coda
import mysql.connector 
from Ospedali import *
from Pazienti import Paziente, comp_meno_gravi, comp_piu_gravi, comp_stesso_colore
import requests
import json
from pprint import pprint
import time

def from_patient_to_dict(pat: Paziente):
    ret = {
        "id_paziente" : pat.id_paziente, #da definire meglio,
        "ospedale" : pat.ospedale,
        "colore" : pat.colore,
        "altri" : pat.altri,
        "piu_gravi" : pat.piu_gravi,
        "meno_gravi" : pat.meno_gravi,
        "t_inizio" : str(pat.t_inizio),
        "t_fine" : str(pat.t_fine),
        "durata": pat.durata
    }

    return ret

def from_dict_to_patient(d: dict):
    pat = Paziente(d["id_paziente"], #da definire meglio,
        d["ospedale"],
        d["colore"],
        d["altri"],
        d["piu_gravi"],
        d["meno_gravi"],
        datetime.strptime(d["t_inizio"], '%Y-%m-%d %H:%M:%S'),
        d["t_fine"],
        d["durata"])
    
    return pat

def from_loh_to_dict(hospitals):
    '''
    Takes as input a list of hospitals (meaning instances of the class "Ospedale") and returns
    a dict where each key is the code of the hospital.
    '''
    ret = dict()
    for h in hospitals:
        ret[h.codice] = {"in_attesa": h.in_attesa, "in_gestione": h.in_gestione,
        "timestamp": h.timestamp}
    return ret
    
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
        p = hospitals[code][color].pop(0)
        p.t_fine = str(end_timestamp)

        p.durata = str(p.t_fine - datetime.strptime(p.t_inizio, '%Y-%m-%d %H:%M:%S'))
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
            altri, piu_gravi, meno_gravi)\
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(query, [p.id_paziente, p.colore, p.ospedale, p.t_inizio, p.t_fine, \
                        p.durata, p.altri,p.piu_gravi, p.meno_gravi])
        connection.close()
        
    with open("Code_ps.json", "w") as f:
        json.dump(hospitals, f)
            

def get_prev():
    with open("prev_hosp.json", "r") as f:
        ret = json.load(f)
    
    return ret


def set_prev(hospitals: dict):
    '''
    Takes as input a dict where each key is the code associated with a hospital and writes
    it in the json file "prev_hosp.json"
    ''' 

    with open("prev_hosp.json", "w") as f:
        json.dump(hospitals, f)



def elabora_dati():

    colors = ['bianco', 'verde', 'azzurro', 'arancio', 'rosso']
    codes = ['001-PS-PSC','001-PS-PSG','001-PS-PSO','001-PS-PSP','001-PS-PS','006-PS-PS',\
        '007-PS-PS','010-PS-PS','004-PS-PS','014-PS-PS','005-PS-PS']

    prev_data_dict = get_prev()

    if len(prev_data_dict) == 0:
        prev_raw_data = requests.get('https://servizi.apss.tn.it/opendata/STATOPS001.json').json()
        prev_data_list = [from_dict_to_hosp(h) for h in prev_raw_data]
        
        for h in prev_data_list:
            for c in colors:
                n = h.in_attesa[c]
                
                p = Paziente(h.codice, c, comp_stesso_colore(c, h.in_attesa),\
                    comp_piu_gravi(c, h.in_attesa),\
                            comp_meno_gravi(c, h.in_attesa), str(h.timestamp))

                for i in range(n):
                    add_patient(p, h.codice, c)
                
                time.sleep(600)
    
    current_raw_data = requests.get('https://servizi.apss.tn.it/opendata/STATOPS001.json').json()
    current_data_list = [from_dict_to_hosp(h) for h in current_raw_data]
    current = from_loh_to_dict(current_data_list)
    prev = from_loh_to_dict(prev_data_list)

    # Adesso iteriamo per gli ospedali successivi al primo e inseriamo i pazienti in modo
    # un po' più preciso
    for c in codes:
        for col in colors:
        #casi in cui bisogna aggiungere pazienti alla coda
            if current[c]['in_attesa'][col] > prev[c]['in_attesa'][col]:
                aum_att = current[c]['in_attesa'][col] - prev[c]['in_attesa'][col]
            
                #Sono aumentati sia in attesa che in gestione
                if current[c]['in_gestione'][col] > prev['in_gestione'][col]:
                    aum_gest = current[c]['in_gestione'][col] - prev['in_gestione'][col]
                    n = aum_gest + aum_att

#    def __init__(self, ospedale, colore, altri, più_gravi, meno_gravi, t_inizio, precedente):

                    for i in range(n):
                        add_patient(Paziente(c, col, comp_stesso_colore(col, current['in_attesa']),\
                            comp_piu_gravi(col, current['in_attesa']),\
                                comp_meno_gravi(col, current['in_attesa']), current['timestamp']),c,col)

                    remove_patient(aum_gest, current['timestamp'], c, col)
            
            #Sono aumentati in attesa ma non in gestione
                else:
                    n = aum_att
            
                    for i in range(n):
                        add_patient(Paziente(c, col, comp_stesso_colore(col, current['in_attesa']),\
                            comp_piu_gravi(col, current['in_attesa']),\
                                comp_meno_gravi(col, current['in_attesa']), current['timestamp']), c, col)
        
            elif current['in_attesa'][col] == prev['in_attesa'][col]:
                if current['in_gestione'][col] > prev['in_gestione'][col]:
                    aum_gest = current['in_gestione'][col] - prev['in_gestione'][col]

                    for i in range(aum_gest):
                        add_patient(Paziente(c, col, comp_stesso_colore(col, current['in_attesa']),\
                            comp_piu_gravi(col, current['in_attesa']),\
                                comp_meno_gravi(col, current['in_attesa']), current['timestamp']), c, col)
                
                    remove_patient(aum_gest, current['timestamp'], c, col)
        
            else:
                dim_att = prev['in_attesa'][col] - current['in_attesa'][col]
                if current['in_attesa'][col] > prev['in_gestione'][col]:
                    aum_gest = current['in_gestione'][col] - prev['in_gestione'][col]
                    n = aum_gest - dim_att

                    for i in range(n):
                        add_patient(Paziente(c, col, comp_stesso_colore(col, current['in_attesa']),
                        comp_piu_gravi(col, current['in_attesa']),\
                                comp_meno_gravi(col, current['in_attesa']), current['timestamp']), c, col)
                
                    remove_patient(aum_gest, current['timestamp'], c, col)
            
                else:
                    remove_patient(dim_att, current['timestamp'])
            
    set_prev(current)

elabora_dati()
