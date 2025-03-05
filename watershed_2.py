import cv2
import numpy as np
import os
import json

# **Criar a interface gráfica antes de acessar os trackbars**
cv2.namedWindow("Watershed Adjust", cv2.WINDOW_NORMAL)
cv2.namedWindow("Controls", cv2.WINDOW_NORMAL)

# **Definir um tamanho inicial para as janelas**
cv2.resizeWindow("Watershed Adjust", 900, 600)
cv2.resizeWindow("Controls", 300, 600)

# Arquivo para armazenar os parâmetros
PARAMS_FILE = "watershed_params.json"

# variaveis que serao usadas no global...
image_path = r"C:\Users\alexandre.panosso\Dropbox\DPro\Microdont\09_Automacao_2025\AMOSTRAS DOS 09 LOTES EOCA\135183\P1_2069_135183.jpg"
display_width = 900
display_height = 600


# Carregar parâmetros salvos ou usar valores padrão
def load_params():
    if os.path.exists(PARAMS_FILE):
        with open(PARAMS_FILE, "r") as f:
            return json.load(f)
    return {"Threshold": 50, "Kernel Size": 3, "Dist Transform Factor": 50}

def save_params():
    """Salva os parâmetros atuais em um arquivo JSON."""
    with open(PARAMS_FILE, "w") as f:
        json.dump(params, f)
    print(f"Parâmetros salvos em {PARAMS_FILE}")

# Inicializar parâmetros
params = load_params()

# Variáveis globais para salvar os resultados
mask = None
result = None

def update_watershed(val=None):
    """Atualiza a segmentação Watershed com base nos parâmetros escolhidos pelo usuário."""
    global mask, result
    
    # Atualizar parâmetros a partir dos trackbars
    params["Threshold"] = cv2.getTrackbarPos("Threshold", "Controls")
    params["Kernel Size"] = max(1, cv2.getTrackbarPos("Kernel Size", "Controls"))
    params["Dist Transform Factor"] = cv2.getTrackbarPos("Dist Transform", "Controls")
    
    # Carregar imagem original
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar um desfoque para suavizar a segmentação
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # **Passo 1: Threshold**
    _, thresh = cv2.threshold(blurred, params["Threshold"], 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # **Passo 2: Aplicar Morfologia para remover ruídos**
    kernel = np.ones((params["Kernel Size"], params["Kernel Size"]), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # **Passo 3: Criar a região segura de fundo**
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # **Passo 4: Criar a região segura de primeiro plano**
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, params["Dist Transform Factor"] * 0.01 * dist_transform.max(), 255, 0)

    # **Passo 5: Encontrar regiões desconhecidas**
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # **Passo 6: Criar marcadores para Watershed**
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # **Passo 7: Aplicar Watershed**
    markers = cv2.watershed(image, markers)
    image[markers == -1] = [0, 0, 255]

    # Criar máscara final
    mask = np.zeros_like(gray)
    mask[markers > 1] = 255

    # **Passo 8: Aplicar a máscara na imagem original**
    result = cv2.bitwise_and(image, image, mask=mask)

    # **Passo 9: Exibir as imagens na interface**
    combined_top = cv2.resize(image, (display_width, display_height // 3))
    combined_middle = cv2.resize(mask, (display_width, display_height // 3))
    combined_bottom = cv2.resize(result, (display_width, display_height // 3))
    
    combined = np.vstack((combined_top, cv2.cvtColor(combined_middle, cv2.COLOR_GRAY2BGR), combined_bottom))
    cv2.imshow("Watershed Adjust", combined)
    cv2.waitKey(1)

def fill_holes_in_mask(mask_path):
    """Preenche apenas as áreas internas da máscara sem afetar as bordas."""
    if not os.path.exists(mask_path):
        print(f"Erro: Arquivo '{mask_path}' não encontrado.")
        return
    
    # Carregar a máscara em escala de cinza
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    
    # Criar uma cópia da máscara para manipulação
    filled_mask = mask.copy()

    # Criar uma máscara extra para Flood Fill (precisa ser 2px maior que a imagem)
    h, w = mask.shape
    floodfill_mask = np.zeros((h + 2, w + 2), np.uint8)

    # Flood Fill começando de um ponto interno (centro da imagem)
    cx, cy = w // 2, h // 2
    if mask[cy, cx] == 0:  # Certifica-se de iniciar no fundo (preto)
        cv2.floodFill(filled_mask, floodfill_mask, (cx, cy), 255)

    # Criar uma máscara dos buracos internos preenchidos
    holes_filled = cv2.bitwise_xor(filled_mask, mask)

    # Combinar a máscara original com os buracos preenchidos (mantendo bordas intactas)
    result_mask = cv2.bitwise_or(mask, holes_filled)

    # Salvar a nova máscara corrigida
    output_path = mask_path.replace("_watershed_mask.jpg", "_full_filled_mask.jpg")
    cv2.imwrite(output_path, result_mask)

    print(f"Máscara interna corrigida e salva em: {output_path}")
    return output_path


def fill_holes_in_mask_old(mask_path):
    """Preenche áreas pretas cercadas por pixels brancos na máscara."""
    if not os.path.exists(mask_path):
        print(f"Erro: Arquivo '{mask_path}' não encontrado.")
        return
    
    # Carregar a máscara em escala de cinza
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    # **Passo 1: Inverter a máscara**
    inverted_mask = cv2.bitwise_not(mask)

    # **Passo 2: Criar uma cópia para manipulação**
    filled_mask = inverted_mask.copy()

    # **Passo 3: Criar uma máscara extra para Flood Fill**
    h, w = mask.shape
    floodfill_mask = np.zeros((h + 2, w + 2), np.uint8)

    # **Passo 4: Aplicar Flood Fill no fundo preto (exterior)**
    cv2.floodFill(filled_mask, floodfill_mask, (0, 0), 255)

    # **Passo 5: Criar a máscara sólida inicial**
    filled_mask = cv2.bitwise_not(filled_mask)
    solid_mask = cv2.bitwise_or(mask, filled_mask)

    # **Passo 6: Detectar buracos internos restantes**
    contours, _ = cv2.findContours(solid_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    # **Passo 7: Preencher todos os contornos internos**
    for cnt in contours:
        cv2.drawContours(solid_mask, [cnt], 0, 255, thickness=cv2.FILLED)

    # **Passo 8: Aplicar operações morfológicas para suavizar**
    kernel = np.ones((5, 5), np.uint8)
    solid_mask = cv2.morphologyEx(solid_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # **Passo 9: Salvar a máscara final**
    output_path = mask_path.replace("_watershed_mask.jpg", "_full_filled_mask.jpg")
    cv2.imwrite(output_path, solid_mask)

    print(f"Máscara totalmente preenchida e salva em: {output_path}")
    return output_path


def save_results():
    """Salva as imagens processadas e os parâmetros."""
    if mask is None or result is None:
        print("Erro: As imagens não foram geradas ainda.")
        return

    base_name, _ = os.path.splitext(image_path)
    mask_path = base_name + "_watershed_mask.jpg"
    result_path = base_name + "_watershed_result.jpg"
    
    cv2.imwrite(mask_path, mask)
    cv2.imwrite(result_path, result)
    
    fill_holes_in_mask(mask_path)
    
    save_params()
    print(f"Resultados salvos:\n- {mask_path}\n- {result_path}")
    
    return mask_path, result_path

# **Criar os Trackbars com callback**
cv2.createTrackbar("Threshold", "Controls", 50, 255, update_watershed)
cv2.createTrackbar("Kernel Size", "Controls", 3, 10, update_watershed)
cv2.createTrackbar("Dist Transform", "Controls", 50, 100, update_watershed)

# **Criar a interface gráfica**

# Atualiza as imagens inicialmente
update_watershed()

# Criar um botão "Salvar Resultado"
while True:
    cv2.imshow("Controls", np.zeros((300, 300, 3), np.uint8))  # Janela vazia para exibir controles
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Tecla ESC para sair
        break
    elif key == ord('s') or key == ord('S'):  # Tecla 's' para salvar
        save_results()

cv2.destroyAllWindows()
