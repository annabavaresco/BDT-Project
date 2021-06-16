from datetime import datetime, timedelta
import requests
import json
from pprint import pprint


class Hospital:

    def __init__(self, code: str, in_gestione: dict(), in_attesa: dict(), timestamp):
        
        self.in_attesa = in_attesa
        self.codice = code
        self.in_gestione = in_gestione
        self.timestamp = timestamp



def from_dict_to_hosp(ospedale):
    att = {'bianco':int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['bianco']),\
            'verde': int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['verde']),\
                'azzurro': int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['azzurro']),\
                    'arancio': int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['arancio']),\
                        'rosso': int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['rosso'])}

    
    gest = {'bianco':int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['bianco'])+
                     int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['bianco']),\
                        'verde': int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['verde'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['verde']),\
                        'azzurro': int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['azzurro'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['azzurro']),\
                        'arancio': int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['arancio'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['arancio']),\
                        'rosso': int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['rosso'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['rosso'])} 


    ret = Hospital(ospedale['risposta']['pronto_soccorso']['reparto']['codice'],
                    gest,
                    att,
                    datetime.strptime(ospedale['risposta']['timestamp'].replace(' ore',''), "%d/%m/%Y %H:%M"),         
    )
    return ret

def from_lod_to_los(lista_di_dizionari):
    ret = []
    for dizionario in lista_di_dizionari:
        ret.append(from_dict_to_hosp(dizionario))
    return ret

resp = requests.get('https://servizi.apss.tn.it/opendata/STATOPS001.json')
hosp = resp.json()
#pprint(hosp[0])
h = from_dict_to_hosp(hosp[0])
#print(type(h.timestamp))
#dt1 = datetime.strptime('2021-05-30 11:30:00',"%d/%m/%Y %H:%M")
#dt2 = '2021-05-30 11:40:00'
#print(type(dt1))
c = ['azzurro', 'arancio']
#from datetime import datetime

