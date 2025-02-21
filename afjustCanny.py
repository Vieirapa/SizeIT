import cv2
import numpy as np

def adjust_canny(image_path):
    """Abre uma interface para ajustar os limiares do Canny manualmente."""

    # Carregar a imagem
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Criar uma função de callback para o Trackbar
    def on_trackbar(val):
        """Atualiza a imagem ao modificar os valores de Canny"""
        low = cv2.getTrackbarPos("Limiar Inferior", "Canny Adjust")
        high = cv2.getTrackbarPos("Limiar Superior", "Canny Adjust")
        edges = cv2.Canny(image, low, high)
        cv2.imshow("Canny Adjust", edges)

    # Criar janela para ajuste
    cv2.namedWindow("Canny Adjust")
    cv2.createTrackbar("Limiar Inferior", "Canny Adjust", 50, 255, on_trackbar)
    cv2.createTrackbar("Limiar Superior", "Canny Adjust", 150, 255, on_trackbar)

    # Exibir imagem inicial
    on_trackbar(0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

image_path = r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\1_2069_135183.jpg"
adjust_canny(image_path)