import logging
import re

from flask import request, jsonify
from collections import defaultdict, deque

from routes import app

logger = logging.getLogger(__name__)

# Function to preprocess the increment rule and avoid using 'count *' during processing
def preprocess_increment_rule(increment):
    increment = increment.strip()

    if increment == 'count * count':
        return lambda count: count * count  # Preprocess to square the count
    elif 'count *' in increment:
        # Extract the multiplier and return a function that multiplies the count
        factor = int(increment.split('*')[1].strip())
        return lambda count: count * factor
    elif 'count +' in increment:
        # Extract the addend and return a function that adds the value
        addend = int(increment.split('+')[1].strip())
        return lambda count: count + addend
    else:
        # Default: if no valid rule, return the count unchanged
        return lambda count: count
    
# Function to parse the markdown input into structured data
def parse_markdown_table(md_table):
    labs = []
    lines = md_table.strip().split("\n")
    
    # Skip header and separator (first two lines)
    for line in lines[2:]:
        parts = re.split(r'\s*\|\s*', line.strip())
        if len(parts) < 5:
            continue  # Skip empty or malformed lines

        lab = int(parts[1])  # Lab ID
        cell_counts = list(map(int, parts[2].split()))  # Cell counts
        increment = preprocess_increment_rule(parts[3].strip())  # Increment rule
        condition = list(map(int, parts[4].split()))  # Condition (three numbers)

        labs.append({
            'lab': lab,
            'cell_counts': cell_counts,
            'increment': increment,
            'condition': condition
        })

    return labs

def simulate_lab_work(labs, total_days=10000, interval=1000):
    analysis_count = defaultdict(int)  # Tracks counts at intervals for each lab
    lab_dict = defaultdict(dict)  # Stores each lab's working dishes and conditions
    res = {}

    # Populate lab_dict with data from labs
    for lab in labs:
        lab_dict[lab['lab']] = {
            'cell_counts': deque(lab['cell_counts']),
            'increment': lab['increment'],
            'condition': lab['condition']
        }

    # Now get the sorted list of lab keys after lab_dict is populated
    lab_keys = sorted(lab_dict.keys())

    # Simulate days
    for day in range(1, total_days + 1):
        # Dictionary to track the new state of cells being passed between labs each day
        next_lab_work = defaultdict(list)

        # Iterate over the labs in sorted order
        for key in lab_keys:
            increment_rule = lab_dict[key]['increment']
            div, lab_if_true, lab_if_false = lab_dict[key]['condition']

            cell_counts = lab_dict[key]["cell_counts"]

            while cell_counts:
                cell_count = cell_counts.popleft()  # Remove the first element in the queue
                new_cell = increment_rule(cell_count)
                
                # Pass the new cell to the appropriate lab based on the condition
                if new_cell % div == 0:
                    next_lab_work[lab_if_true].append(new_cell)
                else:
                    next_lab_work[lab_if_false].append(new_cell)
                analysis_count[key] += 1            
        
            # Move the dishes to the respective labs for the next day
            for key in next_lab_work:
                for cell_count in next_lab_work[key]:   
                    lab_dict[key]["cell_counts"].append(cell_count)
            next_lab_work = defaultdict(list)
        
        if day % interval == 0:
            res[day] = [analysis_count[key] for key in lab_keys]
        print(day)
        print(analysis_count)

    return res

# Define the POST endpoint
@app.route('/lab_work', methods=['POST'])
def lab_work():
    try:
        data = request.json  # Extract the input data
        results = []

        # Process each test case
        for test_case in data:
            labs = parse_markdown_table(test_case)
            result = simulate_lab_work(labs)
            results.append(result)

        return jsonify(results)  # Return the result in JSON format

    except Exception as e:
        return jsonify({"error": str(e)}), 400
