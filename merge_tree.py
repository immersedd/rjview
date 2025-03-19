from buildQueryTree import *
from itertools import combinations
import sys


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class Tree:
    def __init__(self):
        self.nodes = {}
        self.root_id = None

    def add_edge(self, parent_id, child_id):
        if parent_id not in self.nodes:
            self.nodes[parent_id] = Node(parent_id)
            if self.root_id is None:
                self.root_id = parent_id
        if child_id not in self.nodes:
            self.nodes[child_id] = Node(child_id)
        if child_id == self.root_id:
            self.root_id = None

        self.nodes[parent_id].add_child(self.nodes[child_id])

    def assign_properties(self, properties_dict):
        for node_id, properties_obj in properties_dict.items():
            if node_id in self.nodes:
                node = self.nodes[node_id]
                for prop_name in dir(properties_obj):
                    if not prop_name.startswith('__'):
                        prop_value = getattr(properties_obj, prop_name)
                        setattr(node, prop_name, prop_value)

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def get_root(self):
        if self.root_id and self.root_id in self.nodes:
            return self.nodes[self.root_id]

        child_ids = set()
        for node in self.nodes.values():
            child_ids.update(child.node_id for child in node.children)
        for node_id in self.nodes:
            if node_id not in child_ids:
                self.root_id = node_id
                return self.nodes[node_id]

        return None
    def find_all_children(self, node_id):
        result = {}

        def dfs(node):
            for child in node.children:
                result[child.node_id] = child
                dfs(child)

        if node_id in self.nodes:
            dfs(self.nodes[node_id])
        return result

def print_node_attributes(tree, node_id):
    node = tree.get_node(node_id)
    if node:
        print(f"Node {node_id} attributes:")
        for attr in dir(node):
            if not attr.startswith('__'):
                print(f"  {attr}: {getattr(node, attr)}")
    else:
        print(f"Node {node_id} not found.")

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
def replace_ids_with_values(id_list, equals_ids):
    replaced_list = []
    for pair in id_list:
        replaced_pair = []
        for item in pair:
            if item in equals_ids:
                replaced_pair.append(equals_ids[item])
            else:
                replaced_pair.append(item)
        replaced_list.append(replaced_pair)
    return replaced_list


def find_common_sublists_with_indices(list1, list2):
    list2_tuples = {(tuple(tuple(sublist_item) for sublist_item in sublist), index) for index, sublist in enumerate(list2)}
    common_sublists_indices = []

    for index1, sublist1 in enumerate(list1):
        sublist1_tuple = tuple(tuple(sublist_item) for sublist_item in sublist1)
        for sublist2_tuple, index2 in list2_tuples:
            if sublist1_tuple == sublist2_tuple:
                common_sublists_indices.append((sublist1, index1, index2))
                break
    return common_sublists_indices

def group_equivalent_ids_by_value(data):
    equivalent_groups = []
    for pairs in data.values():
        for pair in pairs:
            current_ids = set(pair.values())
            found = False
            for group in equivalent_groups:
                if not group.isdisjoint(current_ids):
                    group.update(current_ids)
                    found = True
                    break
            if not found:
                equivalent_groups.append(current_ids)
    merged = True
    while merged:
        merged = False
        for i in range(len(equivalent_groups)):
            for j in range(i + 1, len(equivalent_groups)):
                if not equivalent_groups[i].isdisjoint(equivalent_groups[j]):
                    equivalent_groups[i].update(equivalent_groups[j])
                    equivalent_groups[j] = set()
                    merged = True
        equivalent_groups = [group for group in equivalent_groups if group]
    return equivalent_groups

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

def transform_data(data):
    transformed_data = {key: set() for key in data}
    for key, values in data.items():
        for search_key, search_values in data.items():
            if key != search_key and set(values).isdisjoint(set(search_values)) == False:
                transformed_data[key].add(search_key)
    return transformed_data
