import turtle
import time
import random
import json
import os
import winsound
from dataclasses import dataclass, field
from typing import List
from enum import Enum, auto

# --- ENUMS ---
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()

# --- MODEL ---
@dataclass
class CarGameModel:
    state: GameState = GameState.MENU
    score: int = 0
    high_score: int = 0
    level: int = 1
    car_x: int = 0
    car_y: int = -220
    fuel: float = 100.0
    road_lines: List[float] = field(default_factory=lambda: [300.0, 150.0, 0.0, -150.0, -300.0])
    enemies: List[List[float]] = field(default_factory=list)
    fuel_items: List[List[float]] = field(default_factory=list)

    @property
    def current_scroll_speed(self) -> float:
        return 14.0 + (self.level - 1) * 2.2

    def update_difficulty(self):
        self.level = (self.score // 10) + 1

    def drain_fuel(self):
        # Drains faster as levels increase
        self.fuel -= 0.15 + (self.level * 0.02)
        if self.fuel < 0: self.fuel = 0

    def save_high_score(self):
        with open("car_highscore.json", "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def load_high_score(self):
        if os.path.exists("car_highscore.json"):
            try:
                with open("car_highscore.json", "r") as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
            except (json.JSONDecodeError, IOError):
                self.high_score = 0
        else:
            self.high_score = 0

# --- VIEW ---
class CarGameView:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.title("TURBO RACER: FUEL RECOVERY")
        self.screen.bgcolor("#0F172A")
        self.screen.setup(width=600, height=800)
        self.screen.tracer(0)

        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.penup()

        # Build Player Car
        self.player_parts = []
        colors = ["#00E5FF", "#0284C7", "#111", "#111", "#FDE047", "#FDE047"]
        sizes = [(2.5, 1.2), (1.5, 0.8), (0.5, 0.3), (0.5, 0.3), (0.2, 0.2), (0.2, 0.2)]
        for i in range(6):
            t = turtle.Turtle("square" if i < 4 else "circle")
            t.color(colors[i]); t.shapesize(sizes[i][0], sizes[i][1]); t.penup()
            self.player_parts.append(t)

        self.enemy_turtles: List[turtle.Turtle] = []
        self.fuel_turtles: List[turtle.Turtle] = []

    def draw_box(self, x, y, w, h, color, border, fill=True):
        self.pen.goto(x - w/2, y + h/2)
        self.pen.color(border)
        if fill:
            self.pen.fillcolor(color)
            self.pen.begin_fill()
        
        self.pen.pendown()
        for _ in range(2):
            self.pen.forward(w); self.pen.right(90)
            self.pen.forward(h); self.pen.right(90)
        self.pen.penup()
        if fill: self.pen.end_fill()

    def draw_fuel_bar(self, fuel_pct):
        # Unity-style UI Positioning (Top Right)
        x, y = 120, 360
        width, height = 150, 20
        
        # Draw Background (Outline)
        self.draw_box(x, y, width, height, "#1E293B", "#475569", fill=True)
        
        # Determine Color based on fuel level
        bar_color = "#00E5FF" # Cyan
        if fuel_pct < 50: bar_color = "#FDE047" # Yellow
        if fuel_pct < 25: bar_color = "#F43F5E" # Red
        
        # Draw the actual "Fill"
        if fuel_pct > 0:
            fill_w = (width * (fuel_pct / 100))
            self.draw_box(x - (width - fill_w)/2, y, fill_w, height, bar_color, bar_color, fill=True)
            
        self.pen.color("white")
        self.pen.goto(x - 120, y - 15)
        self.pen.write("FUEL", font=("Verdana", 8, "bold"))

    def draw_menu(self, my_best):
        self.pen.clear(); self.hide_all()
        self.pen.color("#F8FAFC"); self.pen.goto(0, 200)
        self.pen.write("TURBO RACER", align="center", font=("Verdana", 36, "bold"))
        
        self.draw_box(0, 40, 280, 100, "#1E293B", "#00E5FF")
        self.pen.color("#94A3B8"); self.pen.goto(0, 65)
        self.pen.write("MY HIGH SCORE", align="center", font=("Verdana", 10, "bold"))
        self.pen.color("white"); self.pen.goto(0, 10)
        self.pen.write(f"{my_best}", align="center", font=("Verdana", 32, "bold"))
        
        self.pen.color("#64748B"); self.pen.goto(0, -100)
        self.pen.write("PRESS SPACE TO START", align="center", font=("Verdana", 12, "normal"))
        self.screen.update()

    def draw_game_over(self, score, best, is_new):
        self.draw_box(0, 0, 400, 300, "#0F172A", "#F43F5E" if not is_new else "#10B981")
        self.pen.color("white"); self.pen.goto(0, 80)
        self.pen.write("CRASHED!", align="center", font=("Verdana", 24, "bold"))
        
        self.pen.goto(0, 20); self.pen.write(f"SCORE: {score}", align="center", font=("Verdana", 14, "normal"))
        self.pen.goto(0, -20); self.pen.write(f"BEST: {best}", align="center", font=("Verdana", 14, "normal"))

        if is_new:
            self.pen.color("#FDE047"); self.pen.goto(0, -60)
            self.pen.write("NEW RECORD!", align="center", font=("Verdana", 16, "bold"))

        self.pen.color("#475569"); self.pen.goto(0, -110)
        self.pen.write("SPACE TO RESTART", align="center", font=("Verdana", 10, "bold"))
        self.screen.update()

    def hide_all(self):
        for p in self.player_parts: p.hideturtle()
        for t in self.enemy_turtles: t.hideturtle()
        for f in self.fuel_turtles: f.hideturtle()

    def render(self, model):
        self.pen.clear()
        # Draw road
        self.pen.color("#1E293B"); self.pen.pensize(4)
        for y in model.road_lines:
            for x in [-80, 80]:
                self.pen.goto(x, y + 40); self.pen.pendown(); self.pen.goto(x, y - 40); self.pen.penup()
        
        # Player Update
        for i, part in enumerate(self.player_parts):
            part.showturtle(); part.goto(model.car_x + [0,0,-15,15,-6,6][i], model.car_y + [0,20,-20,-20,35,35][i])
        
        self.update_pool(self.enemy_turtles, model.enemies, "#F43F5E", (2.5, 1.2), "square")
        self.update_pool(self.fuel_turtles, model.fuel_items, "#00E5FF", (0.8, 0.8), "circle")
        
        # HUD Elements
        self.pen.color("white"); self.pen.goto(-270, 350)
        self.pen.write(f"SCORE: {model.score}  LVL: {model.level}", font=("Verdana", 12, "bold"))
        
        self.draw_fuel_bar(model.fuel)
        
        self.screen.update()

    def update_pool(self, pool, data, color, size, shape):
        while len(pool) < len(data):
            t = turtle.Turtle(shape); t.color(color); t.shapesize(size[0], size[1]); t.penup(); pool.append(t)
        for i, d in enumerate(data): pool[i].showturtle(); pool[i].goto(d[0], d[1])
        for j in range(len(data), len(pool)): pool[j].hideturtle()

# --- CONTROLLER ---
class GameController:
    def __init__(self, model, view):
        self.model, self.view = model, view
        self.model.load_high_score()
        self.view.screen.listen()
        self.view.screen.onkeypress(self.handle_space, "space")
        self.view.screen.onkeypress(lambda: self.move(-80), "Left")
        self.view.screen.onkeypress(lambda: self.move(80), "Right")
        self.is_new_best = False

    def handle_space(self):
        if self.model.state != GameState.PLAYING:
            self.model.state = GameState.PLAYING
            self.model.score, self.model.fuel, self.model.level = 0, 100.0, 1
            self.model.enemies, self.model.fuel_items = [], []
            self.is_new_best = False
            winsound.Beep(600, 100)

    def move(self, amount):
        if self.model.state == GameState.PLAYING:
            nx = self.model.car_x + amount
            if -160 <= nx <= 160: 
                self.model.car_x = nx
                winsound.Beep(300, 20)

    def update_logic(self):
        if self.model.state != GameState.PLAYING: return
        
        self.model.drain_fuel()
        if self.model.fuel <= 0: 
            self.end_game()
            return
        
        speed = self.model.current_scroll_speed
        for i in range(len(self.model.road_lines)):
            self.model.road_lines[i] -= speed
            if self.model.road_lines[i] < -400: self.model.road_lines[i] = 400
            
        # Spawn logic
        if random.random() < 0.06:
            self.model.enemies.append([random.choice([-160, -80, 80, 160]), 450, random.uniform(9, 14 + self.model.level)])
        
        if random.random() < 0.015: 
            self.model.fuel_items.append([random.choice([-160, -80, 80, 160]), 450])
            
        # Collision: Enemies
        for e in self.model.enemies[:]:
            e[1] -= e[2]
            if abs(e[0] - self.model.car_x) < 35 and abs(e[1] - self.model.car_y) < 45: 
                self.end_game()
            elif e[1] < -450: 
                self.model.enemies.remove(e)
                self.model.score += 1
                self.model.update_difficulty()
            
        # Collision: Fuel
        for f in self.model.fuel_items[:]:
            f[1] -= speed
            if abs(f[0] - self.model.car_x) < 35 and abs(f[1] - self.model.car_y) < 35:
                self.model.fuel = min(100, self.model.fuel + 35)
                winsound.Beep(1000, 50)
                self.model.fuel_items.remove(f)
            elif f[1] < -450: 
                self.model.fuel_items.remove(f)

    def end_game(self):
        winsound.Beep(200, 500)
        if self.model.score > self.model.high_score:
            self.model.high_score = self.model.score
            self.model.save_high_score()
            self.is_new_best = True
        self.model.state = GameState.GAME_OVER

    def run(self):
        while True:
            if self.model.state == GameState.MENU: 
                self.view.draw_menu(self.model.high_score)
            elif self.model.state == GameState.PLAYING: 
                self.update_logic()
                self.view.render(self.model)
            elif self.model.state == GameState.GAME_OVER:
                self.view.render(self.model)
                self.view.draw_game_over(self.model.score, self.model.high_score, self.is_new_best)
            time.sleep(0.016)

if __name__ == "__main__":
    GameController(CarGameModel(), CarGameView()).run()