# -*- coding: utf-8 -*-
import numpy as np
from collections import deque


def solve(board, pents):
    print("[ * ]"*100)
    solution = [ ]

    solution_board = np.array([[-1 if  (x == 0) else 0 for x in j] for j in board])
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
        print("Starts with this possible Values", len(values))
        unassigned_variables.remove(current_variable)
        selected_value = None
        min_domain_general_reduction = 0

        #print("values")
        #print(values)
        for value in values:
            print("value", value)
            impossible_value = False
            domain_general_reduction = 0
            temp_solution_board = update_state(variables, solution_board, value, variable_id)

            for unassigned_variable in unassigned_variables[:3]:
                (u_variable,u_values) = unassigned_variable
                last_domain_size = len(u_values)
                new_domain = update_domain(variables, temp_solution_board, u_variable, u_values)
                new_domain_size = len(new_domain)

                #if a variable has domain 0 after evaluating a value
                if new_domain_size == 0:
                    impossible_value = True
                    #print("Impossible value")
                    break
                else:
                    domain_general_reduction = domain_general_reduction + (last_domain_size - new_domain_size)

            if impossible_value:
                values.remove(value)
                print("impossible value")


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
            print("Finishes with this possible Values", len(current_variable[1]))

            print("solution_board:")
            print(solution_board)
            solution.append(tile_in_form(variables, current_variable[0], selected_value))

        else:
            print("dead end")
            #Backtracking
            #gives back the current variable to the unassigne variable
            unassigned_variables.append(current_variable)
            #calls the parent variable and back track the state of the board
            last_variable = assigned_variables.pop()
            solution_board = remove_tile(solution_board, last_variable[0])

            #If the domain of the parent variable is empty then
            while len(last_variable[1]) == 0:
                #calls the grand parent variable
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
            #and a cuztom constraing of not leaving "zeros-islands" smaler than the size of the pieces (5 for pentominos)
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
                    temp_board = update_state(variables, board, (form_id,(i, j)), variable)
                    print(temp_board)
                    if not one_overlap(board, (i, j), form):
                        if not island_check(temp_board,5):
                            print("approve")
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

#Check constraint of not overlaping on 0 values (-1 in this case)
def one_overlap(board, pos, form):
    overlaps = False
    for x, tile_row in enumerate(form):
        for y, tile_column in enumerate(tile_row):
            if tile_column == 1 and board[pos[0]+x][pos[1]+y] != 0:
                overlaps = True
                break

    return overlaps

#Check constraint of not overlaping
def tile_overlap(variables, board, variable, value):
    overlaps = False
    (form_id, pos) = value
    tile_form = variables[variable]["forms"][form_id]
    for x, tile_row in enumerate(tile_form):
        for y, tile_column in enumerate(tile_row):
            if tile_column == 1 and board[pos[0]+x][pos[1]+y] != 0:
                overlaps = True
                break

    return overlaps


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


def island_check(board,number):
    zero = np.argwhere(board == 0)
    zero_list = zero.tolist()
    zero_list_sorted = sorted(zero_list, key=lambda x: x[0])
    (X, Y) = np.shape(board)
    neighbors = lambda x, y: [[x2, y2] for x2 in range(x - 1, x + 2)
                              for y2 in range(y - 1, y + 2)
                              if (-1 < x <= X and
                                  -1 < y <= Y and
                                  (x != x2 or y != y2) and
                                  (0 <= x2 <= X) and
                                  (0 <= y2 <= Y))]
    island = []
    un_assigned = zero_list_sorted.copy()
    while len(un_assigned) != 0:
        element = un_assigned[0]
        new_island = [element]
        indicator = 1
        element_list = [element]
        un_assigned.remove(element)
        while indicator != 0:
            previous_indicator = indicator
            indicator = 0
            new_list = []
            for k in range(previous_indicator):
                element = element_list[-k]
                #print('element',element)
                element_neighbor = neighbors(element[0],element[1])
                #print(element_neighbor)
                for i in range(len(un_assigned)):
                    if un_assigned[i] in element_neighbor:
                        new_island.append(un_assigned[i])
                        indicator += 1
                        #print('island',new_island)
                    new_list = new_island[-indicator:]
                    #print('list',new_list)
                for i in new_list:
                    if i in un_assigned:
                        un_assigned.remove(i)
            element_list = new_list
        island.append(new_island)
    island_size = []
    for i in island:
        island_size.append(len(i))
        #print(i)
    output = []
    for i in range(len(island_size)):
        if island_size[i] < number:
            output.append(island[i])
    if len(output) != 0:
        return output
    else:
        return False
