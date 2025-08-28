import os
import sys
import numpy as np
from math import log2 
import random
from IPython.display import Image

# -------------------------------------------
# - COSTANTI
#   • PCHS (tuple)         = contiene i simboli delle altezze in formato lilypond
#   • DURS (tuple di dict) = {ratio:simbolo}
#   • VELS (tuple)         = contiene i simboli delle dinamiche in formato lilypond
#   • EXPR (Dict)          = contiene i simboli delle espressioni in formato lilypond
# -------------------------------------------
# - FUNZIONI:
#   • mapPitch([60,64,67])        -1 = pausa, -2 = spazio (anche singolo int)
#   • mapDur([4, 8, [4,[3,2]]])   00 = valore precedente (anche singolo int)
#   • mapVel([127,64])            00 = senza simbolo (anche singolo int)
#   • mapExp([">","."])           00 = senza simbolo (anche singolo int)
#   • l_mod([34,45,56], 5)        target >= list, se < riporta la lista originale
#   • l_zero([34,00,56], 5)       target >= list, se < riporta la lista originale
#   • dflt(None)                   None, int, lista = crea lista o aggiunge 'zero' alla fine
# -------------------------------------------
# - CLASSI:
#   • _Map(note=[60], dur=[4], vel=[64], exp=[">"])
#                       .note --> recupera lista di altezze
#                       .dur  --> recupera lista di durate
#                       .vel  --> recupera lista di velocities
#                       .exp  --> recupera lista di espressioni
#                       .max  --> rsize della lista più grande

#   • _Print(filename="score", format="pdf", version="2.24.3")
#                       .print_out --> stampa la stringa nel terminale
#                       .make_file --> genera tre files
#
#   • _Voice(note=60, dur=None, vel=None, exp=None,
#            filename="score", format="pdf", version="2.24.3")  --> ereditati dal _Print 
#                       .out       --> genera una stringa in output
#                       .print_out --> stampa la stringa nel terminale
#                       .make_file --> genera tre files)  
#
#   • Staff(voice=lista di Voice,
#           key=None, t_sig=None, clef=None,
#           i_name=None, i_short=None, i_midi=None,
#           filename="score", format="pdf", version="2.24.3") --> ereditati dal _Print 
#                       .out       --> genera una stringa in output
#                       .print_out --> stampa la stringa nel terminale
#                       .make_file --> genera tre files
#   • Score(staff=Nlista di Staff,
#           staff_size=None, indent=None, s_indent=None,
#           title=None, composer=None,
#           size="a4landscape", margins=(10,10,10,10),
#           filename="score", format="pdf", version="2.24.3") --> ereditati da _Print
#                       .out       --> genera una stringa in output
#                       .print_out --> stampa la stringa nel terminale
#                       .make_file --> genera tre files

# -------------------------------------------
# - COSTANTI
#         0       1        2       3        4       5       6        7       8        9       10       11 ...
PCHS = ('c,,,,','cs,,,,','d,,,,','ds,,,,','e,,,,','f,,,,','fs,,,,','g,,,,','gs,,,,','a,,,,','as,,,,','b,,,,', 
        'c,,,', 'cs,,,', 'd,,,', 'ds,,,', 'e,,,', 'f,,,', 'fs,,,', 'g,,,', 'gs,,,', 'a,,,', 'as,,,', 'b,,,', 
        'c,,',  'cs,,',  'd,,',  'ds,,',  'e,,',  'f,,',  'fs,,',  'g,,',  'gs,,',  'a,,',  'as,,',  'b,,', 
        'c,',   'cs,',   'd,',   'ds,',   'e,',   'f,',   'fs,',   'g,',   'gs,',   'a,',   'as,',   'b,', 
        'c ',   'cs ',   'd ',   'ds ',   'e ',   'f ',   'fs ',   'g ',   'gs ',   'a ',   'as ',   'b ', 
        "c'",   "cs'",   "d'",   "ds'",   "e'",   "f'",   "fs'",   "g'",   "gs'",   "a'",   "as'",   "b'", 
        "c''",  "cs''",  "d''",  "ds''",  "e''",  "f''",  "fs''",  "g''",  "gs''",  "a''",  "as''",  "b''", 
        "c'''", "cs'''", "d'''", "ds'''", "e'''", "f'''", "fs'''", "g'''", "gs'''", "a'''", "as'''", "b'''", 
        "c''''","cs''''","d''''","ds''''","e''''","f''''","fs''''","g''''","gs''''","a''''","as''''","b''''", 
        "c'''''","cs'''''","d'''''","ds'''''","e'''''","f'''''","fs'''''","g'''''","gs'''''","a'''''",
        "as'''''","b'''''", "c''''''", "cs''''''", "d''''''", "ds''''''", "e''''''", "f''''''", "fs''''''", 
        "g''''''", "gs''''''", "a''''''", "as''''''", "b''''''")
#          123        124         125        126         127  

STEPS = ( '32',    '16',   '16.', '8',   # simboli lilypond
        '8~32',  '8.',   '8..',   '4',    
        '4~32',  '4~16', '4~16.', '4.',   
        '4.~32', '4..',  '4...', '2',                                                                
        '2~32',  '2~16', '2~16.', '2~8',  
        '2~8~32','2~8.', '2~8..', '2.',   
        '2.~32', '2.~16','2.~16.','2..',  
        '2..~32','2...', '2....', '1')
REGOLA = 1/32  * np.arange(1,33,1)                # tempi assoluti regolari
RATIOS = (1/1,3/2,5/4,6/4,7/4,9/8,11/8,13/8,15/8) # tempi assoluti regolari e irregolari
VALS = [REGOLA/i for i in RATIOS]
DURS = ({}, {},     {},      {},      {},      {},      {},       {},       {})
for n in range(len(VALS)): 
    for i in range(32):
        DURS[n][np.round(VALS[n][i], decimals=5)] = STEPS[i] 

VELS = ('\\ppppp','\\pppp','\\ppp','\\pp','\\p','\\mp','\\mf','\\f','\\ff','\\fff','\\ffff','\\fffff')
EXPR = {
    # Articolazioni
    '>':   '->',     # accent
    '^':   '-^',     # marcato
    '!':   '-!',     # staccato secco
    '.':   '-.',     # staccato
    '_':   '-_',     # tenuto
    '-':   '--',     # legato
    'tie': '~',      # legatura di nota
   
    # Dinamica espressiva
    'expr': '\\espressivo',

    # Ornamenti e abbellimenti
    'tr':        '\\trill',      # trillo
    'm':         '\\mordent',    # mordente
    'cor':       '\\fermata',    # fermata
    'turn':      '\\turn',       # gruppetto
    'arpeggio':  '\\arpeggio',   # arpeggio

    # Glissando e hairpins
    'glissando': '\\glissando',  # glissando
    'cresc':     '\\<',          # inizio crescendo hairpin
    'dim':       '\\>',          # inizio diminuendo hairpin
    'end':       '\\!',          # chiusura hairpin

    # Respiri e arcate
    'breathe':   '\\breathe',    # segno di respiro
    'upbow':     '\\upbow',      # arcata in su
    'downbow':   '\\downbow',    # arcata in giù

    # Armonici
    'harmonic':       '\\harmonic',   # armonico naturale o artificiale
    'flageolet':      '\\flageolet',  # flageolet

    # Pizzicati come markup text
    'pizzicato':      '^\\markup { "pizz." }',          # pizzicato
    'bartokPizz':     '^\\snappizzicato',   # pizzicato Bartók


    00:          '',        # nessuna espressione
    '': '',
    '!':'\\!',
}
# -------------------------------------------
# - FUNZIONI:

def mapPitch(a):
        '''
        Midinote --> Simboli Lilypond
        0-127 -1 = pausa, -2 = spazio, 00 = valore precedente
        IN:  list (int) 
        OUT: list (string) 
        '''
        if type(a) is not list:
            a = [a]                     # Casting
        out = []
        for i in a:
            if type(i) is list:         # se accordo
                x = '< '
                for n in i:
                    if n == -1:
                        x += 'r '
                    elif n == -2:
                        x += 's '
                    else:
                        x += PCHS[n] + ' '
                out.append(x + '>')
            else:
                if i == -1:             # se pausa
                    out.append('r ')   
                elif i == -2:           # se spazio
                    out.append('s ')
                elif i == 00:           # se valore precedente
                    out.append('')     
                else:                   # se nota
                    out.append(PCHS[i]) 
        return out

# a = 60
# a = mapPitch(a)
# print(a)

# a = [60,61,62]
# a = mapPitch(a)
# print(a)

# a = [64,[56,89]]
# a = mapPitch(a)
# print(a)


def mapDur(a):          
        '''
        Durate --> Simboli Lilypond
        00 = valore precedente
        IN:  list (int/list 2D) o int
        OUT: list (string) 
        '''
        if type(a) is not list:
            a = [a]                 # Casting
        out = []                               
        for i in a:
            if type(i) == list:     # se irregolare o puntato
                irr  = []
                sudd = []  
                if sum(i[1]) in (4,8,16,32):
                    for d in i[1]:   
                        out.append(DURS[0][round((1/i[0] / sum(i[1])) * d,5)]) 
                elif sum(i[1]) in (3,3):
                    irr.append('\\tuplet 3/2')
                    for d in i[1]:
                        sudd.append(DURS[1][round((1/i[0] / sum(i[1])) * d,5)])   
                    irr.append(sudd)
                    out.append(irr)
                elif sum(i[1]) in (5,10):
                    irr.append('\\tuplet 5/4')  
                    for d in i[1]:
                        sudd.append(DURS[2][round((1/i[0] / sum(i[1])) * d,5)]) 
                    irr.append(sudd)
                    out.append(irr)
                elif sum(i[1]) in (6,12):
                    irr.append('\\tuplet 6/4') 
                    for d in i[1]:
                        sudd.append(DURS[3][round((1/i[0] / sum(i[1])) * d,5)]) 
                    irr.append(sudd)
                    out.append(irr)
                elif sum(i[1]) in (7,14):
                    irr.append('\\tuplet 7/4')
                    for d in i[1]:   
                        sudd.append(DURS[4][round((1/i[0] / sum(i[1])) * d,5)])
                    irr.append(sudd)
                    out.append(irr)
                elif sum(i[1]) in (9,12):
                    irr.append('\\tuplet 9/8')
                    for d in i[1]:   
                        sudd.append(DURS[5][round((1/i[0] / sum(i[1])) * d,5)])
                    irr.append(sudd)
                    out.append(irr)
                elif sum(i[1]) in (11,22):
                    irr.append('\\tuplet 11/8')
                    for d in i[1]:   
                         sudd.append(DURS[6][round((1/i[0] / sum(i[1])) * d,5)])
                    irr.append(sudd)
                    out.append(irr)
                elif sum(i[1]) in (13,26):
                    irr.append('\\tuplet 13/8')
                    for d in i[1]:   
                        sudd.append(DURS[7][round((1/i[0] / sum(i[1])) * d,5)])
                    irr.append(sudd)
                    out.append(irr)
                elif sum(i[1]) in (15,30):
                    irr.append('\\tuplet 15/8')
                    for d in i[1]:   
                        sudd.append(DURS[8][round((1/i[0] / sum(i[1])) * d,5)])
                    irr.append(sudd)
                    out.append(irr)
            else:
                if i == 00:                  # se 00 valore precedente 
                    out.append('')         
                else:
                    out.append(DURS[0][1/i]) # se regolare  
        return out 

# a = 4
# a = mapDur(a)
# print(a)

# a = [4,8,8]
# a = mapDur(a)
# print(a)

# a = [4,[4,[1,1,1]]]
# a = mapDur(a)
# print(a)

def mapVel(a):
        ''' 
        Velocities --> Simboli Lilypond
        00 = valore precedente
        IN:  list (int)
        OUT: list (string) 
        '''
        if type(a) is not list:
            a = [a]                     # Casting
        out = []       
        for i in a:                
            if i > 0:              
                if 1 <= i <= 9:         
                    out.append(VELS[0])  # ppppp
                elif 10 <= i <= 19:
                    out.append(VELS[1])  # pppp
                elif 20 <= i <= 29:
                    out.append(VELS[2])  # ppp
                elif 30 <= i <= 39:
                    out.append(VELS[3])  # pp
                elif 40 <= i <= 49:
                    out.append(VELS[4])  # p
                elif 50 <= i <= 59:
                    out.append(VELS[5])  # mp
                elif 60 <= i <= 69:
                    out.append(VELS[6])  # mf
                elif 70 <= i <= 79:
                    out.append(VELS[7])  # f
                elif 80 <= i <= 89:
                    out.append(VELS[8])  # ff
                elif 90 <= i <= 99:
                    out.append(VELS[9])  # fff
                elif 100 <= i <= 109:
                    out.append(VELS[10]) # ffff
                else: 
                    out.append(VELS[11]) # fffff
            else:
                out.append('')           # 00 valore precedente 
        return out

# a = 60
# a = mapVel(a)
# print(a)

# a = [60,61,62]
# a = mapVel(a)
# print(a)

def mapExp(a):   
        ''' 
        Simboli --> Simboli Lilypond
        00 = valore precedente
        IN:  list (string)
        OUT: list (string) 
        '''
        if type(a) is not list:
            a = [a]             # Casting
        out = []                          
        for i in a:                   
            out.append(EXPR[i])                    
        return out 

# a = '.'
# a = mapExp(a)
# print(a)

# a = ['.','>']
# a = mapExp(a)
# print(a)

# =============================== metti if se 2D = Accordi se 3D = irregolari

def nDim(a):
    '''Riporta le dimensioni di una lista fino a 3D:
    1D = Tutto
    2D = Accordi (note)
    3D = Ritmi irregolari o puntati
    '''
    if not isinstance(a, list):
        return 0
    elif not a:
        return 1
    else:
        return 1 + max(nDim(item) for item in a)   # Ricorsione

# d = [23,34,45,[34,[45,56]],]
# e = nDim(d)
# print(e)

# ==========================
def l_mod(lista, target):
    '''
    Genera una lista di n elementi (target) ripetendo la lista originale con operatore modulo.
    Se la lista contiene elementi irregolari (liste 2D), li espande correttamente.
    '''
    nl = []
    count = 0
    if nDim(lista) == 3:                 # Se lista 3D (contiene ritmi irregolari)
        idx = 0
        while count < target:            # Fino a quando count < target 
            el = lista[idx % len(lista)] # prende l'elemento corrente
            if type(el) == list:         # se irregolare (2D)
                sudd = []
                for i in el[1]:          # per ogni suddivisione
                    if count < target:
                        sudd.append(i)   # aggiunge la suddivisione 
                        count += 1       # aggiorna il count
                    else:
                        break            # esce dal ciclo se count >= target 
                nl.append([el[0], sudd])
            else:                        # altrimenti aggiorna di 1 
                nl.append(el)
                count += 1
            idx += 1
    else:                                # Se lista 1D o 2D (note o accordi)
        for i in range(target):
            nl.append(lista[i % len(lista)])
    return nl

# a = [[4,[1,1,2,3]],56,67,78,67]
# a = l_mod(a, 10)
# print(a)

def l_zero(lista, target):
    '''
    Genera una lista di n elementi (target) sostituendo gli zeri (00) con ''.
    Se la lista è più corta di target, aggiunge '' alla fine fino a raggiungere target.
    '''
    nl = []
    idx = 0
    for i in range(len(lista)):
        el = lista[i]
        idx += 1
        if nDim(el) == 2:         # Se lista 3D (contiene ritmi irregolari)
            idx += len(el[1])
            idx -= 1
            if el == 00:
                 nl.append('')
            else:
                nl.append(el)
        else:
            if el == 00:
                 nl.append('')
            else:
                nl.append(el)
    for i in range(target-idx):
        nl.append('')
    return nl

# a = [23,34,00,[4,[1,2,4,5]],[4,[1,1,1]]]
# a = l_zero(a,5)
# print(a)

def dflt(a):
    '''
    Genera array di default e aggiunge uno zeropad se aromento è:
    • None
    • int
    • lista
    '''
    if a is None:                      # SE non esiste
        out = [0,'zero']                 # ---> mette default
    elif type(a) is not list:          # SE è int singolo
        out = [a,'zero']                 # --> crea una lista
    elif a[-1] != 'mod' and a[-1] != 'zero': # SE non specifica il modo
        a.append('zero')                     # --> lo mette di default
        out = a
    else:
        out = a                         # altrimenti lo assegna
    return out

# a = dft(None)
# print(a)

def selmode(lista, max):
    if lista[1] == 'mod':             # SE mod
        out = l_mod(lista[0], max)
    else:                             # SE zero
        out = l_zero(lista[0], max) 
    return out

def getdurmax(note,dur,vel,exp):
    '''Trova il size della lista più lunga'''
    idx = 0                # conteggio esatto elementi in durate
    for i in dur:
        if type(i) == list:                  # se irregolare
            idx = idx + len(i[1])
        else: idx += 1                    # se regolare
    return max(len(note),idx,len(vel),len(exp))  # trova il size max

# -------------------------------------------
# - CLASSI:

class _Map:
    '''
    Esegue il mapping.
    Accetta liste di lunghezza diversa in ingresso.
    La lista più lunga DEVE essere quella delle DURATE (0 o > delle altre)
    Genera liste di lunghezza uguale (l_map oppure l_zero)
    e le assegna a variabili d'istanza richiamate nelle classi figlie
    IN:  • pchs = list (int/list 2D) oppure int
         • durs = list (int/list 2D) oppure int
         • vels = list (int) oppure int
         • expr = list (string) oppure int
    '''   
    def __init__(self, note=60,dur=None,vel=None,exp=None):

        self.note = dflt(note)  # Assegna le variabili locali e genera eventuali default (dflt())
        self.dur  = dflt(dur)
        self.vel  = dflt(vel)
        self.exp  = dflt(exp)

        self.note = [self.note[0:-1], self.note[-1]]    # [[seq], tipo] 
        self.dur  = [self.dur[0:-1], self.dur[-1]]
        self.vel  = [self.vel[0:-1], self.vel[-1]]
        self.exp  = [self.exp[0:-1], self.exp[-1]]

        self.note[0] = mapPitch(self.note[0])  # mapping con liste senza 'mod o 'zero'
        self.dur[0]  = mapDur(self.dur[0]) 
        self.vel[0]  = mapVel(self.vel[0]) 
        self.exp[0]  = mapExp(self.exp[0]) 

        self.max  = getdurmax(self.note[0],self.dur[0],self.vel[0],self.exp[0]) # trova il size max delle liste
                                                                                # per normalizzazione
        self.note = selmode(self.note, self.max) # normalizza la lunghezza delle liste
        self.dur  = selmode(self.dur, self.max)  # in due modalità 'mod' oppure 'zero'
        self.vel  = selmode(self.vel, self.max)
        self.exp  = selmode(self.exp, self.max)
 
# p = [60,45,56,[67,78,89],67,56,67]
# d = [4,  [4,[1,1,1]],4,4,'zero']
# v = [60,100,'zero']
# e = ['.','>','mod']

# a = _Map(p, d, v, e)

# print(a.note)
# print(a.dur)
# print(a.vel)
# print(a.exp)

class _Print:
    '''
    Salva un file lilypond (.ly) e lo compila generando:
        - un file grafico
        - un file midi
    IN: • filename (string)
        • format (string [pdf, png, pngalpha, svg, ps])
        • version (string)             
    '''
    def __init__(self,
                 filename="score", format="pdf",
                 version="2.24.3"
                ):

        self.filename  = filename
        self.format    = format
        self.version   = version

    @property
    def print_out(self):
        '''
        Restituisce una stringa con il codice lilypond
        self.outstring lo prende dalle sottoclassi
        '''
        self.outo = f"\n\\version \"{self.version}\"\n\\language \"english\"\n\n{self.outstring}"
        print(self.outo)
    
    @property
    def make_file(self):
        '''
        Genera tre files: .ly .format e .midi
        '''
        self.outo = f"\n\\version \"{self.version}\"\n\\language \"english\"\n{self.outstring}"
        f = open(self.filename + ".ly", "w")  # crea un file di testo...
        f.write(self.outo)                    # lo scrive...
        f.close()                             # lo chiude in python

        cmd = f"lilypond -dresolution=300 -dpixmap-format=png16m --format={self.format} --output={self.filename} {self.filename}.ly"
        os.system(cmd)   

class _Voice(_Print):
    '''
    Costruisce una voce musicale in formato lilypond
    Le liste possono essere di lunghezza differente
    IN: • midinote ([60])          oppure int
        • durate ([4, [4,[3,1]]])  oppure int
        • velocity ([64])          oppure int 
        • espressioni  (['>''])    oppure int
    OUT: un'espressione musicale di lilypond (stringa)
    '''
    def __init__(self,
                 note=60,dur=None,vel=None,exp=None,
                 filename="score", format="pdf", version="2.24.3"
                 ):
        super().__init__(filename,format,version)

        ins = _Map(note,dur,vel,exp)    # Crea liste della stessa lunghezza
        self.note = ins.note
        self.dur  = ins.dur 
        self.vel  = ins.vel 
        self.exp  = ins.exp 
        self.music   = ''
        self.id      = -1
        
        for i in self.dur:
            if type(i)==list:
                self.irr = ''
                self.irr = self.irr + i[0] + ' { '
                for n in i[1]:
                    self.id += 1 
                    self.irr = self.irr + self.note[self.id] + n + self.vel[self.id] + self.exp[self.id] + ' '             
                self.irr = self.irr + '} '
                self.music = self.music + self.irr                            
            else:                                  
                self.id += 1                            
                self.music = self.music + self.note[self.id] + i + self.vel[self.id] + self.exp[self.id] + ' '     
                  
        self.outstring = f"{{ {self.music} }}"
        
    @property
    def out(self):
        return self.outstring
    
# p = [60,64,67,72,67,89,92,96]
# d = [4,  [4,[1,1,1]],4,[4,[2,1,2]]]
# v = [60,90,'mod']
# e = ['>',00,'.','mod']

# a = _Voice(p,d,v,e).make_file

# ============================================================
# PER OGNI PARAMETRO:
# Se 1 sola voce per staff ---> lista
# Se più voci per staff    ---> tuple di liste

class Staff(_Print):
    '''
    Costruisce un rigo musicale in formato lilypond
    Le liste possono essere di lunghezza differente
    IN: • midinote ([60])          oppure int
        • durate ([4, [4,[3,1]]])  oppure int
        • velocity ([64])          oppure int 
        • espressioni  (['>''])    oppure int
        • tonalità (['c', 'major'])
        • tempo ('3/4')
        • chiave ('bass')
        • nome strumento ('Violino')
        • nome abbreviato ('Vl')
        • nome MIDI ('violino')
          https://lilypond.org/doc/v2.23/Documentation/notation/midi-instruments
    OUT: un'espressione musicale di lilypond (stringa)
    '''
    def __init__(self,
                 note=60,dur=None,vel=None,exp=None,              # --> le stesse di _Voice
                 key=None,t_sig=None,clef=None,
                 i_name=None,i_short=None,i_midi=None,
                 filename="score", format="pdf", version="2.24.3" # ereditate da _Print
                 ):
        super().__init__(filename,format,version)

        self.voice = []
        if type(note) == tuple:

            for i, d in enumerate(note):
                voicedur = None if dur is None else dur[i]
                voicevel = None if vel is None else vel[i]
                voiceexp = None if exp is None else exp[i]
    
                a = _Voice(note[i],voicedur,voicevel,voiceexp)
                self.voice.append(a.out)

        else: self.voice.append(_Voice(note,dur,vel,exp).out)

        self.multivoice = ""
        self.items = len(self.voice)
        self.cnt = 0
        for i in self.voice:
            if self.items > 1 and self.cnt < self.items-1:  
                self.multivoice = f"{self.multivoice} \t\t\t\t {i} \n\t\t\t\t   \\\\\n"   # a capo e //
                self.vseq = f"\t <<\n {self.multivoice} \t\t\t\t >>"                      # costruisce la Voice
            elif self.cnt == self.items-1:
                self.multivoice = f"{self.multivoice} \t\t\t\t {i}\n"   # a capo senza //
                self.vseq = f"\t <<\n {self.multivoice} \t\t\t\t >>"  # costruisce la Voice
            else:
                self.multivoice = f"\t {i}"
                self.vseq = self.multivoice
            self.cnt += 1        
         
        self.key    = f"\n\t\t\t\t     \\key {key[0]} \\{key[1]}" if key is not None else ""
        self.t_sig  = f"\n\t\t\t\t     \\numericTimeSignature\n\t\t\t\t     \\time {t_sig}" if t_sig is not None else ""
        self.clef   = f"\n\t\t\t\t  \\clef {clef}" if clef is not None else ""

        self.i_name  = f"\n\t\t\t\t  instrumentName=\"{i_name}\"" if i_name is not None else ""
        self.i_short = f"\n\t\t\t\t  shortInstrumentName=\"{i_short}\"" if i_short is not None else ""
        self.i_midi  = f"\n\t\t\t\t  midiInstrument=\"{i_midi}\"" if i_midi is not None else '\n\t\t\t\t  midiInstrument=\"acoustic grand\"'
                      
        self.outstring = f"\t\t\\new Staff \\with {{{self.i_name}{self.i_short}{self.i_midi}{self.clef}\n\t\t\t\t  }}\n\t\t\t{self.vseq}"
        
    @property
    def out(self):
        return self.outstring

""" p = (60, 72, 84,92)
d = (1,2,4,8)
v = (60, 00, 00, 00 )
e = (['.', 00, 00, '>','mod'], 00, 00, 00)

a = Staff(p,d,v,e).make_file
 """
class Score(_Print):
    '''
        Definisce le caratteristiche della partitura. 
        Formattando gli outputs delle classi precedenti. 
        Di default crea uno StaffGroup.
        IN: • staff (tuple di output di una o più istane di Staff)
            • staff_size (in mm)
            • indent (rientro in mm)
            • s_indent (short indent in mm)
            • titolo (title - stringa)
            • compositore (composer - stringa)
            • size pagina (size - stringa)
              - formati standard: https://lilypond.org/doc/v2.25/Documentation/notation/predefined-paper-sizes
              - se tuple con due int -> custom largh/alt in pixels
            • margini (margins - tuple in mm)
    '''
    def __init__(self, 
                 staff="\n\t\t{c' d' e' f'}",
                 staff_size=None, indent=None, s_indent=None,
                 title=None, composer=None,
                 size="a4landscape", margins=(10,10,10,10),
                 filename="score", format="pdf", version="2.24.3"    # ereditati da _Print
                ):
        super().__init__(filename,format,version)

        if type(staff) == tuple:
            self.staff = staff
        else: 
            self.staff = [staff]

        self.staff_size = f"\n\t#(layout-set-staff-size {staff_size})" if staff_size is not None else ""
        self.indent     = f"\n\tindent = {indent}" if indent is not None else ""
        self.s_indent   = f"\n\tshort-indent = {s_indent}" if s_indent is not None else ""
        self.layout     = f"\n\t\\layout {{{self.staff_size}{self.indent}{self.s_indent}\n\t\t }}"

        self.title      = "\n\ttitle=\""+title+"\"" if title is not None else "" 
        self.composer   = "\n\tcomposer=\""+composer+"\"" if composer is not None else ""
        if type(size) is tuple:          
            self.custom = f"#(set! paper-alist (cons \'(\"mio formato\" . (cons (* {size[0]} mm) (* {size[1]} mm))) paper-alist) )"
            self.size   = "\n\t#(set-paper-size \"mio formato\")"
        else: self.custom, self.size = "", f"\n\t#(set-paper-size \"{size}\")"
        self.margins  = f"\n\ttop-margin={margins[0]}\n\tbottom-margin={margins[1]}\n\tleft-margin={margins[2]}\n\tright-margin={margins[3]}" 

        self.page = f'''\\header {{{self.title}{self.composer}\n\ttagline=\"\"\n\t}}
        {self.custom}\n\\paper {{{self.size}{self.margins}\n\t}}'''

        self.multistaff = ""
        for i in self.staff:
            self.multistaff = self.multistaff + i + "\n"
        self.outstring = f'''{self.page}\n\n\\score {{\n\t\\new StaffGroup\n\t\t<<\n{self.multistaff}\t\t>>\n{self.layout}\n\n\t\\midi {{ }}\n\t}}'''

    @property
    def out(self):
        return self.outstring

# f = [56,78,89,[86,98,65]]
# t = [16,16,8,4]
# i = Staff(f,t).out 
# i = (i,i,i)  
# Score(i,title="che bel pezzo",composer="ciccio",format="pdf").make_file
def euclidean_rhythm(pulses, steps, rotation=0):
    """
    Generazione di pattern euclidei (es. clave, rhythm wheel, Bjorklund algorithm).

    Args:
        pulses (int): Numero di eventi attivi (colpi, suoni)
        steps (int): Numero totale di slot (divisioni del pattern)
        rotation (int): Rotazione ciclica del pattern (default 0)

    Returns:
        list: Pattern binario (1 = nota, 0 = silenzio), es. [1,0,1,0,1,0,0,0]
    
    Esempio:
        euclidean_rhythm(3,8)  # -> [1,0,0,1,0,0,1,0]
    """
    pattern = []
    counts = []
    remainders = []
    divisor = steps - pulses
    remainders.append(pulses)
    level = 0

    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level += 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)

    def build(level):
        if level == -1:
            return [0]
        if level == -2:
            return [1]
        else:
            res = []
            for i in range(counts[level]):
                res += build(level-1)
            if remainders[level]:
                res += build(level-2)
            return res

    pattern = build(level)
    # Pattern binario, ruotato se richiesto
    pattern = pattern[:steps]
    if rotation != 0:
        pattern = pattern[-rotation:] + pattern[:-rotation]
    return pattern

def fibonacci_sequence(n, start=1):
    """
    Genera una sequenza di Fibonacci con numeri rappresentati da 1 ripetuti, 
    intervallati da 0.
    
    Args:
        n (int): Numero di elementi di Fibonacci da generare.
        start (int): Primo numero della sequenza (default 1).
    
    Returns:
        list: Sequenza con numeri rappresentati come 1 ripetuti e separati da 0.
        
    Esempio:
        fibonacci_sequence(5)  
        # -> [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0]
    """
    seq = []
    a, b = start, start
    for _ in range(n):
        seq.extend([1] * a)
        seq.append(0)
        a, b = b, a + b
    return seq
def pattern_to_rhythm(pattern, dur_on=4, dur_off=8):
    """
    Converte un pattern binario in una sequenza di durate (int) o simboli di pausa (str).
    """
    result = []
    for x in pattern:
        if x:
            # evento: durata numerica (int)
            result.append(dur_on)
        else:
            result.append(dur_off)
    return result

def random_walk(dur, start=60, step_choices=[-2, 0, 2], bounds=(36, 96)):
    """
    Genera una camminata casuale sui pitch: salta tutte le pause (stringhe),
    e usa solo gli interi di dur come note.
    """
    seq = []
    current = start
    for d in dur:
        # se è una stringa (pausa), la salto
        if isinstance(d, str):
            continue
        # altrimenti dsp = int duration → genero un passo
        step = np.random.choice(step_choices)
        current = int(np.clip(current + step, bounds[0], bounds[1]))
        seq.append(current)
    return seq
def mirror_rhythm(seq, repetition=False):
    """
    Restituisce la sequenza “specchiata”:
      - se repetition=False: ritorna solo la sequenza invertita
      - se repetition=True: ritorna la sequenza originale seguita dalla sua inversione

    Args:
        seq (list): Sequenza di valori (es. pattern binario, durate, simboli…)
        repetition (bool): se True concatena seq + reverse(seq), altrimenti solo reverse(seq)

    Returns:
        list: Lista specchiata secondo il comportamento di repetition.

    Esempi:
        mirror_rhythm([1,0,1,0], False)  # -> [0,1,0,1]
        mirror_rhythm([1,0,1,0], True)   # -> [1,0,1,0, 0,1,0,1]
        mirror_rhythm(['8','2','8'], True) 
          # -> ['8','2','8', '8','2','8']
    """
    # crea la versione invertita
    mirrored = seq[::-1]
    if repetition:
        # concatena originale + specchiata
        return seq + mirrored
    else:
        # solo la parte specchiata
        return mirrored
        def envelope_follower(length, shape='sine', cycles=1, min_val=0, max_val=127, custom_points=None):
    """
    Genera una sequenza di valori in funzione dell'envelope follower (LFO).

    Args:
        length (int): Lunghezza della sequenza (numero di note/eventi)
        shape (str): Forma dell'inviluppo ('sine', 'triangle', 'saw', 'square', 'custom')
        cycles (float): Numero di cicli dell'inviluppo nell'arco della sequenza
        min_val (int/float): Valore minimo (default 0)
        max_val (int/float): Valore massimo (default 127)
        custom_points (list, opzionale): Lista di punti per shape 'custom', [0..1]

    Returns:
        np.ndarray: Array di valori normalizzati tra min_val e max_val
    """
    x = np.linspace(0, 2 * np.pi * cycles, length)
    if shape == 'sine':
        env = (np.sin(x) + 1) / 2   # [0,1]
    elif shape == 'triangle':
        env = 2 * np.abs(2 * (x / (2 * np.pi) % 1) - 1)  # [0,1]
    elif shape == 'saw':
        env = (x / (2 * np.pi * cycles)) % 1  # [0,1]
    elif shape == 'square':
        env = (np.sign(np.sin(x)) + 1) / 2  # [0,1]
    elif shape == 'custom' and custom_points is not None:
        points = np.array(custom_points)
        env = np.interp(np.linspace(0, 1, length), np.linspace(0, 1, len(points)), points)
    else:
        raise ValueError("Shape non riconosciuta.")
    # Mappa ai valori desiderati
    return env * (max_val - min_val) + min_val
    def mappa_envelope_a_dinamiche(env, dynamic_levels=VELS):
    """
    Mappa i valori dell'envelope a dinamiche testuali lilypond.

    Args:
        env (array/list): Lista o array di valori numerici (0-127)
        dynamic_levels (list): Lista di stringhe lilypond (in ordine crescente di intensità)

    Returns:
        list: Lista di stringhe di dinamica ('\\p', '\\mf', ecc)
    """
    env = np.array(env)
    idx = np.clip(np.round(env / 127 * (len(dynamic_levels)-1)), 0, len(dynamic_levels)-1).astype(int)
    return [dynamic_levels[i] for i in idx]

    def envelope_follower_smooth(velocities):
    """
    Dati i valori di velocity da envelope_follower,
    restituisce:
      - new_vel: dynamics solo sui minimi e massimi locali
      - expr: hairpin commands ('cresc','dim','end')
    """
    v = np.array(velocities)
    N = len(v)
    if N < 2:
        
        return velocities, ['']*N

    
    diffs = np.diff(v)
    signs = np.sign(diffs)

   # min max
    extrema = []
    for i in range(1, len(signs)):
        if signs[i-1] < signs[i]:
            extrema.append((i, 'min'))
        elif signs[i-1] > signs[i]:
            extrema.append((i, 'max'))

    
    if not extrema or extrema[0][1] == 'max':
        extrema.insert(0, (0, 'min'))
    
    if extrema[-1][1] == 'min':
        extrema.append((N-1, 'max'))

    
    new_vel = [0] * N
    expr    = [''] * N

    
    for (i, kind), (j, _) in zip(extrema, extrema[1:]):
        if kind == 'min':
           
            new_vel[i]    = velocities[i]
            expr[i]       = 'cresc'
            new_vel[j]    = velocities[j]
            expr[j]       = 'end'
        else:
            
            new_vel[i]    = velocities[i]
            expr[i]       = 'dim'
            new_vel[j]    = velocities[j]
            expr[j]       = 'end'

    return new_vel, expr
def layout_uniforme(staff_str: str,
                                   nbar: int,
                                   time_num: int = 4,
                                   time_den: int = 4) -> str:
    """
    
    Inserisce '\break' ogni nbar battute contando le durate estratte
    direttamente dal testo LilyPond:
      - Cerca, in ogni token, eventuali cifre (es. '4' in "c'4\\mp")
      - Le usa come denominatore della semiminima
      - Calcola battute accumulate e piazza '\break' ogni volta che si raggiunge un multiplo intero di nbar.

    staff_str: stringa generata da Staff(...).out
    nbar:      quante battute vuoi per rigo
    time_num/time_den: firma del tempo (default 4/4)

    """
    tokens = staff_str.split()
    # token
    durations = []
    idxs      = []
    for i, tok in enumerate(tokens):
        # caratteri numerici contigui 
        digits = ''.join(ch for ch in tok if ch.isdigit())
        if digits:
            durations.append(float(digits))
            idxs.append(i)

    #  durate-> battute
    durs = np.array(durations, dtype=float)
    beat_lengths = (1.0 / durs) * time_den     # semiminime → battute
    cum_beats    = np.cumsum(beat_lengths)     # battute totali
    measures     = cum_beats / time_num        # in misure

    out_tokens = []
    di = 0  # indice su durations/measures
    for i, tok in enumerate(tokens):
        out_tokens.append(tok)
        if di < len(idxs) and i == idxs[di]:
            m = measures[di]
            if abs(m - round(m)) < 1e-6 and int(round(m)) % nbar == 0:
                out_tokens.append(r"\break")
            di += 1

    return " ".join(out_tokens)