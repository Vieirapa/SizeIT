import cv2
import numpy as np
import os

def connect_contours(canny_image_path):
    """Conecta todas as bordas detectadas pelo Canny em uma linha contínua."""
    
    if not os.path.exists(canny_image_path):
        print(f"Erro: Arquivo '{canny_image_path}' não encontrado.")
        return
    
    # Carregar a imagem binária (Canny)
    edges = cv2.imread(canny_image_path, cv2.IMREAD_GRAYSCALE)

    # Encontrar os contornos na imagem binária
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrar contornos pequenos
    min_contour_area = 500  # Ajustável conforme necessário
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

    # Criar uma imagem em branco para desenhar a linha contínua
    connected_image = np.zeros_like(edges)

    # Ordenar e conectar os pontos dos contornos
    for cnt in filtered_contours:
        # Aproximar os contornos para suavizar a linha
        epsilon = 0.005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # Conectar os pontos do contorno com uma linha contínua
        for i in range(len(approx) - 1):
            cv2.line(connected_image, tuple(approx[i][0]), tuple(approx[i+1][0]), (255, 255, 255), 1)

        # Fechar o contorno se for necessário
        if len(approx) > 2:
            cv2.line(connected_image, tuple(approx[-1][0]), tuple(approx[0][0]), (255, 255, 255), 1)

    # Salvar a imagem com a linha contínua
    output_path = canny_image_path.replace("_canny.jpg", "_connected.jpg")
    cv2.imwrite(output_path, connected_image)

    print(f"Linha contínua gerada e salva em: {output_path}")


def process_image(image_path):
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        return
    
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Redução de ruído
    blurred = cv2.medianBlur(gray, 7)

    # Canny com limiar adaptativo (usando Otsu)
    otsu_thresh, _ = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lower_thresh = 0.1 * otsu_thresh
    upper_thresh = 1.0 * otsu_thresh
    edges = cv2.Canny(blurred, lower_thresh, upper_thresh)

    # Transformada de Hough refinada
    circles = cv2.HoughCircles(
        edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=upper_thresh, param2=50, minRadius=5, maxRadius=100
    )

    contour_image = image.copy()
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrar pequenos contornos
    min_contour_area = 1
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
    cv2.drawContours(contour_image, filtered_contours, -1, (0, 255, 0), 2)

    # Salvar imagens
    base_name, _ = os.path.splitext(image_path)
    cv2.imwrite(base_name + "_canny.jpg", edges)
    cv2.imwrite(base_name + "_contornos.jpg", contour_image)

    connect_contours(base_name + "_canny.jpg")

    print("Processamento concluído com ajustes refinados.")



imagepath = r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\1_2069_135183.jpg"
process_image(imagepath)
