from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
from tkinter import ttk
from src.capture_coord import CapturaTela, obter_coordenadas_captura
from src.capture_window import capturar_salvar_e_extrair_texto
import threading
import json
import os
from PIL import Image, ImageTk

class AdicionarCoordenadaTopLevel(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.parent = parent
        self.callback = callback

        self.transient(parent)
        self.grab_set()
        
        window_width = 300
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.title("Adicionar Coordenada")
        self.resizable(False, False)
        
        self.__elements()
        

    def __elements(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Exemplo Coordenada: 234 123").grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
        
        self.entrada_coordenada = ctk.CTkEntry(self)
        self.entrada_coordenada.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

        ctk.CTkLabel(self, text="Altura (padrão: 78)").grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
        
        self.entrada_altura = ctk.CTkEntry(self)
        self.entrada_altura.grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

        ctk.CTkButton(self, text="Adicionar", command=self.adicionar_coordenada).grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    def adicionar_coordenada(self):
        coordenada = self.entrada_coordenada.get().strip()
        altura = self.entrada_altura.get().strip() or "78"  # Se altura estiver vazia, usa "78"
        if coordenada:
            self.callback(coordenada, altura)
            self.destroy()
        else:
            CTkMessagebox(title="Erro", message="A coordenada não pode estar vazia!", icon="cancel")

class AplicacaoPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.__configsWindow()
        self.__frames()
        self.__elements()

        self.imagem_label = None
        self.criar_imagem_label()

        self.flagThreadExtracao = False
        self.coordenadas = self.carregar_coordenadas()
        self.atualizar_tabela()

        self.mainloop()
    
    def __configsWindow(self):
        self.title("Visual PW Material")
        
        # Definir o tamanho da janela
        largura_janela = 600
        altura_janela = 400
        
        # Obter as dimensões da tela
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        
        # Calcular a posição para centralizar
        posicao_x = (largura_tela - largura_janela) // 2
        posicao_y = (altura_tela - altura_janela) // 2
        
        # Definir a geometria da janela (tamanho e posição)
        self.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        
        # Opcional: impedir o redimensionamento da janela
        self.resizable(False, False)

    def __frames(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame esquerdo para coordenadas salvas
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=(0, 5))

        # Frame direito
        self.right_frame = ctk.CTkFrame(self.main_frame,width = 500)
        self.right_frame.pack(side="right", fill="both",expand=True, padx=(5, 0))

        # Frame para botões de zoom
        self.zoom_frame = ctk.CTkFrame(self.left_frame)
        self.zoom_frame.pack(side="right", padx=5)


    def __elements(self):
        # Frame para a tabela
        self.table_frame = ctk.CTkFrame(self.left_frame)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Criação da tabela
        self.coord_table = ttk.Treeview(self.table_frame, columns=("Coordenadas", "Altura"), show="headings")
        self.coord_table.heading("Coordenadas", text="Coordenadas", anchor="center")
        self.coord_table.heading("Altura", text="Altura", anchor="center")
        self.coord_table.column("Coordenadas", anchor="center", width=150, stretch=False)
        self.coord_table.column("Altura", anchor="center", width=100, stretch=False)
        self.coord_table.pack(fill="both", expand=True, side="left")

        # Adicionar evento para prevenir redimensionamento
        self.coord_table.bind('<Button-1>', self.prevenir_redimensionamento)

        # Barra de rolagem para a tabela
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.coord_table.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.coord_table.configure(yscrollcommand=self.scrollbar.set)

        ctk.CTkButton(self.zoom_frame, text="+", width=30, command=self.add).pack(pady=2)
        ctk.CTkButton(self.zoom_frame, text="-", width=30, command=self.rmv).pack(pady=2)

        ctk.CTkButton(self.left_frame, text="Apagar Tudo", command=self.rmvAll).pack(pady=5, side="bottom", fill="x", padx=5)

        # Essa parte é do frame principal (right_frame)
        ctk.CTkButton(self.right_frame, text="Seleciona área das Coordenadas", command=self.capturar_coordenadas).pack(pady=5, padx=5, fill="x")

        self.imagem_frame = ctk.CTkFrame(self.right_frame)
        self.imagem_frame.pack(pady=5, padx=5, fill="x")

        self.btn_iniciar = ctk.CTkButton(self.right_frame, text="Iniciar Captura", command=self.iniciar_extracao)
        self.btn_iniciar.pack(pady=5, padx=5, fill="x")

        self.btn_parar = ctk.CTkButton(self.right_frame, text="Parar Captura", command=self.parar_extracao, state="disabled")
        self.btn_parar.pack(pady=5, padx=5, fill="x")

    def prevenir_redimensionamento(self, event):
        if self.coord_table.identify_region(event.x, event.y) == "separator":
            return "break"

    def criar_imagem_label(self):
        if self.imagem_label:
            self.imagem_label.destroy()
        self.imagem_label = ctk.CTkLabel(self.imagem_frame, text="")
        self.imagem_label.pack(fill="both", expand=True)

    def capturar_coordenadas(self):
        self.withdraw()
        captura = CapturaTela(self)
        captura.wait_window()
        self.deiconify()
        coordenadas = obter_coordenadas_captura()
        if coordenadas:
            if not self.imagem_label:
                self.criar_imagem_label()
            self.coord_table.insert("", "end", values=(coordenadas[0], coordenadas[1]))

    def iniciar_extracao(self):
        coordenadas = obter_coordenadas_captura()
        if coordenadas:
            x1, y1, x2, y2 = coordenadas
            self.withdraw()
            try:
                self.btn_iniciar.configure(state="disabled")
                self.flagThreadExtracao = True
                thread = threading.Thread(target=lambda: capturar_salvar_e_extrair_texto(x1, y1, x2, y2, self))
                thread.daemon = True
                thread.start()
                self.btn_parar.configure(state="normal")
            except KeyboardInterrupt:
                print("Processo interrompido pelo usuário.")
            finally:
                self.deiconify()
        else:
            print("Por favor, capture as coordenadas primeiro.")

    def parar_extracao(self):
        self.flagThreadExtracao = False
        self.btn_iniciar.configure(state="normal")
        self.btn_parar.configure(state="disabled")

    def carregar_coordenadas(self):
        if os.path.exists('coordenadas.json'):
            with open('coordenadas.json', 'r') as f:
                return json.load(f)
        return {"coord": []}

    def salvar_coordenadas(self):
        with open('coordenadas.json', 'w') as f:
            json.dump(self.coordenadas, f)
        print(f"Coordenadas salvas: {self.coordenadas}")

    def atualizar_tabela(self):
        self.coord_table.delete(*self.coord_table.get_children())
        for coord in self.coordenadas["coord"]:
            self.coord_table.insert("", "end", values=(coord[0], coord[1]))

    def add(self):
        AdicionarCoordenadaTopLevel(self, self.adicionar_coordenada)

    def adicionar_coordenada(self, coordenada, altura):
        self.coordenadas["coord"].append([coordenada, altura])
        self.salvar_coordenadas()
        self.atualizar_tabela()

    def rmv(self):
        selecionado = self.coord_table.selection()
        if selecionado:
            item = self.coord_table.item(selecionado)
            coordenada, altura = item['values']
            self.coordenadas["coord"] = [c for c in self.coordenadas["coord"] if c[0] != coordenada or str(c[1]) != str(altura)]
            self.coord_table.delete(selecionado)
            self.salvar_coordenadas()
            print(f"Removido: Coordenada {coordenada}, Altura {altura}")
            print(f"Coordenadas restantes: {self.coordenadas['coord']}")
        else:
            print("Nenhum item selecionado para remover.")

    def rmvAll(self):
        self.coordenadas["coord"].clear()
        self.salvar_coordenadas()
        self.atualizar_tabela()

    def atualizar_imagem(self, caminho_imagem):
        try:
            self.imagem_original = Image.open(caminho_imagem)
            largura, altura = self.imagem_original.size

            self.imagem_frame.configure(width=largura, height=altura)
            foto = ImageTk.PhotoImage(self.imagem_original)

            if not self.imagem_label:
                self.criar_imagem_label()

            self.imagem_label.configure(image=foto, width=largura, height=altura)
            self.imagem_label.image = foto

        except Exception as e:
            print(f"Erro ao atualizar imagem: {e}")