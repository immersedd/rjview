from file_utils import *
from utils.plan_processor import *

tmp_node_uuid = []
ids_feature = {}

def build_query_graph(file, node, level=0):
    for child in node.children:
        build_query_graph(file, child, level + 1)

    if node.node_type in {'Seq Scan', 'Bitmap Heap Scan', 'Index Scan', 'Index Only Scan'}:
        node_table_alias = node.details.get("Alias")
        node_table = node.details.get("Relation Name")

        if node.details.get("Filter"):
            col_of_table = table_columns_j[node_table]
            filter_cond_table = add_prefix_to_columns(reset_condition_z3(remove_invalid_tokens(node.details.get("Filter"))), node_table, col_of_table)
            filter_cond_alias = add_prefix_to_columns(reset_condition_z3(remove_invalid_tokens(node.details.get("Filter"))), node_table_alias, col_of_table)
            filter_cond_x_id = next(ids)
            ids_feature[filter_cond_x_id] = NodeFeature(filter_cond_x_id, full_name=filter_cond_table, alias_name=filter_cond_alias, details=node.details)
            node.link_node.append(filter_cond_x_id)

        if node.node_type in {'Bitmap Heap Scan', 'Index Scan', 'Index Only Scan'} and node.details.get("Index Cond"):
            index_cond_alias = add_ali_in_condi(node_table_alias, remove_brackets(node.details.get("Index Cond")))
            index_cond_full = normalize_condition_with_tables(node_table, remove_brackets(node.details.get("Index Cond")), get_alias_table_mappings()["ori_all"][file[:-5]])
            index_cond_id = next(ids)
            ids_feature[index_cond_id] = NodeFeature(index_cond_id, full_name=index_cond_full, alias_name=index_cond_alias, details=node.details)
            node.parent.link_node.append(index_cond_id)

        if node.node_type == 'Bitmap Heap Scan':
            recheck_cond_alias = add_ali_in_condi(node_table_alias, remove_brackets(node.details.get("Recheck Cond")))
            recheck_cond_full = normalize_condition_with_tables(node_table, remove_brackets(node.details.get("Recheck Cond")), get_alias_table_mappings()["ori_all"][file[:-5]])
            recheck_cond_id = next(ids)
            ids_feature[recheck_cond_id] = NodeFeature(recheck_cond_id, full_name=recheck_cond_full, alias_name=recheck_cond_alias, details=node.details)
            node.parent.link_node.append(recheck_cond_id)

    if node.node_type == 'Hash Join':
        hash_cond_alias = node.details.get("Hash Cond")
        hash_cond_full = replace_alias_with_table(remove_brackets(node.details.get("Hash Cond")), get_alias_table_mappings()["ori_all"][file[:-5]])
        hash_cond_id = next(ids)
        ids_feature[hash_cond_id] = NodeFeature(hash_cond_id, full_name=hash_cond_full, alias_name=hash_cond_alias, details=node.details)

        if node.details.get("Join Filter"):
            join_filter_alias = node.details.get("Join Filter")
            join_filter_full = replace_alias_with_table(remove_brackets(node.details.get("Join Filter")), get_alias_table_mappings()["ori_all"][file[:-5]])
            join_filter_id = next(ids)
            ids_feature[join_filter_id] = NodeFeature(join_filter_id, full_name=join_filter_full, alias_name=join_filter_alias, details=node.details)
            node.link_node.extend([join_filter_id, hash_cond_id])
        else:
            node.link_node.append(hash_cond_id)

    if node.node_type == 'Nested Loop' and node.details.get("Join Filter"):
        join_filter_alias = node.details.get("Join Filter")
        join_filter_full = replace_alias_with_table(remove_brackets(node.details.get("Join Filter")), get_alias_table_mappings()["ori_all"][file[:-5]])
        join_filter_id = next(ids)
        ids_feature[join_filter_id] = NodeFeature(join_filter_id, full_name=join_filter_full, alias_name=join_filter_alias, details=node.details)
        node.link_node.insert(0, join_filter_id)

    if node.node_type == "Aggregate":
        if node.details.get("Subplan Name"):
            node.link_node.insert(0, node.details.get("Subplan Name"))
        elif node.details.get("Filter"):
            filter_id = next(ids)
            ids_feature[filter_id] = NodeFeature(filter_id, node.details.get("Filter"), node.details)
            node.link_node.insert(0, node.details.get("Filter"))
        elif node.parent:
            node.link_node.insert(0, node.children[0].link_node[0])
            if len(node.children) > 1:
                raise Exception("Error in file: " + file)

    if node.node_type in {"Hash", "Materialize", "Memoize"}:
        tmp_uuid = random_uuid()
        tmp_node_uuid.append(tmp_uuid)
        node.link_node.insert(0, tmp_uuid)

        if node.node_type == "Memoize":
            node.parent.link_node.append(node.link_node[0])
            if len(node.link_node) > 1:
                raise Exception("Error in file: " + file)
            node.link_node = []

    if node.node_type == "Merge Join":
        merge_cond_alias = node.details.get("Merge Cond")
        merge_cond_full = replace_alias_with_table(remove_brackets(node.details.get("Merge Cond")), get_alias_table_mappings()["ori_all"][file[:-5]])
        merge_cond_id = next(ids)
        ids_feature[merge_cond_id] = NodeFeature(merge_cond_id, full_name=merge_cond_full, alias_name=merge_cond_alias, details=node.details)
        node.link_node.insert(0, merge_cond_id)

    return node