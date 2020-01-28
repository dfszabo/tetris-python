import tkinter

# constants
PX_WIDTH = 480
PX_HEIGHT = 640
BLOCK_SIZE = PX_HEIGHT / 20
HEIGHT = int(PX_HEIGHT / BLOCK_SIZE)
WIDTH = int(HEIGHT / 2)

print(HEIGHT)
print(WIDTH)

# print for debug
def printGamespace(gameSpace):
    for x in range(HEIGHT):
        for y in range(WIDTH):
            print(gameSpace[x][y], end=" ")
        print()

# drawing the gamespace
def drawGamespace(C, gameSpace):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            C.create_rectangle(x * BLOCK_SIZE,
                            y * BLOCK_SIZE,
                            (x + 1) * BLOCK_SIZE,
                            (y + 1) * BLOCK_SIZE,
                            fill=gameSpace[y][x])

def main():
    # creating and initializing the game space 2d array
    gameSpace = ["black"] * HEIGHT
    for i in range(HEIGHT):
        gameSpace[i] = ["black"] * WIDTH

    # canvas
    top = tkinter.Tk()
    C = tkinter.Canvas(top, bg="black", height=PX_HEIGHT, width=PX_WIDTH)

    gameSpace[5][2] = "green"
    gameSpace[0][3] = "red"


    drawGamespace(C, gameSpace)
    print("in da main")
    # what is this exactly? guess the last step to draw
    C.pack()

    top.mainloop()


if __name__ == "__main__":
    main()