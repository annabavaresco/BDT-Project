from mysql.connector.constants import _obsolete_option
from Ospedali import Hospital
import mysql.connector 
from pprint import pprint
from datetime import datetime, timedelta

#TASSATVO CAPIRE COME RENDERE PIù EFFICIENTE GESTIONE COLORI
#'005-PS-PS'
#possiamo fare che nella funzione sotto il giorno deve per forza essere lunedì

GIORNO = datetime.strptime('2021-05-04 19:10:00', '%Y-%m-%d %H:%M:%S')
   
def estrai_dati(giorno_inizio, codice_ospedale): 
    connection = mysql.connector.connect(
    host = 'emergencyroom.ci8zphg60wmc.us-east-2.rds.amazonaws.com',
    port =  3306,
    user = 'admin',
    database = 'prova',
    password = 'emr00mtr3nt036'
)

    connection.autocommit = True
    cursor = connection.cursor()

    query = "SELECT * FROM prova.ers2 WHERE codice_ospedale = %s AND timestamp \
             between %s AND %s"

    oggi = datetime.strptime('2021-06-12 10:40:00', '%Y-%m-%d %H:%M:%S')
    cursor.execute(query, [codice_ospedale, giorno_inizio, oggi])
    
    result = cursor.fetchall()
    
    connection.close()

    return result

def from_db_to_hospital(db_row):
    att = {'bianco':db_row[2], 'verde': db_row[6], \
        'azzurro': db_row[8], 'arancio': db_row[10], 'rosso': db_row[12]}
    gest = {'bianco': db_row[3], 'verde': db_row[7],\
        'azzurro': db_row[9], 'arancio': db_row[11], 'rosso': db_row[13]}
    h = Hospital(db_row[1], gest, att, db_row[0])
    return h


class Paziente:
    def __init__(self, ospedale, colore, altri, più_gravi, meno_gravi, t_inizio, precedente = None):
        self.id_paziente = 'P' #da definire meglio
        self.ospedale = ospedale
        self.colore = colore
        self.altri = altri
        self.più_gravi = più_gravi
        self.meno_gravi = meno_gravi
        self.t_inizio = t_inizio
        self.t_fine = None
        self.durata = 0
        self.precedente = precedente

class Coda: 
    def __init__(self, codice_ospedale):
        self.codice_ospedale = codice_ospedale
        self.testa = None
        self.coda = None
        self.lungh = 0
    
    def add(self, paziente: Paziente):
        if self.lungh == 0:
            self.testa = paziente
            self.coda = paziente
            self.lungh = 1
        elif self.lungh == 1: 
            self.coda = paziente
            paziente.precedente = self.testa
            self.lungh = 2
        else:
            paziente.precedente = self.coda
            self.coda = paziente
            self.lungh += 1
    
    def remove(self, num: int, timestamp_fine):
        if num > self.lungh:
            raise Exception('Stai cercando di rimuovere più pazienti di quanti ce ne sono\
                in attesa!')
        if self.lungh == 0:
            raise Exception('La coda è vuota, non è possibile rimuovere pazienti!')
        for i in range(num):
            p = self.coda
            p.t_fine = timestamp_fine

            #Verificare che questo tipo di operazione si possa fare con le timestamp
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
            
            if self.lungh == 1 :
                self.testa = None
                self.coda = None
                self.lungh = 0
            elif self.lungh == 2:
                p.precedente = None
                self.coda = self.testa
                self.lungh -= 1
            else:
                self.coda = p.precedente
                p.precedente = None
                self.lungh -= 1

#Già testata e funziona
def comp_più_gravi(colore, ospedale):
    #dato un oggetto della classe ospedale, calcola quanti pazienti in attesa sono più gravi
    # di quello del parametro 'colore'
    col_list = ['verde', 'azzurro', 'arancio', 'rosso']
    res = 0
    if colore == 'bianco':
        for c in col_list:
            res += ospedale.in_attesa[c]
    elif colore == 'verde':
        for c in col_list[1:]:
            res += ospedale.in_attesa[c]
    elif colore == 'azzurro':
        for c in col_list[2:]:
            res += ospedale.in_attesa[c]
    elif colore == 'arancio':
        res += ospedale.in_attesa['rosso']
    return res


#Già testata e funziona
def comp_meno_gravi(colore, ospedale):
    #dato un oggetto della classe ospedale, calcola quanti pazienti in attesa sono meno gravi
    # di quello del parametro 'colore'
    col_list = ['arancio', 'azzurro', 'verde', 'bianco']
    res = 0
    if colore == 'rosso':
        for c in col_list:
            res += ospedale.in_attesa[c]
    elif colore == 'arancio':
        for c in col_list[1:]:
            res += ospedale.in_attesa[c]
    elif colore == 'azzurro':
        for c in col_list[2:]:
            res += ospedale.in_attesa[c]
    elif colore == 'verde':
        res += ospedale.in_attesa['bianco']
    
    return res

def comp_stesso_colore(colore, ospedale):
    res = 0
    if ospedale.in_attesa[colore]>1:
        res += ospedale.in_attesa[colore]-1
    return res


def elabora_dati(dati, codice):
    #I parametri indicano la data di inizio settimana e il codice dell'ospedali per cui si
    #vogliono estrarre i dati. 

    #I dati settimanali vengono recuperati dalla tabella "ers2" e convertiti\
    #in oggetti della classe ospedale

    ospedali = [from_db_to_hospital(dato) for dato in dati]

    #Creazione di una queue per ogni colore
    code_ospedale = {'bianco': Coda(codice), 'giallo': Coda(codice), 'verde':Coda(codice),\
        'azzurro': Coda(codice), 'arancio': Coda(codice), 'rosso': Coda(codice)}

    #iteriamo per gli ospedali aggiungendo e rimuovendo pazienti dalla coda
    #tra i colori manca il giallo perché in realtà non ci dovrebbe essere nemmeno sul json
    #iniziale, i colori ufficiali dei ps sono 5
    cols = ['bianco', 'verde', 'azzurro', 'arancio', 'rosso']
    prec = ospedali[0]
    
    #Iniziamo le code inserendo in ognuna il numero di pazienti che c'erano in attesa al 
    # momento della prima timestamp. Il timestamp di inizio putroppo non sarà accurato,
    # però non ci si può fare niente
    for col in cols:
        num_att = prec.in_attesa[col]
        for i in range(num_att):
            code_ospedale[col].add(Paziente(codice, col, \
                            comp_stesso_colore(col, prec),comp_più_gravi(col, prec),\
                                comp_meno_gravi(col, prec), prec.timestamp))
    # Adesso iteriamo per gli ospedali successivi al primo e inseriamo i pazienti in modo
    # un po' più preciso
    for ospedale in ospedali[1:]:
        
        for col in cols:
        #casi in cui bisogna aggiungere pazienti alla coda
            if ospedale.in_attesa[col] > prec.in_attesa[col]:
                aum_att = ospedale.in_attesa[col] - prec.in_attesa[col]
            
                #Sono aumentati sia in attesa che in gestione
                if ospedale.in_gestione[col] > prec.in_gestione[col]:
                    aum_gest = ospedale.in_gestione[col] - prec.in_gestione[col]
                    n = aum_gest + aum_att

#    def __init__(self, ospedale, colore, altri, più_gravi, meno_gravi, t_inizio, precedente):

                    for i in range(n):
                        code_ospedale[col].add(Paziente(codice, col, \
                            comp_stesso_colore(col, ospedale),comp_più_gravi(col, ospedale),\
                                comp_meno_gravi(col, ospedale), ospedale.timestamp))

                    code_ospedale[col].remove(aum_gest, ospedale.timestamp)
            
            #Sono aumentati in attesa ma non in gestione
                else:
                    n = aum_att
            
                    for i in range(n):
                        code_ospedale[col].add(Paziente(codice, col, \
                            comp_stesso_colore(col, ospedale),comp_più_gravi(col, ospedale),\
                                comp_meno_gravi(col, ospedale), ospedale.timestamp))
        
            elif ospedale.in_attesa[col] == prec.in_attesa[col]:
                if ospedale.in_gestione[col] > prec.in_gestione[col]:
                    aum_gest = ospedale.in_gestione[col] - prec.in_gestione[col]

                    for i in range(aum_gest):
                        code_ospedale[col].add(Paziente(codice, col, \
                            comp_stesso_colore(col, ospedale),comp_più_gravi(col, ospedale),\
                                comp_meno_gravi(col, ospedale), ospedale.timestamp))
                
                    code_ospedale[col].remove(aum_gest, ospedale.timestamp)
        
            else:
                dim_att = prec.in_attesa[col] - ospedale.in_attesa[col]
                if ospedale.in_gestione[col] > prec.in_gestione[col]:
                    aum_gest = ospedale.in_gestione[col] - prec.in_gestione[col]
                    n = aum_gest - dim_att

                    for i in range(n):
                        code_ospedale[col].add(Paziente(codice, col, \
                            comp_stesso_colore(col, ospedale),comp_più_gravi(col, ospedale),\
                                comp_meno_gravi(col, ospedale), ospedale.timestamp))
                
                    code_ospedale[col].remove(aum_gest, ospedale.timestamp)
            
                else:
                    code_ospedale[col].remove(dim_att, ospedale.timestamp)
            
        prec = ospedale

DATI = estrai_dati(GIORNO, '014-PS-PS')
elabora_dati(DATI, '014-PS-PS')