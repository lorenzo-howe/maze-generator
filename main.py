from maze import Maze

m = Maze(15, 15, 3)
m.plot_maze()
m.collect_metrics()
print(m.stats)