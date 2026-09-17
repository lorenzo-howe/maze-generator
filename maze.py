from random import choices, sample, randint, randrange
from matplotlib import pyplot as plt
from math import sqrt
from collections import deque

class Maze:

    def __init__(self, height, width, seeds = 10):

        self.height = height
        self.width = width
        self.seeds = seeds
        self.roots = []
        self.metrics = None
        self.maze = self.build_maze()

    def build_maze(self):

        maze = {}       #{node: neighbours} unrooted tree (acyclic graph)

        frontier = []      #[frontier nodes]
        look_up_key = {}   #{node: key}
        links = []         #hash table: links[i] = {seeds of lineages conncted to lineage i}

        directions = [(0,1),(1,0),(0,-1),(-1,0)]

        for seed in range(self.seeds):                                        #generate seeds

            while True:
                root = (randint(0, self.height-1), randint(0, self.width-1))
                if root not in maze:
                    break
        
            maze[root] = []
            frontier.append(root)
            links.append({seed})
            self.roots.append(root)
            look_up_key[root] = seed

        while frontier:
            # Pick random frontier cell 
            idx = randrange(len(frontier))
            current = frontier[idx]
            seed = look_up_key[current]
        
            # Find UNVISITED neighbors
            neighbors = []

            for dx, dy in directions:
                n = (current[0] + dx, current[1] + dy)
                if 0 <= n[0] < self.height and 0 <= n[1] < self.width:
                    if n not in maze:
                        neighbors.append(n)
                    elif links[look_up_key[n]] != links[seed]:
                        neighbors.append(n)

            if not neighbors:
                frontier[idx], frontier[-1] = frontier[-1], frontier[idx]
                frontier.pop()

                continue

            # organic branching
            branches = choices([1, 2, 3], weights=[12, 3, 1], k=1)[0]
            branches = min(branches, len(neighbors))
            chosen = sample(neighbors, branches)

            for next_cell in chosen:
                if next_cell in maze:
                    if links[look_up_key[next_cell]] != links[seed]:                    
                        merged_set = links[look_up_key[next_cell]] | links[seed]     #hash the lineages to the same set
                        for key in list(merged_set):
                            links[key] = merged_set
                        maze[current].append(next_cell)
                        maze[next_cell].append(current)
                else:
                    look_up_key[next_cell] = seed
                    frontier.append(next_cell)
                    maze[next_cell] = [current]
                    maze[current].append(next_cell)

        return maze


    def plot_maze(self):
        """
        maze: dict {(x,y): [neighbours]}
        Plots nodes and edges on a 2D plane.
        """

        plt.figure(figsize=(10,10))

        # Draw edges
        for (x, y), neighbours in self.maze.items():
            for (nx, ny) in neighbours:
                plt.plot([x, nx], [y, ny])  

        # Draw nodes
        xs = [x for (x, y) in self.maze.keys()]
        ys = [y for (x, y) in self.maze.keys()]
        plt.scatter(xs, ys, s=5)

        plt.axis("equal")
        plt.title("Maze Structure Visualization")
        plt.show()

    def collect_metrics(self):
        "collect metrics for analysis"

        stats = {}
        stats["n_cells"] = self.height *self.width
        stats["height_width_ratio"] = self.height/self.width
        stats["n_seeds"] = self.seeds
        stats.update(self.get_dinamic_features())
        self.stats = stats
        return stats


    def get_dinamic_features(self):

        """Compute dynamic maze metrics using BFS traversal from the start cell (0,0):
        dead ends, branching factor, leaf fraction, solution length, longest path from (0,0), solution tortuosity """
        n_cells = self.width * self.height
        start = (0,0)
        goal = (self.height-1, self.width-1)  

        visited = set()
        queue = deque([(start, 0)])  #cell, distance from root

        dead_ends = 0
        branches_total = 0
        solution_length = None
        longest_path = 0

        while queue:                             #BFS and data collection

            current, dist = queue.popleft()
            visited.add(current)

            neighbours = self.maze[current]
            unvisited_neighbours = [n for n in neighbours if n not in visited]


            branches_total += len(unvisited_neighbours)
            if not unvisited_neighbours:
                dead_ends += 1

            
            if current == goal:
                solution_length = dist

            longest_path = max(longest_path, dist)

            for n in unvisited_neighbours:
                queue.append((n, dist + 1))


        # Average branching factor = total children / n_non_leaf_cells
        branching_factor = branches_total / (n_cells -dead_ends)

        # Solution tortuosity = solution length / straight-line distance
        manhattan_or_euclid = sqrt((goal[0]-start[0])**2 + (goal[1]-start[1])**2)
        solution_tortuosity = solution_length / manhattan_or_euclid

        return {
            "branching_factor": branching_factor,
            "dead_ends": dead_ends,
            "leaf_fraction": dead_ends/n_cells,
            "solution_length": solution_length,
            "longest_path": longest_path,
            "solution_tortuosity": solution_tortuosity,
        }
