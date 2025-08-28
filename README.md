# Generatore di LilyPond in Python – per composizione algoritmica / CAC

Libreria Python per **generare codice LilyPond** a partire da strutture algoritmiche e trasformazioni musicali. Pensata per composizione **algoritmica** e **computer-assisted** (CAC): serie e trasformazioni, pattern ritmici, dinamiche da envelope, costruzione di **Voice/Staff/Score** e **render** automatico in PDF/PNG/MIDI via LilyPond.
---

## Requisiti

* **Python ≥ 3.12.0**
* **LilyPond ≥ 2.24** installato e disponibile in `PATH` (il comando `lilypond` deve funzionare da terminale)

---

## Installazione (con ambiente virtuale)

Consigliato creare un **venv** dedicato:

```bash
# macOS / Linux
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

# Windows (PowerShell)
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
```

Installa la libreria dal sorgente del repo

---

## Idea d’uso (TL;DR)

* **Costruisci** note, durate, dinamiche, espressioni con funzioni/utility (serie, pattern, envelope…)
* **Componi** una `Staff` o più righi, quindi una `Score`
* **Esporta**: `Score(..., format="pdf" | "png" | "svg").make_file`
  → genera `score.ly`, `score.{format}`, `score.midi`


---

## Quickstart — linea con envelope e layout

```python
from pycac import (
    Serie, Staff, Score,
    envelope_follower, envelope_follower_smooth,
    layout_uniforme
)

note_count = 32
notes = list(Serie(len=note_count).recto())

# Envelope per dinamiche (0–127) + hairpin automatici (cresc/ dim / end)
vel_raw = list(envelope_follower(length=note_count,
                                 shape='sine', cycles=4,
                                 min_val=20, max_val=90))
velocities, expressions = envelope_follower_smooth(vel_raw)

# Rigo (voice singola)
staff_str = Staff(
    note=notes,
    dur=[4] * note_count,   # quarti
    vel=velocities,
    exp=expressions,        # hairpin \cresc, \dim, \!
    i_name="Sinusoide"
).out

# A capo ogni 2 battute in 10/4
staff_str = layout_uniforme(staff_str, nbar=2, time_num=10, time_den=4)

# Partitura e render (PNG, PDF, SVG, …)
Score(
    staff=staff_str,
    title="Layout",
    composer="Esempio",
    format="png"
).make_file
```

Output: `score.ly`, `score.png`, `score.midi`.

---

## Esempio — due righi: Fibonacci + Euclideo

```python
from pycac import (
    fibonacci_sequence, euclidean_rhythm,
    pattern_to_rhythm, random_walk,
    Staff, Score
)

# Pattern Fibonacci → durate → altezze con random walk
pat_fib   = fibonacci_sequence(5)
dur_fib   = pattern_to_rhythm(pat_fib, dur_on=8, dur_off=2)
pitches_fib = random_walk(dur_fib, start=64, step_choices=[-2, 0, 2], bounds=(60, 72))

# Pattern Euclideo (Bjorklund) → durate → altezze
pat_euc   = euclidean_rhythm(3, 8)
dur_euc   = pattern_to_rhythm(pat_euc, dur_on=32, dur_off=8)
pitches_euc = random_walk(dur_euc, start=64, step_choices=[-2, 0, 2], bounds=(60, 72))

fib = Staff(note=pitches_fib, dur=dur_fib, i_name="Fibonacci").out
euc = Staff(note=pitches_euc, dur=dur_euc, i_name="Euclideo").out

Score(
    staff=(fib, euc),
    title="Fibonacci + Euclideo",
    composer="Esempio",
    format="pdf"
).make_file
```

---

## Esempio — trasformazioni di serie

```python
from pycac import Serie, Staff, Score

# Serie casuale di 8 elementi attorno a root=60 (MIDI)
s = Serie(len=8, root=60, type='p')

recto      = s.recto()        # ordine diretto
retro      = s.retrograde()   # retrogrado
inverso    = s.inversion()    # inversione
retro_inv  = s.retrinver()    # retrogrado-inverso

# Render rapido del retrogrado
line = Staff(note=retro, dur=[8]*len(retro), i_name="Retrogrado").out
Score(line, title="Serie – Retrogrado", composer="Esempio").make_file
```

---

## API in breve

### Costruzione / rendering

* `Staff(...) -> .out`: costruisce un rigo LilyPond da **note**, **dur**, **vel** (0–127 → \pp … \ff), **exp** (hairpin), **tempo**, **chiave**, **tonalità**, nomi strumento/MIDI ecc.
* `Score(staff=..., title=..., composer=..., format="pdf"|"png"|"svg"|...) -> .make_file`
  Crea `score.ly` e compila con LilyPond producendo **grafica** e **MIDI**.
* `layout_uniforme(staff_str, nbar, time_num=4, time_den=4)`
  Inserisce `\break` ogni *nbar* battute calcolando le durate dal testo LilyPond.

### Pattern e generazione

* `euclidean_rhythm(pulses, steps, rotation=0)` → pattern binario.
* `fibonacci_sequence(n)` → lista di interi.
* `pattern_to_rhythm(pattern, dur_on=8, dur_off=2)` → lista di durate LilyPond.
* `random_walk(durs, start=64, step_choices=[-2,0,2], bounds=(48,84))` → altezze MIDI.
* `mirror_rhythm(pattern, repetition=True)` → simmetria/retrogrado di pattern.

### Serie e altezze

* `Serie(vals=None, root=60, len=None, type='p')`
  Metodi: `recto()`, `retrograde()`, `inversion()`, `retrinver()`;
  `type='i'` (intervalli), `'p'` (MIDI), `'h'` (Hz via `mtof`).

### Dinamiche / espressività

* `envelope_follower(length, shape='sine'|'triangle'|'saw'|'square'|'custom', cycles=1, min_val=0, max_val=127)`
* `envelope_follower_smooth(velocities)` → `(new_velocities, expressions)` con hairpin `cresc`/`dim`/`end`.
* `mappa_envelope_a_dinamiche(env, dynamic_levels=...)` → `['\\p', '\\mf', ...]`

### Utility

* `mtof(midinote)` / `ftom(freq)` conversioni MIDI ↔ Hz.
* Operazioni su accordi (`ChordOp`): `bpf` (passa-banda), `brf` (notch), `shift` (trasposizione).

> La classe `Score` supporta opzioni di layout: `staff_size`, `indent`, `short-indent`, `size` (A4, A3… o custom), `margins`.

---

## Suggerimenti pratici

* Su macOS l’eseguibile può essere in:
  `/Applications/LilyPond.app/Contents/Resources/bin` → aggiungilo al `PATH`.
* La proprietà `.make_file` **scrive** il `.ly` e invoca **LilyPond** (necessita accesso a shell).

---

## Contribuire

PR e issue sono benvenuti. Mantieni gli esempi **riproducibili** e aggiungi test minimi per nuove funzioni (pattern, mapping, layout).

---

## Licenza

Scegli una licenza (es. MIT) e aggiungila come `LICENSE`.

---

**Compatibilità:** Python **3.12.0+** · LilyPond **2.24+**.
