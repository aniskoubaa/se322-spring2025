# Circuit Diagram

## Phase 1: DHT Sensor Only
```
Arduino Nano ESP32    DHT11/DHT22
    3.3V    ----------- VCC
    GND     ----------- GND
    GPIO2   ----------- DATA
```

## Phase 2: DHT Sensor, LED, and Buzzer
```
Arduino Nano ESP32    DHT11/DHT22
    3.3V    ----------- VCC
    GND     ----------- GND
    GPIO2   ----------- DATA

Arduino Nano ESP32    LED
    GPIO13  ----------- LED+ 
    GND     ---- 220Ω - LED-

Arduino Nano ESP32    Buzzer
    GPIO5   ----------- Buzzer+
    GND     ----------- Buzzer-
```

## Breadboard Layout Visual
```
+---------------------+
|   Arduino Nano ESP32|
+---|---|---|---|-----+
    |   |   |   |
    |   |   |   +---- GPIO5 -> Buzzer+
    |   |   |        Buzzer- -> GND
    |   |   |
    |   |   +-------- GPIO13 -> 220Ω -> LED+ 
    |   |            LED- -> GND
    |   |
    |   +------------ GPIO2 -> DHT Data
    |                 DHT VCC -> 3.3V
    |                 DHT GND -> GND
    |
    +---------------- 3.3V, GND
```

**Note**: Always double-check connections before powering on your Arduino to avoid short circuits. 