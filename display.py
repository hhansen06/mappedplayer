import socket
import json
import tkinter as tk
import threading
import signal

exit_event = threading.Event()

def start_server(root):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 6000))  # Port 6000
    server_socket.settimeout(0.5)
    server_socket.listen(5)
    print("Display server listening on port 6000")

    while True:
        try: 
            if exit_event.is_set():
                break
            client_socket, addr = server_socket.accept()
            message = client_socket.recv(1024).decode()
            config = json.loads(message)
            update_display(root, config)
            client_socket.close()
        except socket.timeout:
            pass   
                

def update_display(root, config):
   # print("Received updated configuration:")
  #  print(config)
    draw_displays(root, config)

def draw_displays(root, config):
    for display in config.get('displays', []):
        x1, y1, x2, y2 = display['position']
        # Verwenden einer helleren Farbe für die Linie, um auf schwarzem Hintergrund sichtbar zu sein
        canvas.create_line(x1, y1, x2, y2, fill='red', width=2)  # Rot bleibt sichtbar auf Schwarz
        # Ebenso Textfarbe ändern, damit sie sichtbar ist
        canvas.create_text((x1+x2)/2, (y1+y2)/2, text=display['name'], fill='white')  # Textfarbe zu Weiß geändert
            # Draw crosshair
        mouse_x = config.get('mouse_x', 960)  # Default values are centered if not specified
        mouse_y = config.get('mouse_y', 540)
        canvas.create_line(mouse_x - 10, mouse_y, mouse_x + 10, mouse_y, fill='yellow', width=2)  # Horizontal line of crosshair
        canvas.create_line(mouse_x, mouse_y - 10, mouse_x, mouse_y + 10, fill='yellow', width=2)  # Vertical line of crosshair
 
def exit_handler(event):
   print("exit requested ...")
   exit_event.set()
   root.destroy()


def check():
    root.after(500, check)  #  time in ms.

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda x,y : print('terminal ^C') or exit_handler(None))
    root = tk.Tk()
    server_thread = threading.Thread(target=lambda: start_server(root))
    root.overrideredirect(True)
    root.config(cursor="none") 
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())  # Ensure the window can be closed properly
    canvas = tk.Canvas(root, width=1920, height=1080, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    server_thread.start()
    root.after(500, check)  #  time in ms.
    root.bind_all('<Control-c>', exit_handler)
    root.mainloop()
  
