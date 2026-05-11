# 🚗 TURBO RACER: FUEL RECOVERY

A high-performance **lane-based car survival game** built with Python’s Turtle graphics, featuring **fuel mechanics, dynamic difficulty scaling, and real-time UI rendering**.

---

## 🎮 Gameplay Preview (Concept Flow)

```
START → DRIVE → AVOID ENEMIES → COLLECT FUEL → LEVEL UP → SURVIVE → GAME OVER → RESTART
```

---

## ⚙️ Core Systems (Explained Like a Pro)

### 1. 🚗 Player System (Modular Car Rendering)

Instead of using a single shape, the car is built using **multiple turtle components**:

```
[ Roof ]
[ Body ]
[ Wheels ]  [ Wheels ]
[ Lights ]
```

**How it works:**

* Each part is an independent turtle object
* All parts move together using coordinated offsets
* This simulates a **real car structure**

---

### 2. 🛣️ Infinite Road System (Scrolling Illusion)

```
|  |        ← Road lines move downward
|  |
|  |
```

**Mechanism:**

* Road lines continuously move downward
* When a line exits the screen → it resets to the top
* Creates a **looped infinite road effect**

---

### 3. 🚧 Enemy Spawn Engine

```
Lane positions: [-160, -80, 80, 160]
```

**Logic:**

* Enemies spawn randomly in lanes
* Each enemy has:

  * X position (lane)
  * Y position (start above screen)
  * Speed (scaled with level)

**Animation Flow:**

```
Spawn → Move Down → Collision Check → Remove/Score++
```

---

### 4. ⛽ Fuel System (Core Twist)

This is what makes your game **stand out in a hackathon**.

#### Fuel Drain:

```
fuel -= 0.15 + (level × 0.02)
```

#### Fuel Refill:

```
+35 on collecting fuel item
(max = 100)
```

#### Visual Feedback:

* 🔵 Full → Cyan
* 🟡 Medium → Yellow
* 🔴 Low → Red

**Game Over Trigger:**

```
if fuel <= 0 → GAME OVER
```

---

### 5. 📈 Dynamic Difficulty Scaling

```
level = (score // 10) + 1
```

**Effects:**

* Faster enemies
* Faster road scroll
* Higher fuel drain
* Increased spawn rate

This ensures:

> The game starts easy but becomes progressively intense.

---

### 6. 💥 Collision System (Real-Time Detection)

```
if abs(enemy_x - car_x) < threshold
and abs(enemy_y - car_y) < threshold:
    → crash
```

Used for:

* 🚧 Enemy collision → Game Over
* ⛽ Fuel pickup → Restore fuel

---

### 7. 🧠 State Management System

```
MENU → PLAYING → GAME_OVER
```

| State     | Behavior              |
| --------- | --------------------- |
| MENU      | Show intro UI         |
| PLAYING   | Run game loop         |
| GAME_OVER | Show result + restart |

---

### 8. 🎨 UI / HUD System (Game Feel)

Includes:

* Score + Level display
* Fuel bar (dynamic color)
* Game Over panel
* High score tracking (JSON storage)

---

## 🔁 Game Loop Architecture

```
while True:
    if MENU → draw_menu()
    if PLAYING → update_logic() + render()
    if GAME_OVER → show result screen
```

Frame Rate:

```
~60 FPS using time.sleep(0.016)
```

---

## 🧩 Tech Stack

* Python 🐍
* Turtle Graphics 🎨
* JSON (Data Persistence)
* Winsound (Feedback System)

---

## 🔊 Feedback System

| Action       | Sound     |
| ------------ | --------- |
| Start Game   | Beep      |
| Move         | Click     |
| Collect Fuel | High Beep |
| Crash        | Low Beep  |

---

## 🏆 Hackathon Highlights

### 💡 What Makes This Project Strong

* Modular MVC-like architecture
* Real-time game loop
* Physics-like movement system
* Resource management (fuel)
* Persistent high score system
* Clean UI rendering system

---

## 🚀 Possible Future Upgrades

* Smooth animation (lerp movement)
* Sprite-based car (PNG/GIF)
* Sound engine (pygame mixer)
* Power-ups (shield, slow motion)
* Mobile controls (touch simulation)
* Multiplayer leaderboard

---

## ▶️ How to Run

```bash
python main.py
```

---

## 🧠 Key Takeaway

This project demonstrates how **simple tools (like Turtle)** can be used to build:

* Interactive systems
* Game mechanics
* Scalable architecture

---

## 📌 Author

**Abdullah Al Mamun Zishan**
CSE Student, Feni University
CCO @ ARB Soft Tech

---

## ⭐ Final Thought

> "This isn’t just a game — it’s a system design exercise wrapped in gameplay."
