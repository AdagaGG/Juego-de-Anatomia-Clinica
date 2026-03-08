import pygame
import os
import time

def auto_test():
    from engine import Engine
    
    # Enable a simulated environment
    os.environ['SDL_VIDEODRIVER'] = 'dummy' # In case NO X/display, but windows handles it fine. Let's not use dummy unless needed.
    
    eng = Engine(1280, 800)
    
    print("Capturing Menu State...")
    eng.update(0.1)
    eng.draw()
    pygame.image.save(eng.screen, "c:\\Users\\adria\\.gemini\\antigravity\\brain\\725f37bc-a9ba-4985-a6b3-a81a8a7c934d\\screen_menu.jpg")
    
    print("Capturing Playing Question State...")
    eng.start_game()
    # Mock some dt to skip transition
    eng.update(0.1)
    eng.draw()
    pygame.image.save(eng.screen, "c:\\Users\\adria\\.gemini\\antigravity\\brain\\725f37bc-a9ba-4985-a6b3-a81a8a7c934d\\screen_playing.jpg")
    
    print("Capturing Verified Answer State...")
    eng.handle_answer(eng.pregunta_actual["correcta"])
    eng.update(0.1)
    eng.draw()
    pygame.image.save(eng.screen, "c:\\Users\\adria\\.gemini\\antigravity\\brain\\725f37bc-a9ba-4985-a6b3-a81a8a7c934d\\screen_answer.jpg")
    
    print("Capturing Explosive Game Over State...")
    eng.vidas = 1
    eng.handle_answer((eng.pregunta_actual["correcta"] + 1) % 4) # trigger wrong answer -> game over
    eng.update(0.5) # Simulate 0.5s of physics fall
    eng.draw()
    pygame.image.save(eng.screen, "c:\\Users\\adria\\.gemini\\antigravity\\brain\\725f37bc-a9ba-4985-a6b3-a81a8a7c934d\\screen_gameover.jpg")
    
if __name__ == '__main__':
    auto_test()
