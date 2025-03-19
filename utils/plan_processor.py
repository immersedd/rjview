import re

def reset_condition_z3(condition):
    condition = condition.replace("\'", "\"")
    if condition.find("==") != -1:
        condition = condition.replace("==", "=")
    if condition.find("Or") != -1:
        condition = condition[2:]
        condition = condition.replace(",", " OR ")
    if condition.find("And") != -1:
        condition = condition[3:]
        condition = condition.replace(",", " AND ")
    if condition.find(" = \"__ANY__") != -1:
        inPattern = re.compile(' = \"__ANY__\{(.+?)\}')
        grps = inPattern.findall(condition)
        for grp in grps:
            inList = (", ").join(["'"+x.strip("\"")+"'" for x in grp.split(",")])
            condition = condition.replace(" = \"__ANY__{" + grp + "}\"", " IN (" + inList+")" )
    condition = condition.replace("= \"__LIKE__", "LIKE \"")
    condition = condition.replace("= \"__NOTLIKE__", "NOT LIKE \"")
    condition = condition.replace("= \"__NOTEQUAL__", "!= \"")
    condition = condition.replace("\"", "\'")
    return condition

def remove_invalid_tokens(predicate):
    if not predicate:
        return predicate
    x = re.sub(r'\(\(([a-zA-Z_]+)\)::text ~~ \'(((?!::text).)*)\'::text\)', r"(\1 = '__LIKE__\2')", predicate)
    x = re.sub(r'\(\(([a-zA-Z_]+)\)::text !~~ \'(((?!::text).)*)\'::text\)', r"(\1 = '__NOTLIKE__\2')", x)
    x = re.sub(r'\(\(([a-zA-Z_]+)\)::text <> \'(((?!::text).)*)\'::text\)', r"(\1 = '__NOTEQUAL__\2')", x)
    x = re.sub(r'\(([a-zA-Z_]+) ~~ \'(((?!::text).)*)\'::text\)', r"(\1 = '__LIKE__\2')", x)
    x = re.sub(r'\(([a-zA-Z_]+) !~~ \'(((?!::text).)*)\'::text\)', r"(\1 = '__NOTLIKE__\2')", x)
    x = re.sub(r'\(([a-zA-Z_]+) <> \'(((?!::text).)*)\'::text\)', r"(\1 = '__NOTEQUAL__\2')", x)
    x = re.sub(r'(\'[^\']*\')::[a-z_]+', r'\1', x)
    x = re.sub(r'\(([^\(]+)\)::[a-z_]+', r'\1', x)
    x = re.sub(r'\(([a-z_0-9A-Z\-\(\),. ]+) = ANY \(\'(\{.+?\})\'\[\]\)\)', r"(\1 = '__ANY__\2')", x)
    x = re.sub(r'\(SubPlan ([0-9]+)\)', r"(SubPlan_\1)", x)
    x = re.sub(r'(\w*[:]*[ ]*)SubPlan ([0-9]+)', r"(SubPlan_\2 = 1)", x)
    return x

def add_alias_to_condition(alias, con):
    if ") AND (" not in con:
        condi = con.split(' = ')
        if "." not in condi[0]:
            condi[0] = alias + "." + condi[0]
        if "." not in condi[1]:
            condi[1] = alias + "." + condi[1]
        return "(" + condi[0] + " = " + condi[1] + ")"
    else:
        conds = con.split(" AND ")
        condi = []
        for c in conds:
            cs = remove_brackets(c).split(" = ")
            if "." not in cs[0]:
                cs[0] = alias + "." + cs[0]
            if "." not in cs[1]:
                cs[1] = alias + "." + cs[1]
            condi.append("(" + cs[0] + " = " + cs[1] + ")")
        return "(" + " AND ".join(condi) + ")"

def add_prefix_to_columns(query, table_prefix, columns):
    for column in columns:
        pattern = r'(?<!\.)\b' + re.escape(column) + r'\b'
        query = re.sub(pattern, table_prefix + '.' + column, query)
    return query

def add_filter_tab(table, ftr):
    def replace_matched_terms(text, pattern):
        matches = re.findall(pattern, text)
        matchesSet = set(matches)
        for match in set(matches):
            if match == table:
                text = re.sub(rf"\b{re.escape(match)}\b", f"{table}.{match}", text)
                matchesSet.remove(match)
        for match in matchesSet:
            text = re.sub(rf"\b{re.escape(match)}\b", f"{table}.{match}", text)
        return text
    pattern_min_range_updated = r"\(\s*([^()<>]+?)\s*(?:=|!=|<|>|IS|LIKE|IN|NOT)"
    updated_text_with_matches_replaced = replace_matched_terms(ftr, pattern_min_range_updated)
    if updated_text_with_matches_replaced == ftr:
        print("errrrr")
    return updated_text_with_matches_replaced

def extract_substructures(structure):
    stack = []
    substructures = []

    for char in structure:
        if char == '(':
            stack.append('')
        elif char == ')':
            sub_expr = stack.pop()
            if stack:
                stack[-1] += '(' + sub_expr + ')'
            substructures.append(sub_expr)
        elif char != None:
            if stack:
                stack[-1] += char
    substructures = ["(" + sub + ")" for sub in substructures]
    return substructures

def get_alias2table(root, alias2table):
    if 'Relation Name' in root and 'Alias' in root:
        alias2table[root['Alias']] = root['Relation Name']
    if 'Plans' in root:
        for child in root['Plans']:
            get_alias2table(child, alias2table)