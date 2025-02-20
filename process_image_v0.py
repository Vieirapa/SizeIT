import cv2
import os
import numpy as np

def process_image(image_path):
    # Verifica se o arquivo existe
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        return
    
    # Carregar a imagem
    image = cv2.imread(image_path)
    
    # Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar desfoque para reduzir ruídos
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Aplicar detecção de bordas com Canny
    edges = cv2.Canny(blurred, 50, 150)
    
    # Aplicar limiarização para segmentação
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Criar uma cópia da imagem original para desenhar os contornos
    contour_image = image.copy()
    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)  # Verde para os contornos
    
    # Gerar os nomes dos arquivos de saída
    base_name, _ = os.path.splitext(image_path)
    canny_path = base_name + "_canny.jpg"
    linear_path = base_name + "_linear.jpg"
    contornos_path = base_name + "_contornos.jpg"
    
    # Salvar as imagens
    cv2.imwrite(canny_path, edges)
    cv2.imwrite(linear_path, thresh)
    cv2.imwrite(contornos_path, contour_image)
    
    print(f"Imagens processadas e salvas:")
    print(f"- {canny_path}")
    print(f"- {linear_path}")
    print(f"- {contornos_path}")


filenames = [
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\WIN_20250219_15_07_54_Pro.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\WIN_20250219_15_08_22_Pro.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\WIN_20250219_16_02_45_Pro.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\WIN_20250219_16_02_55_Pro.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\1_2069_135183.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\2_2069_135183.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\P1_2069_135183.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\P2_2069_135183.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\P3_2069_135183.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\P4_2069_135183.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135185\1_2069_135185.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135185\2_2069_135185.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135185\P1_2069_135185.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135185\P2_2069_135185.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135185\P3_2069_135185.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135185\P4_2069_135185.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135187\1_2069_135187.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135187\2_2069_135187.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135187\P1_2069_135187.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135187\P2_2069_135187.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135187\P3_2069_135187.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135187\P4_2069_135187.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135189\1_2069F_135189.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135189\2_2069F_135189.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135189\P1_2069F_135189.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135189\P2_2069F_135189.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135189\P3_2069F_135189.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135189\P4_2069F_135189.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135191\1_2069F_135191.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135191\2_2069F_135191.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135191\P1_2069F_135191.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135191\P2_2069F_135191.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135191\P3_2069F_135191.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135191\P4_2069F_135191.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135193\1_2069F_135193.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135193\2_2069F_135193.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135195\1_2069EF_135195.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135195\2_2069EF_135195.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135195\P1_2069EF_135195.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135195\P2_2069EF_135195.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135195\P3_2069EF_135195.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135195\P4_2069EF_135195.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\1_2069EF_135197.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\2_2069EF_135197.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P1_2069EF_135197.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P1_2069F_135193.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P2_2069EF_135197.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P2_2069F_135193.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P3_2069EF_135197.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P3_2069F_135193.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P4_2069EF_135197.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135197\P4_2069F_135193.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135401\1_2069EF_135401.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135401\2_2069EF_135401.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135401\P1_2069EF_135401.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135401\P2_2069EF_135401.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135401\P3_2069EF_135401.jpg",
r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135401\P4_2069EF_135401.jpg"
]

# Exemplo de uso
if __name__ == "__main__":
    print(f"{filenames}")
    image_path = input("Digite o caminho da imagem JPG: ").strip()
    process_image(image_path)

