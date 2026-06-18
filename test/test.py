# main.py
# ESP32 + MicroPython + NeoPixel/WS2812
# Ocean O2 Data Physicalisation
# 5 Buttons = 5 Jahre
# 5 Plexiglas-Layer = 5 Tiefenzonen
# Bottom-Layer wird zuerst gezeichnet, Datenlayer danach.

from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms

# =======================================================
# 1. HARDWARE-KONFIGURATION
# =======================================================

LED_PIN = 13
NUM_LEDS = 241

# Button-Pins von GND aus nach links:
# Button 1 = 2004
# Button 2 = 2009
# Button 3 = 2014
# Button 4 = 2019
# Button 5 = 2024
BUTTON_PINS = [19, 18, 5, 17, 16]

# Annahme: Button verbindet GPIO mit GND.
# gedrückt = 0, nicht gedrückt = 1
BUTTON_ACTIVE_VALUE = 0
BUTTON_PULL = Pin.PULL_UP

# Globaler Helligkeitsregler:
# 1.0 = volle Datenwerte
# 0.5 = halb so hell
# 0.3 = weicher / weniger Hotspots
BRIGHTNESS = 1

# Wenn ihr lieber ohne Fade testen wollt: False
# Wenn ihr weiche Übergänge wollt: True
USE_FADE = False

# Weißer Bottom-Layer / Basislicht
WEISS = (20, 20, 20)

# =======================================================
# 1. HARDWARE-KONFIGURATION (PROZENTUAL & LÜCKENLOS)
# =======================================================

LED_PIN = 13
NUM_LEDS = 241

BUTTON_PINS = [19, 18, 5, 17, 16]
BUTTON_ACTIVE_VALUE = 0
BUTTON_PULL = Pin.PULL_UP
BRIGHTNESS = 0.5

# Weißer Bottom-Layer / Basislicht (32 LEDs)
BOTTOM_LAYER = [
    28, 29, 30, 31, 32, 84, 85, 86, 129, 130, 165, 166, 167, 168, 169,
    181, 191, 192, 193, 194, 195, 210, 211, 212, 213, 214, 224, 225,
    226, 227, 235, 236
]

# Die verbleibenden 209 Daten-LEDs – jede Zahl existiert exakt 1x!
ZONE_RANGES = [
    # Layer 1: 100-250m (45 LEDs -> Doppelte 126 bereinigt, Lücken geschlossen)
    [14, 15, 26, 27, 33, 34, 82, 83, 121, 123, 124, 125, 127, 128, 134, 135, 136, 137, 138, 158, 159, 160, 161, 162, 163, 164, 170, 171, 182, 186, 196, 197, 199, 205, 206, 209, 215, 221, 222, 223, 228, 232, 233, 234, 237, 240],

    # Layer 2: 250-400m (53 LEDs)
    [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 87, 88, 89, 90, 91, 92, 93, 94, 95, 117, 122, 131, 132, 133, 150, 151, 152, 153, 154, 155, 172, 183, 184, 185, 187, 188, 189, 190, 198, 201, 202, 203, 204, 207, 208, 216, 217, 229, 230, 231, 238, 239],

    # Layer 3: 400-600m (36 LEDs)
    [18, 19, 20, 21, 22, 23, 24, 25, 73, 74, 75, 76, 77, 79, 80, 81, 96, 97, 98, 109, 110, 111, 112, 113, 114, 118, 119, 120, 126, 139, 140, 148, 149, 156, 180, 200, 218],

    # Layer 4: 600-750m (30 LEDs -> Doppelte Einträge am Ende entfernt)
    [6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 48, 49, 65, 66, 67, 68, 69, 70, 71, 72, 99, 115, 116, 141, 142, 143, 173, 174, 175, 176, 219],

    # Layer 5: 750-900m (45 LEDs)
    [0, 1, 2, 3, 4, 5, 46, 47, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 78, 100, 101, 102, 103, 104, 105, 106, 107, 108, 144, 145, 146, 147, 177, 178, 179]
]


# =======================================================
# 2. DATA MAPPING V2
# =======================================================

YEARS = [2004, 2009, 2014, 2019, 2024]
LAYER_LABELS = ['100-250m', '250-400m', '400-600m', '600-750m', '750-900m']

# Eastern Tropical Atlantic | normal
# normal: more O2 = more blue
DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_NORMAL = [
    [(0, 35, 148), (0, 14, 59), (0, 21, 90), (0, 44, 188), (0, 59, 251)],  # 2004
    [(0, 34, 144), (0, 14, 59), (0, 22, 94), (0, 45, 193), (0, 60, 255)],  # 2009
    [(0, 34, 146), (0, 14, 58), (0, 21, 90), (0, 44, 188), (0, 59, 250)],  # 2014
    [(0, 34, 144), (0, 13, 54), (0, 20, 87), (0, 43, 185), (0, 58, 246)],  # 2019
    [(0, 35, 147), (0, 12, 51), (0, 19, 79), (0, 42, 177), (0, 57, 243)],  # 2024
]

# Eastern Tropical Atlantic | inverted
# inverted: less O2 = more blue
DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_INVERTED = [
    [(0, 37, 158), (0, 58, 247), (0, 51, 216), (0, 28, 118), (0, 13, 55)],  # 2004
    [(0, 38, 162), (0, 58, 247), (0, 50, 212), (0, 27, 113), (0, 12, 51)],  # 2009
    [(0, 38, 160), (0, 58, 248), (0, 51, 216), (0, 28, 118), (0, 13, 56)],  # 2014
    [(0, 38, 162), (0, 59, 252), (0, 52, 219), (0, 29, 121), (0, 14, 60)],  # 2019
    [(0, 37, 159), (0, 60, 255), (0, 53, 227), (0, 30, 129), (0, 15, 63)],  # 2024
]

# Peru-Chile OMZ / Eastern Tropical South Pacific | normal
# normal: more O2 = more blue
DATA_COLORS_PERU_CHILE_OMZ_NORMAL = [
    [(0, 56, 238), (0, 12, 51), (0, 13, 56), (0, 27, 116), (0, 39, 165)],  # 2004
    [(0, 55, 235), (0, 12, 51), (0, 13, 55), (0, 27, 113), (0, 39, 164)],  # 2009
    [(0, 54, 231), (0, 13, 53), (0, 14, 58), (0, 26, 112), (0, 38, 161)],  # 2014
    [(0, 56, 240), (0, 13, 55), (0, 14, 59), (0, 26, 112), (0, 38, 160)],  # 2019
    [(0, 60, 255), (0, 13, 55), (0, 15, 63), (0, 27, 113), (0, 38, 163)],  # 2024
]

# Peru-Chile OMZ / Eastern Tropical South Pacific | inverted
# inverted: less O2 = more blue
DATA_COLORS_PERU_CHILE_OMZ_INVERTED = [
    [(0, 16, 68), (0, 60, 255), (0, 59, 250), (0, 45, 190), (0, 33, 141)],  # 2004
    [(0, 17, 71), (0, 60, 255), (0, 59, 251), (0, 45, 193), (0, 33, 142)],  # 2009
    [(0, 18, 75), (0, 59, 253), (0, 58, 248), (0, 46, 194), (0, 34, 145)],  # 2014
    [(0, 16, 66), (0, 59, 251), (0, 58, 247), (0, 46, 194), (0, 34, 146)],  # 2019
    [(0, 12, 51), (0, 59, 251), (0, 57, 243), (0, 45, 193), (0, 34, 143)],  # 2024
]

DATASETS = {
    "m0": {
        "name": "Eastern Tropical Atlantic | normal | mehr O2 = mehr Blau",
        "colors": DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_NORMAL
    },
    "m1": {
        "name": "Eastern Tropical Atlantic | inverted | weniger O2 = mehr Blau",
        "colors": DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_INVERTED
    },
    "m2": {
        "name": "Peru-Chile OMZ | normal | mehr O2 = mehr Blau",
        "colors": DATA_COLORS_PERU_CHILE_OMZ_NORMAL
    },
    "m3": {
        "name": "Peru-Chile OMZ | inverted | weniger O2 = mehr Blau",
        "colors": DATA_COLORS_PERU_CHILE_OMZ_INVERTED
    },
}

# Startmodus:
# m2 = Peru-Chile OMZ normal
current_mode_key = "m2"
current_year_index = 0

# =======================================================
# 3. SETUP
# =======================================================

np = NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)

buttons = [
    Pin(pin_number, Pin.IN, BUTTON_PULL)
    for pin_number in BUTTON_PINS
]

# =======================================================
# 4. HILFSFUNKTIONEN
# =======================================================

def scale_color(color):
    r, g, b = color
    return (
        int(r * BRIGHTNESS),
        int(g * BRIGHTNESS),
        int(b * BRIGHTNESS)
    )


def clear_leds():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()


def set_led_list(led_list, color):
    scaled = scale_color(color)

    for led_idx in led_list:
        if 0 <= led_idx < NUM_LEDS:
            np[led_idx] = scaled


def set_layer(layer_index, color):
    set_led_list(ZONE_RANGES[layer_index], color)


def draw_bottom_layer():
    set_led_list(BOTTOM_LAYER, WEISS)


def build_target_pixels(layer_colors):
    """
    Baut ein komplettes Zielbild für alle LEDs.
    Wichtig:
    1. Erst alles schwarz.
    2. Dann Bottom-Layer weiß.
    3. Danach Datenlayer darüber.
    Dadurch bleiben die Datenlayer sichtbar.
    """
    target_pixels = [(0, 0, 0)] * NUM_LEDS

    # Bottom zuerst
    bottom_scaled = scale_color(WEISS)
    for led_idx in BOTTOM_LAYER:
        if 0 <= led_idx < NUM_LEDS:
            target_pixels[led_idx] = bottom_scaled

    # Datenlayer danach
    for layer_index in range(5):
        target_color = scale_color(layer_colors[layer_index])

        for led_idx in ZONE_RANGES[layer_index]:
            if 0 <= led_idx < NUM_LEDS:
                target_pixels[led_idx] = target_color

    return target_pixels


def write_pixels(pixel_list):
    for i in range(NUM_LEDS):
        np[i] = pixel_list[i]
    np.write()


def show_layer_colors(layer_colors, label=""):
    target_pixels = build_target_pixels(layer_colors)
    write_pixels(target_pixels)

    print("")
    print("AKTIV:", label)
    print("Layer-Farben L1 bis L5:", layer_colors)
    print("Bottom-Layer:", WEISS)
    print("Brightness:", BRIGHTNESS)


def show_year(year_index):
    global current_year_index

    current_year_index = year_index

    dataset = DATASETS[current_mode_key]
    colors = dataset["colors"][year_index]
    year = YEARS[year_index]

    show_layer_colors(
        colors,
        dataset["name"] + " | Jahr " + str(year)
    )


def fade_to_year(year_index, steps=20, delay_ms=20):
    global current_year_index

    dataset = DATASETS[current_mode_key]
    target_colors = dataset["colors"][year_index]

    start_pixels = [np[i] for i in range(NUM_LEDS)]
    target_pixels = build_target_pixels(target_colors)

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

    current_year_index = year_index

    print("")
    print("AKTIV:", dataset["name"], "| Jahr", YEARS[year_index])
    print("Layer-Farben L1 bis L5:", target_colors)


def read_buttons():
    for idx, button in enumerate(buttons):
        if button.value() == BUTTON_ACTIVE_VALUE:
            sleep_ms(40)  # debounce
            if button.value() == BUTTON_ACTIVE_VALUE:
                return idx
    return None


def wait_until_released(button_index):
    while buttons[button_index].value() == BUTTON_ACTIVE_VALUE:
        sleep_ms(20)


def print_help():
    print("")
    print("==================================================")
    print("OCEAN O2 DATA PHYSICALISATION")
    print("ESP32 / NeoPixel / 5 Buttons / 5 Layer")
    print("==================================================")
    print("Button-Pins:", BUTTON_PINS)
    print("Button 1 = 2004")
    print("Button 2 = 2009")
    print("Button 3 = 2014")
    print("Button 4 = 2019")
    print("Button 5 = 2024")
    print("")
    print("Aktueller Datenmodus:", current_mode_key)
    print(DATASETS[current_mode_key]["name"])
    print("")
    print("Brightness:", BRIGHTNESS)
    print("Use fade:", USE_FADE)
    print("==================================================")


# =======================================================
# 5. START
# =======================================================

clear_leds()
print_help()
show_year(current_year_index)

# =======================================================
# 6. LOOP: BUTTON-STEUERUNG
# =======================================================

while True:
    pressed = read_buttons()

    if pressed is not None:
        print("Button erkannt:", pressed + 1, "-> Jahr:", YEARS[pressed])

        if USE_FADE:
            fade_to_year(pressed)
        else:
            show_year(pressed)

        wait_until_released(pressed)

    sleep_ms(20)