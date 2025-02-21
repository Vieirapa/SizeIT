import cv2
import numpy as np
import os

def remove_background_opencv(image_path):
    """Remove o fundo da imagem usando o algoritmo GrabCut do OpenCV."""
    
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        return
    
    # Carregar a imagem original
    image = cv2.imread(image_path)
    
    # Criar máscara inicial para GrabCut
    mask = np.zeros(image.shape[:2], np.uint8)

    # Criar modelos de fundo e primeiro plano (necessário para GrabCut)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # Definir um retângulo que envolve a peça (ajuste conforme necessário)
    h, w = image.shape[:2]
    rect = (10, 10, w-20, h-20)  # Retângulo um pouco menor que a imagem

    # Aplicar GrabCut
    cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

    # Converter a máscara para binária (0 = fundo, 1 = peça)
    mask_bin = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    # Aplicar a máscara na imagem original
    result = image * mask_bin[:, :, np.newaxis]

    # Salvar imagem resultante
    base_name, _ = os.path.splitext(image_path)
    output_path = base_name + "_grabcut.png"
    cv2.imwrite(output_path, result)

    print(f"Fundo removido (GrabCut)! Imagem salva em: {output_path}")


image_path = r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\1_2069_135183.jpg"
remove_background_opencv(image_path)