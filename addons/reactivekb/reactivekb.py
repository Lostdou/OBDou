import sys
import os
import pygame
import pyautogui
import keyboard
import pyaudio
import sounddevice as sd
import array
import math

from app_paths import get_base_dir


class VTuberAvatar:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Avatar")
        self.clock = pygame.time.Clock()
        self.chroma_color = (0, 255, 0)
        self.running = True

        self.show_mouse = "no-mouse" not in sys.argv
        self.simple_kb = "simple-kb" in sys.argv
        self.speak_head = "speak-head" in sys.argv

        self.is_speaking = False
        self.mouse_pos = (960, 540)

        self._cargar_assets()

        if self.speak_head:
            self._iniciar_microfono()

    def _cargar_assets(self):
        assets_dir = os.path.join(get_base_dir(), "assets", "reactivekb")

        def load_img(filename):
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                return pygame.image.load(path).convert_alpha()
            surf = pygame.Surface((300, 300), pygame.SRCALPHA)
            surf.fill((255, 0, 255, 128))
            return surf

        self.body = load_img("mainchar.png")
        self.head_speak_img = load_img("headspeak.png")
        self.mouse_paw = load_img("mouse.png")

        self.kb_idle = load_img("keyboard.png")

        self.kb_down = load_img("keyboard+middle.png")

        self.kb_left = load_img("keyboard+left.png")
        self.kb_right = load_img("keyboard+right.png")
        self.kb_both = load_img("keyboard+spacebar.png")

        self.current_kb = self.kb_idle

    def _iniciar_microfono(self):
        """Inicializa PyAudio para detectar la voz del usuario."""
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            self.audio_threshold = 200
        except Exception as e:
            print(f"No se pudo iniciar el micrófono: {e}")
            self.speak_head = False

    def update(self):
        if self.speak_head and hasattr(self, 'stream'):
            try:
                data = self.stream.read(1024, exception_on_overflow=False)

                samples = array.array('h', data)

                sum_squares = sum(s * s for s in samples)
                rms = math.sqrt(sum_squares / len(samples))

                self.is_speaking = rms > self.audio_threshold
            except Exception:
                self.is_speaking = False

        try:
            if self.simple_kb:
                all_keys = [
                    'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                    'z', 'x', 'c', 'v', 'b', 'n', 'm',
                    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                    'space', 'enter', 'shift', 'ctrl', 'alt', 'tab',
                    'up', 'down', 'left', 'right', 'esc', 'backspace'
                ]
                is_pressed = any(keyboard.is_pressed(k) for k in all_keys)
                self.current_kb = self.kb_down if is_pressed else self.kb_idle
            else:
                left_pressed = any(keyboard.is_pressed(k) for k in ['w', 'a', 's', 'd', 'q', 'e', 'shift'])
                right_pressed = any(keyboard.is_pressed(k) for k in ['up', 'down', 'left', 'right', 'enter', 'space', 'm'])

                if left_pressed and right_pressed:
                    self.current_kb = self.kb_both
                elif left_pressed:
                    self.current_kb = self.kb_left
                elif right_pressed:
                    self.current_kb = self.kb_right
                else:
                    self.current_kb = self.kb_idle
        except Exception:
            pass

    def draw(self):
        self.screen.fill(self.chroma_color)

        self.screen.blit(self.body, (280, 80))

        if self.speak_head and self.is_speaking:
            self.screen.blit(self.head_speak_img, (276, 65))

        if self.show_mouse:
            offset_x = ((1920.0 - self.mouse_pos[0]) / 1920.0) * 40
            offset_y = (self.mouse_pos[1] / 1080.0) * 30
            base_mouse_x = 80
            base_mouse_y = 200
            self.screen.blit(self.mouse_paw, (base_mouse_x + offset_x, base_mouse_y + offset_y))

        self.screen.blit(self.current_kb, (212, 200))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update()
            self.draw()
            self.clock.tick(60)

        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        pygame.quit()


def main():
    if "--run-avatar" in sys.argv:
        app = VTuberAvatar()
        app.run()
    else:
        print("Este script no debe ejecutarse solo. Iniciá OBDou y abrí el avatar desde la interfaz.")


if __name__ == "__main__":
    main()