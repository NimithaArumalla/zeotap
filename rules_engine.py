import mysql.connector
import json

# Establish database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Nimitha@1419.',
    database='zeotap'
)
cursor = conn.cursor()

# Function to insert a rule into the database
def insert_rule(rule_name, rule_string, ast):
    cursor.execute(
        "INSERT INTO rules (rule_name, rule_string, ast) VALUES (%s, %s, %s)",
        (rule_name, rule_string, json.dumps(ast.to_dict()))
    )
    conn.commit()
    return cursor.lastrowid

# Function to fetch a rule from the database
def fetch_rule(rule_id):
    cursor.execute("SELECT rule_string, ast FROM rules WHERE id = %s", (rule_id,))
    row = cursor.fetchone()
    if row:
        rule_string, ast_dict = row
        ast = Node.from_dict(json.loads(ast_dict))
        return rule_string, ast
    return None

# Function to create an AST from a rule string
def create_rule(rule_string):
    import re
    tokens = re.findall(r'(\(|\)|\w+|>|<|=|AND|OR)', rule_string)
    token_iterator = iter(tokens)
    
    def parse():
        token = next(token_iterator)
        if token == '(':
            left = parse()
            operator = next(token_iterator)
            right = parse()
            next(token_iterator)  # skip ')'
            return Node(type="operator", value=operator, left=left, right=right)
        elif token.isnumeric():
            return Node(type="operand", value=int(token))
        else:
            return Node(type="operand", value=token)
    
    return parse()

# Function to combine multiple ASTs
def combine_rules(rules):
    combined_ast = None
    for rule in rules:
        rule_ast = create_rule(rule)
        if combined_ast is None:
            combined_ast = rule_ast
        else:
            combined_ast = Node(type="operator", value="AND", left=combined_ast, right=rule_ast)
    return combined_ast

# Function to evaluate an AST against provided data
def evaluate_rule(ast, data):
    def evaluate(node):
        if node.type == "operand":
            if isinstance(node.value, str):
                parts = node.value.split(' ', 2)
                if len(parts) < 3:
                    return False  # Return False if the operand is not properly structured
                
                key = parts[0]
                condition = parts[1]
                threshold = int(parts[2]) if parts[2].isdigit() else parts[2].strip("'")
                
                value = data.get(key, None)
                
                if condition == '>':
                    return value > threshold
                elif condition == '<':
                    return value < threshold
                elif condition == '=':
                    return value == threshold
                else:
                    return False
            else:
                return False
        elif node.type == "operator":
            left_val = evaluate(node.left)
            right_val = evaluate(node.right)
            
            if node.value == "AND":
                return left_val and right_val
            elif node.value == "OR":
                return left_val or right_val
        return False
    
    return evaluate(ast)

# Define a Node class for AST
class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type  # "operator" for AND/OR, "operand" for conditions
        self.value = value  # e.g., "age > 30"
        self.left = left
        self.right = right

    def to_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        node = cls(type=data["type"], value=data["value"])
        node.left = cls.from_dict(data["left"])
        node.right = cls.from_dict(data["right"])
        return node

    def __str__(self):
        return f'Node(type={self.type}, value={self.value}, left={self.left}, right={self.right})'

# Example usage
rule_name = "Rule1"
rule_string = "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience >5)"
ast = create_rule(rule_string)

# Insert rule into the database
rule_id = insert_rule(rule_name, rule_string, ast)
print(f"Inserted rule with ID: {rule_id}")

# Fetch rule from the database
fetched_rule_string, fetched_ast = fetch_rule(rule_id)
print(f"Fetched rule string: {fetched_rule_string}")
print(f"Fetched AST: {fetched_ast}")

# Define the data to test against
sample_data = {"age": 35, "department": "Sales", "salary": 60000, "experience": 3}

# Evaluate the rule against the data
result = evaluate_rule(fetched_ast, sample_data)
print(result)  # Should print True or False based on the rule

# Close the database connection
cursor.close()
conn.close()
