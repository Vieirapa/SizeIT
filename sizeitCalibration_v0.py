import cv2
import numpy as np
import csv
from datetime import datetime

# Variável global para o fator de escala do texto
TEXT_SCALE_FACTOR = 800
LOG_FILE = "SizeIT_log.csv"

def set_text_scale(factor):
    global TEXT_SCALE_FACTOR
    TEXT_SCALE_FACTOR = factor
    print(f"Escala do texto ajustada para: {TEXT_SCALE_FACTOR}")

def get_text_scale(w, h):
    return max(max(w, h) / TEXT_SCALE_FACTOR, 0.5)  # O mínimo será 0.5

def log_measurement(image_name, measurement_type, values):
    """
    Registra as medições em um arquivo CSV.
    
    :param image_name: Nome da imagem analisada
    :param measurement_type: Tipo de medição (Comprimento ou Diâmetro)
    :param values: Lista de valores medidos
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Criar cabeçalho se o arquivo for novo
        if file.tell() == 0:
            writer.writerow(["Timestamp", "Imagem", "Tipo", "Valores"])
        
        writer.writerow([timestamp, image_name, measurement_type, values])

def calibrate(image_path, real_diameter_mm=10, canny_threshold1=30, canny_threshold2=100, gaussian_blur_size=5, hough_param2=20, dp=1.0, minDist=100, minRadius=50, maxRadius=500):
    # Carregar a imagem de calibração
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar um filtro Gaussiano para suavizar a imagem
    blurred = cv2.GaussianBlur(gray, (gaussian_blur_size, gaussian_blur_size), 0)
    
    # Detectar bordas usando Canny com parâmetros ajustáveis
    edges = cv2.Canny(blurred, canny_threshold1, canny_threshold2)
    
    # Detectar círculos usando a Transformada de Hough com parâmetros ajustáveis
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
                                param1=canny_threshold2, param2=hough_param2, minRadius=minRadius, maxRadius=maxRadius)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, radius = circle
            diameter_pixels = radius * 2
            
            # Calcular a relação pixels/mm
            pixel_per_mm = diameter_pixels / real_diameter_mm
            
            print(f"Diâmetro detectado (pixels): {diameter_pixels}")
            print(f"Relação pixels/mm: {pixel_per_mm}")
            
            return pixel_per_mm
    
    print("Nenhum círculo detectado!")
    return None

def align_image(image_path):
    # Carregar a imagem
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar um filtro Gaussiano para suavizar a imagem
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detectar bordas usando Canny
    edges = cv2.Canny(blurred, 50, 150)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print("Nenhum contorno detectado!")
        return None
    
    # Selecionar o maior contorno (presumindo que seja a peça)
    contour = max(contours, key=cv2.contourArea)
    
    # Obter a caixa delimitadora rotacionada
    rect = cv2.minAreaRect(contour)
    angle = rect[-1]
    
    # Ajustar o ângulo corretamente para manter a peça na horizontal
    if angle < -45:
        angle += 90
    elif angle > 45:
        angle -= 90
    
    # Rotacionar a imagem
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    # Salvar a imagem alinhada
    output_path = image_path.replace(".png", "_ALIGN.png")
    cv2.imwrite(output_path, rotated)
    print(f"Imagem alinhada salva como: {output_path}")
    
    return output_path

def get_piece_length(image_path, pixel_to_mm_ratio):
    # Carregar a imagem
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar um filtro Gaussiano para suavizar a imagem
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detectar bordas usando Canny
    edges = cv2.Canny(blurred, 50, 150)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print("Nenhum contorno detectado!")
        return None
    
    # Selecionar o maior contorno (presumindo que seja a peça)
    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)
    
    # Converter largura de pixels para mm (usando w para o comprimento)
    length_mm = w / pixel_to_mm_ratio
    print(f"Comprimento total da peça: {length_mm:.3f}mm")
    
    # Registrar no log
    log_measurement(image_path, "Comprimento Total", [length_mm])
    
        # Criar uma cópia da imagem para sobrepor a linha de comprimento
    output_image = image.copy()
    font_scale = get_text_scale(w, h)
    cv2.line(output_image, (x, y + h // 2), (x + w, y + h // 2), (255, 0, 0), 2)
    cv2.putText(output_image, f"{length_mm:.3f}mm", (x + w // 2, y + h // 2 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), 2, cv2.LINE_AA)
    
    # Salvar a imagem com a linha sobreposta
    output_path = image_path.replace(".png", "_L.png")
    cv2.imwrite(output_path, output_image)
    print(f"Imagem salva com comprimento identificado: {output_path}")
    
    return length_mm

def measure_diameters(image_path, pixel_to_mm_ratio, positions_mm):
    # Carregar a imagem
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar um filtro Gaussiano para suavizar a imagem
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detectar bordas usando Canny
    edges = cv2.Canny(blurred, 50, 150)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print("Nenhum contorno detectado!")
        return None
    
    # Selecionar o maior contorno (presumindo que seja a peça)
    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)
    
    # Criar uma lista de medições para o log
    measurements = []
    
    for pos_mm in positions_mm:
        pos_px = int(pos_mm * pixel_to_mm_ratio)
        x_pos = x + pos_px
        
        # Encontrar a largura da peça na posição especificada
        scan_line = np.where(edges[:, x_pos] > 0)[0]
        if len(scan_line) >= 2:
            diameter_px = scan_line[-1] - scan_line[0]
            diameter_mm = diameter_px / pixel_to_mm_ratio
            measurements.append(diameter_mm)
    
     # Criar uma cópia da imagem para sobrepor as medições
    output_image = image.copy()
    
    for pos_mm in positions_mm:
        pos_px = int(pos_mm * pixel_to_mm_ratio)
        x_pos = x + pos_px
        
        # Encontrar a largura da peça na posição especificada
        scan_line = np.where(edges[:, x_pos] > 0)[0]
        if len(scan_line) >= 2:
            diameter_px = scan_line[-1] - scan_line[0]
            diameter_mm = diameter_px / pixel_to_mm_ratio
            
            # Desenhar linha vertical indicando a medição
            cv2.line(output_image, (x_pos, scan_line[0]), (x_pos, scan_line[-1]), (0, 255, 0), 2)
            font_scale = get_text_scale(w, h)
            cv2.putText(output_image, f"{diameter_mm:.2f}mm", (x_pos + 5, scan_line[0] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), 1, cv2.LINE_AA)
    
    # Salvar a imagem com as medições sobrepostas
    output_path = image_path.replace(".png", "_M.png")
    cv2.imwrite(output_path, output_image)
    print(f"Imagem salva com medições de diâmetro: {output_path}")
    
    # Registrar no log
    log_measurement(image_path, "Diâmetros", measurements)
    
    return measurements, output_path

"""
image_path_calib = "./mnt/data/calibre.png"
pixel_to_mm_ratio = calibrate(image_path_calib)
if pixel_to_mm_ratio:
    image_path_piece = align_image("./mnt/data/P1.png")
    if image_path_piece:
        tamanho = get_piece_length(image_path_piece, pixel_to_mm_ratio)
        print(f"Tamnho medido :{tamanho}")
        #measure_positions = [10, 20, 30, 40, 50]
        passo = 30
        measure_positions = np.arange(tamanho/passo, tamanho + (tamanho/passo), tamanho/passo)
        medidas = measure_diameters(image_path_piece, pixel_to_mm_ratio, measure_positions)
        print(f"Medidas:{medidas}")
"""
