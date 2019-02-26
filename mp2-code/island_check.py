import numpy as np

board =np.zeros((6,10))
board[1,1] = board[1,0] = board[0,1] = board[1,2] = board[2,1] = 0

number =5
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
            for k in range(previous_indicator):
                indicator = 0
                element = element_list[-previous_indicator+k]
                element_neighbor = neighbors(element[0],element[1])
                for i in range(len(un_assigned)):
                    if un_assigned[i] in element_neighbor:
                        new_island.append(un_assigned[i])
                        indicator += 1
            element_list = new_island[-indicator:]
            for i in element_list:
                if i in un_assigned:
                    un_assigned.remove(i)
        island.append(new_island)
    island_size = []
    for i in island:
        island_size.append(len(i))
    output = []
    for i in range(len(island_size)):
        if island_size[i] < number:
            output.append(island[i])
    if len(output) != 0:
        return output
    else:
        return False
