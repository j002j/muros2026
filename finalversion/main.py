# main.py
# ESP32 + MicroPython + NeoPixel/WS2812
# Ocean O2 Data Physicalisation
# Edition: "Cyan Stress" + Flowy Auto-Play & Subtles Feedback

from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms, ticks_ms, ticks_diff
import math

# =======================================================
# 1. HARDWARE-KONFIGURATION
# =======================================================

LED_PIN = 13
NUM_LEDS = 289  # Volle Matrix

BUTTON_PINS = [19, 18, 5, 17, 16]
BUTTON_ACTIVE_VALUE = 0
BUTTON_PULL = Pin.PULL_UP
BRIGHTNESS = 1.0

# =======================================================
# 2. ZONEN & AUTO-FILL
# =======================================================

BOTTOM_LAYER = [
    28, 29, 30, 31, 32, 84, 85, 86, 129, 130, 165, 166, 167, 168, 169,
    181, 191, 192, 193, 194, 195, 210, 211, 212, 213, 214, 224, 225,
    226, 227, 235, 236
]

ZONE_RANGES = [
    [14, 15, 26, 27, 33, 34, 82, 83, 86, 127, 128, 130, 121, 158, 159, 160, 161, 162, 163, 164, 134, 135, 136, 137, 138, 170, 171, 197, 196, 215, 228, 237, 240, 234, 209, 223, 222, 233, 232, 224, 205, 206, 181, 182],
    [122, 131, 132, 133, 87, 88, 89, 90, 91, 92, 93, 94, 95, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 138, 198, 216, 229, 238, 217, 230, 239, 150, 151, 152, 153, 154, 184, 183, 185, 207, 208, 187, 172, 117, 204],
    [126, 162, 231, 220, 204, 180, 181, 96, 97, 98, 156, 147, 139, 140, 218, 200, 149, 148, 109, 110, 111, 112, 113, 114, 81, 80, 79, 77, 76, 75, 74, 73, 120, 119, 118, 20, 19, 18],
    [19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 69, 70, 71, 72, 115, 116, 65, 66, 67, 68, 173, 174, 175, 176, 141, 142, 143, 99, 48, 49, 219, 203],
    [177, 178, 179, 144, 145, 146, 147, 105, 61, 60, 0, 1, 2, 3, 4, 5, 50, 51, 52, 53, 54, 56, 57, 58, 59, 100, 101, 102, 103, 104, 106, 107, 108]
]

mapped_leds = set(BOTTOM_LAYER)
for layer in ZONE_RANGES:
    mapped_leds.update(layer)
unmapped_leds = [i for i in range(NUM_LEDS) if i not in mapped_leds]
BOTTOM_LAYER.extend(unmapped_leds)

# =======================================================
# 3. DATA MAPPING 
# =======================================================

YEARS = [2004, 2009, 2014, 2019, 2024]

AMBIENT_COLOR = (0, 0, 8)       
BOTTOM_COLOR = (0, 0, 15)       

O2_PALETTE = [
    (140, 135, 110), # Step 0: Knochenweiß (Tot)
    (0, 255, 180),   # Step 1: Grelles Cyan (Warnung)
    (0, 100, 200),   # Step 2: Cyan-Blau 
    (0, 0, 120),     # Step 3: Dunkles Royalblau 
    (0, 0, 200),     # Step 4: Sattes Royalblau
    (0, 0, 255)      # Step 5: Pures, tiefes Royalblau 
]

OMZ_DATA_STEPS = [
    [5, 4, 1, 4, 5], # 2004
    [5, 3, 0, 3, 5], # 2009
    [4, 1, 0, 1, 4], # 2014
    [3, 0, 0, 0, 2], # 2019
    [1, 0, 0, 0, 2], # 2024
]

LAYER_COMPENSATION = [1.0, 1.0, 1.0, 1.0, 1.0]

# =======================================================
# 4. GLOBALE STATUS-VARIABLEN FÜR ANIMATIONEN
# =======================================================

base_pixels = [(0,0,0)] * NUM_LEDS
is_dead_pixel = [False] * NUM_LEDS  
current_year_index = 0

# =======================================================
# 5. SETUP & HELPERS
# =======================================================

np = NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)
buttons = [Pin(pin_number, Pin.IN, BUTTON_PULL) for pin_number in BUTTON_PINS]

def scale_color(color, comp_factor=1.0):
    r, g, b = color
    return (int(r * BRIGHTNESS * comp_factor), int(g * BRIGHTNESS * comp_factor), int(b * BRIGHTNESS * comp_factor))

def clear_leds():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

def build_target_data(year_index):
    t_pixels = [scale_color(AMBIENT_COLOR)] * NUM_LEDS
    t_dead = [False] * NUM_LEDS

    bottom_scaled = scale_color(BOTTOM_COLOR)
    for led_idx in BOTTOM_LAYER:
        if 0 <= led_idx < NUM_LEDS:
            t_pixels[led_idx] = bottom_scaled

    for layer_index in range(5):
        step = OMZ_DATA_STEPS[year_index][layer_index]
        comp = LAYER_COMPENSATION[layer_index]
        layer_color = scale_color(O2_PALETTE[step], comp_factor=comp)
        
        is_dead = (step == 0) 

        for led_idx in ZONE_RANGES[layer_index]:
            if 0 <= led_idx < NUM_LEDS:
                t_pixels[led_idx] = layer_color
                t_dead[led_idx] = is_dead

    return t_pixels, t_dead

# =======================================================
# 6. GIMMICKS: FEEDBACK + BREATHING
# =======================================================

FEEDBACK_EDGE_COLOR = (0, 28, 55)  
FEEDBACK_EDGE_MS = 55            
FEEDBACK_EDGE_BLEND = 0.55        


# Atmen: .
BREATH_SPEED = 1400
BREATH_BASE = 0.97
BREATH_AMOUNT = 0.03

# Fade-Geschwindigkeiten:
BUTTON_FADE_STEPS = 18
BUTTON_FADE_DELAY_MS = 12

AUTOPLAY_FADE_STEPS = 64
AUTOPLAY_FADE_DELAY_MS = 18

POWER_FADE_STEPS = 18
POWER_FADE_DELAY_MS = 10

def get_data_leds():
    """
    Nur die 5 echten Daten-Zonen.
    Bottom, Rand und Auto-Fill gehören NICHT dazu.
    """
    data = set()

    for layer in ZONE_RANGES:
        for led in layer:
            if 0 <= led < NUM_LEDS:
                data.add(led)

    return data


DATA_LEDS = get_data_leds()
FEEDBACK_LEDS = [i for i in range(NUM_LEDS) if i not in DATA_LEDS]


def feedback_kick(restore_after=True):
    """
    Data-neutrales Button-Feedback:
    Nur Rand-/Nicht-Daten-LEDs bekommen kurz einen kühlen Impuls.
    Die eigentlichen Datenzonen bleiben unverändert.
    """
    start_pixels = [np[i] for i in range(NUM_LEDS)]
    fc = scale_color(FEEDBACK_EDGE_COLOR)

    for led in FEEDBACK_LEDS:
        r, g, b = start_pixels[led]

        np[led] = (
            int(r * (1 - FEEDBACK_EDGE_BLEND) + fc[0] * FEEDBACK_EDGE_BLEND),
            int(g * (1 - FEEDBACK_EDGE_BLEND) + fc[1] * FEEDBACK_EDGE_BLEND),
            int(b * (1 - FEEDBACK_EDGE_BLEND) + fc[2] * FEEDBACK_EDGE_BLEND)
        )

    np.write()
    sleep_ms(FEEDBACK_EDGE_MS)

    if restore_after:
        for led in FEEDBACK_LEDS:
            np[led] = start_pixels[led]

        np.write()

def get_breath_factor():
    return BREATH_BASE + BREATH_AMOUNT * math.sin(ticks_ms() / BREATH_SPEED)


def apply_breath_to_color(color, factor):
    r, g, b = color
    return (
        int(r * factor),
        int(g * factor),
        int(b * factor)
    ) 

def render_ocean_breath():
    """
    subtiler Ocean Breath.
    Nur die echten Datenlayer atmen.
    Boden, Rand und Auto-Fill bleiben konstant.
    """
    factor = get_breath_factor()

    for i in range(NUM_LEDS):
        np[i] = base_pixels[i]

    for i in DATA_LEDS:
        r, g, b = base_pixels[i]
        np[i] = (
            int(r * factor),
            int(g * factor),
            int(b * factor)
        )

    np.write()


# =======================================================
# 7. DISPLAY & FADE LOGIC
# =======================================================

def show_year(year_index):
    global current_year_index, base_pixels, is_dead_pixel

    current_year_index = year_index
    base_pixels, is_dead_pixel = build_target_data(year_index)

    for i in range(NUM_LEDS):
        np[i] = base_pixels[i]

    np.write()

    print("AKTIV:", YEARS[year_index])
    for layer_index in range(5):
        step = OMZ_DATA_STEPS[year_index][layer_index]
        comp = LAYER_COMPENSATION[layer_index]
        rgb = scale_color(O2_PALETTE[step], comp)
        print("  Layer", layer_index + 1, "| Step", step, "| RGB", rgb)


def fade_to_year(year_index, steps=BUTTON_FADE_STEPS, delay_ms=BUTTON_FADE_DELAY_MS):
    """
    Weicher Fade zum Zieljahr.
    Buttondruck = zügig.
    Auto-Play = langsamer über andere Parameter.
    """
    global current_year_index, base_pixels, is_dead_pixel

    start_pixels = [np[i] for i in range(NUM_LEDS)]
    target_pixels, target_dead = build_target_data(year_index)

    for step in range(1, steps + 1):
        t = step / steps

        t = t * t * (3 - 2 * t)

        # Zielbild schon in der aktuellen Breath-Helligkeit berechnen
        breath_factor = get_breath_factor()

        for i in range(NUM_LEDS):
            sr, sg, sb = start_pixels[i]

            tr, tg, tb = apply_breath_to_color(target_pixels[i], breath_factor)

            np[i] = (
                int(sr + (tr - sr) * t),
                int(sg + (tg - sg) * t),
                int(sb + (tb - sb) * t)
            )

        np.write()
        sleep_ms(delay_ms)

    current_year_index = year_index
    base_pixels = target_pixels
    is_dead_pixel = target_dead

    render_ocean_breath()

    print("GEWECHSELT ZU:", YEARS[year_index])
    for layer_index in range(5):
        step = OMZ_DATA_STEPS[year_index][layer_index]
        comp = LAYER_COMPENSATION[layer_index]
        rgb = scale_color(O2_PALETTE[step], comp)
        print("  Layer", layer_index + 1, "| Step", step, "| RGB", rgb)


def fade_to_black(steps=POWER_FADE_STEPS, delay_ms=POWER_FADE_DELAY_MS):
    """
    Sanftes Ausschalten, ohne den MicroPython-Stack zu killen.
    Der Code läuft weiter, LEDs gehen nur optisch aus.
    """
    global base_pixels, is_dead_pixel

    start_pixels = [np[i] for i in range(NUM_LEDS)]

    for step in range(1, steps + 1):
        t = step / steps
        t = t * t * (3 - 2 * t)

        for i in range(NUM_LEDS):
            sr, sg, sb = start_pixels[i]
            np[i] = (
                int(sr * (1 - t)),
                int(sg * (1 - t)),
                int(sb * (1 - t))
            )

        np.write()
        sleep_ms(delay_ms)

    clear_leds()
    base_pixels = [(0, 0, 0)] * NUM_LEDS
    is_dead_pixel = [False] * NUM_LEDS

# =======================================================
# 8. BUTTON CONTROLS
# =======================================================

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

# =======================================================
# 9. START & MAIN LOOP
# =======================================================

clear_leds()
show_year(0)

is_system_on = True
auto_play_active = False

POWER_BUTTON_INDEX = 1       
POWER_HOLD_MS = 2000         

AUTOPLAY_BUTTON_INDEX = 4    
AUTOPLAY_HOLD_MS = 5000         

last_interaction_time = ticks_ms()
last_auto_switch = ticks_ms()

AUTO_PLAY_INTERVAL = 8000
ATTRACT_MODE_DELAY = 120000

print("SYSTEM BEREIT.")
print("Button 2 / 2009 kurz: Jahr 2009.")
print("Button 2 / 2009 halten: AN/AUS.")
print("Button 5 / 2024 halten: Auto-Play AN/AUS.")
print("Breathing: nur Datenlayer, Boden/Rand stabil.")


while True:
    current_time = ticks_ms()
    pressed = read_buttons()

    # ===================================================
    # BUTTON GEDRÜCKT
    # ===================================================
    if pressed is not None:
        press_start = ticks_ms()
        hold_done = False

        # -----------------------------------------------
        # BUTTON 2 HOLD: SYSTEM AN/AUS
        # -----------------------------------------------
        if pressed == POWER_BUTTON_INDEX:
            while buttons[POWER_BUTTON_INDEX].value() == BUTTON_ACTIVE_VALUE:
                held_ms = ticks_diff(ticks_ms(), press_start)

                if is_system_on:
                    render_ocean_breath()

                if held_ms >= POWER_HOLD_MS:
                    is_system_on = not is_system_on
                    auto_play_active = False
                    hold_done = True

                    last_interaction_time = ticks_ms()
                    last_auto_switch = ticks_ms()

                    if is_system_on:
                        print("SYSTEM: ON")
                        show_year(current_year_index)
                        feedback_kick(restore_after=True)
                    else:
                        print("SYSTEM: OFF")
                        feedback_kick(restore_after=True)
                        fade_to_black()

                    # warten, bis Button losgelassen wird
                    while buttons[POWER_BUTTON_INDEX].value() == BUTTON_ACTIVE_VALUE:
                        sleep_ms(20)

                    break

                sleep_ms(20)

            if hold_done:
                continue

        # -----------------------------------------------
        # BUTTON 5 HOLD: AUTO-PLAY AN/AUS
        # -----------------------------------------------
        if pressed == AUTOPLAY_BUTTON_INDEX and is_system_on:
            while buttons[AUTOPLAY_BUTTON_INDEX].value() == BUTTON_ACTIVE_VALUE:
                held_ms = ticks_diff(ticks_ms(), press_start)

                render_ocean_breath()

                if held_ms >= AUTOPLAY_HOLD_MS:
                    auto_play_active = not auto_play_active
                    hold_done = True

                    last_interaction_time = ticks_ms()
                    last_auto_switch = ticks_ms()

                    if auto_play_active:
                        print("AUTO-PLAY: ON")
                    else:
                        print("AUTO-PLAY: OFF")

                    feedback_kick(restore_after=True)

                    while buttons[AUTOPLAY_BUTTON_INDEX].value() == BUTTON_ACTIVE_VALUE:
                        sleep_ms(20)

                    break

                sleep_ms(20)

            if hold_done:
                continue

        # -----------------------------------------------
        # NORMALER KURZER BUTTON-KLICK
        # -----------------------------------------------
        wait_until_released(pressed)

        current_time = ticks_ms()
        last_interaction_time = current_time
        last_auto_switch = current_time

        if not is_system_on:
            continue

        if auto_play_active:
            auto_play_active = False
            print("AUTO-PLAY: OFF durch manuelle Eingabe")

        print("Button erkannt:", pressed + 1, "| Jahr:", YEARS[pressed])

        if pressed != current_year_index:
            feedback_kick(restore_after=True)
            fade_to_year(
                pressed,
                steps=BUTTON_FADE_STEPS,
                delay_ms=BUTTON_FADE_DELAY_MS
            )
        else:
            feedback_kick(restore_after=True)

        last_auto_switch = ticks_ms()

    # ===================================================
    # IDLE / AUTO-PLAY
    # ===================================================
    if is_system_on:
        render_ocean_breath()

        idle_time = ticks_diff(current_time, last_interaction_time)
        attract_mode_active = idle_time > ATTRACT_MODE_DELAY

        if auto_play_active or attract_mode_active:
            if ticks_diff(current_time, last_auto_switch) > AUTO_PLAY_INTERVAL:
                next_year = (current_year_index + 1) % len(YEARS)

                if auto_play_active:
                    print("AUTO-PLAY:", YEARS[next_year])
                else:
                    print("ATTRACT-MODE:", YEARS[next_year])

                fade_to_year(
                    next_year,
                    steps=AUTOPLAY_FADE_STEPS,
                    delay_ms=AUTOPLAY_FADE_DELAY_MS
                )

                last_auto_switch = ticks_ms()

    else:
        sleep_ms(20)
