import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game - Main Menu")
        self.geometry("400x300")
        
        title_label = tk.Label(self, text="Chess Game", font=('Helvetica', 24, 'bold'))
        title_label.pack(pady=30)
        
        start_button = tk.Button(self, text="Start Game", command=self.start_game)
        start_button.pack()

    def start_game(self):
        self.destroy()
        game = ChessGame()
        game.mainloop()



class ChessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game")
        self.geometry("600x650")
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.piece_images = self.load_piece_images()
        self.canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.selected_piece = None  # Initialize selected_piece attribute
        self.create_board()  # Move the create_board() call after initializing selected_piece
        self.setup_pieces()
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
        
        # Highlight squares if a piece is selected
        if self.selected_piece:
            start_row = self.drag_data["start_row"]
            start_col = self.drag_data["start_col"]
            piece_identifier = self.board[start_row][start_col]
            legal_moves = self.calculate_legal_moves(piece_identifier, start_row, start_col)
            for move in legal_moves:
                row, col = move
                x1, y1 = col * square_size, row * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=3, tags="highlight")
        
        # Place pieces on the board
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

    def calculate_legal_moves(self, piece_identifier, start_row, start_col):
        legal_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_legal_move(piece_identifier, start_row, start_col, row, col):
                    legal_moves.append((row, col))
        return legal_moves
    
    def highlight_legal_moves(self, piece_identifier, start_row, start_col):
        self.redraw_board()  # Clear previous highlights
        legal_moves = self.calculate_legal_moves(piece_identifier, start_row, start_col)
        for move in legal_moves:
            row, col = move
            x1, y1 = col * (600 // 8), row * (600 // 8)
            x2, y2 = x1 + (600 // 8), y1 + (600 // 8)
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=3, tags="highlight")

    def is_king_in_check_after_move(self, start_row, start_col, dest_row, dest_col):
        piece = self.board[start_row][start_col]
        moved_piece = self.board[dest_row][dest_col]
        self.board[dest_row][dest_col] = piece
        self.board[start_row][start_col] = ''
        king_color = 'white' if piece.startswith('white') else 'black'
        king_pos = self.kings_position[king_color]
        in_check = self.is_king_in_check(king_color)
        # Restore the board state
        self.board[start_row][start_col] = piece
        self.board[dest_row][dest_col] = moved_piece
        return in_check

    def find_blocking_pieces(self, king_color):
        blocking_pieces = []
        king_pos = self.kings_position[king_color]
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.startswith(king_color):
                    legal_moves = self.calculate_legal_moves(piece, row, col)
                    for move in legal_moves:
                        dest_row, dest_col = move
                        if (dest_row, dest_col) == king_pos:
                            blocking_pieces.append(piece)
        return blocking_pieces

    def find_threatening_piece(self, king_color):
        king_pos = self.kings_position[king_color]
        enemy_color = 'white' if king_color == 'black' else 'black'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.startswith(enemy_color):
                    if self.is_legal_move(piece, row, col, king_pos[0], king_pos[1]):
                        return (row, col)
        return None



        
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
                # Check if the selected piece can block or move the king out of check
                king_color = 'white' if self.move_counter % 2 == 0 else 'black'
                if self.is_king_in_check(king_color):
                    if piece.endswith('king'):
                        # If the selected piece is the king, it must move to a safe square
                        legal_moves = self.calculate_legal_moves(piece, row, col)
                        safe_moves = []
                        for move in legal_moves:
                            dest_row, dest_col = move
                            if not self.is_king_in_check_after_move(row, col, dest_row, dest_col):
                                safe_moves.append(move)
                        if safe_moves:
                            self.highlight_legal_moves(piece, row, col)
                        else:
                            # No safe moves for the king, so ignore the click
                            self.selected_piece = None
                    else:
                        # If the selected piece is not the king, it must block the check or capture the threatening piece
                        blocking_pieces = self.find_blocking_pieces(king_color)
                        if blocking_pieces:
                            # Only allow selecting pieces that can block the check
                            if piece in blocking_pieces:
                                self.highlight_legal_moves(piece, row, col)
                            else:
                                # Ignore the click if the selected piece cannot block the check
                                self.selected_piece = None
                        else:
                            # No blocking pieces available, so only allow capturing the threatening piece
                            threatening_piece_pos = self.find_threatening_piece(king_color)
                            if threatening_piece_pos:
                                threatening_piece_row, threatening_piece_col = threatening_piece_pos
                                threatening_piece = self.board[threatening_piece_row][threatening_piece_col]
                                if piece.endswith('pawn') or self.is_legal_move(piece, row, col, threatening_piece_row, threatening_piece_col):
                                    self.highlight_legal_moves(piece, row, col)
                                else:
                                    # Ignore the click if the selected piece cannot capture the threatening piece
                                    self.selected_piece = None
                            else:
                                # No threatening piece found (shouldn't happen), so ignore the click
                                self.selected_piece = None
                else:
                    # King is not in check, highlight legal moves as usual
                    self.highlight_legal_moves(piece, row, col)



        

    def is_castling_move(self, piece_type, start_row, start_col, dest_row, dest_col):
        print(self, piece_type, start_row, start_col, dest_row, dest_col)
        if piece_type == 'king':
            # Check if the king is at its initial position and moving two squares left or right
            if start_row == dest_row and abs(dest_col - start_col) == 2 and \
                    ((start_row == 0 and start_col == 4 and dest_col == 2) or  # Queen side castling for black
                     (start_row == 7 and start_col == 4 and dest_col == 2) or  # Queen side castling for white
                     (start_row == 0 and start_col == 4 and dest_col == 6) or  # King side castling for black
                     (start_row == 7 and start_col == 4 and dest_col == 6)):   # King side castling for white

                # Check if the squares the king moves through are not under attack
                if not self.is_king_in_check('white' if self.move_counter % 2 == 0 else 'black'):
                    enemy_color = 'black' if self.move_counter % 2 == 0 else 'white'
                    if not self.is_square_attacked(start_row, start_col, enemy_color) and \
                       not self.is_square_attacked(start_row, (start_col + dest_col) // 2, enemy_color) and \
                       not self.is_square_attacked(start_row, dest_col, enemy_color):
                        print("Castling move detected")
                        return True
        return False


    def is_square_attacked(self, row, col, attacker_color):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.startswith(attacker_color):
                    if self.is_legal_move(piece, i, j, row, col, checking_check=True):
                        return True
        return False

    def perform_castling(self, king_piece, start_row, start_col, dest_row, dest_col):
        try:
            # Move the king
            self.board[start_row][start_col] = ''  # Clear the king's original position
            self.board[dest_row][dest_col] = king_piece  # Move the king to the destination position
            king_x = dest_col * (600 // 8) + (600 // 8) // 2
            king_y = dest_row * (600 // 8) + (600 // 8) // 2
            self.canvas.coords(king_piece, king_x, king_y)  # Update king's position on the canvas

            # Move the corresponding rook
            if dest_col == 6:  # Kingside castling
                rook_piece = self.board[dest_row][7]  # Get the rook piece
                self.board[dest_row][7] = ''  # Clear the rook's original position
                self.board[dest_row][5] = rook_piece  # Move the rook to the destination position
                rook_x = 5 * (600 // 8) + (600 // 8) // 2
                rook_y = dest_row * (600 // 8) + (600 // 8) // 2
                rook_piece_id = self.canvas.find_withtag(rook_piece)[0]
                self.canvas.coords(rook_piece_id, rook_x, rook_y)  # Update rook's position on the canvas
            elif dest_col == 2:  # Queenside castling
                rook_piece = self.board[dest_row][0]  # Get the rook piece
                self.board[dest_row][0] = ''  # Clear the rook's original position
                self.board[dest_row][3] = rook_piece  # Move the rook to the destination position
                rook_x = 3 * (600 // 8) + (600 // 8) // 2
                rook_y = dest_row * (600 // 8) + (600 // 8) // 2
                rook_piece_id = self.canvas.find_withtag(rook_piece)[0]
                self.canvas.coords(rook_piece_id, rook_x, rook_y)  # Update rook's position on the canvas

        except IndexError:
            print("Error: King or rook piece ID not found on canvas.")
            # Handle the error here, such as displaying an error message or logging it.


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

            # If the piece is dropped back to its original position, just update the coordinates
            if col == self.drag_data["start_col"] and row == self.drag_data["start_row"]:
                self.canvas.coords(self.selected_piece, x, y)
                self.board[row][col] = self.board[self.drag_data["start_row"]][self.drag_data["start_col"]]  # Update the board with the piece identifier
            else:
                piece_identifier = self.board[self.drag_data["start_row"]][self.drag_data["start_col"]]
                # Check if the move is legal
                if self.is_legal_move(piece_identifier, self.drag_data["start_row"], self.drag_data["start_col"], row, col):
                    # Snap the piece to the nearest square
                    self.canvas.coords(self.selected_piece, x, y)
                    self.board[self.drag_data["start_row"]][self.drag_data["start_col"]] = ''  # Clear the previous position

                    # If the destination square is not empty, remove the captured piece from the canvas
                    if self.board[row][col]:
                        captured_piece = self.board[row][col]
                        self.canvas.delete(captured_piece)
                    self.board[row][col] = piece_identifier  # Update the board with the piece identifier
                    self.move_counter += 1  # Increment move counter after each move

                # Check for castling move
                elif piece_identifier.endswith('king') and abs(self.drag_data["start_col"] - col) == 2:
                    print("Castling move detected!")
                    print("King start position:", self.drag_data["start_row"], self.drag_data["start_col"])
                    print("King end position:", row, col)
                    print("Rook start position:", row, 7 if col == 2 else 0)
                    print("Rook end position:", row, 5 if col == 2 else 3)
                    self.perform_castling(self.board[self.drag_data["start_row"]][self.drag_data["start_col"]], self.drag_data["start_row"], self.drag_data["start_col"], row, col)

                # Check for en passant
                elif piece_identifier.startswith('whitepawn') or piece_identifier.startswith('blackpawn'):
                    if abs(row - self.drag_data["start_row"]) == 2:
                        self.en_passant_square = (row, col)
                    elif col != self.drag_data["start_col"] and self.board[row][col] == '':
                        en_passant_row = row - 1 if piece_identifier.startswith('whitepawn') else row + 1
                        en_passant_col = col
                        if (en_passant_row, en_passant_col) == self.en_passant_square:
                            captured_pawn_row = self.drag_data["start_row"]
                            captured_pawn_col = col
                            captured_pawn = self.board[captured_pawn_row][captured_pawn_col]
                            self.board[captured_pawn_row][captured_pawn_col] = ''  # Remove the captured pawn from the board
                            self.canvas.delete(captured_pawn)  # Remove the captured pawn from the canvas
                            
                else:
                    # Move is not legal, ignore the drop action and revert the piece to its original position
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
                # If moving horizontally or vertically
                if start_row == dest_row or start_col == dest_col:
                    step_row = 0 if start_row == dest_row else (1 if dest_row > start_row else -1)
                    step_col = 0 if start_col == dest_col else (1 if dest_col > start_col else -1)

                    current_row = start_row + step_row
                    current_col = start_col + step_col

                    # Check each square along the way for obstacles
                    while current_row != dest_row or current_col != dest_col:
                        if self.board[current_row][current_col] != '':
                            return False  # Path is obstructed
                        current_row += step_row
                        current_col += step_col

                # If moving diagonally
                else:
                    row_direction = 1 if dest_row > start_row else -1
                    col_direction = 1 if dest_col > start_col else -1

                    current_row = start_row + row_direction
                    current_col = start_col + col_direction

                    # Check each square along the way for obstacles
                    while current_row != dest_row or current_col != dest_col:
                        if self.board[current_row][current_col] != '':
                            return False  # Path is obstructed
                        current_row += row_direction
                        current_col += col_direction

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
            return False  # Invalid move for the given piece type





if __name__ == "__main__":
    app = ChessGame() # change to MainMenu() when done coding
    app.mainloop()
