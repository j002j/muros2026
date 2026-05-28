import machine
import neopixel
import time

# --- KONFIGURATION ---
LED_PIN = 13       # LED-Datenkabel an Pin 13
BUTTON_PIN = 16    # Pin 16 als Eingang
NUM_PIXELS = 140    # <--- HIER DEINE EXAKTE ANZAHL AN LEDS EINTRAGEN! (z.B. 8, 12, 30, 60...)

# NeoPixel initialisieren
strip = neopixel.NeoPixel(machine.Pin(LED_PIN), NUM_PIXELS)

# Pin 16 mit Pull-Up
button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

# --- FARBEN DEFINIEREN ---
ROT  = (128, 0, 0)
BLAU = (0, 0, 128) #helligkeit hier anpassen: max = 255

print("Programm gestartet. ALLE LEDs werden BLAU gefärbt.")

while True:
    
    # Zustand abfragen (1 = Normalzustand, 0 = Schalter gedrückt)
    if button.value() == 1:
        # BASE-ZUSTAND: Jede einzelne LED auf BLAU setzen
        for i in range(NUM_PIXELS):
            strip[i] = BLAU
        strip.write()
        
    else:
        # TEST-ZUSTAND (Pin 16 an GND): Alle LEDs werden ROT
        for i in range(NUM_PIXELS):
            strip[i] = ROT
        strip.write()
        print("Signal erkannt! Alle LEDs werden ROT.")
        time.sleep(0.2)
        
    # Den Prozessor entlasten
    time.sleep(0.05)
