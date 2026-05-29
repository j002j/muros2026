# main.py
# ESP32 + MicroPython + NeoPixel/WS2812
# Ocean O2 Data Physicalisation
# 5 Buttons = 5 Jahre
# 5 Plexiglas-Layer = 5 Tiefenzonen
#
# Version: HIGH CONTRAST
# - 2004 ist kräftig marineblau
# - Jahre unterscheiden sich deutlich stärker
# - Layer unterscheiden sich stärker über dunkle/marine/violette Blautöne
# - Bottom-Layer wird zuerst gezeichnet, Datenlayer danach

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

# Globaler Helligkeitsregler
# Für dunkle Marine-Töne ruhig 1.0 lassen.
BRIGHTNESS = 1.0

# Fade an/aus
USE_FADE = True

# Bottom-Layer / Basislicht
# Etwas dunkler als vorher, damit er die Blautöne nicht optisch erschlägt.
WEISS = (8, 10, 12)

BOTTOM_LAYER = [
    28, 29, 30, 31, 32, 84, 85, 86, 129, 130, 165, 166, 167, 168, 169,
    181, 191, 192, 193, 194, 195, 210, 211, 212, 213, 214, 224, 225,
    226, 227, 235, 236
]

ZONE_RANGES = [
    # Layer 1: 100-250m
    [
        14, 15, 26, 27, 33, 34, 82, 83, 86, 127, 128, 130, 121,
        158, 159, 160, 161, 162, 163, 164, 134, 135, 136, 137,
        138, 170, 171, 197, 196, 215, 228, 237, 240, 234, 209,
        223, 222, 233, 232, 224, 205, 206, 181, 182
    ],

    # Layer 2: 250-400m
    [
        122, 131, 132, 133, 87, 88, 89, 90, 91, 92, 93, 94, 95,
        35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 138, 198,
        216, 229, 238, 217, 230, 239, 150, 151, 152, 153, 154,
        184, 183, 185, 207, 208, 187, 172, 117, 204
    ],

    # Layer 3: 400-600m
    [
        126, 162, 231, 220, 204, 180, 181, 96, 97, 98, 156, 147,
        139, 140, 218, 200, 149, 148, 109, 110, 111, 112, 113,
        114, 81, 80, 79, 77, 76, 75, 74, 73, 120, 119, 118,
        20, 19, 18
    ],

    # Layer 4: 600-750m
    [
        19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 69, 70, 71, 72,
        115, 116, 65, 66, 67, 68, 173, 174, 175, 176, 141, 142,
        143, 99, 48, 49, 219, 203
    ],

    # Layer 5: 750-900m
    [
        177, 178, 179, 144, 145, 146, 147, 105, 61, 60, 0, 1, 2,
        3, 4, 5, 50, 51, 52, 53, 54, 56, 57, 58, 59, 100, 101,
        102, 103, 104, 106, 107, 108
    ]
]

# =======================================================
# 2. DATA MAPPING V2
# =======================================================

YEARS = [2004, 2009, 2014, 2019, 2024]
LAYER_LABELS = ['100-250m', '250-400m', '400-600m', '600-750m', '750-900m']

# Eastern Tropical Atlantic | normal
DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_NORMAL = [
    [(0, 35, 148), (0, 14, 59), (0, 21, 90), (0, 44, 188), (0, 59, 251)],
    [(0, 34, 144), (0, 14, 59), (0, 22, 94), (0, 45, 193), (0, 60, 255)],
    [(0, 34, 146), (0, 14, 58), (0, 21, 90), (0, 44, 188), (0, 59, 250)],
    [(0, 34, 144), (0, 13, 54), (0, 20, 87), (0, 43, 185), (0, 58, 246)],
    [(0, 35, 147), (0, 12, 51), (0, 19, 79), (0, 42, 177), (0, 57, 243)],
]

# Eastern Tropical Atlantic | inverted
DATA_COLORS_EASTERN_TROPICAL_ATLANTIC_INVERTED = [
    [(0, 37, 158), (0, 58, 247), (0, 51, 216), (0, 28, 118), (0, 13, 55)],
    [(0, 38, 162), (0, 58, 247), (0, 50, 212), (0, 27, 113), (0, 12, 51)],
    [(0, 38, 160), (0, 58, 248), (0, 51, 216), (0, 28, 118), (0, 13, 56)],
    [(0, 38, 162), (0, 59, 252), (0, 52, 219), (0, 29, 121), (0, 14, 60)],
    [(0, 37, 159), (0, 60, 255), (0, 53, 227), (0, 30, 129), (0, 15, 63)],
]

# Peru-Chile OMZ / Eastern Tropical South Pacific | normal
DATA_COLORS_PERU_CHILE_OMZ_NORMAL = [
    [(0, 56, 238), (0, 12, 51), (0, 13, 56), (0, 27, 116), (0, 39, 165)],
    [(0, 55, 235), (0, 12, 51), (0, 13, 55), (0, 27, 113), (0, 39, 164)],
    [(0, 54, 231), (0, 13, 53), (0, 14, 58), (0, 26, 112), (0, 38, 161)],
    [(0, 56, 240), (0, 13, 55), (0, 14, 59), (0, 26, 112), (0, 38, 160)],
    [(0, 60, 255), (0, 13, 55), (0, 15, 63), (0, 27, 113), (0, 38, 163)],
]

# Peru-Chile OMZ / Eastern Tropical South Pacific | inverted
DATA_COLORS_PERU_CHILE_OMZ_INVERTED = [
    [(0, 16, 68), (0, 60, 255), (0, 59, 250), (0, 45, 190), (0, 33, 141)],
    [(0, 17, 71), (0, 60, 255), (0, 59, 251), (0, 45, 193), (0, 33, 142)],
    [(0, 18, 75), (0, 59, 253), (0, 58, 248), (0, 46, 194), (0, 34, 145)],
    [(0, 16, 66), (0, 59, 251), (0, 58, 247), (0, 46, 194), (0, 34, 146)],
    [(0, 12, 51), (0, 59, 251), (0, 57, 243), (0, 45, 193), (0, 34, 143)],
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
# 2b. HIGH CONTRAST VISUAL ENCODING
# =======================================================

# Ziel:
# 2004 = sehr kräftig marineblau
# 2009 = klar sichtbar anderer Blauton
# 2014 = tiefer / weniger gesättigt
# 2019 = dunkler violettblau
# 2024 = sehr dunkel / violett-marine

# Stärke der datenbasierten Layer-Unterschiede.
# Höher = Layer unterscheiden sich stärker.
COLOR_CONTRAST = 3.0

# Layer-Score wird zusätzlich in Stufen gezogen.
# Das erzeugt sichtbarere Unterschiede zwischen Tiefenlayern.
USE_LAYER_STEPS = True

# Jahres-Farbpaletten:
# Jede Jahrespalette enthält 5 Farben:
# Index 0 = niedriger O2-Score / blasser bzw. dunkler
# Index 4 = hoher O2-Score / kräftiger
#
# Alle Paletten bleiben im Bereich Marineblau / Tiefblau / Violettblau.
YEAR_PALETTES_NORMAL = [
    # 2004: richtig kräftig marineblau, hohe Sättigung
    [
        (0, 10, 85),      # niedrig
        (0, 25, 130),
        (0, 45, 175),
        (0, 70, 220),
        (0, 95, 255),     # hoch: kräftiges Marine/Cyan-Blau
    ],

    # 2009: klar sichtbar anders, weniger cyan, dunkler royal blue
    [
        (10, 0, 75),
        (15, 10, 115),
        (5, 25, 155),
        (0, 45, 195),
        (0, 65, 230),
    ],

    # 2014: tieferes Blau, weniger grün/cyan
    [
        (20, 0, 65),
        (25, 5, 100),
        (15, 15, 135),
        (5, 28, 170),
        (0, 40, 205),
    ],

    # 2019: stärker violettblau
    [
        (35, 0, 55),
        (40, 0, 85),
        (35, 8, 120),
        (25, 18, 150),
        (15, 30, 180),
    ],

    # 2024: dunkelstes Jahr, violett-marine
    [
        (50, 0, 45),
        (55, 0, 70),
        (50, 5, 95),
        (40, 12, 125),
        (28, 20, 155),
    ],
]

# Inverted-Modi: weniger O2 auffälliger/kräftiger.
# Ebenfalls starke Jahresunterschiede.
YEAR_PALETTES_INVERTED = [
    # 2004
    [
        (0, 95, 255),
        (0, 70, 220),
        (0, 45, 175),
        (0, 25, 130),
        (0, 10, 85),
    ],
    # 2009
    [
        (0, 65, 230),
        (0, 45, 195),
        (5, 25, 155),
        (15, 10, 115),
        (10, 0, 75),
    ],
    # 2014
    [
        (0, 40, 205),
        (5, 28, 170),
        (15, 15, 135),
        (25, 5, 100),
        (20, 0, 65),
    ],
    # 2019
    [
        (15, 30, 180),
        (25, 18, 150),
        (35, 8, 120),
        (40, 0, 85),
        (35, 0, 55),
    ],
    # 2024
    [
        (28, 20, 155),
        (40, 12, 125),
        (50, 5, 95),
        (55, 0, 70),
        (50, 0, 45),
    ],
]

# Zusätzliches Jahres-Dimming.
# 2004 bleibt stark, jedes spätere Jahr wird deutlich dunkler.
USE_YEAR_DIMMING = True
YEAR_DIM_FACTORS = [
    1.00,  # 2004
    0.82,  # 2009
    0.68,  # 2014
    0.54,  # 2019
    0.42,  # 2024
]

# Zusätzlicher Mindestboost für 2004, damit es wirklich "doll marineblau" wirkt.
BOOST_2004 = True


def clamp(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def lerp(a, b, t):
    return int(a + (b - a) * t)


def color_lerp(c1, c2, t):
    return (
        lerp(c1[0], c2[0], t),
        lerp(c1[1], c2[1], t),
        lerp(c1[2], c2[2], t)
    )


def is_inverted_mode():
    return current_mode_key in ["m1", "m3"]


def get_year_palette(year_index):
    if is_inverted_mode():
        return YEAR_PALETTES_INVERTED[year_index]
    return YEAR_PALETTES_NORMAL[year_index]


def raw_color_to_score(color):
    """
    Wandelt Data-Colors in Score 0..1 um.
    Blau zählt stark, Grün zählt sichtbar mit.
    Kontrast wird stark erhöht.
    """
    r, g, b = color

    # Score aus Blau + Grün
    score = (b + 0.65 * g) / (255 + 0.65 * 255)

    # Kontrast verstärken
    score = 0.5 + (score - 0.5) * COLOR_CONTRAST
    score = clamp(score, 0.0, 1.0)

    # Optional in Stufen ziehen, damit Layer optisch klarer sind.
    if USE_LAYER_STEPS:
        if score < 0.20:
            score = 0.05
        elif score < 0.40:
            score = 0.30
        elif score < 0.60:
            score = 0.55
        elif score < 0.80:
            score = 0.78
        else:
            score = 1.00

    return score


def score_to_palette_color(score, year_index):
    palette = get_year_palette(year_index)

    pos = score * (len(palette) - 1)
    idx = int(pos)
    t = pos - idx

    if idx >= len(palette) - 1:
        return palette[-1]

    return color_lerp(palette[idx], palette[idx + 1], t)


def apply_year_dimming(layer_colors, year_index):
    if not USE_YEAR_DIMMING:
        return layer_colors

    factor = YEAR_DIM_FACTORS[year_index]
    dimmed = []

    for r, g, b in layer_colors:
        dimmed.append((
            int(clamp(r * factor, 0, 255)),
            int(clamp(g * factor, 0, 255)),
            int(clamp(b * factor, 0, 255))
        ))

    return dimmed


def apply_2004_boost(layer_colors, year_index):
    """
    2004 soll richtig stark marineblau wirken.
    Wir boosten Blau und Grün minimal, Rot bleibt 0 oder niedrig.
    """
    if not BOOST_2004 or year_index != 0:
        return layer_colors

    boosted = []

    for r, g, b in layer_colors:
        boosted.append((
            int(clamp(r * 0.6, 0, 255)),
            int(clamp(g * 1.15 + 8, 0, 255)),
            int(clamp(b * 1.18 + 18, 0, 255))
        ))

    return boosted


def transform_data_colors(raw_colors, year_index):
    """
    Gesamte visuelle Übersetzung:
    1. Rohdatenfarben -> Score
    2. Score -> Jahrespalette
    3. Jahresdimming
    4. 2004-Boost
    """
    colors = []

    for raw_color in raw_colors:
        score = raw_color_to_score(raw_color)
        colors.append(score_to_palette_color(score, year_index))

    colors = apply_year_dimming(colors, year_index)
    colors = apply_2004_boost(colors, year_index)

    return colors


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
        int(clamp(r * BRIGHTNESS, 0, 255)),
        int(clamp(g * BRIGHTNESS, 0, 255)),
        int(clamp(b * BRIGHTNESS, 0, 255))
    )


def clear_leds():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()


def build_target_pixels(layer_colors):
    """
    Baut ein komplettes Zielbild für alle LEDs.
    Wichtig:
    1. Erst alles schwarz.
    2. Dann Bottom-Layer weiß/dunkel.
    3. Danach Datenlayer darüber.
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
    print("Final Layer-Farben L1 bis L5:", layer_colors)
    print("Bottom-Layer:", WEISS)
    print("Brightness:", BRIGHTNESS)


def show_year(year_index):
    global current_year_index

    current_year_index = year_index

    dataset = DATASETS[current_mode_key]
    raw_colors = dataset["colors"][year_index]
    final_colors = transform_data_colors(raw_colors, year_index)
    year = YEARS[year_index]

    show_layer_colors(
        final_colors,
        dataset["name"] + " | Jahr " + str(year)
    )

    print("Raw Layer-Farben L1 bis L5:", raw_colors)


def fade_to_year(year_index, steps=25, delay_ms=18):
    global current_year_index

    dataset = DATASETS[current_mode_key]
    raw_target_colors = dataset["colors"][year_index]
    final_target_colors = transform_data_colors(raw_target_colors, year_index)

    start_pixels = [np[i] for i in range(NUM_LEDS)]
    target_pixels = build_target_pixels(final_target_colors)

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
    print("Raw Layer-Farben L1 bis L5:", raw_target_colors)
    print("Final Layer-Farben L1 bis L5:", final_target_colors)
    print("Brightness:", BRIGHTNESS)


def read_buttons():
    for idx, button in enumerate(buttons):
        if button.value() == BUTTON_ACTIVE_VALUE:
            sleep_ms(40)
            if button.value() == BUTTON_ACTIVE_VALUE:
                return idx
    return None


def wait_until_released(button_index):
    while buttons[button_index].value() == BUTTON_ACTIVE_VALUE:
        sleep_ms(20)


def print_help():
    print("")
    print("==================================================")
    print("OCEAN O2 DATA PHYSICALISATION - HIGH CONTRAST")
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
    print("COLOR_CONTRAST:", COLOR_CONTRAST)
    print("USE_LAYER_STEPS:", USE_LAYER_STEPS)
    print("USE_YEAR_DIMMING:", USE_YEAR_DIMMING)
    print("YEAR_DIM_FACTORS:", YEAR_DIM_FACTORS)
    print("BOOST_2004:", BOOST_2004)
    print("Brightness:", BRIGHTNESS)
    print("Use Fade:", USE_FADE)
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
