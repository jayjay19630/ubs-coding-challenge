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
        
    if isinstance(res, int):
        output.append(res)
    elif isinstance(res, float):
        output.append(round(res, 4))
    else:
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

def add(arg1, variables):
    args = parse_arguments(arg1)
    
    total_sum = 0  # Start with 0, but we will dynamically adjust
    is_int = True  # Track if all arguments are integers
    
    if len(args) == 1:
        raise Exception("Addition requires more than one argument")
    
    for arg in args:
        if is_function_invocation(arg):
            value = evaluate(arg, variables, [])  # Evaluate function
        elif arg in variables:
            value = float(variables[arg]) if '.' in str(variables[arg]) else int(variables[arg])
        else:
            value = float(arg) if '.' in str(arg) else int(arg)
        
        is_int = is_int and isinstance(value, int)
        total_sum += value
    
    return int(total_sum) if is_int else round(total_sum, 4)  # Return int or rounded float


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
    return maxi

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
    return result

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
    return product

def simplify(arg, variables):
    if is_function_invocation(arg):
        return evaluate(arg)
    elif arg in variables:
        return variables[arg]
    elif arg.startswith("\""):
        return get_string(arg)
    else:
        return arg

def replace(arg1, variables):
    args = parse_arguments(arg1)

    # Simplify each argument to resolve variables and functions
    source = simplify(args[0], variables)
    target = simplify(args[1], variables)
    replacement = simplify(args[2], variables)

    # Replace all occurrences of the target in the source
    result = source.replace(target, replacement)

    return result
        
def substring(arg1, variables):
    args = parse_arguments(arg1)

    # Simplify each argument: source (string), start (int), end (int)
    source = simplify(args[0], variables)
    start = int(simplify(args[1], variables))
    end = int(simplify(args[2], variables))

    # Ensure valid range
    if start < 0 or end < 0 or start > end or end > len(source):
        raise ValueError("Invalid start or end index.")
    
    # Extract and return the substring
    result = source[start:end]
    return result

def abso(arg1, variables):
    args = simplify(parse_arguments(arg1)[0])
    return abs(args)

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


def evaluateAll(expressions):
    variables = {}
    output = []
    
    for line_number, exp in enumerate(expressions, start=1):
        try:
            evaluate(exp, variables, output)
        except Exception as e:
            error_message = f"ERROR at line {line_number}"
            output.append(error_message)
            return output
      
    return output
    
def parse(request):
    expressions = request["expressions"]
    output = evaluateAll(expressions)
    return {"output": output}


request = {
    "expressions": [
        "(puts (add 5 5))",
        "(puts \"Hello World!\")",
        "(set x 5)",
        "(puts (concat \"ab\" \"c\"))",
        "(puts (str (add 5 5.0 5)))",
        "(puts (str (add (subtract (multiply (divide -1151 8297) (add -8803 -9473.4851)) 4100) 9799)))",
        "(puts (str (subtract 500 259)))",
        "(puts (add 1))",
        "(puts (substring \"abcdef\" 140 168))",
        "(puts (replace \"Hello World\" \"World\" \"There\"))"
    ]
}
print(parse(request))