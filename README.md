# Maze Generator

Generatore di labirinti casuali su griglia, con un algoritmo di crescita originale a semi multipli, più analisi statistica delle metriche strutturali del labirinto su tante run.

## Come funziona l'algoritmo

Il labirinto è, in pratica, un albero che copre tutta la griglia: ogni cella è collegata alle altre da un solo percorso possibile, senza cicli.

Invece di far crescere il labirinto da un unico punto di partenza, l'algoritmo piazza più **semi** casuali sulla griglia e li fa crescere tutti insieme, un po' alla volta:

1. Ogni seme è l'inizio di un proprio "lignaggio". A ogni passo si sceglie a caso una cella di frontiera (una cella che può ancora espandersi) e si guardano le sue celle vicine sulla griglia.
2. Una cella vicina è un candidato valido per la crescita se:
   - non è ancora stata occupata da nessun lignaggio, oppure
   - è già occupata, ma da un lignaggio diverso dal proprio, che non si è mai fuso con esso.
3. Se la cella vicina appartiene allo **stesso** lignaggio, viene scartata: collegarla creerebbe un ciclo, perché tra le due celle esiste già un percorso attraverso il seme comune.
4. Tra le celle vicine valide, viene scelto un numero di "rami" da aggiungere: nella maggior parte dei casi 1 (il percorso semplicemente si allunga), ma a volte 2 o 3, per dare un aspetto più organico e naturale al labirinto invece di corridoi troppo regolari.
5. Se una cella scelta era libera, entra a far parte del lignaggio corrente e diventa un nuovo punto di crescita. Se invece apparteneva a un lignaggio diverso, i due lignaggi vengono fusi in uno solo: da quel momento in poi nessuna cella dell'uno potrà più collegarsi a una cella dell'altro (altrimenti si formerebbe un ciclo).
6. Una cella di frontiera che non ha più vicini validi viene rimossa dalla frontiera. Il processo continua finché non ci sono più celle di frontiera attive: a quel punto il labirinto è completo e ogni cella della griglia è raggiungibile da qualsiasi altra con un solo percorso.

Il risultato è un labirinto "perfetto" (senza cicli né celle isolate), ma generato facendo crescere e fondere più regioni contemporaneamente invece che da un solo punto, con un branching pesato che lo rende più organico.

## Metriche

Dal labirinto generato vengono calcolate, tramite una traversata in ampiezza (BFS) a partire dalla cella `(0,0)`:

- **dead_ends** — numero di vicoli ciechi
- **branching_factor** — numero medio di diramazioni per cella non terminale
- **leaf_fraction** — frazione di celle che sono vicoli ciechi
- **solution_length** — lunghezza del percorso dalla cella `(0,0)` alla cella opposta `(height-1, width-1)`
- **longest_path** — distanza massima raggiunta da `(0,0)`
- **solution_tortuosity** — rapporto tra la lunghezza della soluzione e la distanza in linea d'aria tra partenza e arrivo

## File
- `maze.py` — classe `Maze`: generazione del labirinto e calcolo delle metriche
- `main.py` — esempio d'uso singolo
- `statistical_analysis.ipynb` — analisi statistica su 1000+ run, effetto del numero di seed sulle metriche

## Uso
```python
from maze import Maze

m = Maze(15, 15, seeds=3)
m.plot_maze()
m.collect_metrics()
print(m.stats)
```
