import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
import time
from threading import Thread, Timer
from tkinter import Tk, Button, Label

# Desactivar el fail-safe de PyAutoGUI
pyautogui.FAILSAFE = False

DEBUG = False  # Cambia a False para desactivar la ventana de depuración

screen_width, screen_height = pyautogui.size()
region = (
    (screen_width - 222) // 2,
    (screen_height - 176) // 2,
    200,
    150
)

superposicion_continua = 0
umbral_superposicion = 1  # Número de ciclos de superposición necesarios
umbral_iou = 0.04  # Umbral de IoU mínimo
umbral_area = 10  # Umbral de área mínima para considerar un contorno
umbral_area_minima = 50  # Umbral de área mínima para recalcular el contorno azul

contours_blue_not_exist = True
contours_blue_original = any

running = False

# Nombre de la ventana a la que se enviarán los eventos de mouse
window_name = "FiveM® by Cfx.re - Family RP"

def calcular_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1 + w1, x2 + w2)
    inter_y2 = min(y1 + h1, y2 + h2)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    box1_area = w1 * h1
    box2_area = w2 * h2

    iou = inter_area / float(box1_area + box2_area - inter_area)
    return iou

def mouse_click():
    window = gw.getActiveWindow()
    
    if window.title == window_name:
        pyautogui.mouseDown()
        pyautogui.mouseUp()
    Timer(1, mouse_click).start()  # Reprogramar el temporizador para que se ejecute cada 1000 ms

def process_frame():
    global running, superposicion_continua, DEBUG, contours_blue_not_exist, contours_blue_original

    while True:
        window = gw.getActiveWindow()
        if not running:
            time.sleep(0.1)
            continue
        if window.title != window_name:
            time.sleep(10)
            continue

        start_time = time.time()
        
        screenshot = pyautogui.screenshot(region=region)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 150, 150])
        upper_red = np.array([5, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red, upper_red)

        lower_blue = np.array([100, 150, 150])
        upper_blue = np.array([130, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours_blue_not_exist:
            contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours_blue = contours_blue_original

        c_red = np.array([])
        c_blue = np.array([])

        if contours_red and contours_blue:
            if contours_blue_not_exist:
                contours_blue_original = contours_blue
            contours_blue_not_exist = False
            c_red = max(contours_red, key=cv2.contourArea)
            x_red, y_red, w_red, h_red = cv2.boundingRect(c_red)
            area_red = w_red * h_red

            c_blue = max(contours_blue, key=cv2.contourArea)
            x_blue, y_blue, w_blue, h_blue = cv2.boundingRect(c_blue)
            area_blue = w_blue * h_blue

            if area_blue < umbral_area_minima:
                contours_blue_not_exist = True

            if area_red > umbral_area and area_blue > umbral_area:
                iou = calcular_iou((x_red, y_red, w_red, h_red), (x_blue, y_blue, w_blue, h_blue))
                print(f"IoU: {iou}")  # Mensaje de depuración

                if iou > umbral_iou:
                    superposicion_continua += 1
                else:
                    superposicion_continua = 0

                if superposicion_continua >= umbral_superposicion:
                    pyautogui.press('e')
                    print("Pulsado e")  # Mensaje de depuración
                    superposicion_continua = 0
                    contours_blue_not_exist = True
                    time.sleep(0.1)

        if DEBUG:
            if c_red.size > 0:
                cv2.drawContours(frame, [c_red], -1, (0, 255, 0), 2)
            if c_blue.size > 0:
                cv2.drawContours(frame, [c_blue], -1, (255, 0, 0), 2)
            cv2.imshow('Frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Liberar memoria
        del screenshot, frame, hsv, mask_red, mask_blue, contours_red, contours_blue

        end_time = time.time()
        #print(f"Frame processing time: {end_time - start_time} seconds")

    cv2.destroyAllWindows()

def start_processing():
    global running
    running = True
    status_label.config(text="Status: Play")
    mouse_click()  # Iniciar el temporizador para los clics del ratón

def stop_processing():
    global running
    running = False
    status_label.config(text="Status: Pause")

def toggle_debug():
    global DEBUG
    DEBUG = not DEBUG
    debug_label.config(text=f"DEBUG: {DEBUG}")

# Crear la interfaz gráfica
root = Tk()
root.title("Control de Procesamiento")
root.geometry("400x300")  # Ajustar el tamaño de la ventana

start_button = Button(root, text="Play", command=start_processing, width=20, height=2)
start_button.pack(pady=10)

stop_button = Button(root, text="Pause", command=stop_processing, width=20, height=2)
stop_button.pack(pady=10)

debug_button = Button(root, text="Toggle DEBUG", command=toggle_debug, width=20, height=2)
debug_button.pack(pady=10)

debug_label = Label(root, text=f"DEBUG: {DEBUG}", font=("Helvetica", 12))
debug_label.pack(pady=10)

status_label = Label(root, text="Status: Pause", font=("Helvetica", 12))
status_label.pack(pady=10)

# Iniciar el hilo de procesamiento de frames
thread = Thread(target=process_frame)
thread.daemon = True
thread.start()

root.mainloop()