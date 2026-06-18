# main.py (KONSOLEN-DEBUGGER)
from machine import Pin
from neopixel import NeoPixel
import sys

# =======================================================
# 1. KONFIGURATION
# =======================================================
LED_PIN = 13       # LED-Datenkabel an Pin 13
NUM_LEDS = 241     # Gesamte Anzahl der LEDs

# --- GLOBAL BRIGHTNESS CONTROL ---
# 0.0 = completely off, 1.0 = maximum brightness
BRIGHTNESS = 1.0   # Set it to 50% brightness here
# ---------------------------------

ZONE_RANGES = [
    [0, 1, 2, 50, 51, 52, 100, 101],                 # Layer 1: Cluster A
    [12, 13, 14, 80, 81, 82, 150, 151, 152],         # Layer 2: Cluster B
    [3, 4, 5, 20, 21, 22, 200, 201, 202, 203],       # Layer 3: Cluster C
    [6, 7, 8, 9, 30, 31, 32, 110, 111, 112],         # Layer 4: Cluster D
    [10, 11, 40, 41, 42, 120, 240]                   # Layer 5: Cluster E
]

# ZONE_RANGES = [
#     range(0, 48),    # Layer 1
#     range(48, 96),   # Layer 2
#     range(96, 144),  # Layer 3
#     range(144, 192), # Layer 4
#     range(192, 241), # Layer 5
# ]


# =======================================================
# 2. DATA-COLORS 
# =======================================================
YEARS = [2004, 2009, 2014, 2019, 2024]

DEBUG_BLAUTOENE = [
    [(0, 0, 20),  (0, 0, 40),  (0, 0, 60),  (0, 0, 80),  (0, 0, 100)], # 2004
    [(0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255)], # 2009
    [(0, 0, 150), (0, 0, 20),  (0, 0, 150), (0, 0, 20),  (0, 0, 150)], # 2014
    [(0, 0, 50),  (0, 0, 100), (0, 0, 150), (0, 0, 200), (0, 0, 250)], # 2019
    [(0, 0, 250), (0, 0, 200), (0, 0, 150), (0, 0, 100), (0, 0, 50)],  # 2024
]

# =======================================================
# 3. SETUP Hardware
# =======================================================
np = NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)

def clear_leds():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

def zeige_jahr(jahr_index):
    colors = DEBUG_BLAUTOENE[jahr_index]
    
    for layer_index in range(5):
        original_color = colors[layer_index]
        
        # Calculate new scaled colors based on BRIGHTNESS
        # int() ensures we don't send float values to the NeoPixel
        scaled_color = (
            int(original_color[0] * BRIGHTNESS),
            int(original_color[1] * BRIGHTNESS),
            int(original_color[2] * BRIGHTNESS)
        )
        
        for led_index in ZONE_RANGES[layer_index]:
            if 0 <= led_index < NUM_LEDS:
                np[led_index] = scaled_color
                
    np.write()
    print(f"\n[OK] LEDs aktualisiert für das Jahr: {YEARS[jahr_index]} (Helligkeit: {BRIGHTNESS*100}%)")
    print(f"-> Skalierte Blauwerte der 5 Layer: {[int(c[2]*BRIGHTNESS) for c in colors]}")

# =======================================================
# 4. KONSOLEN-LOOP
# =======================================================
clear_leds()
print("==================================================")
print("KONSOLEN-DEBUGGER GESTARTET.")
print("Gib im Thonny-Terminal eine Zahl ein und drücke ENTER:")
print("0 = 2004 | 1 = 2009 | 2 = 2014 | 3 = 2019 | 4 = 2024")
print("==================================================")

zeige_jahr(0)

while True:
    eingabe = input("\nWähle Index (0-4): ").strip()
    
    if eingabe in ["0", "1", "2", "3", "4"]:
        idx = int(eingabe)
        zeige_jahr(idx)
    else:
        print("[FEHLER] Ungültige Eingabe! Bitte nur Zahlen von 0 bis 4 eintippen.")