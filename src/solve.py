def parser(nama_file):
    strip = []
    colors = set()
    with open(nama_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        row = list(line.strip('\n'))
        strip.append(row)
        for ch in row:
            colors.add(ch)

    return strip, colors, len(strip[0]), len(strip)


def place_queen(m,queen_x,queen_y,x,y,occupied_colors,total_queen):
    occupied_colors.append(m[y][x])
    queen_x.append(x)
    queen_y.append(y)
    m[y][x] = '#'

def remove_latest_queen(m,queen_x,queen_y,occupied_colors,total_queen):
    m[queen_y[-1]][queen_x[-1]] = occupied_colors[-1]
    coord_x = queen_x.pop()
    coord_y = queen_y.pop()
    occupied_colors.pop()

    return coord_x, coord_y

def check_diagonal(m,i,j):
    max_x = len(m[0])
    max_y = len(m)
    directions = [(-1, 1), (-1,-1), (1,1), (1,-1)]

    for dy, dx in directions:
        y = i + dy
        x = j + dx

        if 0 <= x < max_x and 0 <= y < max_y:
            if m[y][x] == '#':
                return False

    return True
        
def backtrack(board, row, total_x, total_y, colors, occupied_colors, queens_x, queens_y):
    if row == total_y or len(occupied_colors) == len(colors):
        return True

    for col in range(total_x):
        if (board[row][col] not in occupied_colors and
            col not in queens_x and
            row not in queens_y and
            check_diagonal(board, row, col)):
            
            place_queen(board, queens_x, queens_y, col, row, occupied_colors, None)

            if backtrack(board, row + 1, total_x, total_y, colors, occupied_colors, queens_x, queens_y):
                return True

            remove_latest_queen(board, queens_x, queens_y, occupied_colors, None)

    return False

def solve(nama_file):
    board, colors, total_x, total_y = parser(nama_file)
    occupied_colors = []
    queens_x = []
    queens_y = []

    backtrack(board, 0, total_x, total_y, colors, occupied_colors, queens_x, queens_y)

    for row in board:
        print("".join(row))

    return board


# print(parser('test/test.txt'))
solve('test/test.txt')