import cv2
import numpy as np
import os
from background import remove_background

roi_points = []  # Lista para armazenar os pontos da ROI

def select_roi(event, x, y, flags, param):
    """ Função callback para capturar regiões da imagem clicadas pelo usuário. """
    global roi_points
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_points.append((x, y))
        print(f"Selecionado ponto: {x}, {y}")

def back_projection(image_path):
    """Segmenta a peça na imagem usando Back Projection baseada em histograma de cores."""

    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        return
    
    # Carregar a imagem original
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Converter para HSV para melhor segmentação

    # Exibir a imagem para seleção manual das regiões de interesse
    cv2.imshow("Selecione áreas para a referência (clique e pressione ESC)", image)
    cv2.setMouseCallback("Selecione áreas para a referência (clique e pressione ESC)", select_roi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(roi_points) == 0:
        print("Nenhuma região foi selecionada! Usando ROI padrão.")
        roi_points.append((hsv.shape[1]//4, hsv.shape[0]//4))  # Definir uma ROI padrão

    # Criar máscara baseada nas regiões selecionadas
    roi_mask = np.zeros_like(hsv[:, :, 0], dtype=np.uint8)

    for point in roi_points:
        x, y = point
        cv2.circle(roi_mask, (x, y), 10, 255, -1)  # Criar uma pequena região ao redor dos pontos clicados

    roi_pixels = cv2.bitwise_and(hsv, hsv, mask=roi_mask)  # Extrair pixels da ROI

    # **Passo 2: Criar histograma da ROI**
    roi_hist = cv2.calcHist([roi_pixels], [0, 1], roi_mask, [180, 256], [0, 180, 0, 256])  # Histograma H e S
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)  # Normalizar o histograma

    # **Passo 3: Aplicar Back Projection na imagem completa**
    back_proj = cv2.calcBackProject([hsv], [0, 1], roi_hist, [0, 180, 0, 256], scale=1)

    # **Passo 4: Refinamento com operações morfológicas**
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    back_proj = cv2.filter2D(back_proj, -1, kernel)  # Suavizar a projeção

    _, mask = cv2.threshold(back_proj, 50, 255, cv2.THRESH_BINARY)  # Criar máscara binária

    mask = cv2.medianBlur(mask, 5)  # Suavizar a máscara para reduzir ruídos

    # **Passo 5: Aplicar a máscara na imagem original**
    result = cv2.bitwise_and(image, image, mask=mask)

    # **Passo 6: Salvar as imagens resultantes**
    base_name, _ = os.path.splitext(image_path)
    cv2.imwrite(base_name + "_backproj_mask.jpg", mask)
    cv2.imwrite(base_name + "_backproj_result.jpg", result)

    print(f"Sucessfull segmented ! Processed image saved on :\n- {base_name}_backproj_mask.jpg\n- {base_name}_backproj_result.jpg")
    print(f"Processed image : {base_name}.")


def fill_gaps(image_path):
    """Preenche áreas dentro das bordas detectadas no Canny, simulando um preenchimento de área fechado e suave."""
    
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo '{image_path}' não encontrado.")
        return
    
    # Carregar a imagem do Canny
    edges = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # **Passo 1: Fechamento morfológico suave**
    kernel = np.ones((3, 3), np.uint8)  # Reduzimos o kernel para manter detalhes finos
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    # **Passo 2: Aplicar Transformada de Distância para suavizar preenchimento**
    dist_transform = cv2.distanceTransform(cv2.bitwise_not(closed_edges), cv2.DIST_L2, 5)
    _, smoothed_fill = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, cv2.THRESH_BINARY)

    # **Passo 3: Criar máscara para Flood Fill**
    h, w = closed_edges.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)

    # **Passo 4: Aplicar Flood Fill**
    flood_filled = closed_edges.copy()
    cv2.floodFill(flood_filled, mask, (0, 0), 255)  # Preenche a área externa com branco

    # **Passo 5: Suavizar ainda mais com GaussianBlur**
    filled_result = cv2.bitwise_or(closed_edges, cv2.bitwise_not(flood_filled))
    filled_result = cv2.GaussianBlur(filled_result, (5, 5), 1)  # Suavização final

    # **Passo 6: Ligar pontos extremos das bordas abertas**
    contours, _ = cv2.findContours(filled_result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        # Obter os extremos
        leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
        rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
        topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
        bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])

        # Desenhar linhas para conectar áreas abertas
        cv2.line(filled_result, leftmost, rightmost, 255, 1)
        cv2.line(filled_result, topmost, bottommost, 255, 1)

    # **Passo 7: Salvar a imagem final**
    output_path = image_path.replace("_canny.jpg", "_filled_smooth.jpg")
    cv2.imwrite(output_path, filled_result)

    print(f"Fload Fill processed : {output_path}")
    base_name, _ = os.path.splitext(output_path)
    print(f"Processed image : {base_name}.")

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

    print(f"Continous line  : {output_path}")
    base_name, _ = os.path.splitext(output_path)
    print(f"Processed image : {base_name}.")


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

    fill_gaps(base_name + "_canny.jpg")
    connect_contours(base_name + "_canny.jpg")

    print(f"Processed image {base_name}.")




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

# imagepath = r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\P1_2069_135183.jpg"
# imagepath_nobg = remove_background(imagepath)
# print(f"path da imgem sem bg : {imagepath_nobg}")
# process_image(imagepath_nobg)


for name in file_list:
    imagepath_nobg = remove_background(name)
    print(f"path da imgem sem bg : {imagepath_nobg}")
    process_image(imagepath_nobg)
