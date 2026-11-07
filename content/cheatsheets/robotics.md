# Arduino · ESP32 · robotics cheat sheet

> **Hardware safety first.** Never wire or rewire a circuit while it's powered. Check polarity before connecting a battery. Lithium-ion/LiPo cells can catch fire if shorted, punctured or charged wrongly; use a proper charger and never leave them charging unattended.

## Voltage levels

| Board | Logic level | Notes |
|---|---|---|
| Arduino Uno / Nano / Mega | 5 V | Pins source about 20 mA recommended, 40 mA absolute maximum |
| ESP32 | 3.3 V | **Pins are not 5 V tolerant.** Feeding 5 V into a GPIO can damage the chip |

If you connect a 5 V sensor's output to an ESP32, use a level shifter or a voltage divider.

## LED resistor

R = (supply voltage − LED forward voltage) / current. Example: (5 V − 2 V) / 0.01 A = 300 Ω, so use 330 Ω. Never connect an LED straight to a pin without a resistor.

## Powering motors and servos

- Don't power motors or servos from the board's 5 V/3.3 V pin; they draw too much and can reset or damage the board. Use a separate supply.
- Connect the grounds of the two supplies together (common ground).
- Put a diode across a DC motor (a flyback diode) so its voltage spike when switched off doesn't hit your driver. Drive motors with a transistor, MOSFET or motor driver board, not directly from a pin.

## ESP32 gotchas

- On the classic ESP32, GPIO 6–11 connect to the flash chip; don't use them.
- GPIO 0, 2, 12 and 15 are "strapping" pins that affect boot; something wired to them can stop the board from starting.
- ADC2 pins can't be read while Wi-Fi is on; use ADC1 pins for analog readings in Wi-Fi projects.
- Default I²C pins are usually GPIO 21 (SDA) and 22 (SCL), but they can be remapped; check your board's pinout.

## Pattern: blink without blocking

```cpp
unsigned long last = 0;
const unsigned long interval = 500;     // ms

void loop() {
  if (millis() - last >= interval) {    // subtraction keeps working when millis() rolls over
    last = millis();
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
  // other work keeps running here
}
```

`delay()` freezes the whole program; `millis()` lets you do several things at once.

## I²C basics

Two wires (SDA, SCL) plus power and ground. Each device has an address. The bus needs pull-up resistors, typically 4.7 kΩ to the logic voltage; many breakout boards include them. Run an "I²C scanner" sketch to find a device's address if something doesn't respond.
