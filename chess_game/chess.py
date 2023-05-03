import tkinter as tk
from PIL import Image, ImageTk
import winsound

class Chess():
    def __init__(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=640, height = 640)
        self.canvas.pack()
        self.white_pawn = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/w_pawn_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.white_knight = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/w_knight_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.white_bishop = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/w_bishop_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.white_queen = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/w_queen_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.white_king = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/w_king_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.white_rook = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/w_rook_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.white_pawn = ImageTk.PhotoImage(self.white_pawn)
        self.white_knight = ImageTk.PhotoImage(self.white_knight)
        self.white_bishop = ImageTk.PhotoImage(self.white_bishop)
        self.white_queen = ImageTk.PhotoImage(self.white_queen)
        self.white_king = ImageTk.PhotoImage(self.white_king)
        self.white_rook = ImageTk.PhotoImage(self.white_rook)

        self.black_pawn = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/b_pawn_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.black_knight = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/b_knight_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.black_bishop = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/b_bishop_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.black_queen = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/b_queen_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.black_king = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/b_king_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.black_rook = Image.open("C:/Users/harge/WebDevPractice/chess_game/pieces/b_rook_png_shadow_128px.png").resize((80,80), Image.ANTIALIAS)
        self.black_pawn = ImageTk.PhotoImage(self.black_pawn)
        self.black_knight = ImageTk.PhotoImage(self.black_knight)
        self.black_bishop = ImageTk.PhotoImage(self.black_bishop)
        self.black_queen = ImageTk.PhotoImage(self.black_queen)
        self.black_king = ImageTk.PhotoImage(self.black_king)
        self.black_rook = ImageTk.PhotoImage(self.black_rook)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.square_size = 80
        self.current_piece = None
        self.current_piece_id = None
        self.board = {}
        self.whites_move = True
        self.INVALID_MOVE_MSG = "Invalid move!"
        self.original_square = ()
        self.moves = []
        


    def createBoard(self):
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    self.canvas.create_rectangle(i * 80, j * 80, (i+1) * 80, (j+1) * 80, fill="white", tags="light_square")
                else:
                    self.canvas.create_rectangle(i * 80, j * 80, (i+1) * 80, (j+1) * 80, fill="gray", tags="dark_square")
        
        # Starter white/black pawns
        x = 40
        pawn = 0
        for i in range(8):
            self.canvas.create_image(x, 520, anchor="center", image=self.white_pawn, tags=f"w_pawn{pawn}")
            self.canvas.create_image(x, 120, anchor = "center", image=self.black_pawn, tags=f"b_pawn{pawn}")     
            pawn += 1
            x += 80
        
        # Starter white rooks
        self.canvas.create_image(40, 600, anchor="center", image=self.white_rook, tags="w_rook1")
        self.canvas.create_image(600, 600, anchor="center", image=self.white_rook, tags="w_rook2")

        #Starter white knights
        self.canvas.create_image(120,600, anchor="center", image=self.white_knight, tags="w_knight1")
        self.canvas.create_image(520, 600, anchor="center", image=self.white_knight, tags="w_knight2")
        #Starter white bishops
        self.canvas.create_image(200, 600, anchor="center", image=self.white_bishop, tags="w_bishop_dark")
        self.canvas.create_image(440, 600, anchor="center", image=self.white_bishop, tags="w_bishop_light")
        #Starter white king and queen
        self.canvas.create_image(280, 600, anchor="center", image=self.white_queen, tags="w_queen")
        self.canvas.create_image(360, 600, anchor="center", image=self.white_king, tags="w_king")
        
        #Starter black rooks
        self.canvas.create_image(40, 40, anchor = "center", image=self.black_rook, tags="b_rook1")
        self.canvas.create_image(600, 40, anchor = "center", image=self.black_rook, tags="b_rook2")
        #Starter black nights
        self.canvas.create_image(120, 40, anchor = "center", image=self.black_knight, tags="b_knight1")
        self.canvas.create_image(520, 40, anchor = "center", image=self.black_knight, tags="b_knight2")
        #Starter black bishops
        self.canvas.create_image(200, 40, anchor = "center", image=self.black_bishop, tags="b_bishop_light")
        self.canvas.create_image(440, 40, anchor = "center", image=self.black_bishop, tags="b_bishop_dark")
        #Starter back king and queen
        self.canvas.create_image(280, 40, anchor = "center", image=self.black_queen, tags="b_queen")
        self.canvas.create_image(360, 40, anchor = "center", image=self.black_king, tags="b_king")
        
        row = 1
        for col in range(8):
            self.board[(row, col)] = f"b_pawn{col}"
        row = 6
        for col in range(8):
            self.board[(row, col)] = f"w_pawn{col}"

        for i in range(2, 6): # rows 2 to 5
            for j in range(8):
                self.board[(i, j)] = "Empty"            

        self.board[(0,0)] = "b_rook1"
        self.board[(0,1)] = "b_knight1"
        self.board[(0,2)] = "b_bishop_light"
        self.board[(0,3)] = "b_queen"
        self.board[(0,4)] = "b_king"
        self.board[(0,5)] = "b_bishop_dark"
        self.board[(0,6)] = "b_knight2"
        self.board[(0,7)] = "b_rook2"

        self.board[(7,0)] = "w_rook1"
        self.board[(7,1)] = "w_knight1"
        self.board[(7,2)] = "w_bishop_dark"
        self.board[(7,3)] = "w_queen"
        self.board[(7,4)] = "w_king"
        self.board[(7,5)] = "w_bishop_light"
        self.board[(7,6)] = "w_knight2"
        self.board[(7,7)] = "w_rook1"

        # [(from coordintates), (to cooridnates), piece]
        self.moves_made = []
    
    def checkValidMove(self):
        pass

    
    def on_click(self, event):
        x, y = event.x, event.y
        col, row = x // self.square_size, y // self.square_size
        self.original_square = (row, col)
        # Move the image to the clicked square
        print(row, col)
        piece_id = event.widget.find_closest(event.x, event.y)[0]
        piece = self.canvas.itemcget(piece_id, "tags").split(" ")[0]
        self.current_piece_id = piece_id
        self.current_piece = piece
        if self.whites_move and piece[0] == 'b' or self.current_piece == "light_square" or self.current_piece == "dark_square":
            print(self.INVALID_MOVE_MSG)
            return
        if not self.whites_move and piece[0] == 'w' or self.current_piece == "light_square" or self.current_piece == "dark_square":
            print(self.INVALID_MOVE_MSG)
            return


    def on_drag(self, event):
        # Find the square that the mouse is dragging to
        x, y = event.x, event.y
        col, row = x // self.square_size, y // self.square_size
        piece = self.canvas.itemcget(self.current_piece_id, "tags").split(" ")[0]
        if piece in ("light_square", "dark_square", ""):
            return
        if self.whites_move and piece[0] == 'b' or self.current_piece == "light_square" or self.current_piece == "dark_square":
            return
        if not self.whites_move and piece[0] == 'w' or self.current_piece == "light_square" or self.current_piece == "dark_square":
            return
        self.canvas.coords(self.current_piece_id, x, y)

    def capture_piece(self, row, col):
        overlap_ids = self.canvas.find_overlapping(*self.canvas.bbox(self.current_piece_id))

        # Remove the current piece from the list of overlapping ids
        overlap_ids = [id for id in overlap_ids if id != self.current_piece_id]
        overlap_tags = [self.canvas.itemcget(id, "tags").split(" ")[0] for id in overlap_ids]

        # Remove the rest of the overlapping objects
        for tag, id in zip(overlap_tags, overlap_ids):
            if tag == "dark_square" or tag == "light_square":
                continue
            else:
                self.canvas.delete(id)

    # Check if it is a check, if it is a stalemate, or checkmate, or draw
    def check_stale_mate_draw(self):
        pass

    # pawns are 0-7
    def check_valid_pawn_move(self, old_row, old_col, new_row, new_col, pawn_num):
        # Pawn on original square for white
        if self.whites_move:
            # pawn jumping one or two squares first move
            if old_row == 6 and new_col == pawn_num and (old_row-new_row == 1 or old_row-new_row == 2) and self.board[new_row, new_col] == "Empty":
                return True
            # Normal pawn move forward
            if old_row != 6 and new_col == old_col and old_row-new_row == 1 and self.board[(new_row, new_col)] == "Empty":
                return True
            # Pawn capturing a piece
            if old_row != 6 and self.board[(new_row, new_col)][0] == 'b' and self.board[(new_row, new_col)] != "b_king" and \
                (new_col - old_col == 1 or new_col - old_col == -1) and old_row - new_row == 1:
                return True
            if old_row == 6 and self.board[(new_row, new_col)][0] == 'b' and self.board[(new_row, new_col)] != "b_king" and \
                (new_col - old_col == 1 or new_col - old_col == -1) and old_row - new_row == 1:
                return True
        else:
            # pawn jumping one or two squares first move
            if old_row == 1 and new_col == pawn_num and (new_row - old_row == 1 or new_row -old_row == 2) and self.board[new_row, new_col] == "Empty":
                return True
            # Normal pawn move forward
            if old_row != 1 and new_col == old_col and new_row-old_row == 1 and self.board[(new_row, new_col)] == "Empty":
                return True
            # Pawn capturing a piece
            if old_row != 1 and self.board[(new_row, new_col)][0] == 'w' and self.board[(new_row, new_col)] != "w_king" and \
                (old_col - new_col == 1 or old_col - new_col == -1) and new_row - old_row == 1:
                return True
            if old_row == 1 and self.board[(new_row, new_col)][0] == 'w' and self.board[(new_row, new_col)] != "w_king" and \
                (old_col - new_col == 1 or old_col - new_col == -1) and new_row - old_row == 1:
                return True
        return False

    def check_valid_knight_move(self, old_row, old_col, new_row, new_col):
        # Forward left or right
        row_diff = abs(new_row - old_row)
        col_diff = abs(new_col - old_col)
        if self.whites_move:
            if ((row_diff, col_diff) == (2,1) or (row_diff, col_diff) == (1,2)) and self.board[(new_row, new_col)] != "b_king":
                return True
        else:
            if ((row_diff, col_diff) == (2,1) or (row_diff, col_diff) == (1,2)) and self.board[(new_row, new_col)] != "w_king":
                return True
        return False

    def check_valid_bishop_move(self, old_row, old_col, new_row, new_col):
        # check if bishop is moving diagonally
        if abs(old_row - new_row) != abs(old_col - new_col):
            return False
        if self.whites_move and self.board[(new_row, new_col)] == "b_king":
            return False
        if not self.whites_move and self.board[(new_row, new_col)] == "w_king":
            return False
        # determine direction of movement
        row_step = 1 if new_row > old_row else -1
        col_step = 1 if new_col > old_col else -1
        # check each square on the diagonal
        row, col = old_row + row_step, old_col + col_step
        while row != new_row and col != new_col:
            if self.board.get((row, col)) != "Empty":
                # there is a piece blocking the way
                return False
            row += row_step
            col += col_step
        return True
    
    def check_valid_rook_move(self, old_row, old_col, new_row, new_col):
        pass

    def check_valid_queen_move(self, old_row, old_col, new_row, new_col):
        pass

    def check_vald_king_move(self, old_row, old_col, new_row, new_col):
        pass

    def check_valid_move(self, old_row, old_col, new_row, new_col, piece):
        square_moved_to = self.board[(new_row, new_col)]
        if self.whites_move and square_moved_to[0] == 'w':
            return False
        if not self.whites_move and square_moved_to[0] == 'b':
            return False
        if "pawn" in piece:
            return self.check_valid_pawn_move(old_row, old_col, new_row, new_col, int(piece[6]))
        if "knight" in piece:
            return self.check_valid_knight_move(old_row, old_col, new_row, new_col)
        if "bishop" in piece:
            return self.check_valid_bishop_move(old_row, old_col, new_row, new_col)
        return True


    def on_release(self, event):
        # Calculate the row and column of the destination square
        x, y = event.x, event.y
        col, row = x // self.square_size, y // self.square_size
        old_row, old_col = self.original_square
        # Move the current piece to the destination square
        dest_x, dest_y = col*self.square_size+40, row*self.square_size+40
        piece = self.canvas.itemcget(self.current_piece_id, "tags").split(" ")[0]
        if piece in ("light_square", "dark_square", ""):
            return
        # White move validation check
        if self.whites_move:
            if piece[0] != 'w':
                print(self.INVALID_MOVE_MSG)
                return
            if not self.check_valid_move(old_row, old_col, row, col, piece):
                self.canvas.coords(self.current_piece_id, old_col*self.square_size+40, old_row*self.square_size+40)
                print(self.INVALID_MOVE_MSG)
                return
            self.canvas.coords(self.current_piece_id, dest_x, dest_y)
            self.board[(old_row,old_col)] = "Empty"
            self.board[(row, col)] = self.current_piece
            self.moves_made.append([self.original_square, (row, col), self.current_piece])
            self.capture_piece(row, col)
            self.check_stale_mate_draw()
            print(self.moves_made)
            self.whites_move = not self.whites_move   
        # Blacks move validation check
        else:
            if piece[0] != 'b':
                print(self.INVALID_MOVE_MSG)
                return
            if not self.check_valid_move(old_row, old_col, row, col, piece):
                self.canvas.coords(self.current_piece_id, old_col*self.square_size+40, old_row*self.square_size+40)
                print(self.INVALID_MOVE_MSG)
                return
            self.canvas.coords(self.current_piece_id, dest_x, dest_y)
            self.board[(old_row,old_col)] = "Empty"
            self.board[(row, col)] = self.current_piece
            self.moves_made.append([self.original_square, (row, col), self.current_piece])
            self.capture_piece(row, col)
            self.check_stale_mate_draw()
            self.whites_move = True
 
    def play(self):
        self.createBoard()
        self.root.mainloop()

def main():
    chess = Chess()
    chess.play()

if __name__ == "__main__":
    main()



"""
PIECE ID's

Black:
Left Rook: 89
Left night: 91
Light squared bishop: 93
Queen: 95
King: 96
Dark Squared Bishop: 94
Right knight: 92
Right rook: 90
Pawns: 1:66, 2:68, 3:70, 4:72, 5:74, 6:76, 7:78, 8:80

White:
Left Rook: 81
Left knight: 83
Dark squared bishop: 85
Queen: 87
King: 88
Light squared bishop: 86
Right Knight: 84
Right Rook: 82
Pawns: 1:65, 2:67, 3:69, 4:71, 5:73, 6:75, 7:77, 8:79
"""