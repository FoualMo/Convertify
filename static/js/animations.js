document.addEventListener("DOMContentLoaded", () => {

  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  let mouse = { x: null, y: null };
  window.addEventListener('mousemove', e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  let particles = [];
  const particleCount = 80;

  for (let i=0; i<particleCount; i++){
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random()*3 + 1,
      speedX: (Math.random()-0.5)*0.5,
      speedY: (Math.random()-0.5)*0.5,
      alpha: Math.random()*0.5 + 0.3
    });
  }

  function animateParticles(){
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
      if(mouse.x !== null){
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if(dist < 150){
          p.x += dx * 0.002;
          p.y += dy * 0.002;
        }
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2);
      ctx.fillStyle = `rgba(255,255,255,${p.alpha})`;
      ctx.fill();

      p.x += p.speedX;
      p.y += p.speedY;

      if(p.x < 0 || p.x > canvas.width) p.speedX *= -1;
      if(p.y < 0 || p.y > canvas.height) p.speedY *= -1;
    });

    requestAnimationFrame(animateParticles);
  }

  animateParticles();
});
