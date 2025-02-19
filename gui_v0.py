import tkinter as tk
from tkinter import filedialog, Label, Frame, ttk, PhotoImage
import cv2
from PIL import Image, ImageTk
import sizeitCalibration as sc
import os

class SizeITApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SizeIT - Medição de Peças")
        self.root.geometry("900x600")
        self.root.configure(bg="#ecf0f1")
        
        self.image_calib_path = None
        self.image_piece_path = None
        self.pixel_to_mm_ratio = None
        
        # Criar frames para layout
        self.frame_left = Frame(root, width=80, bg="#34495e")  # Área de botões reduzida
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y)
        
        self.frame_right = Frame(root, width=820, bg="#ecf0f1")  # Área de exibição de imagem
        self.frame_right.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        self.frame_bottom = Frame(root, width=820, height=150, bg="#dfe6e9")  # Área para tabela de medidas
        self.frame_bottom.pack(side=tk.BOTTOM, fill=tk.X)
        
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
        
        # Área de exibição de resultados e imagem (painel direito)
        self.label_result = Label(self.frame_right, text="Resultados aparecerão aqui", font=("Arial", 12), bg="#ecf0f1")
        self.label_result.pack(pady=10)
        
        self.label_image = Label(self.frame_right, bg="#ecf0f1")
        self.label_image.pack()
        
        # Criar tabela para exibir os resultados
        self.tree = ttk.Treeview(self.frame_bottom, columns=("Medição", "Valor (mm)"), show="headings")
        self.tree.heading("Medição", text="Medição")
        self.tree.heading("Valor (mm)", text="Valor (mm)")
        self.tree.column("Medição", width=200)
        self.tree.column("Valor (mm)", width=150)
        self.tree.pack(pady=10, fill=tk.X)
    
    def measure_piece(self):
        if not self.image_piece_path or not self.pixel_to_mm_ratio:
            self.label_result.config(text="Calibre e selecione uma imagem primeiro!")
            return
        length_mm = sc.get_piece_length(self.image_piece_path, self.pixel_to_mm_ratio)
        measure_positions = [10, 20, 30, 40, 50]
        diameters = sc.measure_diameters(self.image_piece_path, self.pixel_to_mm_ratio, measure_positions)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tree.insert("", "end", values=("Comprimento", f"{length_mm:.2f}"))
        for i, diameter in enumerate(diameters):
            self.tree.insert("", "end", values=(f"Diâmetro {measure_positions[i]}mm", f"{diameter:.2f}"))
        
        processed_path = self.image_piece_path.replace(".png", "_M.png")
        if os.path.exists(processed_path):
            self.display_image(processed_path)
            self.image_piece_path = processed_path
    
if __name__ == "__main__":
    root = tk.Tk()
    app = SizeITApp(root)
    root.mainloop()
