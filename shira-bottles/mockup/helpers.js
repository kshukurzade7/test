// warm studio wall with soft out-of-focus shelf bottles
function wallCanvas() {
  const c = document.createElement('canvas'); c.width = 2048; c.height = 1024;
  const g = c.getContext('2d');
  const grd = g.createLinearGradient(0, 0, 0, 1024);
  grd.addColorStop(0, '#CDB79C'); grd.addColorStop(0.55, '#E3D2BC'); grd.addColorStop(1, '#C9B092');
  g.fillStyle = grd; g.fillRect(0, 0, 2048, 1024);
  const glow = g.createRadialGradient(1024, 420, 40, 1024, 420, 900);
  glow.addColorStop(0, 'rgba(255,246,230,0.7)'); glow.addColorStop(1, 'rgba(255,246,230,0)');
  g.fillStyle = glow; g.fillRect(0, 0, 2048, 1024);
  g.filter = 'blur(26px)';
  [[260, '#8E2A2A'], [430, '#C9852E'], [1620, '#5A1E3E'], [1790, '#B8662A']].forEach(([x, col]) => {
    g.fillStyle = col; g.globalAlpha = 0.55;
    g.beginPath(); g.roundRect(x - 55, 380, 110, 520, 40); g.fill();
    g.fillRect(x - 22, 170, 44, 230);
    g.fillStyle = '#EDE3D2'; g.globalAlpha = 0.6; g.fillRect(x - 56, 660, 112, 170);
  });
  g.globalAlpha = 1; g.filter = 'none';
  return c;
}

function woodCanvas() {
  const c = document.createElement('canvas'); c.width = 2048; c.height = 1024;
  const g = c.getContext('2d');
  g.fillStyle = '#8A5A33'; g.fillRect(0, 0, 2048, 1024);
  let seed = 9; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let y = 0; y < 1024; y += 2) {
    const v = Math.sin(y * 0.03) * 0.5 + Math.sin(y * 0.011 + 2) * 0.35 + Math.sin(y * 0.17) * 0.15;
    const l = 0.86 + v * 0.14;
    g.fillStyle = `rgba(${168 * l | 0},${112 * l | 0},${66 * l | 0},0.6)`; g.fillRect(0, y, 2048, 2);
  }
  for (let i = 0; i < 1600; i++) {
    g.strokeStyle = `rgba(70,40,18,${0.04 + rnd() * 0.1})`; g.lineWidth = 0.6 + rnd() * 1.6;
    const y = rnd() * 1024, x = rnd() * 2048, len = 120 + rnd() * 600;
    g.beginPath(); g.moveTo(x, y); g.bezierCurveTo(x + len * 0.3, y + rnd() * 5 - 2.5, x + len * 0.6, y + rnd() * 5 - 2.5, x + len, y + rnd() * 3 - 1.5); g.stroke();
  }
  return c;
}

