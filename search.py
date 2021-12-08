from queue import Queue, PriorityQueue

from utils import test_floor


def bfs(graph, start, end, weights):
    frontier = Queue()
    frontier.put(start)
    explored = []
    parent = {}

    while True:
        if frontier.empty():
            return "BFS: Path not found", [], float('+inf')
        current_node = frontier.get()
        explored.append(current_node)

        # Check if node is final
        if current_node == end:
            return "BFS", backtrace(parent, start, end), get_path_weight(backtrace(parent, start, end), weights)

        for node in graph[current_node]:
            if node not in explored:
                parent[node] = current_node
                frontier.put(node)


def dfs(graph, start, end, weights):
    frontier = [start]
    explored = []
    parent = {}

    while True:
        if len(frontier) == 0:
            return "DFS: Path not found", [], float('+inf')
        current_node = frontier.pop()
        explored.append(current_node)

        # Check if node is goal-node
        if current_node == end:
            return "DFS", backtrace(parent, start, end), get_path_weight(backtrace(parent, start, end), weights)

        # expanding nodes
        for node in reversed(graph[current_node]):
            if node not in explored:
                parent[node] = current_node
                frontier.append(node)


def ucs_weight(from_node, to_node, weights=None):
    return weights[(from_node, to_node)] if weights else 1


def ucs(graph, start, end, weights=None):
    frontier = PriorityQueue()
    frontier.put((0, start))  # (priority, node)
    explored = []
    parent = {}

    while True:
        if frontier.empty():
            return "UCS: Path not found", [], float('+inf')

        ucs_w, current_node = frontier.get()
        explored.append(current_node)

        if current_node == end:
            return "UCS", backtrace(parent, start, end), get_path_weight(backtrace(parent, start, end), weights)

        for node in graph[current_node]:
            if node not in explored:
                parent[node] = current_node
                frontier.put((
                    ucs_w + ucs_weight(current_node, node, weights),
                    node
                ))


def heuristic(a, b):
    def _get_block_coords(block):
        skips = block // 12 + 1
        x = 44 + (block % 12) * 16
        # draw line between blocks
        for y in range(240, 0, -1):
            if skips:
                if test_floor({'x': x, 'y': y}):
                    skips -= 1
            if not skips:
                return x - 4, y + 16
        return x-4, 240+16

    (x1, y1) = _get_block_coords(a)
    (x2, y2) = _get_block_coords(b)
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(graph, start, end, weights):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        current = frontier.get()

        if current == end:
            break

        for next in graph[current]:
            new_cost = cost_so_far[current] + ucs_weight(current, next, weights)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, end)
                frontier.put(next, priority)
                came_from[next] = current

    return "ASTAR", backtrace(came_from, start, end), get_path_weight(backtrace(came_from, start, end), weights)


def backtrace(parent, start, end):
    try:
        path = [end]
        while path[-1] != start:
            path.append(parent[path[-1]])
        path.reverse()
        return path
    except KeyError:
        return []


def get_path_weight(l: list, weights):
    res = 0
    for i in range(len(l) - 1):
        res += weights[(l[i], l[i+1])]
    return res
