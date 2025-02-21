import cv2
import numpy as np
import os

def remove_background_grabcut_custom(image_path, low_thresh, high_thresh):
    """Remove o fundo da imagem usando GrabCut com máscara baseada nos limiares do Canny."""

    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        return
    
    # Carregar imagem original
    image = cv2.imread(image_path)

    # Converter para escala de cinza e aplicar Canny com os valores escolhidos
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, low_thresh, high_thresh)

    # Criar máscara para GrabCut com base nas bordas detectadas
    mask = np.zeros(image.shape[:2], np.uint8)
    mask[edges > 0] = cv2.GC_PR_FGD  # Pixels com borda são marcados como provável primeiro plano

    # Criar modelos de fundo e primeiro plano
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # Aplicar GrabCut
    cv2.grabCut(image, mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)

    # Criar máscara binária final
    mask_bin = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype('uint8')

    # Aplicar a máscara na imagem original
    result = image * mask_bin[:, :, np.newaxis]

    # Suavizar bordas com operações morfológicas
    kernel = np.ones((3, 3), np.uint8)
    mask_bin = cv2.morphologyEx(mask_bin, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Salvar imagem final
    base_name, _ = os.path.splitext(image_path)
    output_path = base_name + "_grabcut_custom.png"
    cv2.imwrite(output_path, result)

    print(f"Fundo removido (GrabCut com Canny ajustado)! Imagem salva em: {output_path}")

image_path = r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\1_2069_135183.jpg"
remove_background_grabcut_custom(image_path, 40, 200)  # Substitua pelos valores escolhidos