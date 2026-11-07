# 3D printing cheat sheet

> **Safety.** The nozzle runs at 200 °C or more and the bed can reach 60–110 °C. Keep hands, hair and loose sleeves clear while it moves. Don't leave a printer running unattended, keep thermal-runaway protection enabled in firmware, and keep a smoke detector nearby. Print ABS/ASA in a ventilated space.

## Starting temperatures (always check the spool label)

| Filament | Nozzle | Bed | Notes |
|---|---|---|---|
| PLA | 190–220 °C | 50–60 °C | Easiest; low heat tolerance |
| PETG | 230–250 °C | 70–85 °C | Strong; stringy; sticks hard to smooth PEI, so use a release layer |
| ABS / ASA | 240–260 °C | 90–110 °C | Warps; needs an enclosure and ventilation |
| TPU | 210–230 °C | 30–60 °C | Flexible; print slowly, direct-drive helps |

These are typical ranges, not guarantees; each brand and printer differs. Run a temperature tower when you switch filament.

## Troubleshooting

| Symptom | Likely causes | Try |
|---|---|---|
| First layer won't stick | Nozzle too high, dirty bed, bed too cool | Re-level / re-do Z offset, clean with isopropyl alcohol, raise bed temp |
| Warping or corners lifting | Cooling too fast, drafts, poor adhesion | Brim, enclosure, less part-cooling fan for ABS |
| Stringing | Wet filament, temp too high, retraction too low | Dry filament, lower temp, tune retraction |
| Under-extrusion / gaps | Clog, temp too low, worn extruder gear | Raise temp, check the path, cold-pull |
| Layer shifts | Belts loose, speed/acceleration too high, collision | Tighten belts, lower speed, check for curled edges |
| Rough top surface | Too little infill/top layers | More top layers, higher infill |

Wet filament (popping sounds, fuzzy surface) is a common cause of many of these; dry it before blaming settings.

## Design for printing

- Overhangs steeper than about 45° usually need supports.
- Keep walls at least 2× the nozzle diameter thick (0.8 mm for a 0.4 mm nozzle).
- Orient parts so layer lines run across the direction of the load, not along it; layers are weakest between each other.
- Leave 0.2–0.4 mm of clearance between parts that must fit together.
- Holes print slightly small; test-fit and adjust.

## Slicer terms

- **Layer height**: smaller means smoother but slower (0.2 mm is common with a 0.4 mm nozzle).
- **Infill**: interior fill; 10–20 % is enough for most parts.
- **Perimeters/walls**: usually add more strength than infill does.
- **Retraction**: pulls filament back during travel moves to reduce stringing.
