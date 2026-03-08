import pygame
import random
from assets import Assets, Colors
from entities import Button, Entity, ECGMonitor, TimerBar

# Import Data Models
from database import base_de_datos

# Estados Globales
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAMEOVER = "GAMEOVER"

class Engine:
    def __init__(self, width=1280, height=800):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Monitor Vital OOP: Dra. Perfinka (CRT Edition)")
        self.clock = pygame.time.Clock()
        self.state = STATE_MENU
        self.running = True

        # Game Session Variables
        self.vidas = 3
        self.puntos = 0
        self.preguntas_restantes = []
        self.pregunta_actual = None
        self.es_codigo_azul = False
        self.bpm = 60
        self.tiempo_total = 20.0
        self.tiempo_restante = 20.0
        self.respuestas_concluidas = False
        self.pregunta_numero = 1
        
        # Audio Context
        self.is_audio_init = False
        self._init_sounds()
        
        # UI Entidades
        self.btn_start = Button(width//2 - 150, height//2 + 100, 300, 60, "INICIAR TURNO")
        self.btn_retry = Button(width//2 - 150, height//2 + 150, 300, 60, "NUEVO TURNO")
        self.btn_continue = Button(width - 240, height - 80, 200, 50, "CONTINUAR")
        
        # Monitor Componentes
        # Left Panel (ECG)
        self.ecg = ECGMonitor(40, 60, 800, 220)
        
        # Opciones AABB (4 Buttons) Bottom Area
        self.opciones_btns = []
        btn_w, btn_h = 550, 80
        start_x, start_y = (width - (btn_w*2 + 20)) // 2, 500
        
        for i, letter in enumerate(["A", "B", "C", "D"]):
            row, col = i // 2, i % 2
            x = start_x + (col * (btn_w + 20))
            y = start_y + (row * (btn_h + 20))
            btn = Button(x, y, btn_w, btn_h, f"Option {letter}", letter)
            self.opciones_btns.append(btn)

        # Physics
        self.falling_ui = []
        
        # Face State
        self.face_state = "neutral" # neutral, happy, angry
        self.speech_text = "Analizando paciente..."

        # Scanlines surface pre-calc
        self.scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 4):
            pygame.draw.line(self.scanline_surface, (0, 0, 0, 40), (0, y), (width, y), 2)
        
        # Vignette overlay
        self.vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # We can simulate a vignette using alpha shapes, but keeping it simple with a dark border
        pygame.draw.rect(self.vignette_surface, (0, 0, 0, 80), (0, 0, width, height), 20)

    def _init_sounds(self):
        try:
            pygame.mixer.init()
            self.is_audio_init = True
        except:
            print("Warning: Audio Mixer init failed. Running in silent mode.")

    def play_sound(self, stype):
        if not self.is_audio_init: return
        pass

    def start_game(self):
        self.vidas = 3
        self.puntos = 0
        self.bpm = 60
        self.pregunta_numero = 1
        pool = base_de_datos.copy()
        random.shuffle(pool)
        self.preguntas_restantes = pool[:5]
        
        self.falling_ui.clear()
        self.load_next_question()
        self.state = STATE_PLAYING

    def load_next_question(self):
        if not self.preguntas_restantes:
            self.trigger_gameover(victory=True)
            return

        self.pregunta_actual = self.preguntas_restantes.pop(0)
        self.respuestas_concluidas = False
        self.face_state = "neutral"
        self.speech_text = "Analizando paciente..."
        
        self.es_codigo_azul = self.pregunta_actual["es_codigo_azul"]
        
        if self.es_codigo_azul:
            self.tiempo_total = 5.0
            self.bpm = 140
        else:
            self.tiempo_total = 20.0
            self.bpm = 60
            
        self.tiempo_restante = self.tiempo_total
        
        self.pregunta_numero = min(5, self.pregunta_numero)
        
        # Popular Botones
        for idx, btn in enumerate(self.opciones_btns):
            raw_text = self.pregunta_actual["opciones"][idx]
            # Strip redundant A. B. C. D. prefixes
            if len(raw_text) > 3 and raw_text[0].isupper() and raw_text[1:3] in [". ", ") "]:
                raw_text = raw_text[3:]
            btn.text = raw_text
            btn.disabled = False
            btn.state_color = Colors.PRIMARY_GREEN

    def handle_answer(self, btn_index):
        if self.respuestas_concluidas: return
        
        self.respuestas_concluidas = True
        correcta = self.pregunta_actual["correcta"]
        
        for btn in self.opciones_btns:
            btn.disabled = True
            btn.state_color = Colors.GRAY
            
        btn_sel = self.opciones_btns[btn_index] if btn_index != -1 else None

        if btn_index == correcta:
            self.puntos += 10
            btn_sel.state_color = Colors.PRIMARY_GREEN
            self.play_sound("success")
            self.face_state = "happy"
            self.speech_text = "Correcto. No espere un premio."
        else:
            self.vidas -= 1
            if btn_sel: btn_sel.state_color = Colors.ALERT_RED
            self.opciones_btns[correcta].state_color = Colors.PRIMARY_GREEN
            self.play_sound("error")
            self.face_state = "angry"
            self.speech_text = "¡Patético! Siguiente."

            if self.vidas <= 0:
                self.trigger_gameover(victory=False)

    def trigger_gameover(self, victory):
        self.state = STATE_GAMEOVER
        self.play_sound("flatline" if not victory else "success")
        
        if not victory:
            # Physical Destruction of UI Elements
            for btn in self.opciones_btns:
                btn.acc_y = random.uniform(800, 1500)  # Gravedad 
                btn.vel_x = random.uniform(-200, 200) # Explosion horizontal
                btn.angular_vel = random.uniform(-5, 5)
                self.falling_ui.append(btn)

    def update(self, dt):
        if self.state == STATE_MENU:
            self.btn_start.update(dt)

        elif self.state == STATE_PLAYING:
            # ECG is always running
            self.ecg.color = Colors.ALERT_RED if self.es_codigo_azul else Colors.PRIMARY_GREEN
            self.ecg.update(dt, self.bpm)
            
            if not self.respuestas_concluidas:
                self.tiempo_restante -= dt
                if self.tiempo_restante <= 0:
                    self.handle_answer(-1) # Timeout
            
            for btn in self.opciones_btns:
                btn.update(dt)
                
            if self.respuestas_concluidas:
                self.btn_continue.update(dt)

        elif self.state == STATE_GAMEOVER:
            self.btn_retry.update(dt)
            for item in self.falling_ui:
                item.update_physics(dt)

    def draw_crt_effects(self):
        # Scanlines
        self.screen.blit(self.scanline_surface, (0,0))
        # Vignette
        self.screen.blit(self.vignette_surface, (0,0))
        # Flicker (Random brightness change)
        if random.random() > 0.95:
            flicker = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            flicker.fill((0, 0, 0, 10))
            self.screen.blit(flicker, (0,0))

    def draw(self):
        self.screen.fill(Colors.BG)
        font_title = Assets.get_font(42)
        font_main = Assets.get_font(24)
        font_small = Assets.get_font(18)
        font_doctor = Assets.get_font(20)

        # Draw Inner Frame Bounds (Monitor CRT)
        border_rect = pygame.Rect(10, 10, self.screen.get_width()-20, self.screen.get_height()-20)
        pygame.draw.rect(self.screen, Colors.MONITOR_FRAME, border_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 255, 65, 80), border_rect, 2, border_radius=12)
        
        # Monitor Topbar
        topbar_rect = pygame.Rect(10, 10, self.screen.get_width()-20, 36)
        pygame.draw.rect(self.screen, Colors.BG, topbar_rect, border_radius=12)
        pygame.draw.line(self.screen, (0, 255, 65, 80), (10, 46), (self.screen.get_width()-10, 46), 1)
        tb_text = font_small.render("MONITOR VITAL • DRA. PERFINKA", True, Colors.PRIMARY_GREEN)
        self.screen.blit(tb_text, (20, 18))

        if self.state == STATE_MENU:
            # Boot Overlay / Menu
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0, 200))
            self.screen.blit(overlay, (0,0))
            
            boot_panel = pygame.Rect(self.screen.get_width()//2 - 360, self.screen.get_height()//2 - 150, 720, 300)
            pygame.draw.rect(self.screen, (2,2,2), boot_panel, border_radius=8)
            pygame.draw.rect(self.screen, (0, 255, 65, 80), boot_panel, 2, border_radius=8)
            
            titulo = font_title.render("SISTEMA CRT EN LÍNEA", True, Colors.PRIMARY_GREEN)
            self.screen.blit(titulo, (boot_panel.centerx - titulo.get_width()//2, boot_panel.top + 40))
            
            self.btn_start.draw(self.screen)

        elif self.state == STATE_PLAYING or (self.state == STATE_GAMEOVER and not self.falling_ui):
            # ===== LEFT PANEL (ECG) ======
            # x: 40, y: 60, w: 800, h: 220
            self.ecg.draw(self.screen)
            
            # Tags under ECG
            freq_str = f"{self.bpm} bpm"
            estado_str = "CÓDIGO AZUL" if self.es_codigo_azul else "NORMAL"
            estado_color = Colors.ALERT_RED if self.es_codigo_azul else Colors.PRIMARY_GREEN
            
            f_txt = font_main.render(freq_str, True, Colors.PRIMARY_GREEN)
            self.screen.blit(f_txt, (40, 290))
            
            # Blink logic for codigo azul Tag
            draw_tag = True
            if self.es_codigo_azul and pygame.time.get_ticks() % 500 > 250:
                draw_tag = False
                
            if draw_tag:
                e_txt = font_main.render(estado_str, True, estado_color)
                self.screen.blit(e_txt, (700, 290))

            # ===== RIGHT PANEL ======
            # x: 860, y: 60, w: 380, h: 250
            rp_rect = pygame.Rect(860, 60, 380, 250)
            
            # Stats (Vidas, Puntos)
            t_vid = font_main.render(f"VIDAS: {self.vidas}", True, Colors.PRIMARY_GREEN)
            t_pts = font_main.render(f"PUNTOS: {self.puntos}", True, Colors.PRIMARY_GREEN)
            # Question Counter
            t_preg = font_main.render(f"PREGUNTA: {self.pregunta_numero}/5", True, Colors.PRIMARY_GREEN)
            
            self.screen.blit(t_vid, (860, 60))
            self.screen.blit(t_pts, (860, 90))
            self.screen.blit(t_preg, (860, 120))
            
            # Doctor Portrait
            face_img = Assets.get_image(f"doctor-{self.face_state}.png", (120, 120))
            # Background frame for face
            face_frame = pygame.Rect(860, 160, 120, 120)
            pygame.draw.rect(self.screen, (17,17,17), face_frame, border_radius=8)
            pygame.draw.rect(self.screen, Colors.PRIMARY_GREEN if self.face_state=="happy" else (Colors.ALERT_RED if self.face_state=="angry" else Colors.WHITE), face_frame, 2, border_radius=8)
            
            self.screen.blit(face_img, (860, 160))
            
            # Doctor Speech
            dialog_rect = pygame.Rect(1000, 180, 240, 100)
            Assets.render_text_wrapped(self.screen, self.speech_text, Colors.ALERT_RED, dialog_rect, font_doctor)


            # ===== GAME AREA (Bottom) ======
            ga_rect = pygame.Rect(40, 330, self.screen.get_width()-80, self.screen.get_height()-350)
            pygame.draw.rect(self.screen, (0,0,0, 200), ga_rect, border_radius=8)
            pygame.draw.rect(self.screen, Colors.PRIMARY_GREEN, ga_rect, 2, border_radius=8)
            
            # Question Box
            if self.pregunta_actual:
                q_box = pygame.Rect(60, 350, self.screen.get_width()-120, 120)
                pygame.draw.rect(self.screen, (0,255,65, 12), q_box, border_radius=5)
                # Left accent border
                pygame.draw.rect(self.screen, Colors.ALERT_RED, (60, 350, 4, 120), border_radius=2)
                
                Assets.render_text_wrapped(self.screen, self.pregunta_actual["pregunta"], Colors.PRIMARY_GREEN, q_box.inflate(-40, -40), font_main)

            # Botones
            for btn in self.opciones_btns:
                btn.draw(self.screen)
                
            # Controles bottom
            # Timer
            timer_y = 680
            timer_w = 400
            pygame.draw.rect(self.screen, (0,0,0, 120), (60, timer_y, timer_w, 20), border_radius=10)
            pygame.draw.rect(self.screen, (255,255,255, 10), (60, timer_y, timer_w, 20), 1, border_radius=10)
            
            ratio = max(0, self.tiempo_restante / self.tiempo_total)
            if ratio > 0:
                bar_color = Colors.PRIMARY_GREEN if ratio > 0.25 else Colors.ALERT_RED
                pygame.draw.rect(self.screen, bar_color, (60, timer_y, int(timer_w * ratio), 20), border_radius=10)
                
            t_timer = font_main.render(f"{int(self.tiempo_restante)}s", True, Colors.ALERT_RED)
            self.screen.blit(t_timer, (470, timer_y - 2))
            
            # Feedback
            if self.respuestas_concluidas:
                feedback_msg = self.pregunta_actual["feedback_acierto"] if (self.tiempo_restante>0 and self.vidas>0 and self.face_state=="happy") else self.pregunta_actual["feedback_error"]
                fb_color = Colors.PRIMARY_GREEN if (self.vidas>0 and self.face_state == "happy") else Colors.ALERT_RED
                t_fb = font_doctor.render(feedback_msg, True, fb_color)
                # Position over the continue button
                self.screen.blit(t_fb, (550, timer_y - 2))
                self.btn_continue.draw(self.screen)

        if self.state == STATE_GAMEOVER:
            # Oscurecemos la pantalla actual sutilmente si es game over con animacion
            if self.falling_ui:
                # We need to render the background once to let items fall over it. We'll just dim it constantly.
                pass
            
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200) if not self.falling_ui else (0,0,0,240))
            self.screen.blit(overlay, (0,0))
            
            for item in self.falling_ui:
                item.draw(self.screen)

            # Memo Card
            card = pygame.Rect(self.screen.get_width()//2 - 320, 200, 640, 300)
            pygame.draw.rect(self.screen, (13,13,8), card, border_radius=6)
            pygame.draw.rect(self.screen, (255,255,255,8), card, 2, border_radius=6)
            
            if self.vidas <= 0:
                # Expulsado
                t_fin = "MEMORÁNDUM DE EXPULSIÓN"
                render_fin = font_title.render(t_fin, True, Colors.PRIMARY_GREEN) # The CSS uses primary green for memo text generally
                self.screen.blit(render_fin, (card.centerx - render_fin.get_width()//2, 230))
                
                c1 = font_main.render("Causa: Incompetencia Anatómica.", True, Colors.PRIMARY_GREEN)
                c2 = font_main.render("Detalle: Incapacidad para identificar estructuras críticas.", True, Colors.PRIMARY_GREEN)
                # Signature
                c3 = font_main.render("Firma: Dra. Perfinka", True, Colors.PRIMARY_GREEN)
                
                self.screen.blit(c1, (card.x + 40, 300))
                self.screen.blit(c2, (card.x + 40, 340))
                self.screen.blit(c3, (card.right - c3.get_width() - 40, 420))
                
            else:
                # Aprobado
                t_fin = "CERTIFICADO DE APROBACIÓN"
                render_fin = font_title.render(t_fin, True, Colors.PRIMARY_GREEN)
                self.screen.blit(render_fin, (card.centerx - render_fin.get_width()//2, 230))
                
                c1 = font_main.render("Resultado: Turno completado sin víctimas mortales.", True, Colors.PRIMARY_GREEN)
                c2 = font_main.render(f"Desempeño: Aceptable.      Puntuación Final: {self.puntos}", True, Colors.PRIMARY_GREEN)
                
                self.screen.blit(c1, (card.x + 40, 300))
                self.screen.blit(c2, (card.x + 40, 340))

            self.btn_retry.draw(self.screen)

        # Apply post-processing CRT ALWAYS
        self.draw_crt_effects()
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == STATE_MENU and self.btn_start.is_hovered:
                    self.start_game()
                elif self.state == STATE_PLAYING and self.respuestas_concluidas and self.btn_continue.is_hovered:
                    self.pregunta_numero += 1
                    self.load_next_question()
                elif self.state == STATE_PLAYING and not self.respuestas_concluidas:
                    for i, btn in enumerate(self.opciones_btns):
                        if btn.is_hovered:
                            self.handle_answer(i)
                elif self.state == STATE_GAMEOVER and self.btn_retry.is_hovered:
                    self.start_game()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            if dt > 0.1: dt = 0.1
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
