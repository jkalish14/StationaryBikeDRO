from machine import Pin, mem16
import time

p2=Pin(2, Pin.OUT)

@micropython.viper
def gpio_on(value : int, addr : int):

    GPIO_SET_REG = ptr32(addr)
    GPIO_SET_REG[0] = value

@micropython.viper
def gpio_off(value : int, addr : int):
    GPIO_CLEAR_REG = ptr32( addr)
    GPIO_CLEAR_REG[0] = value



# gpio_on((1 << 13 ) | (1 << 12), 0x3FF44008)
# time.sleep(2)
# gpio_off((1 << 13 ) | (1 << 12), 0x3FF44008)

gpio_off((1 << 13) | ( 1 << 12), 0x3FF4400C)

time.sleep(2)
gpio_on( , 0x3FF44008)