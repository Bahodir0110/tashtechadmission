import React, { useEffect, useRef } from 'react';

/**
 * Premium Engineering Background Canvas (Grey Theme):
 * - Mechanical gears in precision line art
 * - Physics & calculus engineering formulas in JetBrains Mono
 * - Atomic orbitals & microchip symbols
 * - Responsive mouse particle reaction
 */
export default function EngineeringCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const mouse = { x: null, y: null, radius: 160 };

    const formulaTexts = [
      'E = mc²',
      'F = m·a',
      'V = I·R',
      '∫ f(x) dx',
      'e^(iπ) + 1 = 0',
      '∇ × B = μ₀J',
      'Δx·Δp ≥ ℏ/2',
      'σ = E·ε',
      'τ = r × F',
      'λ = h/p',
      'Σ F = 0',
      'η = 1 - Tc/Th',
      '∮ B·dl = μ₀I',
      'lim (sin x)/x = 1',
      'PV = nRT',
      'd²x/dt² + ω²x = 0',
      'TashTech Engineering'
    ];

    class FloatingFormula {
      constructor() {
        this.reset(true);
      }

      reset(initial = false) {
        this.text = formulaTexts[Math.floor(Math.random() * formulaTexts.length)];
        this.x = Math.random() * width;
        this.y = initial ? Math.random() * height : height + 30;
        this.vx = (Math.random() - 0.5) * 0.35;
        this.vy = -(Math.random() * 0.35 + 0.18);
        this.fontSize = Math.floor(Math.random() * 5) + 12;
        this.isOrange = Math.random() > 0.45;
        this.baseAlpha = Math.random() * 0.28 + 0.2;
        this.alpha = this.baseAlpha;
        this.oscillation = Math.random() * Math.PI * 2;
        this.oscSpeed = Math.random() * 0.02 + 0.01;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.oscillation += this.oscSpeed;
        this.x += Math.sin(this.oscillation) * 0.3;

        if (mouse.x !== null && mouse.y !== null) {
          const dx = mouse.x - this.x;
          const dy = mouse.y - this.y;
          const dist = Math.hypot(dx, dy);
          if (dist < mouse.radius) {
            const force = (mouse.radius - dist) / mouse.radius;
            this.x -= (dx / dist) * force * 2.5;
            this.y -= (dy / dist) * force * 2.5;
          }
        }

        if (this.y < -40 || this.x < -100 || this.x > width + 100) {
          this.reset(false);
        }
      }

      draw() {
        ctx.save();
        ctx.font = `600 ${this.fontSize}px 'JetBrains Mono', 'Courier New', monospace`;
        ctx.fillStyle = this.isOrange ? '#e54519' : '#475569';
        ctx.globalAlpha = this.alpha;
        ctx.fillText(this.text, this.x, this.y);
        ctx.restore();
      }
    }

    class MechanicalGear {
      constructor(x, y, radius, teeth, speed, isOrange) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.teeth = teeth;
        this.angle = Math.random() * Math.PI * 2;
        this.speed = speed;
        this.isOrange = isOrange;
      }

      update() {
        this.angle += this.speed;
      }

      draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);

        ctx.strokeStyle = this.isOrange ? 'rgba(229, 69, 25, 0.32)' : 'rgba(100, 116, 139, 0.24)';
        ctx.lineWidth = 1.6;

        const step = (Math.PI * 2) / this.teeth;
        const toothDepth = this.radius * 0.18;
        const rOuter = this.radius + toothDepth;
        const rInner = this.radius - toothDepth * 0.3;

        ctx.beginPath();
        for (let i = 0; i < this.teeth; i++) {
          const a1 = i * step;
          const a2 = a1 + step * 0.25;
          const a3 = a1 + step * 0.55;
          const a4 = a1 + step * 0.8;

          const p1x = Math.cos(a1) * rInner;
          const p1y = Math.sin(a1) * rInner;
          const p2x = Math.cos(a2) * rOuter;
          const p2y = Math.sin(a2) * rOuter;
          const p3x = Math.cos(a3) * rOuter;
          const p3y = Math.sin(a3) * rOuter;
          const p4x = Math.cos(a4) * rInner;
          const p4y = Math.sin(a4) * rInner;

          if (i === 0) ctx.moveTo(p1x, p1y);
          else ctx.lineTo(p1x, p1y);
          ctx.lineTo(p2x, p2y);
          ctx.lineTo(p3x, p3y);
          ctx.lineTo(p4x, p4y);
        }
        ctx.closePath();
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(0, 0, this.radius * 0.65, 0, Math.PI * 2);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(0, 0, this.radius * 0.25, 0, Math.PI * 2);
        ctx.stroke();

        const spokeCount = 4;
        for (let s = 0; s < spokeCount; s++) {
          const sa = (s * Math.PI * 2) / spokeCount;
          ctx.beginPath();
          ctx.moveTo(Math.cos(sa) * this.radius * 0.25, Math.sin(sa) * this.radius * 0.25);
          ctx.lineTo(Math.cos(sa) * this.radius * 0.65, Math.sin(sa) * this.radius * 0.65);
          ctx.stroke();
        }

        ctx.restore();
      }
    }

    class EngineeringSymbol {
      constructor() {
        this.reset(true);
      }

      reset(initial = false) {
        this.type = Math.random() > 0.5 ? 'atom' : 'chip';
        this.x = Math.random() * width;
        this.y = initial ? Math.random() * height : height + 50;
        this.vx = (Math.random() - 0.5) * 0.25;
        this.vy = -(Math.random() * 0.25 + 0.12);
        this.size = Math.random() * 16 + 24;
        this.angle = 0;
        this.spin = (Math.random() - 0.5) * 0.012;
        this.alpha = Math.random() * 0.22 + 0.14;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.angle += this.spin;

        if (this.y < -60) {
          this.reset(false);
        }
      }

      draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        ctx.strokeStyle = 'rgba(229, 69, 25, 0.35)';
        ctx.lineWidth = 1.3;

        if (this.type === 'atom') {
          ctx.fillStyle = '#ea580c';
          ctx.beginPath();
          ctx.arc(0, 0, 3, 0, Math.PI * 2);
          ctx.fill();

          for (let e = 0; e < 3; e++) {
            ctx.save();
            ctx.rotate((e * Math.PI) / 3);
            ctx.beginPath();
            ctx.ellipse(0, 0, this.size * 0.6, this.size * 0.25, 0, 0, Math.PI * 2);
            ctx.stroke();
            ctx.restore();
          }
        } else {
          const s = this.size * 0.5;
          ctx.strokeRect(-s, -s, s * 2, s * 2);
          ctx.strokeRect(-s * 0.6, -s * 0.6, s * 1.2, s * 1.2);
          const pinLen = 5;
          for (let p = -s + 4; p <= s - 4; p += 7) {
            ctx.beginPath();
            ctx.moveTo(p, -s);
            ctx.lineTo(p, -s - pinLen);
            ctx.moveTo(p, s);
            ctx.lineTo(p, s + pinLen);
            ctx.moveTo(-s, p);
            ctx.lineTo(-s - pinLen, p);
            ctx.moveTo(s, p);
            ctx.lineTo(s + pinLen, p);
            ctx.stroke();
          }
        }

        ctx.restore();
      }
    }

    class CircuitNode {
      constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2 + 1;
        this.isOrange = Math.random() > 0.45;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > width) this.vx = -this.vx;
        if (this.y < 0 || this.y > height) this.vy = -this.vy;

        if (mouse.x !== null && mouse.y !== null) {
          const dx = mouse.x - this.x;
          const dy = mouse.y - this.y;
          const dist = Math.hypot(dx, dy);
          if (dist < mouse.radius) {
            const force = (mouse.radius - dist) / mouse.radius;
            this.x -= (dx / dist) * force * 2;
            this.y -= (dy / dist) * force * 2;
          }
        }
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.isOrange ? '#e54519' : '#94a3b8';
        ctx.globalAlpha = this.isOrange ? 0.75 : 0.45;
        ctx.fill();
      }
    }

    const formulas = Array.from({ length: 18 }, () => new FloatingFormula());
    const symbols = Array.from({ length: 7 }, () => new EngineeringSymbol());
    const nodes = Array.from({ length: Math.min(Math.floor(width / 24), 45) }, () => new CircuitNode());

    const gears = [
      new MechanicalGear(width * 0.1, height * 0.22, 68, 14, 0.003, true),
      new MechanicalGear(width * 0.1 + 105, height * 0.22 + 45, 45, 10, -0.0045, false),
      new MechanicalGear(width * 0.9, height * 0.38, 85, 18, -0.0025, true),
      new MechanicalGear(width * 0.88, height * 0.78, 60, 12, 0.0035, false),
      new MechanicalGear(width * 0.08, height * 0.82, 75, 16, -0.003, true)
    ];

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      gears[0].x = width * 0.1; gears[0].y = height * 0.22;
      gears[1].x = width * 0.1 + 105; gears[1].y = height * 0.22 + 45;
      gears[2].x = width * 0.9; gears[2].y = height * 0.38;
      gears[3].x = width * 0.88; gears[3].y = height * 0.78;
      gears[4].x = width * 0.08; gears[4].y = height * 0.82;
    };

    const handleMouseMove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    const handleMouseLeave = () => {
      mouse.x = null;
      mouse.y = null;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      gears.forEach((gear) => {
        gear.update();
        gear.draw();
      });

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.hypot(dx, dy);

          if (dist < 115) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);

            const alpha = (1 - dist / 115) * 0.2;
            ctx.strokeStyle = nodes[i].isOrange || nodes[j].isOrange 
              ? `rgba(229, 69, 25, ${alpha})` 
              : `rgba(148, 163, 184, ${alpha * 0.6})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      nodes.forEach((n) => {
        n.update();
        n.draw();
      });

      symbols.forEach((s) => {
        s.update();
        s.draw();
      });

      formulas.forEach((f) => {
        f.update();
        f.draw();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-0 opacity-85 max-w-full overflow-hidden"
    />
  );
}
