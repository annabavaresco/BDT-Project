from Ospedali import Hospital, InAttesa, InGestione
import mysql.connector 
from pprint import pprint


#TASSATVO CAPIRE COME RENDERE PIù EFFICIENTE GESTIONE COLORI
#'005-PS-PS'
#possiamo fare che nella funzione sotto il giorno deve per forza essere lunedì 
def estrai_dati_settimanali(giorno, codice_ospedale): 
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
             between '2021-05-05 00:00:00' AND '2021-05-12 23:59:59'"

    cursor.execute(query, [codice_ospedale])
    
    result = cursor.fetchall()
    
    connection.close()

    return result

def from_db_to_hospital(db_row):
    att = InAttesa(db_row[2], db_row[4], db_row[6], db_row[8], db_row[10], db_row[12])
    gest = InGestione(db_row[3], db_row[5], db_row[7], db_row[9], db_row[11], db_row[13])
    h = Hospital(db_row[1], gest, att, db_row[0])
    return h


class Paziente:
    def __init__(self, ospedale, colore, altri, più_gravi, meno_gravi, t_inizio, precedente):
        self.id_paziente = 'Gino' #da definire meglio
        self.ospedale = ospedale
        self.colore = colore
        self.altri = altri
        self.più_gravi = più_gravi
        self.meno_gravi = meno_gravi
        self.t_inizio = t_inizio
        self.t_fine = None
        self.durata = 0
        self.precedente = None

class Coda: 
    def __init__(self, colore, codice_ospedale):
        self.colore = colore
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
                    values (p.id_paziente, p.colore, p.ospedale, p.t_inizio, p.t_fine, \
                        p.durata, p.altri,p.più_gravi, p.meno_gravi)"

            cursor.execute(query)
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

def elabora_dati_settimanali(data, codice):

    #I dati settimanali vengono recuperati dalla tabella "ers2" e convertiti\
    #in oggetti della classe ospedale
    dati = estrai_dati_settimanali(data, codice) #ha senso fare quelli settimanali??
    ospedali = [from_db_to_hospital(dato) for dato in dati]

    #Creazione di una queue per ogni colore

    bianchi = Coda('bianco', codice)
    gialli = Coda('giallo', codice)
    verdi = Coda('verde', codice)
    azzurri = Coda('azzurro', codice)
    arancioni = Coda('arancio', codice)
    rossi = Coda('rosso', codice)

    #iteriamo per gli ospedali aggiungendo e rimuovendo pazienti dalla coda

    prec = ospedali[0]
    for ospedale in ospedali[1:]:
        #casi in cui bisogna aggiungere pazienti alla coda
        if ospedale.in_attesa.bianco > prec.in_attesa.bianco:
            aum_att = ospedale.in_attesa.bianco - prec.in_attesa.bianco
            
            #Sono aumentati sia in attesa che in gestione
            if ospedale.in_gestione.bianco > prec.in_gestione.bianco:
                aum_gest = ospedale.in_gestione.bianco - prec.in_gestione.bianco
                n = aum_gest + aum_att

                for i in range(n):
                    bianchi.add(PAZIENTE)

                bianchi.remove(aum_gest, ospedale.timestamp)
            
            #Sono aumentati in attesa ma non in gestione
            else:
                n = aum_att
            
                for i in range(n):
                    bianchi.add(PAZIENTE)# definire il paziente
        
        elif ospedale.in_attesa.bianco == prec.in_attesa.bianco:
            if ospedale.in_gestione.bianco > prec.in_gestione.bianco:
                aum_gest = ospedale.in_gestione.bianco - prec.in_gestione.bianco

                for i in range(aum_gest):
                    bianchi.add(PAZIENTE) # definire il paziente
                
                bianchi.remove(aum_gest, ospedale.timestamp)
        
        else:
            dim_att = prec.in_attesa.bianco - ospedale.in_attesa.bianco
            if ospedale.in_gestione.bianco > prec.in_gestione.bianco:
                aum_gest = ospedale.in_gestione.bianco - prec.in_gestione.bianco
                n = aum_gest - dim_att

                for i in range(n):
                    bianchi.add(PAZIENTE)
                
                bianchi.remove(aum_gest, ospedale.timestamp)
            
            else:
                bianchi.remove(dim_att, ospedale.timestamp)
            
        prec = ospedale