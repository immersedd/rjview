import networkx as nx
from collections import defaultdict

def extract_unique_nodes(edges):
    nodes = {node for edge in edges for node in edge}
    if None in nodes:
        raise ValueError("Node list contains None.")
    return list(nodes)

def map_uuid_to_edges(edges, uuid_mapping):
    def generate_pairs(lst):
        return [(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]
    updated_edges = []
    for key, value in uuid_mapping.items():
        updated_edges.extend(generate_pairs(value))
    for source, target in edges:
        if source in uuid_mapping and target in uuid_mapping:
            updated_edges.append((uuid_mapping[source][-1], uuid_mapping[target][0]))
        elif source in uuid_mapping:
            updated_edges.append((uuid_mapping[source][-1], target))
        elif target in uuid_mapping:
            updated_edges.append((source, uuid_mapping[target][0]))
        else:
            updated_edges.append((source, target))
    return updated_edges

def filter_none_edges(edges):
    return [edge for edge in edges if None not in edge]

def add_root_to_graph(edges, root_label):
    source_nodes = {edge[0] for edge in edges}
    target_nodes = {edge[1] for edge in edges}
    root_nodes = list(source_nodes - target_nodes)
    if len(root_nodes) != 1:
        raise ValueError("Multiple root nodes detected")
    return [(root_label, root_nodes[0])] + edges

def get_subtrees_from_edges(edge_list):
    def create_graph(edges):
        G = nx.DiGraph()
        G.add_edges_from(edges)
        return G
    def generate_subtrees(G):
        return {node: list(nx.dfs_tree(G, source=node).edges()) for node in G.nodes}
    def sort_list(lst):
        return sorted(lst)
    G = create_graph(edge_list)
    subtrees = generate_subtrees(G)
    values = [sort_list(subtree) for subtree in subtrees.values() if subtree]
    return values

def add_self_loops_to_leaf_nodes(edges):
    out_degree = {}
    for edge in edges:
        if edge[0] not in out_degree:
            out_degree[edge[0]] = 0
        if edge[1] not in out_degree:
            out_degree[edge[1]] = 0
    for edge in edges:
        out_degree[edge[0]] += 1
    leaf_nodes = [node for node, degree in out_degree.items() if degree == 0]
    new_edges = edges.copy()
    for leaf in leaf_nodes:
        if [leaf, "f"] not in new_edges:
            new_edges.append([leaf, "f"])
    return new_edges

def find_connected_order(edges):
    graph = defaultdict(list)
    for edge in edges:
        a, b = edge
        graph[a].append(b)
        graph[b].append(a)
    def dfs(node, visited, order):
        visited.add(node)
        order.append(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                dfs(neighbour, visited, order)
    visited = set()
    orders = []
    for node in graph:
        if node not in visited:
            order = []
            dfs(node, visited, order)
            orders.append(order)
    return orders