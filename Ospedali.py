from datetime import datetime




class InGestione:
    def __init__(self, bianco: int, giallo: int, verde: int, azzurro: int, arancio: int, rosso: int):
        self.arancio = arancio
        self.azzurro = azzurro
        self.bianco = bianco
        self.giallo = giallo
        self.rosso = rosso
        self.verde = verde

class InAttesa:
    def __init__(self, bianco: int, giallo: int, verde: int, azzurro: int, arancio: int, rosso: int):
        self.arancio = arancio
        self.azzurro = azzurro
        self.bianco = bianco
        self.giallo = giallo
        self.rosso = rosso
        self.verde = verde

class Hospital:

    def __init__(self, code: str, in_gestione: InGestione, in_attesa: InAttesa, timestamp):
        
        self.in_attesa = in_attesa
        self.codice = code
        self.in_gestione = in_gestione
        self.timestamp = timestamp



def from_dict_to_hosp(ospedale):
    att = InAttesa(int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['bianco']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['giallo']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['verde']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['azzurro']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['arancio']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['attesa']['rosso'])) 

    
    gest = InGestione(int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['bianco'])+
                     int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['bianco']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['giallo'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['giallo']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['verde'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['verde']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['azzurro'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['azzurro']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['arancio'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['arancio']),
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['ambulatorio']['rosso'])+
                    int(ospedale['risposta']['pronto_soccorso']['reparto']['osservazione']['rosso']))  


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


