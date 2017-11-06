# microbit-fireworks
microFireWorks.py - NeoPixel fireworks animation for the BBC micro:bit

Used to create fireworks animation in <a href="https://twitter.com/Our_Frank/status/927229036794916865">this video</a> using two sets of 1 metre 60 NeoPixel strips (and two micro:bits).

60 NeoPixels is too much draw for the micro:bit power supply. We used 4 x 1.2v rechargeable AA batteries to power the NeoPixels separately from the micro:bit and level shifted the output from the micro:bit using a MOSFET level shifter circuit like <a href="https://elinux.org/RPi_GPIO_Interface_Circuits#Classic_MOSFET_level_shifter">this.</a> We found that R2 (only) needed to be a 1M resistor (rather than a 10M one as at the link). A 10M resistor combined with the internal capacitance of the MOSFET messed up the PWM signal and massively confused the NeoPixels - which was interesting but looked nothing like fireworks...
