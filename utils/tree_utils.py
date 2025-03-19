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