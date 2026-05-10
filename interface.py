"""Connect 4 GUI vs an MCTS bot, rendered with pygame."""
import copy
import sys

import numpy as np
import pygame

from monte_carlo_connect4 import MCTS, Node, Board

BG = (251, 250, 246)
INK = (31, 41, 51)
MUTED = (123, 135, 148)
BOARD_BG = (61, 90, 128)
EMPTY = BG
P1 = (224, 122, 95)
P2 = (245, 193, 46)
WIN_GLOW = (255, 244, 149)
BTN_BG = (236, 233, 224)
BTN_HOVER = (255, 244, 149)

CELL = 80
COLS, ROWS = 7, 6
PAD = 18
BOARD_W = COLS * CELL + 2 * PAD
BOARD_H = ROWS * CELL + 2 * PAD
WIN_W = BOARD_W + 80
WIN_H = BOARD_H + 200

DROP_MS = 320
BUDGET = 3000


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    return 1 - (1 - t) ** 2


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Connect 4")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("HelveticaNeue,Helvetica,Arial", 26)
        self.font_sub = pygame.font.SysFont("HelveticaNeue,Helvetica,Arial", 14)
        self.font_btn = pygame.font.SysFont("HelveticaNeue,Helvetica,Arial", 14)
        self.reset()

    def reset(self):
        self.board = Board()
        self.turn = 1
        self.last_move = None
        self.win_cells = set()
        self.game_over = False
        self.status = ""
        self.dropping = None
        self.thinking = False
        self.hover_col = None
        self.btn_rect = None

    @property
    def board_origin(self):
        return (WIN_W - BOARD_W) // 2, 100

    def cell_center(self, row, col):
        bx, by = self.board_origin
        cx = bx + PAD + col * CELL + CELL // 2
        cy = by + PAD + (5 - row) * CELL + CELL // 2
        return cx, cy

    def col_at(self, x, y):
        bx, by = self.board_origin
        if not (bx + PAD <= x < bx + BOARD_W - PAD):
            return None
        if not (by - 40 <= y < by + BOARD_H):
            return None
        return int((x - bx - PAD) // CELL)

    def start_drop(self, col, turn):
        if self.board.next[col] >= 6 or self.dropping or self.thinking:
            return
        row = int(self.board.next[col])
        self.dropping = {
            "col": col, "row": row, "turn": turn,
            "start": pygame.time.get_ticks(),
            "color": P1 if turn == 1 else P2,
        }

    def update_drop(self):
        if not self.dropping:
            return
        if pygame.time.get_ticks() - self.dropping["start"] < DROP_MS:
            return
        row, col, turn = self.dropping["row"], self.dropping["col"], self.dropping["turn"]
        self.board.board[row, col] = turn
        self.board.next[col] += 1
        self.last_move = (row, col)
        self.dropping = None
        if self._check_winner():
            return
        self.turn = -self.turn
        if self.turn == -1 and not self.game_over:
            self.thinking = True
            self.status = "MCTS thinking…"

    def do_ai_move(self):
        # Render once with the "thinking" status visible, then compute synchronously.
        self.draw()
        pygame.display.flip()
        root = Node(state=copy.deepcopy(self.board))
        best = MCTS(BUDGET, root)
        diff = np.argwhere(best.state.board != self.board.board)
        col = int(diff[0][1])
        self.thinking = False
        self.status = ""
        self.start_drop(col, -1)

    def _check_winner(self):
        winner = self.board.Winner()
        if winner == 0 and not self.board.IsTerminal():
            return False
        line = self._winning_line()
        if line:
            self.win_cells = set(line)
        self.game_over = True
        if winner == 1:
            self.status = "you win"
        elif winner == -1:
            self.status = "MCTS wins"
        else:
            self.status = "draw"
        return True

    def _winning_line(self):
        b = self.board.board
        for r in range(ROWS):
            for c in range(COLS - 3):
                v = b[r, c]
                if v != 0 and v == b[r, c + 1] == b[r, c + 2] == b[r, c + 3]:
                    return [(r, c + i) for i in range(4)]
        for r in range(ROWS - 3):
            for c in range(COLS):
                v = b[r, c]
                if v != 0 and v == b[r + 1, c] == b[r + 2, c] == b[r + 3, c]:
                    return [(r + i, c) for i in range(4)]
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                v = b[r, c]
                if v != 0 and v == b[r + 1, c + 1] == b[r + 2, c + 2] == b[r + 3, c + 3]:
                    return [(r + i, c + i) for i in range(4)]
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                v = b[r, c]
                if v != 0 and v == b[r - 1, c + 1] == b[r - 2, c + 2] == b[r - 3, c + 3]:
                    return [(r - i, c + i) for i in range(4)]
        return None

    def draw(self):
        self.screen.fill(BG)

        title = self.font_title.render("Connect 4  ·  MCTS", True, INK)
        self.screen.blit(title, (40, 28))
        sub = self.status if self.status else "you  vs  MCTS"
        self.screen.blit(self.font_sub.render(sub, True, MUTED), (40, 62))

        bx, by = self.board_origin
        pygame.draw.rect(self.screen, BOARD_BG,
                         (bx, by, BOARD_W, BOARD_H), border_radius=18)

        for r in range(ROWS):
            for c in range(COLS):
                cx, cy = self.cell_center(r, c)
                v = self.board.board[r, c]
                color = EMPTY if v == 0 else (P1 if v == 1 else P2)
                if (r, c) in self.win_cells:
                    pygame.draw.circle(self.screen, WIN_GLOW, (cx, cy), 36)
                pygame.draw.circle(self.screen, color, (cx, cy), 28)
                if self.last_move == (r, c) and not self.win_cells:
                    pygame.draw.circle(self.screen, INK, (cx, cy), 32, width=2)

        if (self.hover_col is not None and not self.game_over
                and not self.dropping and not self.thinking and self.turn == 1
                and self.board.next[self.hover_col] < 6):
            cx = bx + PAD + self.hover_col * CELL + CELL // 2
            top_y = by - 18
            surf = pygame.Surface((56, 56), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*P1, 170), (28, 28), 22)
            self.screen.blit(surf, (cx - 28, top_y - 28))

        if self.dropping:
            now = pygame.time.get_ticks()
            t = ease_out(min(1.0, (now - self.dropping["start"]) / DROP_MS))
            target_cx, target_cy = self.cell_center(self.dropping["row"],
                                                    self.dropping["col"])
            top_y = by - 18
            cy = lerp(top_y, target_cy, t)
            pygame.draw.circle(self.screen, self.dropping["color"],
                               (target_cx, int(cy)), 28)

        if self.game_over:
            btn_w, btn_h = 160, 38
            bx2 = (WIN_W - btn_w) // 2
            by2 = WIN_H - 70
            self.btn_rect = pygame.Rect(bx2, by2, btn_w, btn_h)
            hover = self.btn_rect.collidepoint(*pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, BTN_HOVER if hover else BTN_BG,
                             self.btn_rect, border_radius=10)
            label = self.font_btn.render("play again", True, INK)
            self.screen.blit(label, label.get_rect(center=self.btn_rect.center))
        else:
            self.btn_rect = None

    def handle_event(self, ev):
        if ev.type == pygame.QUIT:
            return False
        if ev.type == pygame.MOUSEMOTION:
            self.hover_col = self.col_at(*ev.pos)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = ev.pos
            if self.game_over and self.btn_rect and self.btn_rect.collidepoint(mx, my):
                self.reset()
                return True
            if not self.game_over and self.turn == 1 and not self.dropping and not self.thinking:
                col = self.col_at(mx, my)
                if col is not None:
                    self.start_drop(col, 1)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            return False
        return True

    def loop(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if not self.handle_event(ev):
                    running = False
            self.update_drop()
            self.draw()
            pygame.display.flip()
            if self.thinking and not self.dropping:
                self.do_ai_move()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    Game().loop()
