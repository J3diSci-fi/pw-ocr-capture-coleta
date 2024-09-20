import tkinter as tk
from PIL import ImageGrab
import json

class CapturaTela(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.attributes('-fullscreen', True)
        self.attributes('-alpha', 0.2)
        self.configure(bg='grey')

        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.current_rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        if self.current_rect:
            self.canvas.delete(self.current_rect)

        self.current_rect = self.canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline='red')

    def on_release(self, event):
        x1 = int(min(self.start_x, event.x))
        y1 = int(min(self.start_y, event.y))
        x2 = int(max(self.start_x, event.x))
        y2 = int(max(self.start_y, event.y))

        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        screenshot.save("temp/captura_de_tela.png")
        print("Captura de tela salva como 'captura_de_tela.png'")

        coordenadas = {
            "inicio": {"x": x1, "y": y1},
            "fim": {"x": x2, "y": y2}
        }
        
        with open("temp/coordenadas_captura.json", "w") as arquivo_json:
            json.dump(coordenadas, arquivo_json, indent=4)
        
        print("Coordenadas da captura salvas em 'coordenadas_captura.json'")

        self.destroy()

def obter_coordenadas_captura():
    try:
        with open("temp/coordenadas_captura.json", "r") as arquivo_json:
            coordenadas = json.load(arquivo_json)
        
        x_inicial = coordenadas["inicio"]["x"]
        y_inicial = coordenadas["inicio"]["y"]
        x_final = coordenadas["fim"]["x"]
        y_final = coordenadas["fim"]["y"]
        
        return x_inicial, y_inicial, x_final, y_final
    except FileNotFoundError:
        print("Arquivo de coordenadas não encontrado.")
        return None
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON.")
        return None
    except KeyError:
        print("Formato de dados inválido no arquivo JSON.")
        return None