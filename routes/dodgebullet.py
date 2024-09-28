import logging
from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)

# Parse the map string
def parse_map(map_str):
    grid = [list(line) for line in map_str.split("\n")]
    player_pos = None
    bullets = []
    
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == "*":
                player_pos = (r, c)
            elif cell in "udrl":
                bullets.append((r, c, cell))
    
    return grid, player_pos, bullets

# Helper to move bullets
def move_bullets(bullets, grid):
    new_bullets = []
    for r, c, direction in bullets:
        new_r, new_c = r, c
        if direction == 'u':
            new_r -= 1
        elif direction == 'd':
            new_r += 1
        elif direction == 'l':
            new_c -= 1
        elif direction == 'r':
            new_c += 1
        
        # Ensure bullets stay inside the grid, or stop moving if they go out of bounds
        if 0 <= new_r < len(grid) and 0 <= new_c < len(grid[0]):
            new_bullets.append((new_r, new_c, direction))
    
    return new_bullets

# Possible directions to move: (delta_row, delta_col, direction)
move_directions = [(-1, 0, 'u'), (1, 0, 'd'), (0, -1, 'l'), (0, 1, 'r')]
opp_bullet = {
    "l": "r",
    "r": "l",
    "u": "d",
    "d": "u"
}

# Helper to check if a move is safe
def is_safe_move(r, c, move, grid):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] != opp_bullet[move]

# Helper to check if a bullet will hit the player after its move
def is_safe_after_bullet_move(r, c, bullets):
    for br, bc, d in bullets:
        if d == 'u':
            new_r, new_c = br - 1, bc
        elif d == 'd':
            new_r, new_c = br + 1, bc
        elif d == 'l':
            new_r, new_c = br, bc - 1
        elif d == 'r':
            new_r, new_c = br, bc + 1
        
        if (r, c) == (new_r, new_c):
            return False
    return True

# Recursive DFS to dodge bullets without using a visited set
def dodge_bullets(grid, player_pos, bullets, instructions):
    print(bullets)
    print(player_pos)
    for dr, dc, move in move_directions:
        new_r = player_pos[0] + dr
        new_c = player_pos[1] + dc
        
        # Check if the move is safe
        if is_safe_move(new_r, new_c, move, grid) and is_safe_after_bullet_move(new_r, new_c, bullets):
            next_bullets = move_bullets(bullets, grid)
            new_instructions = instructions[:] + [move]
            
            # If the bullets are not moving anymore and the player is in a safe spot, return the path
            if not next_bullets:
                return new_instructions
            
            # Recur with the new state
            result = dodge_bullets(grid, (new_r, new_c), next_bullets, new_instructions)
            
            # If a valid path is found, return it
            if result:
                return result
    
    # If no valid move found, return None
    return None

@app.route('/dodge', methods=['POST'])
def dodge_endpoint():
    # Use request.data to fetch the text body
    map_str = request.data.decode('utf-8')
    grid, player_pos, bullets = parse_map(map_str)
    
    print(grid)
    print(player_pos)
    print(bullets)
    
    # Try to find instructions to dodge all bullets using DFS without visited set
    instructions = dodge_bullets(grid, player_pos, bullets, [])
    
    # If no valid instructions, return null
    if instructions is None:
        return jsonify({"instructions": None})
    
    return jsonify({"instructions": instructions})

