import logging
import re

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

def puts(arg, variables, output): #done
    res = arg
    if is_function_invocation(arg):
        res = evaluate(arg, variables, output)  
    elif arg in variables:
        res = variables[arg]
        
    output.append(get_string(res))
    
    return None

def sets(arg, variables): #done
    args = arg.split(" ", 1)
    name = args[0]
    arg_to_set = args[1]
    
    if name in variables:
        raise Exception()

    #checks func
    if is_function_invocation(arg_to_set):
        variables[name] = evaluate(arg_to_set, variables, [])
    else:
        variables[name] = arg_to_set
        
    return None


def concat(arg, variables): 
    args = parse_arguments(arg)
    arg1 = find_string(args[0], variables)
    arg2 = find_string(args[1], variables)
    
    return "\"" + get_string(arg1) + get_string(arg2) + "\""
    
def lowercase(arg1, variables): #done
    if is_function_invocation(arg1):
        arg1 = evaluate(arg1, variables, [])
    elif arg1 in variables:
        arg1 = variables[arg1]
        
    return "\"" + get_string(arg1).lower() + "\""

def uppercase(arg1, variables): #done
    if is_function_invocation(arg1):
        arg1 = evaluate(arg1, variables, [])
    elif arg1 in variables:
        arg1 = variables[arg1]
        
    return "\"" + get_string(arg1).upper() + "\""
    
def stri(arg1, variables): #done
    if is_function_invocation(arg1):
        arg1 = evaluate(arg1, variables, [])
    elif arg1 in variables:
        arg1 = variables[arg1]
    
    if arg1.startswith("\""):
        return arg1
    else:
        if "." in arg1:
            idx = arg1.find(".")
            return "\"" + arg1[:idx + 5] + "\""
        return "\"" + arg1 + "\""
    
def parse_arguments(arg1):
    """Custom function to split arguments, respecting function applications and escaped strings."""
    args = []
    current_arg = []
    depth = 0  # To track parentheses
    inside_string = False  # To track whether we're inside an escaped string

    i = 0
    while i < len(arg1):
        char = arg1[i]

        # Toggle the inside_string flag when we encounter an escaped quote (but not in the middle of a function)
        if char == '\\' and i + 1 < len(arg1) and arg1[i + 1] == '"':
            inside_string = not inside_string
            current_arg.append(char)  # Add the backslash to the current_arg
            current_arg.append(arg1[i + 1])  # Add the quote to the current_arg
            i += 2
            continue

        # Handle parentheses for function invocation depth, but only when not inside a string
        if char == '(' and not inside_string:
            depth += 1
        elif char == ')' and not inside_string:
            depth -= 1

        # Split only when we're outside function invocations and strings
        if char == ' ' and depth == 0 and not inside_string:
            if current_arg:
                args.append(''.join(current_arg).strip())
                current_arg = []
        else:
            current_arg.append(char)
        
        i += 1

    # Add the last argument if present
    if current_arg:
        args.append(''.join(current_arg).strip())

    return args

def add(arg1, variables): #done
    args = parse_arguments(arg1)
    
    total_sum = 0  # Start with 0, but we will dynamically adjust
    is_int = True  # Track if all arguments are integers
    
    if len(args) == 1:
        raise Exception("Addition requires more than one argument")
    
    for arg in args:
        value = get_number(arg, variables)
        
        is_int = is_int and isinstance(value, int)
        total_sum += value
    
    return str(int(total_sum) if is_int else total_sum)  # Return int or  float


def mini(arg1, variables): #done
    args = parse_arguments(arg1)
    mini = float('inf')
    for arg in args:
        mini = min(mini, get_number(arg, variables))
    return str(mini)  

def maxi(arg1, variables): #done
    args = parse_arguments(arg1)
    maxi = float('-inf')
    for arg in args:
        maxi = max(maxi, get_number(arg, variables))
    return str(maxi)

def get_number(arg, variables): #done
    if is_function_invocation(arg):
        return get_number(evaluate(arg, variables, []), variables)
    elif arg in variables:
        return float(variables[arg]) if "." in variables[arg] else int(variables[arg])
    else:
        return float(arg) if "." in arg else int(arg)
    
def find_string(arg, variables):
    if is_function_invocation(arg):
        return evaluate(arg, variables, [])
    elif arg in variables:
        return variables[arg]
    else:
        return arg


def gt(arg1, variables): #done
    args = parse_arguments(arg1)
    arg1 = get_number(args[0], variables)
    arg2 = get_number(args[1], variables)
    if arg1 > arg2:
        return "true"
    else:
        return "false"

def lt(arg1, variables): #done
    args = parse_arguments(arg1)
    arg1 = get_number(args[0], variables)
    arg2 = get_number(args[1], variables)

    if arg1 < arg2:
        return "true"
    else:
        return "false"


def subtract(arg1, variables): 
    args = parse_arguments(arg1)
        
    is_int = True  # Track if all arguments are integers
    
    if is_function_invocation(args[0]):
        result = evaluate(args[0], variables, [])  # Evaluate function
        is_int = is_int and isinstance(result, int)
    elif args[0] in variables:
        result = float(variables[args[0]]) if '.' in str(variables[args[0]]) else int(variables[args[0]])
        is_int = is_int and isinstance(result, int)
    else:
        result = float(args[0]) if '.' in str(args[0]) else int(args[0])
        is_int = is_int and isinstance(result, int)
    
    for arg in args[1:]:
        if is_function_invocation(arg):
            value = evaluate(arg, variables, [])  # Evaluate function
        elif arg in variables:
            value = float(variables[arg]) if '.' in str(variables[arg]) else int(variables[arg])
        else:
            value = float(arg) if '.' in str(arg) else int(arg)
        
        is_int = is_int and isinstance(value, int)
        result -= value  # Subtract the value
    
    return int(result) if is_int else float(result)

def divide(arg1, variables):
    args = parse_arguments(arg1)
    if len(args) == 1:
        raise Exception()
    arg1 = get_number(args[0], variables)
    arg2 = get_number(args[1], variables)
    
    return str(arg1 / arg2)

def multiply(arg1, variables):
    args = parse_arguments(arg1)
    product = 1
    
    if len(args) == 1:
        raise Exception("Addition requires more than one argument")
    
    for arg in args:
        value = get_number(arg, variables)
        product *= value
    return str(product)

def replace(arg1, variables):
    args = parse_arguments(arg1)

    # Simplify each argument to resolve variables and functions
    source = find_string(args[0], variables)
    target = get_string(find_string(args[1], variables))
    replacement = get_string(find_string(args[2], variables))

    # Replace all occurrences of the target in the source
    result = source.replace(target, replacement)

    return result
        
def substring(arg1, variables):
    args = parse_arguments(arg1)

    # Simplify each argument: source (string), start (int), end (int)
    source = get_string(find_string(args[0], variables))
    start = get_number(args[1], variables)
    end = get_number(args[2], variables)
    # Ensure valid range
    if start < 0 or end < 0 or start > end or end >= len(source):
        raise ValueError("Invalid start or end index.")
    
    # Extract and return the substring
    result = source[start:end]
    return "\"" + result + "\""

def abso(arg1, variables):
    res = get_number(arg1, variables)
    return str(abs(res))

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
    elif function == "abs":
        return abso(args[1], variables)
    elif function == "gt":
        return gt(args[1], variables)
    elif function == "lt":
        return lt(args[1], variables)
    
def evaluateAll(expressions):
    variables = {}
    output = []
    
    for line_number, exp in enumerate(expressions, start=1):
            evaluate(exp, variables, output)
            
    return output

    
def parse(request):
    expressions = request["expressions"]
    output = evaluateAll(expressions)
    return {"output": output}


#when  i get home, change round to just get last 4 dp by string
request = {
    "expressions": [
        "(puts \"heloo\")",
        "(set x 5)",
        "(puts (uppercase (lowercase (str (abs (multiply 1 324 -34))))))",
        "(puts (concat \"heloo\" (concat \"heloo\" \"heloo\")))",
        "(puts (replace \"heloo\" \"o\" (concat \"heloo\" \"heloo\")))"
    ]
}
print(parse(request))