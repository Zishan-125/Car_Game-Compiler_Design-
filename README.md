# 🚗 TURBO RACER: FUEL RECOVERY (Interactive README)

<!-- ===================== HERO ANIMATION ===================== -->
<p align="center">
  <canvas id="carAnim" width="600" height="200"></canvas>
</p>

<script>
const canvas = document.getElementById("carAnim");
const ctx = canvas.getContext("2d");

let x = 0;

function drawRoad() {
    ctx.fillStyle = "#0F172A";
    ctx.fillRect(0, 0, 600, 200);

    ctx.strokeStyle = "#334155";
    ctx.lineWidth = 3;

    for (let i = 0; i < 10; i++) {
        ctx.beginPath();
        ctx.moveTo(60 + i * 50, 0);
        ctx.lineTo(60 + i * 50, 200);
        ctx.stroke();
    }
}

function drawCar() {
    // body
    ctx.fillStyle = "#00E5FF";
    ctx.fillRect(x, 120, 60, 20);

    // roof
    ctx.fillStyle = "#0284C7";
    ctx.fillRect(x + 15, 105, 30, 15);

    // wheels
    ctx.fillStyle = "#000";
    ctx.fillRect(x + 10, 140, 10, 10);
    ctx.fillRect(x + 40, 140, 10, 10);
}

function loop() {
    drawRoad();
    drawCar();
    x += 2;
    if (x > 600) x = -60;
    requestAnimationFrame(loop);
}

loop();
</script>

---

# 🎮 GAME FLOW (LIVE SYSTEM VISUALIZATION)





