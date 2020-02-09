from tkinter import *
from random import seed
from random import randint
import time
import copy

# seed random number generator
seed(1)

# constants
PX_WIDTH = 480
PX_HEIGHT = 640
BLOCK_SIZE = PX_HEIGHT / 20
HEIGHT = int(PX_HEIGHT / BLOCK_SIZE)
WIDTH = int(HEIGHT / 2)
TICK_CNT = 1

current_piece = randint(0, 6)
current_x = 3
current_y = 0
current_rotation = 0

scores = 0

ticks = 0

colors = ["black", "blue", "orange", "green", "yellow", "red", "purple", "brown"]


tetrominos = [
    [[0, 1, 0, 0],
     [0, 1, 1, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 0]],

    [[0, 1, 0, 0],
     [0, 1, 1, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 0]],

    [[0, 0, 1, 0],
     [0, 1, 1, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 0]],

    [[0, 1, 0, 0],
     [0, 1, 0, 0],
     [0, 1, 0, 0],
     [0, 1, 0, 0]],

    [[0, 1, 1, 0],
     [0, 1, 1, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],

    [[0, 1, 0, 0],
     [0, 1, 0, 0],
     [0, 1, 1, 0],
     [0, 0, 0, 0]],

    [[0, 0, 1, 0],
     [0, 0, 1, 0],
     [0, 1, 1, 0],
     [0, 0, 0, 0]]
]

def rotatedIndex(rotation, index):
    if rotation == 0:
        return index
    if rotation == 1:
        # 0  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15
        # 12 8  4  0  13 9  5  1  14 10 6   2   15  11  7   3
        return int(12 - ((index % 4) * 4) + int(index / 4))
    if rotation == 2:
        return 15 - index
    if rotation == 3:
        # 0  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15
        # 3  7  11 15 2  6  10 14 1  5  9   13  0   4   8   12
        return int(15 - int(index / 4) - ((3 - (index % 4)) * 4))

def doesItFit(piece, rota, in_x, in_y, gameSpace):
    piece_x = in_y
    piece_y = in_x
    idx = 0

    for x in range(4):
        for y in range(4):
            idx = rotatedIndex(rota, x * 4 + y)
            gs_x = piece_x + x
            gs_y = piece_y + y
            if tetrominos[piece][int(idx / 4)][idx % 4] != 0:
                if gs_x >= 0 and gs_x < HEIGHT and gs_y >= 0 and gs_y < WIDTH:
                    if gameSpace[gs_x][gs_y] != 0:
                        return 0
                else:
                    return 0
    return 1

# print for debug
def printGamespace(gameSpace):
    for x in range(HEIGHT):
        for y in range(WIDTH):
            print(gameSpace[x][y], end=" ")
        print()

# drawing the gamespace
def drawGamespace(C, squares_list, gameSpace):
    ### print("in drawGamespace")
    #gameSpace[randint(0, HEIGHT-1)][randint(0, WIDTH-1)] = 1
    for y in range(HEIGHT):
        for x in range(WIDTH):
            C.itemconfig(squares_list[y * WIDTH + x], fill=colors[gameSpace[y][x]])

    #draw current piece
    for x in range(4):
        for y in range(4):
            idx = rotatedIndex(current_rotation, x * 4 + y)
            if tetrominos[current_piece][int(idx / 4)][idx % 4] != 0:
                C.itemconfig(squares_list[(current_y + x) * WIDTH + (current_x + y)], fill="white")

def spawnNewPiece(gameSpace):
    ### print("in spawnNewPiece")
    global current_x
    current_x = 3
    global current_y
    current_y = 0
    global current_rotation
    current_rotation = 0
    global current_piece
    current_piece = randint(0, 6)

    return doesItFit(current_piece, current_rotation, current_x, current_y, gameSpace)

# calculating the "goodness" or fitness of the gameSpace
def calculateFitness(gameSpace):
    lineFillednessFactor = 0
    lineSolved = 0
    holes = 1
    maxHeight = 1

    # calculating highest solid block
    for y in range(WIDTH):
        for x in range(HEIGHT - 1, 0, -1):
            if gameSpace[x][y] != 0 and maxHeight < x:
                maxHeight = x + 1

    # calculating how filled the lines are from the left to right also
    # if there is any solved line(s) (line fully filled with blocks)
    for x in range(HEIGHT):
        currentRowFilledness = 0
        for y in range(WIDTH):
            if gameSpace[x][y] != 0:
                currentRowFilledness += 1
        if currentRowFilledness == WIDTH:
            lineSolved += 1
        lineFillednessFactor += currentRowFilledness * (x + 5)

    # calculating holes in the gamespace
    for y in range(WIDTH):
        hasColumnAnySolidBlock = False
        for x in range(HEIGHT):
            if hasColumnAnySolidBlock == False and gameSpace[x][y] != 0:
                hasColumnAnySolidBlock = True
            if hasColumnAnySolidBlock and gameSpace[x][y] == 0:
                holes += 10

    #return int((100000 + (100 * lineFillednessFactor - (maxHeight ** 3 / 1000))) / (holes ** 3)) << lineSolved ** 3
    return int((1000 * lineFillednessFactor) / (holes * (maxHeight ** 2))) << lineSolved

def bot(gameSpace):
    global current_rotation
    global current_x
    local_y = current_y
    target_x = current_x
    target_rot = current_rotation
    bestFitness = -1

    for rot in range(4):
        for x in range(WIDTH + 3):
            if doesItFit(current_piece, rot, x - 3 , local_y, gameSpace) == 1:
                # moving down until it stucks
                while doesItFit(current_piece, rot, x - 3 , local_y + 1, gameSpace) == 1:
                    local_y += 1
                # fitting the piece into the BOTs gameSpace
                for px in range(4):
                    for py in range(4):
                        idx = rotatedIndex(rot, px * 4 + py)
                        if tetrominos[current_piece][int(idx / 4)][idx % 4] == 1:
                            gameSpace[local_y + px][x - 3 + py] = current_piece + 1
                # if the resulting gamespace fitness is better then the current best one
                # then change the target coordinates for the best solution to the current one
                if calculateFitness(gameSpace) > bestFitness:
                    bestFitness = calculateFitness(gameSpace)
                    target_x = x - 3
                    target_rot = rot
                # removing the piece for the next iteration
                for px in range(4):
                    for py in range(4):
                        idx = rotatedIndex(rot, px * 4 + py)
                        if tetrominos[current_piece][int(idx / 4)][idx % 4] == 1:
                            gameSpace[local_y + px][x - 3 + py] = 0
    # depending on our current position move the current piece towards the target
    # first do the rotation
    ### print('target_rot={:d}, target_x={:d}'.format(target_rot, target_x))
    if target_rot != current_rotation:
        if target_rot > current_rotation:
            current_rotation += 1
        else:
            current_rotation -= 1
    # if rotation is correct than move it horrizontally
    elif target_x != current_x:
        if target_x > current_x:
            current_x += 1
        else:
            current_x -= 1

def checkAndRemoveFilledLines(gameSpace):
    global scores
    first_found_line_y_coord = 0
    found_lines = 0

    for x in range(HEIGHT):
        num_of_blocks_in_row = 0
        for y in range(WIDTH):
            if gameSpace[x][y] != 0:
                num_of_blocks_in_row += 1
        if num_of_blocks_in_row == WIDTH:
            found_lines += 1
            if first_found_line_y_coord == 0:
                first_found_line_y_coord = x
    # if there was filled lines then add to score and erase the lines
    if found_lines != 0:
        scores += 10
        for x in range(first_found_line_y_coord + found_lines - 1, found_lines, -1):
            ### print("x is {:d}".format(x))
            gameSpace[x] = copy.deepcopy(gameSpace[x - found_lines])

def update(C, squares_list, gameSpace):
    global ticks
    ticks = (ticks + 1) % TICK_CNT
    global current_y
    global scores

    bot(gameSpace)

    if ticks == 0:
        # if it able to move down than move it down
        if doesItFit(current_piece, current_rotation, current_x, current_y + 1, gameSpace) == 1:
            current_y += 1
        else:
            scores += 1
            print("scores: {:d}".format(scores))
            for x in range(4):
                for y in range(4):
                    idx = rotatedIndex(current_rotation, x * 4 + y)
                    if tetrominos[current_piece][int(idx / 4)][idx % 4] != 0:
                        if current_y + x >= HEIGHT or current_x + y >= WIDTH:
                            while 1:
                                print("current_rotation={:d}, idx={:d}".format(current_rotation, idx))
                                print("y={:d}, x={:d}".format(current_y + x, current_x + y))
                                time.sleep(1)
                                print("dafaq")
                        gameSpace[current_y + x][current_x + y] = current_piece + 1
            checkAndRemoveFilledLines(gameSpace)
            if not spawnNewPiece(gameSpace):
                return 0
    return 1
    #C.after(1, update, C, squares_list, gameSpace)

def main():
    # canvasd
    root = Tk()
    C = Canvas(root, bg="black", height=PX_HEIGHT, width=PX_WIDTH)
    C.pack()

    # for storing the rectangles
    squares_list = []

    # init
    # creating and initializing the game space 2d array
    gameSpace = [0] * HEIGHT
    for i in range(HEIGHT):
        gameSpace[i] = [0] * WIDTH

    for y in range(HEIGHT):
        for x in range(WIDTH):
            squares_list.append(C.create_rectangle(x * BLOCK_SIZE,
                                y * BLOCK_SIZE,
                                (x + 1) * BLOCK_SIZE,
                                (y + 1) * BLOCK_SIZE,
                                fill=colors[gameSpace[y][x]]))

    while update(C, squares_list, gameSpace):
        drawGamespace(C, squares_list, gameSpace)
        root.update_idletasks()
        root.update()

if __name__ == "__main__":
    main()