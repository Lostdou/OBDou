import socket
import threading
import queue
import re
import io
import time
from gtts import gTTS
import pygame

class TTSBot:
    def __init__(self, channel, comando="!s", idioma="es"):
        self.channel = channel
        self.comando = comando
        self.idioma = idioma
        self.tts_queue = queue.Queue()
        self.is_running = False
        self.sock = None

    def limpiar_mensaje(self, mensaje):
        mensaje = re.sub(r'http[s]?://\S+', '', mensaje)
        mensaje = re.sub(r'www\.\S+', '', mensaje)
        mensaje = re.sub(r'(.)\1{3,}', r'\1\1', mensaje)
        mensaje = re.sub(r'[^\w\s.,!?áéíóúÁÉÍÓÚñÑ]', '', mensaje)
        return mensaje.strip()

    def tts_worker(self):
        pygame.mixer.init()
        while self.is_running:
            try:
                text = self.tts_queue.get(timeout=1)
            except queue.Empty:
                continue
                
            try:
                tts = gTTS(text=text, lang=self.idioma)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                pygame.mixer.music.load(fp)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy() and self.is_running:
                    time.sleep(0.1)
            except Exception as e:
                print(f"[!] Error reproduciendo TTS: {e}")
            finally:
                self.tts_queue.task_done()

    def listen_chat(self):
        server = 'irc.chat.twitch.tv'
        port = 6667
        nickname = 'justinfan12345'

        self.sock = socket.socket()
        self.sock.settimeout(1.0) 
        
        try:
            self.sock.connect((server, port))
            self.sock.send(f"NICK {nickname}\n".encode('utf-8'))
            self.sock.send(f"JOIN #{self.channel.lower()}\n".encode('utf-8'))
            print(f"[*] TTS Bot conectado al chat: {self.channel}")
        except Exception as e:
            print(f"[!] Error conectando a Twitch: {e}")
            return

        while self.is_running:
            try:
                resp = self.sock.recv(2048).decode('utf-8', errors='ignore')
                
                if resp.startswith('PING'):
                    self.sock.send("PONG\n".encode('utf-8'))
                
                elif len(resp) > 0:
                    for line in resp.split('\r\n'):
                        match = re.search(r':(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.*)', line)
                        if match:
                            username = match.group(1)
                            message_raw = match.group(2).strip()
                            
                            if message_raw.startswith(self.comando):
                                texto_sin_comando = message_raw[len(self.comando):].strip()
                                mensaje_limpio = self.limpiar_mensaje(texto_sin_comando)
                                
                                if mensaje_limpio:
                                    print(f"[{username}]: {mensaje_limpio} -> [Enviado a TTS]")
                                    self.tts_queue.put(f"{username} dice: {mensaje_limpio}")
                                    
            except socket.timeout:
                continue 
            except Exception:
                pass
                
        self.sock.close()
        print("[*] TTS Bot desconectado de Twitch.")

    def start(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self.tts_worker, daemon=True).start()
            threading.Thread(target=self.listen_chat, daemon=True).start()
            print("[*] Módulo TTS Iniciado.")

    def stop(self):
        if self.is_running:
            self.is_running = False
            print("[*] Deteniendo módulo TTS...")