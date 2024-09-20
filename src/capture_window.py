import mss
import cv2
import numpy as np
import time
import easyocr

reader = easyocr.Reader(['pt'])  # Inicialize com os idiomas desejados

def capturar_area_retangular(sct, area):
    screenshot = sct.grab(area)
    frame = np.array(screenshot)
    return cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

def extrair_texto_da_imagem(imagem):
    resultado = reader.readtext(imagem)
    textos_e_coordenadas = []
    for (bbox, texto, confianca) in resultado:
        x1, y1 = map(int, bbox[0])
        x2, y2 = map(int, bbox[2])
        textos_e_coordenadas.append((texto, (x1, y1, x2, y2), confianca))
    return textos_e_coordenadas

def capturar_salvar_e_extrair_texto(x1, y1, x2, y2, master, intervalo=0.5):
    with mss.mss() as sct:
        area = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        
        while master.flagThreadExtracao:
            inicio = time.time()
            
            frame = capturar_area_retangular(sct, area)
            nome_arquivo = "temp/captura.png"
            cv2.imwrite(nome_arquivo, frame)
            
            print(f"Imagem {nome_arquivo} salva.")
            
            texto_extraido = extrair_texto_da_imagem(frame)
            if texto_extraido:
                print(f"Texto extraído da imagem {nome_arquivo}:")
                print(texto_extraido)
            else:
                print(f"Nenhum texto encontrado na imagem {nome_arquivo}.")
            
            # Atualizar a imagem na interface de forma segura
            master.after(0, lambda: master.atualizar_imagem(nome_arquivo))
            
            tempo_decorrido = time.time() - inicio
            tempo_espera = max(0, intervalo - tempo_decorrido)
            time.sleep(tempo_espera)