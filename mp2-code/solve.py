# -*- coding: utf-8 -*-
import numpy as np
from collections import deque


def solve(board, pents):
    print("[ * ]"*100)
    solution = [ ]

    solution_board = board * 0
    #variables = define_initial_variables(solution_board, [pents[9],pents[2]])
    variables = define_initial_variables(solution_board, pents)
    unassigned_variables = [ ]
    assigned_variables = deque([ ])

    #test_board = np.array([[0,1,1,1,1],[0,1,1,0,1],[1,1,0,0,1],[0,1,1,1,1],[0,0,1,1,1]])
    #has_small_holes(test_board)

    for var, val in variables.items():
        #LRV: create a list of variables showing first the variables with fewer domain
        unassigned_variables.append((var,val["domain"]))
        unassigned_variables = sorted(unassigned_variables, key =  lambda item: len(item[1]))

    while len(unassigned_variables) > 0:
        current_variable = unassigned_variables[0]
        print("Variable", current_variable[0])
        print("unassigned_variables", len(unassigned_variables))
        print("Assigned_variables", len(assigned_variables))
        (variable_id , values) = current_variable
        dead_end = False
        #print("# of posible Values", len(values))
        unassigned_variables.remove(current_variable)
        selected_value = None
        impossible_values = [ ]
        min_domain_general_reduction = 0

        #print("values")
        #print(values)
        for value in values:
            #print("value", value)
            impossible_value = False
            domain_general_reduction = 0
            temp_solution_board = update_state(variables, solution_board, value, variable_id)

            for unassigned_variable in unassigned_variables[:3]:

                (u_variable,u_values) = unassigned_variable
                last_domain_size = len(u_values)

                new_domain = update_domain(variables, temp_solution_board, u_variable, u_values)
                new_domain_size = len(new_domain)

                #print("possible new domain", new_domain_size)

                if new_domain_size == 0:
                    impossible_value = True
                    #print("Impossible value")
                    break
                else:
                    domain_general_reduction = domain_general_reduction + (last_domain_size - new_domain_size)

            if impossible_value:
                current_variable[1].remove(value)
                break

            else:
                if min_domain_general_reduction == 0:
                    selected_value = value
                    min_domain_general_reduction = domain_general_reduction;

                elif domain_general_reduction < min_domain_general_reduction:
                    min_domain_general_reduction = domain_general_reduction;
                    selected_value = value

        #After checking all the values
        if selected_value:
            values.remove(selected_value)
            solution_board = update_state(variables, solution_board, selected_value, variable_id)
            unassigned_variables = [(var[0],update_domain(variables, solution_board, var[0], var[1])) for var in unassigned_variables]
            assigned_variables.append(current_variable)

            print("solution_board:")
            print(solution_board)
            solution.append(tile_in_form(variables, current_variable[0], selected_value))

        else:
            print("dead end")
            #Backtracking

            last_variable = assigned_variables.pop()
            solution_board = remove_tile(solution_board, last_variable[0])
            unassigned_variables.append(current_variable)

            while len(last_variable[1]) == 0:
                last_last_variable = assigned_variables.pop()
                unassigned_variables.append(last_variable)
                last_variable = last_last_variable
                solution_board = remove_tile(solution_board, last_variable[0])
                del solution[-1]

            #Reset the domain of all the unassigned variables for the last state
            unassigned_variables = [(var[0],update_domain(variables, solution_board, var[0], variables[var[0]]["domain"])) for var in unassigned_variables]

            unassigned_variables.append(last_variable)
            unassigned_variables = sorted(unassigned_variables, key =  lambda item: len(item[1]))
            del solution[-1]

            print(solution_board)

    return solution


#Method to define the store the dorms and the initial domain of each tile
def define_initial_variables(board, pents):
    variables = dict()

    for tile in pents:
        tile_id = np.max(tile[0])
        tile_shape = np.array([[(x/x) if not (x == 0) else 0 for x in j] for j in tile])
        rep_shape = False

        for v,var in enumerate(variables):
            #check if this type of tile have been found before
            if np.array_equal(variables[var]["forms"][0],tile_shape):
                variables[tile_id] =  variables[var]
                rep_shape = True
                break

        if rep_shape == False:
            variables[tile_id] =  {"forms":forms(tile_shape), "domain":[ ]}
            #define the initial domine with the unary: the tile has to be completly in the board
            variables[tile_id]["domain"] = set_domain(variables, board, tile_id)

    return variables

#Set the domain for a tile in a specific board
def set_domain(variables,board, variable):
    domain = [ ]
    tile_forms = variables[variable]["forms"]
    for i, row in enumerate(board):
        for j, column in enumerate(row):
            for form_id, form in tile_forms.items():
                if not overflows_the_board(board, (i, j), form):
                    #locate the tile on position
                    domain.append((form_id,(i, j)))

    return domain


def update_domain(variables, new_board,variable, old_domain):
    new_domain = [ ]
    for value in old_domain:
        if not tile_overlap(variables, new_board, variable, value):
            new_domain.append(value)

    return new_domain

# To produce the different form that a tile can have
def forms(tile):
    temp_form_id = 0;
    forms = dict()
    forms[temp_form_id] = tile
    temp_form_id = temp_form_id + 1
    alt_forms = [np.rot90(tile) , np.rot90(np.rot90(tile)) , np.rot90(np.rot90(np.rot90(tile))), np.flip(tile), np.rot90(np.flip(tile)) , np.rot90(np.rot90(np.flip(tile))), np.rot90(np.rot90(np.rot90(np.flip(tile))))]

    for i, alt in enumerate(alt_forms):
        rep = False
        for form_id, form in forms.items():
            if np.array_equal(alt,form):
                rep = True
                break

        if not rep:
            forms[temp_form_id] = alt
            temp_form_id = temp_form_id + 1

    return forms


#Check constraint of laying completly on the board
def overflows_the_board(board, pos, tile):
    overflow_value = False
    #recognize the board dimensions
    board_high = len(board)
    board_width = len(board[0])

    #recognize the tile dimensions
    high = len(tile)
    width = len(tile[0])

    #position to try
    row = pos[0]
    column = pos[1]

    if row + high > board_high or column + width > board_width:
        overflow_value = True

    return overflow_value


#Check constraint of not overlaping
def tile_overlap(variables, board, variable, value):
    overlaps = False
    (form_id, pos) = value
    tile_form = variables[variable]["forms"][form_id]
    for x, tile_row in enumerate(tile_form):
        for y, tile_column in enumerate(tile_row):
            #print("position", pos)
            #print("x:",x)
            if tile_column == 1 and board[pos[0]+x][pos[1]+y] != 0:
                overlaps = True
                break

    return overlaps

#More constrain method to avoid false movements
def has_small_holes(board):
    zeros = [ ]
    islands = dict()

    (high, width) = board.shape
    for i, row in enumerate(board):
        for j, column in enumerate(row):
            if column == 0:
                zeros.append((i,j))
                islands[(i,j)] = [(i,j)]


    for z in zeros:
        for land in islands.keys():
            if z != land:
                if abs(z[0] - land[0]) == 1 or abs(z[1] - land[1]) == 1:
                    islands[land].append(z)

    final_islands = [v for v in islands.values()]
    print(final_islands)


#Create a new board with the variable possitionated in the last stat board
def update_state(variables, board, value, variable):
    new_board = np.copy(board)
    (form_id, pos) = value
    tile_form = variables[variable]["forms"][form_id]

    for x, tile_row in enumerate(tile_form):
        for y, tile_column in enumerate(tile_row):
            if tile_column == 1:
                new_board[pos[0]+x][pos[1]+y] = variable

    return new_board

def remove_tile(board, tile_id):
    for x, row in enumerate(board):
        for y, column in enumerate(row):
            if column == tile_id:
                board[x][y] = 0

    return board

def tile_in_form(variables, variable, value):
    (form_id, pos) = value
    form_variable = variables[variable]["forms"][form_id]
    form_variable = form_variable.astype(int) * variable
    return (form_variable, pos)
