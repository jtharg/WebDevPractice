board = []
for row in range(8):
    for col in range(8):
        board.append((row, col))


# bishop
row, col = 7, 4

for i in range(1, min(row, 7 - col) + 1):
    # Check the square at (row - i, col + i)
    print(row - i, col + i)

# Iterate through the diagonal that starts at (row, col) and goes up and to the left
for i in range(1, min(row, col) + 1):
    # Check the square at (row - i, col - i)
    print(row - i, col - i)

# Iterate through the diagonal that starts at (row, col) and goes down and to the right
for i in range(1, min(7 - row, 7 - col) + 1):
    # Check the square at (row + i, col + i)
    print(row + i, col + i)

# Iterate through the diagonal that starts at (row, col) and goes down and to the left
for i in range(1, min(7 - row, col) + 1):
    # Check the square at (row + i, col - i)
    print(row + i, col - i)