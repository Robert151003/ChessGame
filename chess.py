import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class ChessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game")
        self.geometry("600x650")
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.piece_images = self.load_piece_images()
        self.canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.create_board()
        self.setup_pieces()
        self.selected_piece = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.move_counter = 0  # Initialize move counter
        self.kings_position = {'white': (7, 4), 'black': (0, 4)}  # Track kings' positions
        self.turn_label = tk.Label(self, text="White's Turn", font=('Helvetica', 14))
        self.turn_label.pack(side="bottom")


    def load_piece_images(self):
        pieces = {}
        for color in ['white', 'black']:
            for piece in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
                img = Image.open(f"Pieces/{color}{piece}.png")
                img = img.resize((75, 75), Image.LANCZOS)
                pieces[f'{color}{piece}'] = ImageTk.PhotoImage(img)
        return pieces

    def create_board(self):
        self.canvas.bind("<Button-1>", self.on_square_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)
        self.redraw_board()

    def redraw_board(self):
        self.canvas.delete("all")  # Clear the canvas
        square_size = 600 // 8
        for i in range(8):
            for j in range(8):
                x1, y1 = j * square_size, i * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                color = "white" if (i+j) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square")
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece:
                    self.place_piece(i, j, piece)

    def setup_pieces(self):
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for i in range(8):
            self.board[0][i] = f'black{piece_order[i]}'
            self.board[1][i] = 'blackpawn'
            self.board[6][i] = 'whitepawn'
            self.board[7][i] = f'white{piece_order[i]}'
        self.redraw_board()

    def place_piece(self, row, col, piece):
        x = col * (600 // 8) + (600 // 8) // 2
        y = row * (600 // 8) + (600 // 8) // 2
        self.canvas.create_image(x, y, anchor='center', image=self.piece_images[piece], tags="piece")


    def switch_turn(self):
        if self.move_counter % 2 == 0:
            self.turn_label.config(text="White's Turn")
        else:
            self.turn_label.config(text="Black's Turn")
    
    def update_kings_position(self):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece.endswith('king'):
                    self.kings_position[piece[:5]] = (row, col)
    def is_king_in_check(self, king_color):
        enemy_color = 'black' if king_color == 'white' else 'white'
        king_pos = self.kings_position[king_color]

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece.startswith(enemy_color):
                    if self.is_legal_move(piece, row, col, king_pos[0], king_pos[1], checking_check=True):
                        return True
        return False

    
    def on_square_click(self, event):
        col = event.x // (600 // 8)
        row = event.y // (600 // 8)
        if 0 <= row < 8 and 0 <= col < 8:
            piece = self.board[row][col]
            if (self.move_counter % 2 == 0 and piece and piece.startswith('white')) or \
               (self.move_counter % 2 != 0 and piece and piece.startswith('black')):
                self.selected_piece = self.canvas.find_closest(event.x, event.y)[0]
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self.drag_data["start_col"] = col
                self.drag_data["start_row"] = row
                self.drag_data["x_offset"] = event.x - (col * (600 // 8) + (600 // 8) // 2)
                self.drag_data["y_offset"] = event.y - (row * (600 // 8) + (600 // 8) // 2)

    def on_drag(self, event):
        if self.selected_piece:
            # Adjust the position based on the offset
            x = event.x - self.drag_data["x_offset"]
            y = event.y - self.drag_data["y_offset"]
            self.canvas.coords(self.selected_piece, x, y)

    def on_drop(self, event):
        if self.selected_piece:
            col = min(max(event.x // (600 // 8), 0), 7)
            row = min(max(event.y // (600 // 8), 0), 7)
            x = col * (600 // 8) + (600 // 8) // 2
            y = row * (600 // 8) + (600 // 8) // 2

            if col == self.drag_data["start_col"] and row == self.drag_data["start_row"]:
                self.canvas.coords(self.selected_piece, x, y)
                self.board[row][col] = self.board[self.drag_data["start_row"]][self.drag_data["start_col"]]  # Update the board with the piece identifier
            else:
                piece_identifier = self.board[self.drag_data["start_row"]][self.drag_data["start_col"]]
                if self.is_legal_move(piece_identifier, self.drag_data["start_row"], self.drag_data["start_col"], row, col):  # Check if the move is legal
                    # Snap the piece to the nearest square
                    self.canvas.coords(self.selected_piece, x, y)
                    self.board[self.drag_data["start_row"]][self.drag_data["start_col"]] = ''  # Clear the previous position
                    if self.board[row][col]:  # If the destination square is not empty
                        captured_piece = self.board[row][col]
                        self.canvas.delete(captured_piece)  # Remove the captured piece from the canvas
                    self.board[row][col] = piece_identifier  # Update the board with the piece identifier
                    self.move_counter += 1  # Increment move counter after each move
                else:
                    # Move is not legal, ignore the drop action
                    self.canvas.coords(self.selected_piece, self.drag_data["x"], self.drag_data["y"])

            self.selected_piece = None
            self.update_kings_position()
            self.switch_turn()
            self.redraw_board()

             # After move logic
            if self.is_king_in_check('white'):
                messagebox.showinfo("Check", "White king is in check!")
            elif self.is_king_in_check('black'):
                messagebox.showinfo("Check", "Black king is in check!")

    def is_legal_move(self, piece_identifier, start_row, start_col, dest_row, dest_col, checking_check=False):
        piece_type = piece_identifier[5:]  # Extracting the type of piece from the identifier
        color = piece_identifier[:5]  # Extracting the color of the piece from the identifier
        
        if piece_type == 'pawn':
            # Pawn moves
            if color == 'white':
                if start_col == dest_col and start_row - dest_row == 1:
                    return True  # Normal move forward
                elif start_row == 6 and start_col == dest_col and start_row - dest_row == 2:
                    return True  # Initial double move forward
                elif abs(start_col - dest_col) == 1 and start_row - dest_row == 1:
                    # Capture move diagonally
                    if self.board[dest_row][dest_col].startswith('black'):
                        return True
            elif color == 'black':
                if start_col == dest_col and dest_row - start_row == 1:
                    return True  # Normal move forward
                elif start_row == 1 and start_col == dest_col and dest_row - start_row == 2:
                    return True  # Initial double move forward
                elif abs(start_col - dest_col) == 1 and dest_row - start_row == 1:
                    # Capture move diagonally
                    if self.board[dest_row][dest_col].startswith('white'):
                        return True

                    
        elif piece_type == 'rook':
            # Rook moves (straight lines)
            if start_row == dest_row:
                # Horizontal move
                if start_col < dest_col:
                    for col in range(start_col + 1, dest_col):
                        if self.board[start_row][col]:
                            return False  # Path obstructed
                    if self.board[dest_row][dest_col] == '' or \
                       (color == 'white' and self.board[dest_row][dest_col].startswith('black')) or \
                       (color == 'black' and self.board[dest_row][dest_col].startswith('white')):
                        return True
                elif start_col > dest_col:
                    for col in range(dest_col + 1, start_col):
                        if self.board[start_row][col]:
                            return False  # Path obstructed
                    if self.board[dest_row][dest_col] == '' or \
                       (color == 'white' and self.board[dest_row][dest_col].startswith('black')) or \
                       (color == 'black' and self.board[dest_row][dest_col].startswith('white')):
                        return True
            elif start_col == dest_col:
                # Vertical move
                if start_row < dest_row:
                    for row in range(start_row + 1, dest_row):
                        if self.board[row][start_col]:
                            return False  # Path obstructed
                    if self.board[dest_row][dest_col] == '' or \
                       (color == 'white' and self.board[dest_row][dest_col].startswith('black')) or \
                       (color == 'black' and self.board[dest_row][dest_col].startswith('white')):
                        return True
                elif start_row > dest_row:
                    for row in range(dest_row + 1, start_row):
                        if self.board[row][start_col]:
                            return False  # Path obstructed
                    if self.board[dest_row][dest_col] == '' or \
                       (color == 'white' and self.board[dest_row][dest_col].startswith('black')) or \
                       (color == 'black' and self.board[dest_row][dest_col].startswith('white')):
                        return True


        elif piece_type == 'knight':
            # Knight moves (L-shape)
            if (abs(dest_row - start_row) == 2 and abs(dest_col - start_col) == 1) or \
               (abs(dest_row - start_row) == 1 and abs(dest_col - start_col) == 2):
                if self.board[dest_row][dest_col] == '' or \
                   (color == 'white' and self.board[dest_row][dest_col].startswith('black')) or \
                   (color == 'black' and self.board[dest_row][dest_col].startswith('white')):
                    return True


        elif piece_type == 'bishop':
            # Bishop moves (diagonals)
            if abs(dest_row - start_row) == abs(dest_col - start_col):
                # Diagonal move
                if dest_row > start_row:
                    row_direction = 1
                else:
                    row_direction = -1
                if dest_col > start_col:
                    col_direction = 1
                else:
                    col_direction = -1

                row, col = start_row + row_direction, start_col + col_direction
                while row != dest_row and col != dest_col:
                    if self.board[row][col]:
                        return False  # Path obstructed
                    row += row_direction
                    col += col_direction
                if self.board[dest_row][dest_col] == '' or \
                   (color == 'white' and self.board[dest_row][dest_col].startswith('black')) or \
                   (color == 'black' and self.board[dest_row][dest_col].startswith('white')):
                    return True


            
        elif piece_type == 'queen':
            # Check if the move is either perfectly vertical, horizontal, or diagonal
            if start_row == dest_row or start_col == dest_col or abs(dest_row - start_row) == abs(dest_col - start_col):
                # The move is in a straight line or diagonal, now check if the path is clear

                step_row = 0 if start_row == dest_row else (dest_row - start_row) // abs(dest_row - start_row)
                step_col = 0 if start_col == dest_col else (dest_col - start_col) // abs(dest_col - start_col)

                current_row = start_row + step_row
                current_col = start_col + step_col

                # Check each square along the way for obstacles
                while current_row != dest_row or current_col != dest_col:
                    if self.board[current_row][current_col] != '':
                        # Path is obstructed
                        if (color == 'white' and self.board[current_row][current_col][0] == 'b') or \
                           (color == 'black' and self.board[current_row][current_col][0] == 'w'):
                            return True  # Can capture opponent's piece
                        else:
                            return False  # Path is blocked by same color piece
                    current_row += step_row
                    current_col += step_col

                # Check the destination square
                if self.board[dest_row][dest_col] == '' or \
                   (color == 'white' and self.board[dest_row][dest_col][0] == 'b') or \
                   (color == 'black' and self.board[dest_row][dest_col][0] == 'w'):
                    return True  # The path is clear
                else:
                    return False  # Path is blocked by a friendly piece
            else:
                return False  # Not a valid queen move


        elif piece_type == 'king':
            # King moves
            if abs(dest_row - start_row) <= 1 and abs(dest_col - start_col) <= 1:
                if self.board[dest_row][dest_col] == '' or \
                   (color == 'white' and self.board[dest_row][dest_col].startswith('black')) or \
                   (color == 'black' and self.board[dest_row][dest_col].startswith('white')):
                    return True
            # Castling rules can be added here if needed
            return False  # Invalid move for the given piece type








if __name__ == "__main__":
    app = ChessGame()
    app.mainloop()
