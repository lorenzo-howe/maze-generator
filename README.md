# Maze Generator

Genera labirinti casuali su griglia usando una crescita simultanea da più "seed" (lignaggi), con branching organico pesato. Include analisi statistica delle metriche strutturali (dead ends, lunghezza soluzione, tortuosità) su run multiple.

## File
- `maze.py` — classe `Maze`: generazione e calcolo metriche
- `main.py` — esempio d'uso singolo
- `statistical_analysis.ipynb` — analisi statistica su 1000+ run, effetto del numero di seed

## Uso
\`\`\`python
from maze import Maze
m = Maze(15, 15, seeds=3)
m.plot_maze()
m.collect_metrics()
print(m.stats)
\`\`\`
