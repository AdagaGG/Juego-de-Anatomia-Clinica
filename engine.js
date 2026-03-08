import { ECGMonitor, KinematicEntity } from './entities.js';
import { baseDeDatos } from './database.js';

export class Engine {
    constructor() {
        this.state = 'MENU'; // MENU, PLAYING, GAMEOVER

        this.vidas = 3;
        this.puntos = 0;
        this.preguntaActualData = null;
        this.preguntasRestantes = [];
        this.esCodigoAzul = false;
        this.bpm = 60;
        this.tiempoTotal = 20.0;
        this.tiempoRestante = 20.0;
        this.respuestasConcluidas = false;
        this.preguntaNumero = 1;

        // DOM Nodes
        this.ui = {
            bootOverlay: document.getElementById('bootOverlay'),
            startBtn: document.getElementById('startBtn'),
            monitorFrame: document.getElementById('monitorFrame'),
            memoOverlay: document.getElementById('memoOverlay'),
            retryBtn: document.getElementById('retryBtn'),
            vidas: document.getElementById('vidas'),
            puntos: document.getElementById('puntuacion'),
            preguntaActual: document.getElementById('preguntaActual'),
            frequencia: document.getElementById('frequencia'),
            estadoTag: document.getElementById('estadoTag'),
            pregunta: document.getElementById('pregunta'),
            options: document.querySelectorAll('.opt'),
            timerFill: document.getElementById('timerFill'),
            timerText: document.getElementById('timerText'),
            feedback: document.getElementById('feedback'),
            continueBtn: document.getElementById('continueBtn'),
            doctorFace: document.querySelector('.doctor-portrait .face'),
            speechText: document.getElementById('speechText'),
            gameArea: document.querySelector('.game-area'),
            questionBox: document.querySelector('.question-box'),
            controlsArea: document.querySelector('.controls')
        };

        // Entities
        this.ecg = new ECGMonitor('ecgCanvas');
        this.kinematicButtons = Array.from(this.ui.options).map(btn => new KinematicEntity(btn));

        this.lastTime = performance.now();
        this.running = false;

        this.bindEvents();
    }

    bindEvents() {
        this.ui.startBtn.addEventListener('click', () => this.startGame());
        this.ui.retryBtn.addEventListener('click', () => this.startGame());
        this.ui.continueBtn.addEventListener('click', () => this.loadNextQuestion());

        this.ui.options.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!this.respuestasConcluidas) {
                    const idx = parseInt(btn.getAttribute('data-index'));
                    this.handleAnswer(idx);
                }
            });
        });
    }

    playSound(type) {
        if (!this.audioCtx) return;
        if (this.audioCtx.state === 'suspended') this.audioCtx.resume();

        const osc = this.audioCtx.createOscillator();
        const gainNode = this.audioCtx.createGain();
        osc.connect(gainNode);
        gainNode.connect(this.audioCtx.destination);

        const now = this.audioCtx.currentTime;

        if (type === 'success') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(600, now);
            osc.frequency.exponentialRampToValueAtTime(1200, now + 0.1);
            gainNode.gain.setValueAtTime(0.1, now);
            gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
            osc.start(now);
            osc.stop(now + 0.2);
        } else if (type === 'error') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(150, now);
            osc.frequency.exponentialRampToValueAtTime(100, now + 0.3);
            gainNode.gain.setValueAtTime(0.1, now);
            gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
            osc.start(now);
            osc.stop(now + 0.3);
        } else if (type === 'flatline') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(400, now);
            gainNode.gain.setValueAtTime(0.1, now);
            gainNode.gain.linearRampToValueAtTime(0.1, now + 2.5);
            gainNode.gain.linearRampToValueAtTime(0.01, now + 3.0);
            osc.start(now);
            osc.stop(now + 3.0);
        } else if (type === 'tick') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(800, now);
            gainNode.gain.setValueAtTime(0.05, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
            osc.start(now);
            osc.stop(now + 0.05);
        }
    }

    initBackgroundAudio() {
        if (!this.audioCtx) return;
        if (this.audioPlaying) return; // already init
        this.audioPlaying = true;

        // Aquatic 8-bit Arpeggiator (Gameboy Style)
        this.musicGain = this.audioCtx.createGain();
        this.musicGain.gain.value = 0.08;

        // Delay node for the "Aquatic/Ethereal" reflection
        this.echoDelay = this.audioCtx.createDelay();
        this.echoDelay.delayTime.value = 0.33; // 330ms delay
        this.echoFeedback = this.audioCtx.createGain();
        this.echoFeedback.gain.value = 0.4; // Feedback amount

        this.echoDelay.connect(this.echoFeedback);
        this.echoFeedback.connect(this.echoDelay);
        this.echoDelay.connect(this.musicGain);
        this.musicGain.connect(this.audioCtx.destination);

        // Medical/Calm Chords arpeggiated
        const seq1 = [60, 64, 67, 71, 74, 71, 67, 64]; // Cmaj9
        const seq2 = [56, 60, 63, 68, 72, 68, 63, 60]; // Abmaj7
        const seq3 = [53, 56, 60, 63, 67, 63, 60, 56]; // Fmin9
        const sequences = [seq1, seq1, seq2, seq3];

        let noteIdx = 0;
        let seqIdx = 0;

        const playNote = () => {
            if (this.state === 'GAMEOVER') {
                this.audioPlaying = false;
                return;
            }

            let currentSeq = sequences[seqIdx];
            let note = currentSeq[noteIdx];

            // If Code Blue, shift down a semitone to create tension and instability
            if (this.esCodigoAzul) note -= 1;

            let freq = 440 * Math.pow(2, (note - 69) / 12);

            let osc = this.audioCtx.createOscillator();
            let gain = this.audioCtx.createGain();

            // Gameboy Chip sound
            osc.type = 'square';
            osc.frequency.value = freq;

            osc.connect(gain);
            gain.connect(this.musicGain);
            gain.connect(this.echoDelay); // route to echo

            let now = this.audioCtx.currentTime;
            gain.gain.setValueAtTime(0, now);
            gain.gain.linearRampToValueAtTime(this.esCodigoAzul ? 0.06 : 0.04, now + 0.05);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

            osc.start(now);
            osc.stop(now + 0.4);

            noteIdx++;
            if (noteIdx >= currentSeq.length) {
                noteIdx = 0;
                seqIdx = (seqIdx + 1) % sequences.length;
            }

            // Faster tempo during Code Blue
            let tempo = this.esCodigoAzul ? 150 : 250;
            this.musicTimer = setTimeout(playNote, tempo);
        };

        playNote();

        // Heartbeat Sub Bass (Medical motif kept)
        this.beatOsc = this.audioCtx.createOscillator();
        this.beatGain = this.audioCtx.createGain();
        this.beatOsc.type = 'triangle';
        this.beatOsc.frequency.value = 45; // Sub bass kick
        this.beatGain.gain.value = 0; // Modulated in update() using ECG phase
        this.beatOsc.connect(this.beatGain);
        this.beatGain.connect(this.audioCtx.destination);
        this.beatOsc.start();
    }

    startLoop() {
        if (!this.running) {
            this.running = true;
            this.lastTime = performance.now();
            requestAnimationFrame((time) => this.loop(time));
        }
    }

    loop(time) {
        let dt = (time - this.lastTime) / 1000.0;
        this.lastTime = time;

        if (Math.abs(dt) > 0.1) dt = 0.1; // Cap dt

        this.update(dt);
        this.draw();

        if (this.running) {
            requestAnimationFrame((t) => this.loop(t));
        }
    }

    update(dt) {
        if (this.state === 'PLAYING') {
            this.ecg.update(dt, this.bpm, this.esCodigoAzul);

            if (!this.respuestasConcluidas) {
                let lastSec = Math.ceil(this.tiempoRestante);
                this.tiempoRestante -= dt;
                let currentSec = Math.ceil(this.tiempoRestante);

                // Audio beep mapping
                if (this.esCodigoAzul && this.tiempoRestante < 6 && currentSec < lastSec) {
                    this.playSound('tick');
                }

                if (this.tiempoRestante <= 0 && lastSec > 0) {
                    this.handleAnswer(-1);
                }
            }

            // Procedural Psychological Audio Modulation
            if (this.audioCtx) {
                // Heartbeat Pulse Modulation locked to ECG visual phase!
                const cycleLength = 8000 / this.bpm;
                let cycle = (this.ecg.offset / cycleLength) % 1.0;

                let beatVol = 0;
                if (cycle > 0.28 && cycle < 0.35) beatVol = 0.15; // First thump
                if (cycle > 0.48 && cycle < 0.55) beatVol = 0.10; // Second thump

                if (this.beatGain && this.beatGain.gain) {
                    this.beatGain.gain.setTargetAtTime(beatVol, this.audioCtx.currentTime, 0.01);
                }
            }
        } else if (this.state === 'GAMEOVER') {
            this.kinematicButtons.forEach(kb => kb.updatePhysics(dt));
        }
    }

    draw() {
        if (this.state === 'PLAYING') {
            this.ecg.draw();

            // UI Updates
            this.ui.frequencia.innerText = `${this.bpm} bpm`;
            if (this.esCodigoAzul) {
                this.ui.estadoTag.innerText = "CÓDIGO AZUL";
                this.ui.estadoTag.className = "estado alert";
                // Flicker
                this.ui.estadoTag.style.opacity = (Math.floor(Date.now() / 200) % 2 === 0) ? '1' : '0.2';
                this.ui.monitorFrame.style.borderColor = "#ff0055";
            } else {
                this.ui.estadoTag.innerText = "NORMAL";
                this.ui.estadoTag.className = "estado normal";
                this.ui.estadoTag.style.opacity = '1';
                this.ui.monitorFrame.style.borderColor = "#00ff41";
            }

            const ratio = Math.max(0, this.tiempoRestante / this.tiempoTotal);
            this.ui.timerFill.style.width = `${ratio * 100}%`;
            this.ui.timerText.innerText = `${Math.ceil(this.tiempoRestante)}s`;

            if (ratio < 0.25 || this.esCodigoAzul) {
                this.ui.timerFill.style.backgroundColor = '#ff0055';
                this.ui.timerText.style.color = '#ff0055';
            } else {
                this.ui.timerFill.style.backgroundColor = '#00ff41';
                this.ui.timerText.style.color = '#00ff41';
            }
        }
    }

    setDoctorState(face, text) {
        this.ui.doctorFace.className = `face ${face}`;
        this.ui.speechText.innerText = text;
        this.ui.speechText.style.color = face === 'angry' ? '#ff0055' : '#00ff41';
    }

    startGame() {
        // Initialize AudioContext on first intentional click (Start button)
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            this.initBackgroundAudio();
        } else if (this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }

        // Check if music dropped and restart 
        if (!this.audioPlaying && this.audioCtx) {
            this.initBackgroundAudio();
        }

        this.vidas = 3;
        this.puntos = 0;
        this.preguntaNumero = 1;

        let pool = [...baseDeDatos];
        pool.sort(() => Math.random() - 0.5);
        this.preguntasRestantes = pool.slice(0, 15);

        this.ui.bootOverlay.style.display = 'none';
        this.ui.memoOverlay.style.display = 'none';
        this.ui.gameArea.style.opacity = '1';
        this.ui.questionBox.style.opacity = '1';
        this.ui.controlsArea.style.opacity = '1';

        this.kinematicButtons.forEach(kb => kb.reset());

        this.state = 'PLAYING';
        this.startLoop();
        this.loadNextQuestion();
    }

    loadNextQuestion() {
        if (this.preguntasRestantes.length === 0) {
            this.triggerGameover(true);
            return;
        }

        this.preguntaActualData = this.preguntasRestantes.shift();
        this.respuestasConcluidas = false;

        this.setDoctorState('neutral', 'Analizando paciente...');
        this.ui.continueBtn.style.display = 'none';
        this.ui.feedback.innerText = '';

        this.esCodigoAzul = this.preguntaActualData.es_codigo_azul;
        this.tiempoTotal = this.esCodigoAzul ? 5.0 : 20.0;
        this.tiempoRestante = this.tiempoTotal;
        this.bpm = this.esCodigoAzul ? 140 : 60;

        this.ui.vidas.innerText = this.vidas;
        this.ui.puntos.innerText = this.puntos;
        this.ui.preguntaActual.innerText = `${this.preguntaNumero}/15`;

        this.ui.pregunta.innerText = this.preguntaActualData.pregunta;

        this.ui.options.forEach((btn, idx) => {
            let rawText = this.preguntaActualData.opciones[idx];
            if (rawText.length > 3 && rawText[0] === rawText[0].toUpperCase() && (rawText.substr(1, 2) === '. ' || rawText.substr(1, 2) === ') ')) {
                rawText = rawText.substr(3);
            }
            btn.querySelector('.txt').innerText = rawText;
            btn.className = 'opt'; // Reset class
            btn.disabled = false;
        });
    }

    handleAnswer(idx) {
        if (this.respuestasConcluidas) return;
        this.respuestasConcluidas = true;

        const correcta = this.preguntaActualData.correcta;

        this.ui.options.forEach(btn => {
            btn.disabled = true;
            btn.classList.add('disabled');
        });

        const btnSel = idx !== -1 ? this.ui.options[idx] : null;

        if (idx === correcta) {
            this.playSound('success');
            this.puntos += 10;
            this.ui.puntos.innerText = this.puntos;
            btnSel.classList.add('correct');
            this.setDoctorState('happy', 'Correcto. Mantenlo vivo.');
            this.ui.feedback.innerText = this.preguntaActualData.feedback_acierto;
            this.ui.feedback.style.color = '#00ff41';
        } else {
            this.playSound('error');
            this.vidas -= 1;
            this.ui.vidas.innerText = this.vidas;
            if (btnSel) btnSel.classList.add('wrong');
            this.ui.options[correcta].classList.add('correct');
            this.setDoctorState('angry', '¡Incompetente! Estás matando al paciente.');
            this.ui.feedback.innerText = this.preguntaActualData.feedback_error;
            this.ui.feedback.style.color = '#ff0055';

            if (this.vidas <= 0) {
                setTimeout(() => this.triggerGameover(false), 1500); // Wait a bit to show feedback before blowing up
                return; // Early return to not show continue button
            }
        }

        this.ui.continueBtn.style.display = 'block';
    }

    triggerGameover(victory) {
        this.state = 'GAMEOVER';
        this.ui.continueBtn.style.display = 'none';

        // Kill ambient psychology
        if (this.beatGain) this.beatGain.gain.setTargetAtTime(0, this.audioCtx.currentTime, 0.1);
        clearTimeout(this.musicTimer);
        this.audioPlaying = false;

        if (!victory) {
            this.playSound('flatline');
            this.setDoctorState('angry', 'ESTÁS DESPEDIDO. LARGATE.');
            this.ui.questionBox.style.opacity = '0';
            this.ui.controlsArea.style.opacity = '0';

            // Trigger UI physics
            this.kinematicButtons.forEach(kb => kb.triggerExplosion());

            setTimeout(() => {
                this.ui.memoOverlay.style.display = 'flex';
                this.ui.memoOverlay.querySelector('h2').innerText = 'MEMORÁNDUM DE EXPULSIÓN';
                this.ui.memoOverlay.querySelector('p:nth-of-type(1)').innerHTML = `<strong>Causa:</strong> Incompetencia Anatómica.`;
                this.ui.memoOverlay.querySelector('p:nth-of-type(2)').innerHTML = `<strong>Detalle:</strong> Paciente fallecido bajo su cargo.`;
                this.ui.memoOverlay.style.border = "3px solid #ff0055";
                document.querySelector('.memo-card').style.border = "3px solid #ff0055";
                document.querySelector('.memo-card h2').style.color = "#ff0055";
            }, 3000);
        } else {
            this.setDoctorState('happy', 'Turno completado.');
            this.ui.memoOverlay.style.display = 'flex';
            this.ui.memoOverlay.querySelector('h2').innerText = 'CERTIFICADO DE APROBACIÓN';
            this.ui.memoOverlay.querySelector('p:nth-of-type(1)').innerHTML = `<strong>Resultado:</strong> Sobrevivió el turno.`;
            this.ui.memoOverlay.querySelector('p:nth-of-type(2)').innerHTML = `<strong>Puntuación:</strong> ${this.puntos}`;
            document.querySelector('.memo-card').style.border = "3px solid #00ff41";
            document.querySelector('.memo-card h2').style.color = "#00ff41";
        }
    }
}
