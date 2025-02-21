import tkinter as tk
from tkinter import filedialog, Label, Frame, ttk, PhotoImage
import cv2
from PIL import Image, ImageTk
import sizeitCalibration as sc
import os
import numpy as np

class SizeITApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SizeIT - Medição de Peças")
        self.root.geometry("900x600")
        self.root.configure(bg="#ecf0f1")
        
        self.image_calib_path = None
        self.image_piece_path = None
        self.pixel_to_mm_ratio = None
        
        # Criar frame esquerdo (barra de botões) ocupando a altura total
        self.frame_left = Frame(root, width=80, bg="#34495e")
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y)
        
        # Criar frame direito principal que conterá a imagem e a tabela
        self.frame_right = Frame(root, bg="#ecf0f1")
        self.frame_right.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        # Criar paned window para permitir redimensionamento dinâmico
        self.paned_window = tk.PanedWindow(self.frame_right, orient=tk.VERTICAL, sashwidth=5, bg="#bdc3c7")
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Criar frame superior (80% do espaço direito) para exibição da imagem
        self.frame_top = Frame(self.paned_window, bg="#ecf0f1")
        self.paned_window.add(self.frame_top, height=480)
        
        # Criar frame inferior (20% do espaço direito) para tabela de medidas
        self.frame_bottom = Frame(self.paned_window, bg="#dfe6e9")
        self.paned_window.add(self.frame_bottom, height=120)
        
        # Ajustar a tabela dinamicamente com o redimensionamento
        self.frame_bottom.bind("<Configure>", self.adjust_table_rows)
        
        # Carregar e redimensionar ícones
        self.icon_load_calib = self._resize_icon("icons/calib.png", 40, 40)
        self.icon_load_piece = self._resize_icon("icons/piece.png", 40, 40)
        self.icon_calibrate = self._resize_icon("icons/calibrate.png", 40, 40)
        self.icon_align = self._resize_icon("icons/align.png", 40, 40)
        self.icon_measure = self._resize_icon("icons/measure.png", 40, 40)
        
        # Criar botões apenas com ícones e tooltip
        self.btn_load_calib = ttk.Button(self.frame_left, image=self.icon_load_calib, command=self.load_calib_image)
        self.btn_load_calib.pack(pady=10)
        self._create_tooltip(self.btn_load_calib, "Carregar imagem de calibração")
        
        self.btn_load_piece = ttk.Button(self.frame_left, image=self.icon_load_piece, command=self.load_piece_image)
        self.btn_load_piece.pack(pady=10)
        self._create_tooltip(self.btn_load_piece, "Carregar imagem da peça")
        
        self.btn_calibrate = ttk.Button(self.frame_left, image=self.icon_calibrate, command=self.run_calibration)
        self.btn_calibrate.pack(pady=10)
        self._create_tooltip(self.btn_calibrate, "Executar calibração")
        
        self.btn_align = ttk.Button(self.frame_left, image=self.icon_align, command=self.align_piece)
        self.btn_align.pack(pady=10)
        self._create_tooltip(self.btn_align, "Alinhar peça")
        
        self.btn_measure = ttk.Button(self.frame_left, image=self.icon_measure, command=self.measure_piece)
        self.btn_measure.pack(pady=10)
        self._create_tooltip(self.btn_measure, "Medir peça")
        
        # Área de exibição de resultados e imagem (painel superior)
        self.label_result = Label(self.frame_top, text="Resultados aparecerão aqui", font=("Arial", 12), bg="#ecf0f1")
        self.label_result.pack(pady=10)
        
        self.label_image = Label(self.frame_top, bg="#ecf0f1")
        self.label_image.pack()
        
        # Criar tabela para exibir os resultados (painel inferior)
        self.tree = ttk.Treeview(self.frame_bottom, columns=("Medição", "Valor (mm)"), show="headings")
        self.tree.heading("Medição", text="Medição")
        self.tree.heading("Valor (mm)", text="Valor (mm)")
        self.tree.column("Medição", width=200)
        self.tree.column("Valor (mm)", width=150)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)
    
    def adjust_table_rows(self, event):
        row_height = 20  # Altura aproximada de uma linha na Treeview
        num_rows = max(1, event.height // row_height)  # Calcular quantas linhas cabem
        self.tree.configure(height=num_rows)

    def display_image(self, img_path):
        if not os.path.exists(img_path):
            self.label_result.config(text="Erro ao carregar a imagem!")
            return
        
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.resize((600, 450), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(image)
        self.label_image.config(image=img_tk)
        self.label_image.image = img_tk
    
    def _resize_icon(self, path, width, height):
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        else:
            print(f"Erro: Ícone não encontrado - {path}")
            return None 
 
    def _create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.wm_overrideredirect(True)
        label = Label(tooltip, text=text, font=("Arial", 10), bg="black", fg="white", padx=5, pady=3)
        label.pack()
        
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def hide_tooltip(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip) 
    
    def load_calib_image(self):
        self.image_calib_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if self.image_calib_path:
            self.label_result.config(text=f"Imagem de calibração carregada: {os.path.basename(self.image_calib_path)}")
            self.display_image(self.image_calib_path)
    
    def load_piece_image(self):
        self.image_piece_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if self.image_piece_path:
            self.label_result.config(text=f"Imagem da peça carregada: {os.path.basename(self.image_piece_path)}")
            self.display_image(self.image_piece_path)
    
    def run_calibration(self):
        if not self.image_calib_path:
            self.label_result.config(text="Selecione uma imagem de calibração!")
            return
        self.pixel_to_mm_ratio = sc.calibrate(self.image_calib_path)
        if self.pixel_to_mm_ratio:
            self.label_result.config(text=f"Calibração realizada: {self.pixel_to_mm_ratio:.3f} pixels/mm")
        else:
            self.label_result.config(text="Falha na calibração!")
    
    def align_piece(self):
        if not self.image_piece_path:
            self.label_result.config(text="Selecione uma imagem da peça!")
            return
        aligned_path = sc.align_image(self.image_piece_path)
        if aligned_path and os.path.exists(aligned_path):
            self.display_image(aligned_path)
            self.image_piece_path = aligned_path
            self.label_result.config(text="Imagem alinhada com sucesso!")
        else:
            self.label_result.config(text="Falha no alinhamento!")
    
    def measure_piece(self):
        if not self.image_piece_path or not self.pixel_to_mm_ratio:
            self.label_result.config(text="Calibre e selecione uma imagem primeiro!")
            return
        length_mm = sc.get_piece_length(self.image_piece_path, self.pixel_to_mm_ratio)
                
        # definindo nro medidas
        nro_medidas = 10
        passo = length_mm/nro_medidas
        measure_positions = np.arange(passo, length_mm + passo, passo)
        
        diameters, output_path = sc.measure_diameters(self.image_piece_path, self.pixel_to_mm_ratio, measure_positions)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
                
        self.tree.insert("", "end", values=("Comprimento", f"{length_mm:.2f}"))
        for i, diameter in enumerate(diameters):
            self.tree.insert("", "end", values=(f"Diâmetro {measure_positions[i]}mm", f"{diameter:.2f}"))
        
        # colocando a imagem resultante da medida
        self.display_image(output_path)
    
    
if __name__ == "__main__":
    root = tk.Tk()
    app = SizeITApp(root)
    root.mainloop()

