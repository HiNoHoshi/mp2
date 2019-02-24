# -*- coding: utf-8 -*-
import numpy as np
from queue import PriorityQueue
import datetime



def solve(board, pents):
    """
    This is the function you will implement. It will take in a numpy array of the board
    as well as a list of n tiles in the form of numpy arrays.

    -Use np.flip and np.rot90 to manipulate pentominos.

    -You can assume there will always be a solution.
    """
    solution = [ ]

    solution_board = board * 0
    #print(solution_board)
    variables = define_initial_variables(solution_board, pents)
    variables = dict(sorted(variables.items(), key =  lambda item: len(item[1]["domain"])))
    unasigned_variables = dict()


    for variable, values in variables.items():
        unasigned_variables[variable] = values["domain"]

    for variable, values in variables.items():
        print("Variable", variable)
        del unasigned_variables[variable]
        selected_value = 0
        min_domain_general_reduction = 0

        print(datetime.datetime.now())
        for value in values["domain"]:

            if not tile_overlap(solution_board, value):
                impossible_value = False
                domain_general_reduction = 0

                temp_solution_board = update_state(solution_board, value, variable)

                for unasigned_variable, temp_domain in unasigned_variables.items():
                    last_domain_size = len(temp_domain)
                    new_domain_size = len(set_domain(temp_solution_board, variables[unasigned_variable]["forms"]))

                    if new_domain_size == 0:
                        impossible_value = True
                        break
                    else:
                        domain_general_reduction = domain_general_reduction + (last_domain_size - new_domain_size)

                if not impossible_value:
                    if min_domain_general_reduction == 0:
                        selected_value = value
                        min_domain_general_reduction = domain_general_reduction;

                    elif domain_general_reduction > min_domain_general_reduction:
                        min_domain_general_reduction = domain_general_reduction;
                        selected_value = value


        print("solution_board:")
        print(solution_board)
        solution_board = update_state(solution_board, selected_value, variable)
        solution.append(formating_solution(selected_value, variable))

    #print(solution_board)
    return solution



#Method to format the solution for a tile based on the value and its Id
def formating_solution(value, pent_id):
    pos_row = -1
    pos_column = -1
    origin_pent = [ ]

    for i, row in enumerate(value):
        temp_row = [ ]
        for j, column in enumerate(row):
            if -1 in column:
                temp_row.append(0)
            else:
                temp_row.append(pent_id)
                if pos_row == -1:
                    pos_row = column[0] - i
                if pos_column == -1:
                    pos_column = column[1]

        origin_pent.append(temp_row)

    return (np.array(origin_pent),(pos_row, pos_column))


#Method to define the store the dorms and the initial domain of each tile
def define_initial_variables(board, pents):
    variables = dict()

    for tile in pents:
        tile_shape = np.array([[(x/x) if not (x == 0) else 0 for x in j] for j in tile])
        rep_shape = False
        #print("variables",variables)
        for v,var in enumerate(variables):
            #check if this type of tile have been found before
            if np.array_equal(variables[var]["forms"][0],tile_shape):
                variables[np.max(tile[0])] =  variables[var]
                rep_shape = True
                break

        if rep_shape == False:
            variables[np.max(tile[0])] =  {"forms":forms(tile_shape), "domain":[ ]}
            #define the initial domine with the unary: the tile has to be completly in the board
            variables[np.max(tile[0])]["domain"] = set_domain(board, variables[np.max(tile[0])]["forms"])

    return variables


#Set the domain for a tile in a specific board
def set_domain(board, forms):
    domain = [ ]
    for i, row in enumerate(board):
        for j, column in enumerate(row):
            for form in forms:
                if not overflows_the_board(board, (i, j), form):
                    value = define_position_value(form,(i,j))
                    if not tile_overlap(board, value):
                        #locate the tile on position
                        domain.append(value)

    return domain

# To produce the different form that a tile can have
def forms(tile):
    forms = [ ]
    forms.append(tile)

    alt_forms = [np.flip(tile), np.rot90(tile) , np.rot90(np.rot90(tile)) , np.rot90(np.rot90(np.rot90(tile)))]

    for i, alt in enumerate(alt_forms):
        rep = False
        for form in forms:
            if np.array_equal(alt,form):
                rep = True
                break

        if not rep:
            forms.append(alt)

    return forms


#Return a positioned tile with a coordinate in each of its boxes and a tupple (-1,-1) for its empty spaces
def define_position_value(tile, pos):
    position_tile = np.zeros(tile.shape, dtype = 'i,i')
    for i,tile_row in enumerate(tile):
        for j, tile_column in enumerate(tile_row):
            if not tile_column == 0:
                position_tile[i][j] = ((pos[0]+i),(pos[1]+j))
            else:
                position_tile[i][j] = (-1,-1)

    return position_tile


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
def tile_overlap(board, value):
    overlaps = False
    for y, tile_row in enumerate(value):
        for x, tile_column in enumerate(tile_row):
            if not (-1 in tile_column):
                if (board[tile_column[0]][tile_column[1]] != 0):
                    overlaps = True
                    break

    return overlaps


#Create a new board with the variable possitionated in the last stat board
def update_state(board, value, variable):
    new_board = np.copy(board)
    for y, tile_row in enumerate(value):
        for x, tile_column in enumerate(tile_row):
            if not -1 in tile_column:
                new_board[tile_column[0]][tile_column[1]] = variable

    return new_board


"""
The solution returned
is of the form [(p1, (row1, col1))...(pn,  (rown, coln))]
where pi is a tile (may be rotated or flipped), and (rowi, coli) is
the coordinate of the upper left corner of pi in the board (lowest row and column index
that the tile covers).
"""
