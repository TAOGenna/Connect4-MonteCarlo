"""
Local-only driver: emit one frame per ply of a self-play game between two
MCTS bots, then a few extra frames highlighting the winning line. ffmpeg
the frames into an mp4 for the project thumbnail.
"""

import copy
import os
import random
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch

from monte_carlo_connect4 import MCTS, Node, Board

random.seed(7)
np.random.seed(7)

FRAME_DIR = "anim_frames"

BG = "#fbfaf6"
INK = "#1f2933"
MUTED = "#7b8794"
BOARD = "#3d5a80"
EMPTY = "#fbfaf6"
P1 = "#e07a5f"
P2 = "#f5c12e"
WIN_GLOW = "#fff495"

ROWS, COLS = 6, 7
BUDGET = 200


def winning_line(board):
    b = board.board
    rows, cols = ROWS, COLS
    for r in range(rows):
        for c in range(cols - 3):
            v = b[r, c]
            if v != 0 and v == b[r, c + 1] == b[r, c + 2] == b[r, c + 3]:
                return [(r, c + i) for i in range(4)]
    for r in range(rows - 3):
        for c in range(cols):
            v = b[r, c]
            if v != 0 and v == b[r + 1, c] == b[r + 2, c] == b[r + 3, c]:
                return [(r + i, c) for i in range(4)]
    for r in range(rows - 3):
        for c in range(cols - 3):
            v = b[r, c]
            if v != 0 and v == b[r + 1, c + 1] == b[r + 2, c + 2] == b[r + 3, c + 3]:
                return [(r + i, c + i) for i in range(4)]
    for r in range(3, rows):
        for c in range(cols - 3):
            v = b[r, c]
            if v != 0 and v == b[r - 1, c + 1] == b[r - 2, c + 2] == b[r - 3, c + 3]:
                return [(r - i, c + i) for i in range(4)]
    return None


def draw_frame(idx, board, move_num, last_move, win_line=None, glow=False):
    fig = plt.figure(figsize=(9.2, 5.2), dpi=160, facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[3.2, 1.0], wspace=0.18,
                          left=0.04, right=0.96, top=0.92, bottom=0.08)

    ax_board = fig.add_subplot(gs[0])
    ax_side = fig.add_subplot(gs[1])

    ax_board.set_xlim(-0.5, COLS - 0.5)
    ax_board.set_ylim(-0.5, ROWS - 0.5)
    ax_board.set_aspect("equal")
    ax_board.set_xticks([])
    ax_board.set_yticks([])
    for s in ax_board.spines.values():
        s.set_visible(False)
    ax_board.set_facecolor(BG)

    pad = 0.46
    board_bg = FancyBboxPatch(
        (-pad, -pad),
        COLS - 1 + 2 * pad,
        ROWS - 1 + 2 * pad,
        boxstyle="round,pad=0.0,rounding_size=0.25",
        facecolor=BOARD, edgecolor="none",
    )
    ax_board.add_patch(board_bg)

    win_set = set(win_line) if win_line else set()
    for r in range(ROWS):
        for c in range(COLS):
            v = board.board[r, c]
            color = EMPTY if v == 0 else (P1 if v == 1 else P2)
            in_win = (r, c) in win_set
            if in_win and glow:
                ax_board.add_patch(Circle((c, r), 0.46,
                                          facecolor=WIN_GLOW, edgecolor="none",
                                          alpha=0.55, zorder=2))
            ax_board.add_patch(Circle((c, r), 0.36,
                                      facecolor=color, edgecolor="none",
                                      zorder=3))
            if last_move == (r, c):
                ax_board.add_patch(Circle((c, r), 0.40,
                                          facecolor="none",
                                          edgecolor=INK, linewidth=1.4,
                                          alpha=0.55, zorder=4))

    ax_side.set_xlim(0, 1)
    ax_side.set_ylim(0, 1)
    ax_side.set_xticks([])
    ax_side.set_yticks([])
    for s in ax_side.spines.values():
        s.set_visible(False)
    ax_side.set_facecolor(BG)

    ax_side.text(0.0, 0.92, "MCTS  ·  self play",
                 fontsize=13, color=INK, weight=500, transform=ax_side.transAxes)
    ax_side.text(0.0, 0.85, f"connect 4",
                 fontsize=10, color=MUTED, transform=ax_side.transAxes)

    ax_side.text(0.0, 0.62, f"move",
                 fontsize=10, color=MUTED, transform=ax_side.transAxes)
    ax_side.text(0.0, 0.54, f"{move_num}",
                 fontsize=28, color=INK, weight=400, transform=ax_side.transAxes)

    ax_side.scatter([0.08], [0.34], s=160, c=P1, edgecolors="none",
                    transform=ax_side.transAxes, clip_on=False)
    ax_side.text(0.18, 0.33, "player 1",
                 fontsize=10, color=MUTED, transform=ax_side.transAxes)
    ax_side.scatter([0.08], [0.24], s=160, c=P2, edgecolors="none",
                    transform=ax_side.transAxes, clip_on=False)
    ax_side.text(0.18, 0.23, "player 2",
                 fontsize=10, color=MUTED, transform=ax_side.transAxes)

    if win_line is not None:
        winner_color = P1 if board.board[win_line[0]] == 1 else P2
        ax_side.scatter([0.08], [0.10], s=180, c=winner_color,
                        edgecolors=INK, linewidths=0.9,
                        transform=ax_side.transAxes, clip_on=False)
        ax_side.text(0.18, 0.09, "wins",
                     fontsize=10, color=INK, weight=500,
                     transform=ax_side.transAxes)

    fig.savefig(os.path.join(FRAME_DIR, f"frame_{idx:03d}.png"),
                facecolor=BG)
    plt.close(fig)


def main():
    if os.path.exists(FRAME_DIR):
        shutil.rmtree(FRAME_DIR)
    os.makedirs(FRAME_DIR, exist_ok=True)

    board = Board()
    turn = 1
    move_num = 0
    last_move = None

    draw_frame(0, board, move_num, last_move)
    frame_idx = 1

    while not board.IsTerminal() and board.Winner() == 0:
        root = Node(state=copy.deepcopy(board))
        best = MCTS(BUDGET, root)
        diff = np.argwhere(best.state.board != board.board)
        r, c = diff[0]
        board.board[r, c] = turn
        board.next[c] += 1
        move_num += 1
        last_move = (int(r), int(c))
        draw_frame(frame_idx, board, move_num, last_move)
        frame_idx += 1
        turn = -turn

    win = winning_line(board)
    if win is not None:
        for _ in range(8):
            draw_frame(frame_idx, board, move_num, last_move, win_line=win, glow=True)
            frame_idx += 1
        for _ in range(4):
            draw_frame(frame_idx, board, move_num, last_move, win_line=win, glow=False)
            frame_idx += 1

    print(f"Wrote {frame_idx} frames to {FRAME_DIR}/")


if __name__ == "__main__":
    main()
