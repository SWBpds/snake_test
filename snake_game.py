import tkinter as tk
import random

# ============================================================
#  常量配置
# ============================================================
CELL_SIZE   = 20                        # 每格像素大小
GRID_WIDTH  = 30                        # 网格列数
GRID_HEIGHT = 20                        # 网格行数
INIT_SPEED  = 150                       # 初始速度 (ms/帧)
SPEED_STEP  = 5                         # 每吃一个食物加速 (ms)
MIN_SPEED   = 50                        # 最快速度上限

# 颜色方案
COLOR_BG        = "#1a1a2e"              # 背景
COLOR_GRID      = "#16213e"              # 网格线
COLOR_SNAKE     = "#00d2ff"              # 蛇身
COLOR_SNAKE_HEAD= "#0af0b1"              # 蛇头
COLOR_FOOD      = "#ff6b6b"              # 食物
COLOR_TEXT      = "#e0e0e0"              # 文字
COLOR_SCORE_BG  = "#0f3460"              # 计分栏背景

# 方向向量
DIRECTIONS = {
    "Up":    (0, -1),
    "Down":  (0,  1),
    "Left":  (-1, 0),
    "Right": (1,  0),
}
OPPOSITE  = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}


# ============================================================
#  游戏主类
# ============================================================
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        # -- 顶部信息栏 ---------------------------------------
        self.info_frame = tk.Frame(root, bg=COLOR_SCORE_BG, height=40)
        self.info_frame.pack(fill=tk.X)
        self.info_frame.pack_propagate(False)

        self.score_label = tk.Label(
            self.info_frame, text="Score: 0", fg=COLOR_TEXT,
            bg=COLOR_SCORE_BG, font=("Consolas", 14, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=16)

        self.best_label = tk.Label(
            self.info_frame, text="Best: 0", fg="#ffd700",
            bg=COLOR_SCORE_BG, font=("Consolas", 14, "bold"))
        self.best_label.pack(side=tk.RIGHT, padx=16)

        # -- 画布 ---------------------------------------------
        self.canvas_width  = GRID_WIDTH  * CELL_SIZE
        self.canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(
            root, width=self.canvas_width, height=self.canvas_height,
            bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack()

        # -- 底部控制栏 ---------------------------------------
        self.ctrl_frame = tk.Frame(root, bg=COLOR_SCORE_BG, height=40)
        self.ctrl_frame.pack(fill=tk.X)
        self.ctrl_frame.pack_propagate(False)

        self.status_label = tk.Label(
            self.ctrl_frame, text="Press SPACE to start | Arrow keys or WASD to move",
            fg=COLOR_TEXT, bg=COLOR_SCORE_BG, font=("Consolas", 10))
        self.status_label.pack(expand=True)

        # -- 绑定键盘 -----------------------------------------
        root.bind("<KeyPress>", self._on_key)

        # -- 状态变量 -----------------------------------------
        self.best_score = 0
        self.reset()

    # --------------------------------------------------------
    def reset(self):
        """Reset game state but keep high score"""
        if hasattr(self, "_after_id") and self._after_id:
            self.root.after_cancel(self._after_id)

        # Snake initial position: horizontal 3 segments
        start_x = GRID_WIDTH  // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y),
                      (start_x - 1, start_y),
                      (start_x - 2, start_y)]
        self.direction  = "Right"
        self.next_dir   = "Right"       # buffered input to prevent instant reverse
        self.food       = None
        self.score      = 0
        self.speed      = INIT_SPEED
        self.game_over  = True
        self._after_id  = None

        self._spawn_food()
        self._draw()

    # --------------------------------------------------------
    #  Food
    # --------------------------------------------------------
    def _spawn_food(self):
        """Spawn food at a random empty cell"""
        occupied = set(self.snake)
        if len(occupied) >= GRID_WIDTH * GRID_HEIGHT:
            return  # board is full (player wins)
        while True:
            fx = random.randint(0, GRID_WIDTH  - 1)
            fy = random.randint(0, GRID_HEIGHT - 1)
            if (fx, fy) not in occupied:
                self.food = (fx, fy)
                break

    # --------------------------------------------------------
    #  Draw
    # --------------------------------------------------------
    def _draw(self):
        self.canvas.delete("all")

        # --- grid lines ---
        for x in range(0, self.canvas_width + 1, CELL_SIZE):
            self.canvas.create_line(x, 0, x, self.canvas_height,
                                    fill=COLOR_GRID, width=1)
        for y in range(0, self.canvas_height + 1, CELL_SIZE):
            self.canvas.create_line(0, y, self.canvas_width, y,
                                    fill=COLOR_GRID, width=1)

        # --- food ---
        if self.food:
            fx, fy = self.food
            x1 = fx * CELL_SIZE + 2
            y1 = fy * CELL_SIZE + 2
            x2 = x1 + CELL_SIZE - 4
            y2 = y1 + CELL_SIZE - 4
            self.canvas.create_oval(x1, y1, x2, y2,
                                    fill=COLOR_FOOD, outline="")

        # --- snake ---
        for i, (sx, sy) in enumerate(self.snake):
            x1 = sx * CELL_SIZE + 1
            y1 = sy * CELL_SIZE + 1
            x2 = x1 + CELL_SIZE - 2
            y2 = y1 + CELL_SIZE - 2
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=color, outline="")

        # Game Over overlay
        if self.game_over:
            self.canvas.create_rectangle(
                0, 0, self.canvas_width, self.canvas_height,
                fill="#000000", stipple="gray50", outline="")
            self.canvas.create_text(
                self.canvas_width // 2, self.canvas_height // 2 - 15,
                text="GAME OVER", fill="#ff6b6b",
                font=("Consolas", 24, "bold"))
            self.canvas.create_text(
                self.canvas_width // 2, self.canvas_height // 2 + 25,
                text="Press SPACE to restart", fill=COLOR_TEXT,
                font=("Consolas", 12))

        # update score labels
        self.score_label.config(text=f"Score: {self.score}")
        if self.score > self.best_score:
            self.best_score = self.score
        self.best_label.config(text=f"Best: {self.best_score}")

    # --------------------------------------------------------
    #  Keyboard input
    # --------------------------------------------------------
    def _on_key(self, event):
        key = event.keysym

        if key == "space":
            if self.game_over:
                self._start()
            return

        if self.game_over:
            return

        # Arrow keys / WASD
        key_map = {
            "Up":    "Up",    "w": "Up",    "W": "Up",
            "Down":  "Down",  "s": "Down",  "S": "Down",
            "Left":  "Left",  "a": "Left",  "A": "Left",
            "Right": "Right", "d": "Right", "D": "Right",
        }
        new_dir = key_map.get(key)
        if new_dir is None:
            return

        # prevent instant reverse
        if new_dir != OPPOSITE.get(self.direction):
            self.next_dir = new_dir

    # --------------------------------------------------------
    #  Start
    # --------------------------------------------------------
    def _start(self):
        self.reset()
        self.game_over = False
        self.status_label.config(text="Playing... Arrow keys or WASD to move")
        self._draw()
        self._tick()

    # --------------------------------------------------------
    #  Game loop
    # --------------------------------------------------------
    def _tick(self):
        if self.game_over:
            return

        # apply buffered direction
        self.direction = self.next_dir
        dx, dy = DIRECTIONS[self.direction]

        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        # --- wall collision ---
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self._end_game()
            return

        # --- self collision (exclude tail since it will move away) ---
        will_eat = (new_head == self.food)
        body_to_check = self.snake if will_eat else self.snake[:-1]
        if new_head in body_to_check:
            self._end_game()
            return

        # --- move ---
        self.snake.insert(0, new_head)
        if will_eat:
            self.score += 1
            self.speed = max(MIN_SPEED, self.speed - SPEED_STEP)
            self._spawn_food()
        else:
            self.snake.pop()

        self._draw()

        self._after_id = self.root.after(self.speed, self._tick)

    # --------------------------------------------------------
    def _end_game(self):
        self.game_over = True
        self.status_label.config(text="Press SPACE to restart")
        self._draw()


# ============================================================
#  Entry point
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()

    # center window
    root.update_idletasks()
    w = GRID_WIDTH  * CELL_SIZE
    h = GRID_HEIGHT * CELL_SIZE + 80
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    game = SnakeGame(root)
    root.mainloop()
