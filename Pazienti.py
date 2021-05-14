from Ospedali import Hospital, InAttesa, InGestione
import mysql.connector 
from pprint import pprint
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
    def __init__(self, ospedale, colore, altri, più_gravi, meno_gravi, t_inizio, t_fine, precedente):
        self.id_paziente = 'Gino' #da definire meglio
        self.ospedale = ospedale
        self.colore = colore
        self.altri = altri
        self.più_gravi = più_gravi
        self.meno_gravi = meno_gravi
        self.t_inizio = t_inizio
        self.t_fine = t_fine
        self.durata = t_fine-t_inizio
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
    
    def remove(self, num: int):
        if num > self.lungh:
            raise Exception('Stai cercando di rimuovere più pazienti di quanti ce ne sono\
                in attesa!')
        if self.lungh == 0:
            raise Exception('La coda è vuota, non è possibile rimuovere pazienti!')
        for i in range(num):
            p = self.coda
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

    