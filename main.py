import cv2
import os
import sizeitCalibration as sc  # Importa o módulo de funções

def main():
    # Caminho das imagens
    image_path_calib = "./mnt/data/calibre.png"
    image_path_piece = "./mnt/data/P2_.png"

    # Etapa 1: Calibração
    print("Iniciando calibração...")
    pixel_to_mm_ratio = sc.calibrate(image_path_calib)
    if not pixel_to_mm_ratio:
        print("Erro: Falha na calibração. Verifique a imagem de referência.")
        return
    print(f"Relação de calibração: {pixel_to_mm_ratio:.3f} pixels/mm")

    # Etapa 2: Alinhamento da imagem
    print("Alinhando imagem...")
    aligned_image_path = sc.align_image(image_path_piece)
    if not aligned_image_path:
        print("Erro: Falha no alinhamento da imagem.")
        return

    # Etapa 3: Medir comprimento da peça
    print("Medição do comprimento da peça...")
    length_mm = sc.get_piece_length(aligned_image_path, pixel_to_mm_ratio)
    if length_mm:
        print(f"Comprimento total da peça: {length_mm:.3f} mm")
    
    # Etapa 4: Medir diâmetros em posições específicas
    measure_positions = [10, 20, 30, 40, 50]  # Posições em mm
    print("Medição de diâmetros em posições específicas...")
    diameters = sc.measure_diameters(aligned_image_path, pixel_to_mm_ratio, measure_positions)
    if diameters:
        print("Diâmetros medidos:", diameters)
    
    print("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
