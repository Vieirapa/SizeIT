import cv2
import numpy as np
import os
from rembg import remove

def remove_background(image_path):
    """Remove automaticamente o fundo da imagem usando rembg (U²-Net)."""
    
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        return
    
    # Carregar imagem original
    image = cv2.imread(image_path)

    # Converter para RGBA antes de processar
    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # Aplicar remoção de fundo com U²-Net (rembg)
    output = remove(image_rgba)

    # Salvar resultado
    base_name, _ = os.path.splitext(image_path)
    output_path = base_name + "_no_bg.png"
    cv2.imwrite(output_path, output)

    print(f"Fundo removido com sucesso! Imagem salva em: {output_path}")
    
    return output_path
