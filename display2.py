import logging
from logging.handlers import RotatingFileHandler
import sys
import cv2
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk


# Logging-Konfiguration
log_file_path = '/var/log/mappedplayer/display.log'
logging.basicConfig(handlers=[RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=5)],
                    level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


class VideoPlayerApp:
    def __init__(self, root, video_configs):
        self.root = root
        self.root.title("Multi-Video Player")
        self.root.geometry("1920x1080")
        
        self.video_configs = video_configs
        self.running = True
        self.threads = []

        for config in self.video_configs:
            self.create_video_canvas(config)

    def create_video_canvas(self, config):
        # Erstelle ein Canvas für das Video
        canvas = tk.Canvas(self.root, width=config['width'], height=config['height'])
        canvas.place(x=config['x'], y=config['y'])
        config['canvas'] = canvas

        # Starte einen Thread für die Video-Wiedergabe
        thread = Thread(target=self.play_video, args=(config,))
        thread.daemon = True
        thread.start()
        self.threads.append(thread)

    def play_video(self, config):
        # Lade das Video mit OpenCV
        cap = cv2.VideoCapture(config['file'])
        canvas = config['canvas']

                # Erhalte die Framerate des Videos
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_time = 1 / fps  # Zeit pro Frame in Sekunden

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break  # Video ist zu Ende

            # Konvertiere das Bildformat für tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (config['width'], config['height']))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Aktualisiere das Canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            canvas.image = imgtk

            # Aktuelle Frame-Position berechnen
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            current_time = current_frame * frame_time
      #      print(f"Video: {config['file']} - Frame: {current_frame}, Time: {current_time:.2f} seconds")

            # Warte ein bisschen, um die Video-Framerate einzuhalten
          #  self.root.update_idletasks()
      #      self.root.update()

        cap.release()

    def on_close(self):
        self.running = False
        self.root.destroy()



if __name__ == '__main__':
    hostname = "test"
    logging.info("mappedplayer display2 started.")

    video_configs = [
  #      {"file": "content/test2-320x240.mkv", "x": 50, "y": 50, "width": 320, "height": 240},
        {"file": "content/test2-640x480.mkv", "x": 500, "y": 50, "width": 640, "height": 480},
        {"file": "content/test1-640x480.mkv", "x":50,"y": 500,"width": 640, "height": 480}
    ]

    root = tk.Tk()
    root.overrideredirect(True)
    root.config(cursor="none") 
    app = VideoPlayerApp(root, video_configs)

    # Setze eine Methode zum sicheren Schließen
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()