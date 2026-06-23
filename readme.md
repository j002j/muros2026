# Ocean Oxygen Physicalisation

![Titelbild](muros2026/20260529_194259.jpg)


An interactive physical computing installation that visualises dissolved oxygen patterns in ocean Oxygen Minimum Zones (OMZs) through light, depth and material.

The installation uses an ESP32, a 289 LED NeoPixel matrix, five physical buttons and five stacked milky acrylic layers. Instead of showing the dataset on a screen, oxygen values are translated into a spatial light object. Each acrylic layer represents a depth zone, while each button selects a different year.

The project focuses on two ocean regions:

- **Peru-Chile Oxygen Minimum Zone**
- **Eastern Tropical Atlantic Oxygen Minimum Zone**

Both regions are used as case studies for communicating ocean deoxygenation, marine stress and the fragile visual language of oxygen loss.

---

## Project Idea

Oxygen Minimum Zones are ocean regions where dissolved oxygen is very low. They are natural features of the ocean, but ocean warming and climate-driven changes can intensify deoxygenation and affect marine ecosystems.

This installation turns that abstract phenomenon into a physical experience.

The visual system follows a **“Bleached Ocean” / “Cyan Stress”** aesthetic:

- deep blue = oxygen-rich / stable
- cyan = stressed transition state
- pale bleached tones = oxygen-depleted / fragile
- layered acrylic = ocean depth
- soft diffusion = underwater atmosphere

The goal is not to create a precise scientific chart, but a data-based physical interpretation that makes oxygen loss emotionally readable.

---

## Interaction

The installation has five physical buttons.

| Button | Year |
|---|---|
| Button 1 | 2004 |
| Button 2 | 2009 |
| Button 3 | 2014 |
| Button 4 | 2019 |
| Button 5 | 2024 |

Pressing a button changes the displayed year.  
The LED matrix fades into the selected data state instead of switching abruptly.

Additional interaction modes:

| Interaction | Function |
|---|---|
| Short button press | Select year |
| Hold Button 2 | Switch installation on/off |
| Hold Button 5 | Start/stop Auto-Play |
| Idle mode | Subtle ocean breathing |
| Auto-Play | Automatically moves through the years |

The interaction is intentionally simple: the object should feel like a calm ocean artefact, not like a technical control panel.

---

## Visual Mapping

The installation maps oxygen conditions to a custom colour palette.

```python
O2_PALETTE = [
    (140, 135, 110), # Step 0: bleached / oxygen-depleted
    (0, 255, 180),   # Step 1: stressed cyan
    (0, 100, 200),   # Step 2: cyan-blue
    (0, 0, 120),     # Step 3: dark royal blue
    (0, 0, 200),     # Step 4: saturated blue
    (0, 0, 255)      # Step 5: deep ocean blue
]
```

The mapping is intentionally atmospheric, but still data-based.
It is designed to make later years appear more stressed, pale and fragile where oxygen decreases.

## Regions
Peru-Chile OMZ

The Peru-Chile OMZ is used as one of the main visual scenarios.
It represents a strong oxygen minimum zone in the eastern tropical Pacific and is especially suitable for a dramatic visual story because oxygen depletion can be spatially intense.

In the installation, this region is mapped across five depth layers and five selected years.

Eastern Tropical Atlantic OMZ

The Eastern Tropical Atlantic region is included as a second ocean case study.
It allows comparison between different oxygen minimum zone dynamics and helps communicate that ocean deoxygenation is not a single local event, but part of a broader marine pattern.

The code can be adapted to switch between the two regional mappings.

## Hardware

Main components:

Component	Description
Microcontroller	ESP32
LEDs	NeoPixel / WS2812 matrix
LED count	289 LEDs
Interaction	5 physical push buttons
Material	5 milky acrylic layers
Power	External 5V LED power supply
Pin Configuration
Component	ESP32 Pin
LED data pin	GPIO 13
Button 1	GPIO 19
Button 2	GPIO 18
Button 3	GPIO 5
Button 4	GPIO 17
Button 5	GPIO 16

The buttons use internal pull-up resistors and are active-low.
This means that pressing a button connects the GPIO pin to GND.

## Software

The installation is written in MicroPython and runs directly on the ESP32.

Recommended editor:

Thonny

Main libraries:

```python
from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms, ticks_ms, ticks_diff
import math
```
MicroPython usually includes NeoPixel support by default.
If needed, the NeoPixel package can be installed through Thonny’s package manager.

## Inspiration

Brainstorming and visual research:
https://www.figma.com/board/NZpllUfHZYUcmpAbdbsu1X/Morus2026

## Sources and References

Scientific and data references:

NOAA Ocean Exploration – What is an oxygen minimum zone?
https://oceanexplorer.noaa.gov/ocean-fact/omz/
NOAA National Centers for Environmental Information – World Ocean Atlas
https://www.ncei.noaa.gov/products/world-ocean-atlas
World Ocean Atlas 2023 Data
https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/
Copernicus Marine – Global Ocean Biogeochemistry Hindcast
https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_BGC_001_029/description
Karstensen et al. – Oxygen minimum zones in the eastern tropical Atlantic and Pacific oceans
https://oceanrep.geomar.de/7187/

Technical references:

MicroPython
https://micropython.org/
Thonny Python IDE
https://thonny.org/
Adafruit NeoPixel Überguide
https://learn.adafruit.com/adafruit-neopixel-uberguide

## Credits

Created as part of a data physicalisation project on ocean oxygen decline and marine stress.


