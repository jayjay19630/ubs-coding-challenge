import logging
import re

from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)
def is_function_invocation(expression):
    return expression[0] == "(" and expression[-1] == ")"

def find_function_end(arg):
    """Find the index where the function invocation ends."""
    if not arg.startswith("("):
        return -1  # Not a function invocation, no need to find an end

    count = 0  # To track parentheses
    for i, char in enumerate(arg):
        if char == "(":
            count += 1
        elif char == ")":
            count -= 1
            if count == 0:
                return i + 1  # Return index after the closing parenthesis
    return -1  # Mismatched parentheses, should raise an error in a real scenario

def find_string_end(arg):
    """Find the index where the quoted string ends."""
    pattern = r'\"(.*?)\"'
    match = re.search(pattern, arg)
    if match:
        return match.end()  # Return the position right after the quoted string
    return -1

def is_string(expression):
    return expression[:2] == "\"" and expression[-2:] == "\""

def is_bool(expression):
    return expression == "true" or expression == "false"

def is_number(expression):
    try:
        float(expression)
        return True
    except ValueError:
        return False
    
def get_string(exp):
    pattern = r'\"(.*?)\"'
    return re.findall(pattern, exp)[0]

def puts(arg, variables, output):
    #checks func
    if is_function_invocation(arg):
        res = evaluate(arg, variables, output)  
    elif arg in variables:
        res = variables[arg]
    elif arg.strip().startswith("\""):
        res = get_string(arg)
    else:
        res = str(arg)
    output.append(res)

def sets(arg, variables):
    args = arg.split(" ", 1)
    name = args[0]
    arg_to_set = args[1]
    
    #checks func
    if is_function_invocation(arg_to_set):
        arg_to_set = evaluate(arg_to_set, variables, [])
    
    elif is_bool(arg_to_set):
        variables[name] = bool(arg_to_set)
    elif is_number(arg_to_set):
        variables[name] = float(arg_to_set)
    else:
        variables[name] = get_string(arg_to_set)
        
    return None

def concat(arg, variables):
    arg = arg.strip()
    
    if not arg.strip().startswith('\"'):
        
        func_end = find_function_end(arg)
        if func_end > 0:
            # First part is a function invocation
            arg1 = arg[:func_end].strip()  # The function invocation
            arg2 = arg[func_end:].strip()  # The rest of the argument
        else:
            # Split the argument into two parts
            args = arg.split(" ", 1)
            arg1 = args[0].strip()
            arg2 = args[1].strip()

        if is_function_invocation(arg1):
            arg1 = evaluate(arg1, variables, [])
        else:
            arg1 = variables[arg1]
        
        if is_function_invocation(arg2):
            arg2 = evaluate(arg2, variables, [])
        elif arg2 in variables:
            arg2 = variables[arg2]
        else:
            arg2 = get_string(arg2)
            
        return arg1 + arg2
    
    else:
        # First part is a quoted string
        string_end = find_string_end(arg)  # Find where the first quoted string ends
        arg1 = re.findall(r'\"(.*?)\"', arg)[0]  # Extract the first quoted string
        remaining = arg[string_end:].strip()  # The remaining part of the argument

        # Handle the second argument (variable, function invocation, or string)
        if remaining:
            if is_function_invocation(remaining):
                arg2 = evaluate(remaining, variables, [])
            elif remaining in variables:
                arg2 = variables[remaining]
            else:
                arg2 = get_string(remaining)
        else:
            arg2 = ""

        return arg1 + arg2
    
def lowercase(arg1, variables):    
    if is_function_invocation(arg1):
        arg1 = evaluate(arg1, variables, [])
    
    if arg1 in variables:
        return variables[arg1].lower()
    else:
        return get_string(arg1).lower()

def uppercase(arg1, variables):
    if is_function_invocation(arg1):
        arg1 = evaluate(arg1, variables, [])
    
    if arg1 in variables:
        return variables[arg1].upper()
    else:
        return get_string(arg1).upper()
    
def stri(arg1, variables):
    if arg1 in variables:
        return str(variables[arg1])
    elif is_function_invocation(arg1):
        return str(evaluate(arg1, variables, []))
    else:
        return str(arg1)
    
def parse_arguments(arg1):
    """Custom function to split arguments, respecting function applications."""
    args = []
    current_arg = []
    depth = 0  # To track parentheses

    for char in arg1:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        
        if char == ' ' and depth == 0:
            # Only split on spaces outside of function invocations
            if current_arg:
                args.append(''.join(current_arg).strip())
                current_arg = []
        else:
            current_arg.append(char)
    
    # Add the last argument if present
    if current_arg:
        args.append(''.join(current_arg).strip())
    
    return args

def add(arg1, variables):
    args = parse_arguments(arg1)
    total_sum = 0.0  # Initialize as float
    for arg in args:
        if is_function_invocation(arg):
            total_sum += evaluate(arg, variables, [])  # Evaluate function
        elif arg in variables:
            total_sum += float(variables[arg])  # Fetch value from variables
        else:
            total_sum += float(arg)  # Convert to float
    return round(total_sum, 4)  # Round to 4 decimal places

def mini(arg1, variables):
    args = parse_arguments(arg1)
    mini = float('inf')
    for arg in args:
        if is_function_invocation(arg):
            mini = min(mini, evaluate(arg, variables, []))  # Evaluate function
        elif arg in variables:
            mini = min(mini, variables[arg])  # Fetch value from variables
        else:
            mini = min(mini, float(arg))  # Convert to float
    return round(mini, 4)  # Round to 4 decimal places

def maxi(arg1, variables):
    args = parse_arguments(arg1)
    maxi = float('-inf')
    for arg in args:
        if is_function_invocation(arg):
            maxi = max(maxi, evaluate(arg, variables, []))  # Evaluate function
        elif arg in variables:
            maxi = max(maxi, float(variables[arg]))  # Fetch value from variables
        else:
            maxi = max(maxi, float(arg))  # Convert to float
    return round(maxi, 4)  # Round to 4 decimal places

def subtract(arg1, variables):
    args = parse_arguments(arg1)
    if is_function_invocation(args[0]):
        result = evaluate(args[0], variables, [])  # Evaluate function
    elif args[0] in variables:
        result = float(variables[args[0]])  # Convert to float
    else:
        result = float(args[0])  # Initialize with the first argument
    
    for arg in args[1:]:
        if is_function_invocation(arg):
            result -= evaluate(arg, variables, [])  # Evaluate function
        elif arg in variables:
            result -= float(variables[arg])  # Fetch value from variables
        else:
            result -= float(arg)  # Convert to float
    return round(result, 4)  # Round to 4 decimal places

def divide(arg1, variables):
    args = parse_arguments(arg1)
    if is_function_invocation(args[0]):
        result = evaluate(args[0], variables)  # Evaluate function
    elif args[0] in variables:
        result = float(variables[args[0]])  # Convert to float
    else:
        result = float(args[0])  # Initialize with the first argument
    
    for arg in args[1:]:
        if is_function_invocation(arg):
            result /= evaluate(arg, variables, [])  # Evaluate function
        elif arg in variables:
            result /= float(variables[arg])  # Fetch value from variables
        else:
            result /= float(arg)  # Convert to float
    return round(result, 4)  # Round to 4 decimal places

def multiply(arg1, variables):
    args = parse_arguments(arg1)
    product = 1.0  # Initialize as float
    
    for arg in args:
        if is_function_invocation(arg):
            product *= evaluate(arg, variables, [])  # Evaluate function
        elif arg in variables:
            product *= float(variables[arg])  # Fetch value from variables
        else:
            product *= float(arg)  # Convert to float
    return round(product, 4)  # Round to 4 decimal places
    
def replace(arg1, variables):
    return ""

def substring(arg1, variables):
    return ""
    
def evaluate(exp, variables, output):
    args = exp[1:-1].split(" ", 1)
    function = args[0]
    if function == "puts":
        puts(args[1], variables, output)
    elif function == "set":
        sets(args[1], variables)
    elif function == "concat":
        return concat(args[1], variables)
    elif function == "uppercase":
        return uppercase(args[1], variables)
    elif function == "lowercase":
        return lowercase(args[1], variables)
    elif function == "str":
        return stri(args[1], variables)
    elif function =="add":
        return add(args[1], variables)
    elif function =="multiply":
        return multiply(args[1], variables)
    elif function =="subtract":
        return subtract(args[1], variables)
    elif function =="divide":
        return divide(args[1], variables)
    elif function == "replace":
        return replace(args[1], variables)
    elif function == "substring":
        return substring(args[1], variables)
    elif function == "max":
        return maxi(args[1], variables)
    elif function == "min":
        return mini(args[1], variables)


def evaluateAll(expressions):
    variables = {}
    output = []
    
    print(expressions)
    
    for exp in expressions:
        evaluate(exp, variables, output)
      
    return output
    
@app.route('/lisp-parser', methods=['POST'])
def parse():
    req = request.json
    expressions = req["expressions"]
    output = evaluateAll(expressions)
    return jsonify({"output": output})
