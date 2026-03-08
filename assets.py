import pygame

class Colors:
    BG = (5, 5, 5)
    MONITOR_FRAME = (7, 7, 7)
    PRIMARY_GREEN = (0, 255, 65)
    DARK_GREEN = (0, 100, 20)
    ALERT_RED = (255, 0, 85)
    DARK_RED = (100, 0, 20)
    WHITE = (255, 255, 255)
    GRAY = (150, 150, 150)

class Assets:
    _images = {}
    _fonts = {}

    @classmethod
    def get_image(cls, path, size=(100, 100), fallback_color=Colors.DARK_GREEN, border_color=Colors.PRIMARY_GREEN):
        """ Procedural fallback rendering to ensure execution despite missing files """
        key = f"{path}_{size[0]}x{size[1]}"
        if key not in cls._images:
            try:
                img = pygame.image.load(path).convert_alpha()
                cls._images[key] = pygame.transform.scale(img, size)
            except (pygame.error, FileNotFoundError):
                # Generación procedural
                surface = pygame.Surface(size)
                surface.fill(fallback_color)
                pygame.draw.rect(surface, border_color, surface.get_rect(), 3)
                
                # Draw a generic face/icon pattern
                pygame.draw.circle(surface, border_color, (size[0]//2, size[1]//2 - 10), 10) # head
                pygame.draw.arc(surface, border_color, (size[0]//2 - 15, size[1]//2 + 5, 30, 20), 0, 3.14, 2) # body line
                
                cls._images[key] = surface
        return cls._images[key]

    @classmethod
    def get_font(cls, size=24):
        if size not in cls._fonts:
            if not pygame.font.get_init():
                pygame.font.init()
            # Try to load a generic monospace, fallback to standard sysfont
            cls._fonts[size] = pygame.font.SysFont('Courier New', size, bold=True)
        return cls._fonts[size]

    @classmethod
    def render_text_wrapped(cls, surface, text, color, rect, font, aa=True):
        """ Draws wrapped text inside a bounding box """
        rect = pygame.Rect(rect)
        y = rect.top
        lineSpacing = -2
        fontHeight = font.size("Tg")[1]

        words = text.split(' ')
        while words:
            line_words = []
            while words and font.size(' '.join(line_words + [words[0]]))[0] < rect.width:
                line_words.append(words.pop(0))
            
            line_text = ' '.join(line_words)
            if not line_text: 
                line_text = words.pop(0) # Word too long

            text_surface = font.render(line_text, aa, color)
            surface.blit(text_surface, (rect.left, y))
            y += fontHeight + lineSpacing
            if y >= rect.bottom:
                break
