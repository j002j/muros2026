```markdown
# Problembehebung: ESP32 "Device is busy" & Thonny Absturz auf macOS

## 1. Das ursprüngliche Problem
Beim Versuch, den ESP32 mit der IDE **Thonny** auf dem Mac anzusteuern, erschien folgende Fehlermeldung:
> *Device is busy or does not respond. Your options: wait until it completes current work; use Ctrl+C to interrupt current work...*

Zusätzlich stürzte das eingebaute MicroPython-Flash-Werkzeug von Thonny mit einem Python-Fehler ab:
`AttributeError: 'NoneType' object has no attribute 'port'`

### Ursachen-Analyse:
1. **Kein MicroPython auf dem Board:** Der ESP32 wurde im Werkszustand geliefert (meistens mit C++ Firmware) und verstand Thonny nicht.
2. **Thonny-Software-Bug:** Ein bekannter Fehler im Zusammenspiel zwischen Thonny, macOS und Python 3.14 verhinderte, dass Thonny den USB-Port korrekt zuordnen und die Firmware flashen konnte.
3. **Anaconda-Konflikt:** Auf dem Mac ist Anaconda installiert, weshalb Standard-Terminalbefehle wie `pip` oder `python3` in die Anaconda-Umgebung umgeleitet wurden, wo das Flash-Werkzeug (`esptool`) fehlte.

---

## 2. Der Lösungsansatz
Da die grafische Oberfläche von Thonny blockiert war, wurde die Installation von MicroPython komplett an Thonny vorbei über das native **macOS-Terminal** durchgeführt. Dabei wurde das offizielle Espressif-Flash-Werkzeug (`esptool`) direkt über den spezifischen Anaconda-Pfad installiert und ausgeführt.

---

## 3. Konkreter Lösungsweg (Schritt für Schritt)

### Schritt 1: Thonny schließen
Thonny vollständig beenden (`Cmd + Q`), damit die USB-Verbindung zum ESP32 nicht blockiert wird.

### Schritt 2: Den USB-Port des ESP32 ermitteln
Das macOS-Terminal öffnen und alle aktiven USB-Schnittstellen auflisten:
```bash
ls /dev/cu.*

```

*Ergebnis:* Der korrekte Port wurde als **`/dev/cu.usbserial-1410`** identifiziert (da der verbaute CP2102N-Chip korrekt vom Mac erkannt wurde).

### Schritt 3: Flash-Tool in der Anaconda-Umgebung installieren

Da Anaconda als Standard-Python genutzt wird, musste das Tool über den absoluten Anaconda-Pfad installiert werden:

```bash
/opt/anaconda3/bin/pip install esptool

```

### Schritt 4: Alten Flash-Speicher des ESP32 löschen

Um Reste alter Firmware zu entfernen, wurde der Speicher geleert:

```bash
/opt/anaconda3/bin/python3 -m esptool --port /dev/cu.usbserial-1410 erase_flash

```

*Hinweis:* Sobald im Terminal `Connecting...` erscheint, muss der **BOOT-Knopf** auf dem ESP32 gedrückt gehalten werden.

### Schritt 5: MicroPython-Firmware aufspielen

Die aktuelle MicroPython `.bin`-Datei (z. B. `v1.28.0.bin`) von der offiziellen Website herunterladen. Den Befehl im Terminal vorbereiten, ein Leerzeichen tippen und die Datei per Drag & Drop in das Terminal ziehen:

```bash
/opt/anaconda3/bin/python3 -m esptool --chip esp32 --port /dev/cu.usbserial-1410 write_flash -z 0x1000 /Pfad/zur/heruntergeladenen/datei.bin

```

*Hinweis:* Auch hier bei `Connecting...` den **BOOT-Knopf** am ESP32 gedrückt halten, bis der Upload startet (Prozentanzeige läuft bis 100%).

---

## 4. Ergebnis & Nächste Schritte

Nachdem `Hash of data verified.` im Terminal stand, wurde der ESP32 erfolgreich geflasht.

**Vorgehen jetzt in Thonny:**

1. ESP32 einmal kurz vom USB-Kabel trennen und wieder anstecken.
2. Thonny öffnen.
3. Unter *Werkzeuge -> Optionen -> Interpreter* als Gerät **MicroPython (ESP32)** und als Port explizit **`/dev/cu.usbserial-1410`** auswählen.
4. Den roten **Stop-Button** in Thonny drücken.
5. In der Shell erscheinen die drei Pfeile (`>>>`) – der ESP32 ist nun einsatzbereit für die LED-Steuerung.

## Wenn der Fehler nochmal vorkommt
```bash
ls /dev/cu.*
```

die ausgaben oben in das XXX unten einsetzten:

```bash
/opt/anaconda3/bin/python3 -m esptool --port /dev/cu.XXX erase_flash
```
Da die .bin-Datei wahrscheinlich noch in deinem Download-Ordner ist, musst diese nur wieder reingeschoben werden. Befehl eintippen, Leerzeichen, Datei per Drag & Drop reinziehen (und wieder den BOOT-Knopf drücken):

```bash
/opt/anaconda3/bin/python3 -m esptool --chip esp32 --port /dev/cu.usbserial-1410 write_flash -z 0x1000 /Pfad/zur/heruntergeladenen/datei.bin
```


```

```