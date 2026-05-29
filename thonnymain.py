# main.py
# ESP32 + MicroPython + NeoPixel/WS2812 + 5 Buttons
# Für Thonny auf den ESP32 speichern als: main.py

from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms

# =======================================================
# 1. HIER MORGEN ANPASSEN
# =======================================================

# Pin, an dem DIN/Data-In vom LED-Board hängt
LED_PIN = XX

# Gesamtanzahl der LEDs auf eurem Board/Streifen
NUM_LEDS = XX

# Pins der 5 Buttons in dieser Reihenfolge:
# Button 1 = 2004
# Button 2 = 2009
# Button 3 = 2014
# Button 4 = 2019
# Button 5 = 2024
BUTTON_PINS = [XX, XX, XX, XX, XX]

# Button-Schaltung:
# Standard hier: Button verbindet GPIO mit GND, deshalb PULL_UP und gedrückt = 0.
# Falls eure Buttons andersrum mit 3.3V arbeiten: siehe Kommentar weiter unten.
BUTTON_ACTIVE_VALUE = 0
BUTTON_PULL = Pin.PULL_UP

# LEDs unter den 5 Plexiglas-Layern.
# Morgen müsst ihr hier eintragen, welche LED-Indizes unter welchem Layer liegen.
#
# Variante A: Wenn LEDs schön linear aufgeteilt sind:
# ZONE_RANGES = [
#     range(0, 5),
#     range(5, 10),
#     range(10, 15),
#     range(15, 20),
#     range(20, 25),
# ]
#
# Variante B: Wenn die LEDs unregelmäßig unter den Formen liegen:
# ZONE_RANGES = [
#     [0, 1, 2, 7, 8],
#     [3, 4, 5, 9, 10],
#     [6, 11, 12, 13],
#     [14, 15, 16, 17],
#     [18, 19, 20, 21, 22],
# ]

ZONE_RANGES = [
    range(XX, XX),  # Layer 1: 100-250m
    range(XX, XX),  # Layer 2: 250-400m
    range(XX, XX),  # Layer 3: 400-600m
    range(XX, XX),  # Layer 4: 600-750m
    range(XX, XX),  # Layer 5: 750-900m
]

# Wählt hier, welchen Datensatz / Modus ihr testen wollt:
#
# "atlantic_normal"
# "atlantic_inverted"
# "peru_normal"
# "peru_inverted"
#
# Empfehlung für finale Version wahrscheinlich:
# DATA_MODE = "peru_normal"

DATA_MODE = "XX"

# Gesamthelligkeit, falls es zu grell ist.
# 1.0 = volle Werte aus Data Mapping
# 0.5 = halb so hell
BRIGHTNESS_SCALE = XX


# =======================================================
# 2. DATA MAPPING AUS EURER TXT
# =======================================================

YEARS = [2004, 2009, 2014, 2019, 2024]
LAYER_LABELS = ['100-250m', '250-400m', '400-600m', '600-750m', '750-900m']

# Eastern Tropical Atlantic | normal
# normal: more O2 = more blue
DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_NORMAL = [
    [(0, 0, 148), (0, 0, 59), (0, 0, 90), (0, 0, 188), (0, 0, 251)],  # 2004
    [(0, 0, 144), (0, 0, 59), (0, 0, 94), (0, 0, 193), (0, 0, 255)],  # 2009
    [(0, 0, 146), (0, 0, 58), (0, 0, 90), (0, 0, 188), (0, 0, 250)],  # 2014
    [(0, 0, 144), (0, 0, 54), (0, 0, 87), (0, 0, 185), (0, 0, 246)],  # 2019
    [(0, 0, 147), (0, 0, 51), (0, 0, 79), (0, 0, 177), (0, 0, 243)],  # 2024
]

# Eastern Tropical Atlantic | inverted
# inverted: less O2 = more blue
DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_INVERTED = [
    [(0, 0, 158), (0, 0, 247), (0, 0, 216), (0, 0, 118), (0, 0, 55)],  # 2004
    [(0, 0, 162), (0, 0, 247), (0, 0, 212), (0, 0, 113), (0, 0, 51)],  # 2009
    [(0, 0, 160), (0, 0, 248), (0, 0, 216), (0, 0, 118), (0, 0, 56)],  # 2014
    [(0, 0, 162), (0, 0, 252), (0, 0, 219), (0, 0, 121), (0, 0, 60)],  # 2019
    [(0, 0, 159), (0, 0, 255), (0, 0, 227), (0, 0, 129), (0, 0, 63)],  # 2024
]

# Peru-Chile OMZ / Eastern Tropical South Pacific | normal
# normal: more O2 = more blue
DATA_COLORS_PERU_CHILE_OMZ_NORMAL = [
    [(0, 0, 238), (0, 0, 51), (0, 0, 56), (0, 0, 116), (0, 0, 165)],  # 2004
    [(0, 0, 235), (0, 0, 51), (0, 0, 55), (0, 0, 113), (0, 0, 164)],  # 2009
    [(0, 0, 231), (0, 0, 53), (0, 0, 58), (0, 0, 112), (0, 0, 161)],  # 2014
    [(0, 0, 240), (0, 0, 55), (0, 0, 59), (0, 0, 112), (0, 0, 160)],  # 2019
    [(0, 0, 255), (0, 0, 55), (0, 0, 63), (0, 0, 113), (0, 0, 163)],  # 2024
]

# Peru-Chile OMZ / Eastern Tropical South Pacific | inverted
# inverted: less O2 = more blue
DATA_COLORS_PERU_CHILE_OMZ_INVERTED = [
    [(0, 0, 68), (0, 0, 255), (0, 0, 250), (0, 0, 190), (0, 0, 141)],  # 2004
    [(0, 0, 71), (0, 0, 255), (0, 0, 251), (0, 0, 193), (0, 0, 142)],  # 2009
    [(0, 0, 75), (0, 0, 253), (0, 0, 248), (0, 0, 194), (0, 0, 145)],  # 2014
    [(0, 0, 66), (0, 0, 251), (0, 0, 247), (0, 0, 194), (0, 0, 146)],  # 2019
    [(0, 0, 51), (0, 0, 251), (0, 0, 243), (0, 0, 193), (0, 0, 143)],  # 2024
]


# =======================================================
# 3. MODE AUSWÄHLEN
# =======================================================

DATASETS = {
    "atlantic_normal": DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_NORMAL,
    "atlantic_inverted": DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_INVERTED,
    "peru_normal": DATA_COLORS_PERU_CHILE_OMZ_NORMAL,
    "peru_inverted": DATA_COLORS_PERU_CHILE_OMZ_INVERTED,
}

if DATA_MODE not in DATASETS:
    raise ValueError("DATA_MODE ist ungültig. Nutze: atlantic_normal, atlantic_inverted, peru_normal oder peru_inverted.")

DATA_COLORS = DATASETS[DATA_MODE]


# =======================================================
# 4. SETUP
# =======================================================

np = NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)

buttons = [
    Pin(pin_number, Pin.IN, BUTTON_PULL)
    for pin_number in BUTTON_PINS
]

current_button_index = 0


# =======================================================
# 5. HILFSFUNKTIONEN
# =======================================================

def scale_color(color):
    """Skaliert RGB-Werte global herunter, falls es zu hell ist."""
    r, g, b = color
    r = int(r * BRIGHTNESS_SCALE)
    g = int(g * BRIGHTNESS_SCALE)
    b = int(b * BRIGHTNESS_SCALE)
    return (r, g, b)


def clear_leds():
    """Alle LEDs ausschalten."""
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()


def set_zone(layer_index, color):
    """
    Setzt alle LEDs, die zu einem Plexiglas-Layer gehören.
    layer_index: 0 bis 4
    color: (r, g, b)
    """
    color = scale_color(color)

    for led_index in ZONE_RANGES[layer_index]:
        if 0 <= led_index < NUM_LEDS:
            np[led_index] = color


def show_year(button_index):
    """
    Zeigt einen Jahreszustand.
    button_index:
    0 = 2004
    1 = 2009
    2 = 2014
    3 = 2019
    4 = 2024
    """
    colors_for_year = DATA_COLORS[button_index]

    for layer_index in range(5):
        set_zone(layer_index, colors_for_year[layer_index])

    np.write()

    print("DATA_MODE:", DATA_MODE)
    print("Showing year:", YEARS[button_index])
    print("Layer colors:", colors_for_year)


def fade_to_year(button_index, steps=20, delay_ms=20):
    """
    Weicher Übergang zum neuen Jahr.
    """
    target_colors = DATA_COLORS[button_index]

    start_pixels = [np[i] for i in range(NUM_LEDS)]
    target_pixels = [(0, 0, 0)] * NUM_LEDS

    for layer_index in range(5):
        target_color = scale_color(target_colors[layer_index])

        for led_index in ZONE_RANGES[layer_index]:
            if 0 <= led_index < NUM_LEDS:
                target_pixels[led_index] = target_color

    for step in range(1, steps + 1):
        t = step / steps

        for i in range(NUM_LEDS):
            sr, sg, sb = start_pixels[i]
            tr, tg, tb = target_pixels[i]

            r = int(sr + (tr - sr) * t)
            g = int(sg + (tg - sg) * t)
            b = int(sb + (tb - sb) * t)

            np[i] = (r, g, b)

        np.write()
        sleep_ms(delay_ms)


def read_buttons():
    """
    Prüft, ob einer der 5 Buttons gedrückt wurde.
    Gibt Button-Index 0 bis 4 zurück oder None.
    """
    for idx, button in enumerate(buttons):
        if button.value() == BUTTON_ACTIVE_VALUE:
            sleep_ms(40)  # debounce
            if button.value() == BUTTON_ACTIVE_VALUE:
                return idx
    return None


def wait_until_released(button_index):
    """
    Wartet, bis gedrückter Button losgelassen wird.
    Verhindert mehrfaches Auslösen.
    """
    while buttons[button_index].value() == BUTTON_ACTIVE_VALUE:
        sleep_ms(20)


def startup_test():
    """
    Kurzer Starttest: alle Zonen einmal schwach blau.
    Hilft morgen zu prüfen, ob LED_PIN und NUM_LEDS stimmen.
    """
    test_color = scale_color((0, 0, 80))

    for layer_index in range(5):
        set_zone(layer_index, test_color)
        np.write()
        sleep_ms(250)

    sleep_ms(300)
    clear_leds()


# =======================================================
# 6. START
# =======================================================

clear_leds()
startup_test()
show_year(current_button_index)


# =======================================================
# 7. LOOP
# =======================================================

while True:
    pressed = read_buttons()

    if pressed is not None and pressed != current_button_index:
        current_button_index = pressed
        fade_to_year(current_button_index)
        wait_until_released(pressed)

    sleep_ms(20)