import turtle
import time
import random
import json
import os
from dataclasses import dataclass, field
from typing import List, Tuple
from enum import Enum, auto

# --- ENUMS ---
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()

# --- MODEL ---
@dataclass
class CarGameModel:
    state: GameState = GameState.MENU
    score: int = 0
    high_score: int = 0
    level: int = 1
    car_x: int = 0
    car_y: int = -200
    road_lines: List[float] = field(default_factory=lambda: [300.0, 150.0, 0.0, -150.0, -300.0])
    enemies: List[List[float]] = field(default_factory=list) 
    
    # Base Speeds
    base_scroll_speed: float = 12.0
    base_enemy_speed_min: float = 6.0
    base_enemy_speed_max: float = 10.0

    @property
    def current_scroll_speed(self) -> float:
        # Increases speed by 2 for every level
        return self.base_scroll_speed + (self.level - 1) * 2.5

    def update_difficulty(self):
        # Increase level every 10 points
        new_level = (self.score // 10) + 1
        if new_level > self.level:
            self.level = new_level

    def save_high_score(self):
        with open("car_highscore.json", "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def load_high_score(self):
        if os.path.exists("car_highscore.json"):
            try:
                with open("car_highscore.json", "r") as f:
                    self.high_score = json.load(f).get("high_score", 0)
            except: self.high_score = 0

# --- VIEW ---
class CarGameView:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.title("Python MVC Car Racer: Pro Edition")
        self.screen.bgcolor("#333") 
        self.screen.setup(width=500, height=700)
        self.screen.tracer(0)

        self.player = turtle.Turtle("square")
        self.player.shapesize(stretch_wid=2, stretch_len=1)
        self.player.color("cyan")
        self.player.penup()

        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.penup()
        
        self.enemy_turtles: List[turtle.Turtle] = []

    def draw_road(self, model: CarGameModel):
        self.pen.clear()
        self.pen.color("white")
        self.pen.pensize(5)
        for y_pos in model.road_lines:
            self.pen.goto(0, y_pos + 40)
            self.pen.pendown()
            self.pen.goto(0, y_pos - 40)
            self.pen.penup()
            
        self.pen.color("yellow")
        for x_side in [-200, 200]:
            self.pen.goto(x_side, -350)
            self.pen.pendown()
            self.pen.goto(x_side, 350)
            self.pen.penup()

    def draw_menu(self, high_score):
        self.pen.clear()
        self.player.hideturtle()
        self.pen.color("white")
        self.pen.goto(0, 100)
        self.pen.write("TURBO RACER", align="center", font=("Courier", 30, "bold"))
        self.pen.goto(0, 0)
        self.pen.write(f"High Score: {high_score}", align="center", font=("Courier", 16, "normal"))
        self.pen.goto(0, -100)
        self.pen.write("Press 'Space' to Race", align="center", font=("Courier", 14, "italic"))
        self.screen.update()

    def render(self, model: CarGameModel):
        self.draw_road(model)
        self.player.showturtle()
        self.player.goto(model.car_x, model.car_y)

        # HUD (Heads Up Display)
        self.pen.color("white")
        self.pen.goto(-230, 310)
        self.pen.write(f"Score: {model.score}", align="left", font=("Courier", 14, "bold"))
        self.pen.goto(230, 310)
        self.pen.write(f"LVL: {model.level}", align="right", font=("Courier", 14, "bold"))

        # Enemy Pool Handling
        while len(self.enemy_turtles) < len(model.enemies):
            t = turtle.Turtle("square")
            t.color("red")
            t.shapesize(stretch_wid=2, stretch_len=1)
            t.penup()
            self.enemy_turtles.append(t)

        for i, enemy_data in enumerate(model.enemies):
            self.enemy_turtles[i].showturtle()
            self.enemy_turtles[i].goto(enemy_data[0], enemy_data[1])

        for j in range(len(model.enemies), len(self.enemy_turtles)):
            self.enemy_turtles[j].hideturtle()

        self.screen.update()

# --- CONTROLLER ---
class GameController:
    def __init__(self, model: CarGameModel, view: CarGameView):
        self.model = model
        self.view = view
        self.model.load_high_score()
        self.view.screen.listen()
        self.view.screen.onkeypress(self.start_game, "space")
        self.view.screen.onkeypress(self.move_left, "Left")
        self.view.screen.onkeypress(self.move_right, "Right")

    def start_game(self):
        if self.model.state != GameState.PLAYING:
            self.model.state = GameState.PLAYING
            self.model.score = 0
            self.model.level = 1
            self.model.enemies = []

    def move_left(self):
        if self.model.car_x > -160: self.model.car_x -= 40
    def move_right(self):
        if self.model.car_x < 160: self.model.car_x += 40

    def update_logic(self):
        if self.model.state != GameState.PLAYING: return

        # 1. Update Road Speed
        scroll = self.model.current_scroll_speed
        for i in range(len(self.model.road_lines)):
            self.model.road_lines[i] -= scroll
            if self.model.road_lines[i] < -350:
                self.model.road_lines[i] = 350

        # 2. Spawn Enemies (Difficulty increases spawn rate slightly)
        spawn_chance = 0.04 + (self.model.level * 0.005)
        if random.random() < spawn_chance:
            lane_x = random.choice([-150, -50, 50, 150])
            # Enemy speed also scales with level
            speed_min = self.model.base_enemy_speed_min + self.model.level
            speed_max = self.model.base_enemy_speed_max + (self.model.level * 1.5)
            self.model.enemies.append([lane_x, 400, random.uniform(speed_min, speed_max)])

        # 3. Collision and Scoring
        for enemy in self.model.enemies[:]:
            enemy[1] -= enemy[2]
            if abs(enemy[0] - self.model.car_x) < 30 and abs(enemy[1] - self.model.car_y) < 40:
                self.handle_game_over()
            if enemy[1] < -400:
                self.model.enemies.remove(enemy)
                self.model.score += 1
                self.model.update_difficulty()

    def handle_game_over(self):
        self.model.state = GameState.MENU
        if self.model.score > self.model.high_score:
            self.model.high_score = self.model.score
            self.model.save_high_score()
        for t in self.view.enemy_turtles: t.hideturtle()

    def run(self):
        while True:
            if self.model.state == GameState.MENU:
                self.view.draw_menu(self.model.high_score)
            else:
                self.update_logic()
                self.view.render(self.model)
            time.sleep(0.02)

if __name__ == "__main__":
    game_controller = GameController(CarGameModel(), CarGameView())
    game_controller.run()