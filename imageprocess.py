import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def process_image(image_path, num_samples=20):
    # Carregar a imagem
    image = cv2.imread(image_path)
    
    # Obter diretório e nome do arquivo
    directory, filename = os.path.split(image_path)
    base_name, _ = os.path.splitext(filename)
    
    # Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar desfoque para reduzir ruído
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Aplicar limiarização adaptativa
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Detectar bordas usando Canny
    edges = cv2.Canny(thresh, 50, 150)
    
    # Encontrar contornos na imagem binária
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Criar uma máscara preta do mesmo tamanho da imagem
    mask = np.zeros_like(gray)
    
    # Desenhar os contornos na máscara
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)
    
    # Obter as coordenadas da máscara onde a peça está presente
    y_indices, x_indices = np.where(mask == 255)
    
    # Criar uma grade de pontos para medições transversais
    x_min, x_max = np.min(x_indices), np.max(x_indices)
    x_samples = np.linspace(x_min, x_max, num_samples).astype(int)
    
    # Armazenar as medidas de largura
    width_measurements = []
    
    for x in x_samples:
        y_values = y_indices[x_indices == x]  # Pegar todas as alturas (y) nessa coluna x
        if len(y_values) > 0:
            y_min, y_max = np.min(y_values), np.max(y_values)
            width_measurements.append((x, y_min, y_max, y_max - y_min))
    
    # Converter os dados em um DataFrame
    df_measurements = pd.DataFrame(width_measurements, columns=["X", "Y_Min", "Y_Max", "Width"])
    
    # Salvar imagens intermediárias
    cv2.imwrite(os.path.join(directory, f"{base_name}_gray.jpg"), gray)
    cv2.imwrite(os.path.join(directory, f"{base_name}_thresh.jpg"), thresh)
    cv2.imwrite(os.path.join(directory, f"{base_name}_edges.jpg"), edges)
    cv2.imwrite(os.path.join(directory, f"{base_name}_mask.jpg"), mask)
    
    # Criar uma cópia da máscara para desenhar medições
    mask_with_lines = mask.copy()
    for x, y_min, y_max, width in width_measurements:
        cv2.line(mask_with_lines, (x, y_min), (x, y_max), (255, 0, 0), 1)
    cv2.imwrite(os.path.join(directory, f"{base_name}_measurements.jpg"), mask_with_lines)
    
    return df_measurements

# Exemplo de uso
# df_results = process_image("caminho_para_imagem.jpg")
# print(df_results)


file_list = [
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\0_P1_2069EF_133066.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\10_P1_2069_133058.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\11_P1_2069_133705.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\12_P2_2069_133705.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\13_P1_2069_135183.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\14_P3_2069_135183.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\1_P1_2069F_133068.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\2_P2_2069EF_133066.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\3_P2_2069F_133068.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\4_P1_2069F_133070.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\5_P1_2069F_133072.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\6_P1_2069F_133074.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\7_P2_2069F_133070.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\8_P2_2069F_133072.jpg",
    r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\99_EOCA\Investigacao_EOCA_\AMOSTRAS DOS 08 LOTES EOCA_2022\PictureTaken\9_P2_2069F_133074.jpg",
]
#
#
# modelo de tratamento de imagens criado em 05/05/25
# por enquanto eh a melhor opcao de arrancar o fundo e criar mascadas, mas ainda nao mede nada direito . . .
#
# 
for  name in file_list:
    df_results = process_image(name)
    print (df_results)
