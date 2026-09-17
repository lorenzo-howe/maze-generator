from random import choices, sample, randint, randrange
from matplotlib import pyplot as plt
from math import sqrt
from collections import deque

class Maze:
    """
    Random maze generator on a grid.

    The maze grows from several random starting cells ("seeds") at the same
    time instead of a single one. Each seed's growth is a "lineage": as long
    as a lineage expands into empty cells it just grows normally, but when
    two different lineages happen to grow next to each other they get merged
    into one. Cells belonging to the SAME lineage are never connected to each
    other, which is what keeps the final maze free of loops: it is always one
    connected tree spanning the whole grid, with exactly one path between any
    two cells.
    """

    def __init__(self, height, width, seeds = 10):

        self.height = height
        self.width = width
        self.seeds = seeds
        self.roots = []
        self.metrics = None
        self.maze = self.build_maze()

    def build_maze(self):
        """
        Grow the maze from multiple seeds at once until every reachable cell
        has been claimed and no lineage has anywhere left to expand.

        `links` is the key trick: `links[i]` holds the set of lineage ids that
        have been merged with lineage `i`. Two cells are only allowed to
        connect if they belong to different (not-yet-merged) lineages, or if
        one of them is brand new. This is what prevents loops: connecting two
        cells of the SAME lineage would close a cycle, since a path already
        exists between them through their shared seed.
        """

        maze = {}       #{node: neighbours} unrooted tree (acyclic graph)

        frontier = []      #[frontier nodes] cells that may still be able to grow
        look_up_key = {}   #{node: lineage id of the seed it grew from}
        links = []         #links[i] = set of lineage ids merged with lineage i so far

        directions = [(0,1),(1,0),(0,-1),(-1,0)]

        for seed in range(self.seeds):                                        #place the seeds on random, non-overlapping cells

            while True:
                root = (randint(0, self.height-1), randint(0, self.width-1))
                if root not in maze:
                    break

            maze[root] = []
            frontier.append(root)
            links.append({seed})            #each seed starts as its own lineage
            self.roots.append(root)
            look_up_key[root] = seed

        while frontier:
            # Pick a random frontier cell to grow from (keeps growth from all
            # lineages interleaved and unpredictable, instead of finishing one
            # lineage before starting the next)
            idx = randrange(len(frontier))
            current = frontier[idx]
            seed = look_up_key[current]

            # A neighbor is a valid growth target if it is either unclaimed,
            # or already claimed but by a lineage that hasn't merged with ours
            # yet (connecting same-lineage cells would create a loop, so those
            # are skipped)
            neighbors = []

            for dx, dy in directions:
                n = (current[0] + dx, current[1] + dy)
                if 0 <= n[0] < self.height and 0 <= n[1] < self.width:
                    if n not in maze:
                        neighbors.append(n)
                    elif links[look_up_key[n]] != links[seed]:
                        neighbors.append(n)

            if not neighbors:
                # this cell has nothing left to grow into: drop it from the
                # frontier (swap with the last element for O(1) removal)
                frontier[idx], frontier[-1] = frontier[-1], frontier[idx]
                frontier.pop()

                continue

            # Organic branching: usually extend in a single direction, but
            # occasionally fork into 2 or 3 at once, capped by how many valid
            # neighbors are actually available
            branches = choices([1, 2, 3], weights=[12, 3, 1], k=1)[0]
            branches = min(branches, len(neighbors))
            chosen = sample(neighbors, branches)

            for next_cell in chosen:
                if next_cell in maze:
                    # neighbor belongs to another, not-yet-merged lineage:
                    # connect the two cells and merge the lineages so that
                    # neither can ever be reconnected to the other again
                    if links[look_up_key[next_cell]] != links[seed]:
                        merged_set = links[look_up_key[next_cell]] | links[seed]     #hash the lineages to the same set
                        for key in list(merged_set):
                            links[key] = merged_set
                        maze[current].append(next_cell)
                        maze[next_cell].append(current)
                else:
                    # neighbor is unclaimed: it joins the current lineage and
                    # becomes a new growth point
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

        # Since the maze is a tree, BFS from (0,0) never revisits a cell and
        # reaches every cell through exactly one path, so it can double as
        # both the traversal and the "solve the maze" step.
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
