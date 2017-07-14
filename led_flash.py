""" This is a LED Flash program on Raspberry Pi 3 onboard (LED0). """
# -*- coding: utf-8 -*-
import time

FLASH_TIMES = 5
FLASH_INTERVAL = 0.2
FILEPATH = '/sys/class/leds/led0/brightness'

def led_on():
    f = open(FILEPATH, 'w')
    f.write('1')
    f.close()
    
def led_off():
    f = open(FILEPATH, 'w')
    f.write('0')
    f.close()

def led_flash():
    for i in range(FLASH_TIMES):
        led_on()
        time.sleep(FLASH_INTERVAL)
        led_off()
        time.sleep(FLASH_INTERVAL)

if __name__ == "__main__":
    led_flash()

