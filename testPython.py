import pyautogui
import cv2
import numpy as np
import time

screen_width, screen_height = pyautogui.size()
# Definir la región de la pantalla a capturar
region = (
    (screen_width - 222) // 2,  # Coordenada X para centrar
    (screen_height - 176) // 2, # Coordenada Y para centrar
    200,                        # Ancho de la región 222
    150                         # Alto de la región 176
)

while True:
    # Capturar la región de la pantalla
    screenshot = pyautogui.screenshot(region=region)
    # Convertir la imagen a un formato compatible con OpenCV
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Convertir la imagen al espacio de color HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detectar el color rojo
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)

    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # Detectar el color azul
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Encontrar contornos
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours_red and contours_blue:
        # Contorno más grande para el rojo
        c_red = max(contours_red, key=cv2.contourArea)
        x_red, y_red, w_red, h_red = cv2.boundingRect(c_red)

        # Contorno más grande para el azul
        c_blue = max(contours_blue, key=cv2.contourArea)
        x_blue, y_blue, w_blue, h_blue = cv2.boundingRect(c_blue)

        # Verificar superposición
        if (x_red < x_blue + w_blue and
            x_red + w_red > x_blue and
            y_red < y_blue + h_blue and
            y_red + h_red > y_blue):
            # Presionar 'e' si hay superposición
            time.sleep(0.02)
            pyautogui.press('e')
            print("Pulsado e")
            time.sleep(0.1)  # Ajusta según sea necesario

    # Mostrar imagen (opcional)
    cv2.drawContours(frame, [c_red], -1, (0, 255, 0), 2)
    cv2.drawContours(frame, [c_blue], -1, (255, 0, 0), 2)
    cv2.imshow('Frame', frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

