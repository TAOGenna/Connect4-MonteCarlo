import tkinter as tk
import numpy as np
from monte_carlo_connect4 import MCTS, Node, Board
import copy

class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.board = Board()
        self.turn = 1  # +1 for player, -1 for AI
        self.buttons = []
        self.canvas = None
        self.game_over = False
        
        self.create_widgets()
        self.display_board()

    def create_widgets(self):
        # Create a canvas for the game board with rounded corners
        self.canvas = tk.Canvas(self.root, width=700, height=600, bg='#2C3E50', bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=7)
        
        # Frame for the column buttons, positioned directly above the canvas (no extra space)
        button_frame = tk.Frame(self.root, bg='#2C3E50', bd=0)
        button_frame.grid(row=1, column=0, columnspan=7, sticky="ew")

        # Create column buttons with smooth, rounded corners and pastel colors
        for col in range(7):
            button = tk.Button(button_frame, text=str(col+1), width=4, height=2, 
                               command=lambda col=col: self.player_move(col), 
                               font=('Helvetica', 14, 'bold'), fg='#fff', bg='#3498DB', relief='flat', 
                               highlightthickness=0, activebackground='#1ABC9C', bd=0, 
                               pady=10, padx=10)
            button.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")
            self.buttons.append(button)
            
            # Bind hover effects for buttons
            button.bind("<Enter>", lambda e, btn=button: btn.config(bg="#1ABC9C"))
            button.bind("<Leave>", lambda e, btn=button: btn.config(bg="#3498DB"))

        # Make column buttons stretch as well
        for col in range(7):
            button_frame.grid_columnconfigure(col, weight=1)

        # Create a frame for the Try Again and Exit buttons
        control_frame = tk.Frame(self.root, bg='#34495E')
        control_frame.grid(row=2, column=0, columnspan=7, pady=10)

        # Create the "Try Again" button
        try_again_button = tk.Button(control_frame, text="Try Again", width=12, height=2, 
                                      command=self.reset_game, font=('Helvetica', 14, 'bold'), 
                                      fg='#fff', bg='#3498DB', relief='flat', highlightthickness=0, 
                                      activebackground='#1ABC9C', bd=0, pady=10, padx=10)
        try_again_button.grid(row=0, column=0, padx=10)

        # Create the "Exit" button
        exit_button = tk.Button(control_frame, text="Exit", width=12, height=2, 
                                command=self.exit_game, font=('Helvetica', 14, 'bold'), 
                                fg='#fff', bg='#E74C3C', relief='flat', highlightthickness=0, 
                                activebackground='#C0392B', bd=0, pady=10, padx=10)
        exit_button.grid(row=0, column=1, padx=10)

    def display_board(self):
        self.canvas.delete("all")  # Clear canvas

        display = {0: ".", 1: "X", -1: "O"}
        for row in range(6):
            for col in range(7):
                x1 = col * 100 + 10
                y1 = (5 - row) * 100 + 10
                x2 = col * 100 + 90
                y2 = (5 - row) * 100 + 90
                color = 'white' if self.board.board[row][col] == 0 else 'red' if self.board.board[row][col] == 1 else 'yellow'
                
                # Smooth, rounded corners for the pieces on the board
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline='black', width=2)

    def player_move(self, col):
        if self.game_over or self.board.next[col] >= 6:
            return

        row = self.board.next[col]
        self.board.board[row][col] = self.turn
        self.board.next[col] += 1
        self.display_board()
        if self.check_winner():
            self.end_game("You win!")
        else:
            self.turn = -self.turn
            self.ai_move()

    def ai_move(self, budget=2000):
        if self.game_over:
            return

        root = Node(state=copy.deepcopy(self.board))
        best_node = MCTS(budget, root)
        action = np.argwhere(best_node.state.board != self.board.board)[0]
        col = action[1]
        print(f"AI places at column {col}.")
        
        row = self.board.next[col]
        self.board.board[row][col] = self.turn
        self.board.next[col] += 1
        self.display_board()
        if self.check_winner():
            self.end_game("AI wins!")
        else:
            self.turn = -self.turn

    def check_winner(self):
        winner = self.board.Winner()
        if winner != 0:
            return True
        return False

    def end_game(self, message):
        self.game_over = True
        self.canvas.create_text(350, 300, text=message, font=('Helvetica', 24), fill="white")
        for button in self.buttons:
            button.config(state=tk.DISABLED)

    def reset_game(self):
        """Reset the game to the initial state."""
        self.board = Board()
        self.turn = 1
        self.game_over = False
        self.display_board()
        for button in self.buttons:
            button.config(state=tk.NORMAL)

    def exit_game(self):
        """Close the application."""
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Connect 4")
    root.geometry("800x650")  # Set window size to fit everything better
    root.config(bg="#34495E")  # Background color for the window (a soft gray-blue)
    game = Connect4GUI(root)
    root.mainloop()
