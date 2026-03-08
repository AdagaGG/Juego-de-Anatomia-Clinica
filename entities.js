export class ECGMonitor {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.offset = 0;
        this.points = [];
        this.color = '#00ff41'; // Primary Green
    }

    update(dt, bpm, isCodeBlue) {
        this.color = isCodeBlue ? '#ff0055' : '#00ff41';
        this.offset += 150 * dt; // Speed of wave

        if (this.offset > this.width) {
            this.offset = 0;
            this.points = [];
        }

        const centerY = this.height / 2;
        let y = centerY;

        // Cycle calculated based on bpm
        const cycleLength = 8000 / bpm;
        let cycle = (this.offset / cycleLength) % 1.0;

        if (cycle > 0.3 && cycle < 0.4) {
            const sp_phase = (cycle - 0.3) / 0.1;
            if (sp_phase < 0.33) y += 15;
            else if (sp_phase < 0.66) y -= 60;
            else y += 30;
        } else if (cycle > 0.5 && cycle < 0.6) {
            y -= Math.sin(((cycle - 0.5) / 0.1) * Math.PI) * 20;
        }

        // Noise
        y += (Math.random() * 4) - 2;

        this.points.push({ x: this.offset, y: y });
        // Keep points mapped to width boundaries
        this.points = this.points.filter(p => p.x > 0);
    }

    draw() {
        // Fade effect to simulate CRT persistence phosphor
        this.ctx.fillStyle = 'rgba(5, 5, 5, 0.1)';
        this.ctx.fillRect(0, 0, this.width, this.height);

        this.ctx.beginPath();
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = 3;
        this.ctx.shadowBlur = 10;
        this.ctx.shadowColor = this.color;

        for (let i = 0; i < this.points.length; i++) {
            const p = this.points[i];
            if (i === 0) {
                this.ctx.moveTo(p.x, p.y);
            } else {
                this.ctx.lineTo(p.x, p.y);
            }
        }
        this.ctx.stroke();
    }
}

export class KinematicEntity {
    constructor(domElement) {
        this.el = domElement;
        this.velX = 0;
        this.velY = 0;
        this.accX = 0;
        this.accY = 0;
        this.angularVel = 0;
        this.angle = 0;

        // Original positions
        const rect = this.el.getBoundingClientRect();
        this.x = 0; // We will use CSS transforms relative to their original steady state
        this.y = 0;

        // Save inline styles if necessary
        this.isActive = false;
    }

    triggerExplosion() {
        this.isActive = true;
        this.accY = 800 + Math.random() * 700; // Gravity
        this.velX = (Math.random() - 0.5) * 400; // Explosion horizontal
        this.angularVel = (Math.random() - 0.5) * 600; // Rotation speed
        this.el.style.position = 'relative';
        this.el.style.zIndex = '1000';
    }

    updatePhysics(dt) {
        if (!this.isActive) return;

        // Kinematics: s = v0*t + 0.5*a*t^2; v = v0 + at
        let ds_x = this.velX * dt + 0.5 * this.accX * (dt * dt);
        let ds_y = this.velY * dt + 0.5 * this.accY * (dt * dt);

        this.x += ds_x;
        this.y += ds_y;

        this.velX += this.accX * dt;
        this.velY += this.accY * dt;

        this.angle += this.angularVel * dt;

        this.el.style.transform = `translate(${this.x}px, ${this.y}px) rotate(${this.angle}deg)`;
    }

    reset() {
        this.isActive = false;
        this.x = 0;
        this.y = 0;
        this.velX = 0;
        this.velY = 0;
        this.accX = 0;
        this.accY = 0;
        this.angle = 0;
        this.angularVel = 0;
        this.el.style.transform = `translate(0px, 0px) rotate(0deg)`;
        this.el.style.position = '';
        this.el.style.zIndex = '';
    }
}
