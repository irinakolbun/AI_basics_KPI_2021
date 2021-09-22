from queue import Queue, PriorityQueue


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
            return "BFS: Path found", backtrace(parent, start, end), get_path_weight(backtrace(parent, start, end), weights)

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
            return "DFS: Path found", backtrace(parent, start, end), get_path_weight(backtrace(parent, start, end), weights)

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
            return "UCS: Path found", backtrace(parent, start, end), get_path_weight(backtrace(parent, start, end), weights)

        for node in graph[current_node]:
            if node not in explored:
                parent[node] = current_node
                frontier.put((
                    ucs_w + ucs_weight(current_node, node, weights),
                    node
                ))


def get_path_weight(l: list, weights):
    res = 0
    for i in range(len(l) - 1):
        res += weights[(l[i], l[i+1])]
    return res


def backtrace(parent, start, end):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    return path

