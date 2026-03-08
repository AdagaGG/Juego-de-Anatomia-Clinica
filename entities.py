import pygame
import math
from assets import Assets, Colors

class Entity:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        # Cinematic Variables
        self.vel_x = 0
        self.vel_y = 0
        self.acc_x = 0
        self.acc_y = 0
        self.angular_vel = 0
        self.angle = 0

    def update_physics(self, dt):
        """
        Integración Cinemática Estricta:
        v = v_0 + a * t
        s = s_0 + v_0 * t + 0.5 * a * t^2 
        """
        # Desplazamiento
        ds_x = self.vel_x * dt + 0.5 * self.acc_x * (dt ** 2)
        ds_y = self.vel_y * dt + 0.5 * self.acc_y * (dt ** 2)
        
        self.rect.x += ds_x
        self.rect.y += ds_y
        
        # Nueva Velocidad
        self.vel_x += self.acc_x * dt
        self.vel_y += self.acc_y * dt
        
        # Rotación
        self.angle += self.angular_vel * dt

    def collides_aabb(self, x, y):
        return self.rect.collidepoint(x, y)

class Button(Entity):
    def __init__(self, x, y, width, height, text, letter=""):
        super().__init__(x, y, width, height)
        self.text = text
        self.letter = letter
        self.is_hovered = False
        self.disabled = False
        self.state_color = Colors.PRIMARY_GREEN # Default green
        self.bg_color = Colors.BG

    def update(self, dt):
        if not self.disabled:
            mouse_pos = pygame.mouse.get_pos()
            self.is_hovered = self.collides_aabb(*mouse_pos)
            self.bg_color = Colors.DARK_GREEN if self.is_hovered else Colors.BG

    def draw(self, surface):
        # Apply transforms if falling (physics)
        if self.angle != 0:
            # We'd use a temporary surface to rotate, but for optimization we just draw rects.
            pass 

        # Draw Base
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.state_color, self.rect, 2, border_radius=4)
        
        # Draw text
        font = Assets.get_font(16)
        letter_font = Assets.get_font(20)
        
        text_rect = self.rect.copy()
        
        if self.letter:
            let_surf = letter_font.render(self.letter, True, self.state_color)
            surface.blit(let_surf, (self.rect.x + 10, self.rect.y + 15))
            text_rect.x += 40
            text_rect.width -= 40
        
        text_rect.y += 10
        text_rect.height -= 10
        Assets.render_text_wrapped(surface, self.text, self.state_color, text_rect, font)

class TimerBar:
    def __init__(self, x, y, width, height, total_time):
        self.rect = pygame.Rect(x, y, width, height)
        self.total_time = total_time
        self.time_left = total_time
        self.is_critical = False

    def get_ratio(self):
        return max(0.0, self.time_left / self.total_time)

    def draw(self, surface):
        ratio = self.get_ratio()
        fill_width = int(self.rect.width * ratio)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        
        color = Colors.ALERT_RED if self.is_critical or ratio < 0.25 else Colors.PRIMARY_GREEN
        
        pygame.draw.rect(surface, Colors.DARK_GREEN, self.rect)
        if fill_width > 0:
            pygame.draw.rect(surface, color, fill_rect)
        pygame.draw.rect(surface, Colors.WHITE, self.rect, 1)

class ECGMonitor:
    """ Genera el trazado en vivo del Electrocardiograma usando splines matemáticos procedimentales """
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.offset = 0
        self.points = []
        self.color = Colors.PRIMARY_GREEN
        
    def update(self, dt, bpm):
        self.offset += 150 * dt  # Speed of wave
        if self.offset > self.rect.width:
            self.offset = 0
            self.points.clear()
            
        # Generar "onda"
        center_y = self.rect.centery
        local_x = self.offset
        
        # Simplified math wave for heartbeat
        y = center_y
        cycle = (self.offset / (8000/bpm)) % 1.0
        
        if 0.3 < cycle < 0.4:  # QRS Spikes
            sp_phase = (cycle - 0.3) / 0.1
            if sp_phase < 0.33: y += 10
            elif sp_phase < 0.66: y -= 40
            else: y += 20
        elif 0.5 < cycle < 0.6: # T wave
            y -= math.sin((cycle - 0.5) / 0.1 * math.pi) * 15
            
        y += (pygame.time.get_ticks() % 3) - 1 # Noise
        
        self.points.append((self.rect.x + local_x, y))
        
        # Keep points mapped to width boundaries (fade out old)
        self.points = [p for p in self.points if p[0] > self.rect.x]

    def draw(self, surface):
        pygame.draw.rect(surface, (10, 20, 10), self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 1)
        
        if len(self.points) > 1:
            pygame.draw.lines(surface, self.color, False, self.points, 2)
