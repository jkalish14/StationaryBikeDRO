from machine import Pin
import micropython
import time
import utime

micropython.alloc_emergency_exception_buf(100)

# Gear ration: (Flywheel rotations)/(Pedal Rotations) 
GEAR_RATIO = 4.

# LED / 7 Segement paths to ground
LED_LIST = [12, 25, 15, 26, 14, 27, 0, 4] # RPi GPIO Pins that the LEDS are connected to

# Defines the pins needed to create the specified number on the 7 segement display
SEVEN_SEG_DICT = {0 : [15, 27, 4, 26, 12, 25],
                  1:  [12, 26]  ,
                  2 : [25, 12, 14, 27, 4], 
                  3 : [25, 12, 14, 26, 4],
                  4 : [12, 14, 26, 15],
                  5 : [12, 15, 14, 26, 4],
                  6 : [12, 15, 14, 26, 4, 27],
                  7 : [25, 12, 26],
                  8 : [14, 15, 27, 4, 26, 12, 25],
                  9 : [14, 15, 26, 12, 25],
                  "dp" : [0],
                  "All" : [14, 15, 27, 4, 26, 12, 25, 0]}

# Power-bus power pins
HIGH_LED_PWR = const(13)
MED_LED_PWR =  const(32)
LOW_LED_PWR =  const(33)
LED_PWR_LIST = [HIGH_LED_PWR, MED_LED_PWR, LOW_LED_PWR]

# 7 Segement display power pins
DIGIT_1 = const(17)
DIGIT_2 = const(16)
DIGIT_3 = const(2)
DIGIT_PWR_LIST = [DIGIT_1, DIGIT_2, DIGIT_3]

# GPIO pin the Hall effect is read from
HALL_EFFECT = 35

# How long to leave the LEDS on for (trades brightness for execution time)
SLEEP_TIME_S = 0.001

# ESP32 Specific Registers (controls the toggeling of GPIO pins)
GPIO_IN_REG = const(0x3FF4403C)
GPIO_OUT_W1TS_REG = const(0x3FF44008)
GPIO_OUT_W1TC_REG = const(0x3FF4400C)
GPIO_IN1_REG = const(0x3FF44040 )
GPIO_OUT1_W1TS_REG = const(0x3FF44014)
GPIO_OUT1_W1TC_REG = const(0x3FF44018)

# Read the GPIO state of a specified pin number
@micropython.viper
def gpio_state(pinNum : int) -> bool:
    
    if pinNum < 32:
        REG = ptr32(GPIO_IN_REG)
    else:
        pinNum -= 32
        REG = ptr32(GPIO_IN1_REG)

    return bool(REG[0] & ( 1 << pinNum))

# provided a binary mask, set the value in the register that toggle GPIO Pins 1-31 on
@micropython.viper
def gpio_on(value : int):
    GPIO_SET_REG = ptr32(GPIO_OUT_W1TS_REG)
    GPIO_SET_REG[0] = value

# provided a binary mask, set the value in the register that toggle GPIO Pins 32-39 on
@micropython.viper
def gpio_on1(value : int):
    GPIO_SET_REG = ptr32(GPIO_OUT1_W1TS_REG)
    GPIO_SET_REG[0] = value

# provided a binary mask, set the value in the register that toggle GPIO Pins 1-31 off
@micropython.viper
def gpio_off(value : int):
    GPIO_CLEAR_REG = ptr32(GPIO_OUT_W1TC_REG)
    GPIO_CLEAR_REG[0] = value

# provided a binary mask, set the value in the register that toggle GPIO Pins 32-39 off
@micropython.viper
def gpio_off1(value:int):
    GPIO_CLEAR_REG = ptr32(GPIO_OUT1_W1TC_REG)
    GPIO_CLEAR_REG[0] = value

# combine an integer list of pins into a single binary expression
def turn_pinlist_on(list):
    register_value_0 = 0x0
    register_value_1 = 0x0

    for pin in list:
        if pin < 32:
            register_value_0 |= (1 << pin)
        else:
            register_value_1 |= (1 << (pin-32))
    
    # turn on the associated pins
    gpio_on(register_value_0)
    gpio_on1(register_value_1)

# combine an integer list of pins into a single binary expression
def turn_pinlist_off(list):
    register_value_0 = 0x0
    register_value_1 = 0x0

    for pin in list:
        if pin < 32:
            register_value_0 |= (1 << pin)
        else:
            register_value_1 |= (1 << (pin-32))
    
    # turn off the associated pins
    gpio_off(register_value_0)
    gpio_off1(register_value_1)

# Helper function to time the execution of code
def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

# Iniailize DRO pins and set all GPIO pins high (no paths to ground) and 
def init_DRO_pins():
    [Pin(pin, Pin.OUT) for pin in LED_LIST + LED_PWR_LIST + DIGIT_PWR_LIST]
    turn_pinlist_on(LED_LIST + LED_PWR_LIST + DIGIT_PWR_LIST)

# Provided a percent, determine the number of LEDS to illuminate
# @timed_function
def update_leds(percent):

    # The logic on the LEDs is backwards, so lets reverse that here
    off = turn_pinlist_on
    on = turn_pinlist_off

    if percent > 100:
        percent = 100

    num_leds = int(percent*24.0/100.0)
    
    leds = LED_LIST
    
    # update low LED Bank
    if num_leds >= 8:
        on(leds + [LOW_LED_PWR])
    else:
        # Leds are in opposite order for the first bank
        on(leds[-num_leds:] + [LOW_LED_PWR])

    time.sleep(SLEEP_TIME_S)

    # Turn off the LEDS and their power
    off(leds + [LOW_LED_PWR])


    # Update med LED bank
    num_med_leds = num_leds - 8
    if num_med_leds > 0 :
        if num_med_leds >= 8:
            on(leds+ [MED_LED_PWR])
        else:
            on(leds[0:num_med_leds]+ [MED_LED_PWR])

        time.sleep(SLEEP_TIME_S)

        # Turn off the LEDS
        off(leds + [MED_LED_PWR])

    # update High LED Bank
    num_high_leds = num_leds - 16
    if num_high_leds > 0:
        if num_high_leds >= 8:
            on(leds + [HIGH_LED_PWR])
        else:
            on(leds[0:num_high_leds] + [HIGH_LED_PWR])

        time.sleep(SLEEP_TIME_S)
        # Turn off the LEDS
        off(leds + [HIGH_LED_PWR])

# Given an integer, update the 7 segment displays to display the  number
# @timed_function
def update_display(val):
    # off = turn_pinlist_on
    # on = turn_pinlist_off

    Seven_Seg_Dict = SEVEN_SEG_DICT

    digits  = [int(d) for d in str(val)]
    if len(digits) == 1:
        digits = [0,0, digits[0]]
    elif len(digits) == 2:
        digits = [0, digits[0], digits[1]]
    elif len(digits) > 3:
        digits = digits[-3:]

    # update Display digit 1
    target = Seven_Seg_Dict[digits[-1]] + [DIGIT_1]
    turn_pinlist_off(target)
    turn_pinlist_on(target)

    # update Display digit 2
    target = Seven_Seg_Dict[digits[-2]] + [DIGIT_2]
    turn_pinlist_off(target)
    turn_pinlist_on(target)
    
    # Update display digit 3
    target = Seven_Seg_Dict[digits[-3]] + [DIGIT_3]
    turn_pinlist_off(target)
    turn_pinlist_on(target)

# Helper function to round the calculated RPM
def round_to_nearest(x, base=5):
    return int(base * round(x/base))

# Calculate the RPMs by averaing the time difference in the buffer
# This function is only called by the ISR
# @timed_function
def calculate_rpm(Pin):
    global hall_effect_buffer
    global rpm_num

    # record the time
    hall_effect_buffer.append(utime.ticks_ms())
    hall_effect_buffer.pop(0)

    # Calculate the average time between pulses
    diff_len = len(hall_effect_buffer)-1
    diff = [0]*diff_len
    rng = range(0, diff_len)
    for i in rng:
        diff[i] = utime.ticks_diff(hall_effect_buffer[i+1],hall_effect_buffer[i])/1000.0

    avg_diff = sum(diff)/float(diff_len)
    
    # from the avg_diff, calculate the RPM and deal with the divide by zero error that could arise
    if avg_diff == 0:
        rpm_num = 0
    else:
        # RPMS will be rather inconsistant, so instead, round the results to 0 or 5
        rpm_num = round_to_nearest(60./(avg_diff*GEAR_RATIO), 5)

    # Print and return the results
    print("rpm: ", rpm_num)         


# Initialize the pins and buffers that will be used
init_DRO_pins()

# Set the hall effect pin as an input
he_pin = Pin(HALL_EFFECT, Pin.IN)

# Initialize the needed variables
hall_effect_buffer = [0.,]*10
rpm_num = 0
led_val = 0
last_update_time = 0

# Initilize the interrupt service routine
he_pin.irq(handler=calculate_rpm, trigger=Pin.IRQ_FALLING)

# Run the update loop indefinitely 
while True: 
    now = utime.ticks_us()
    if now - last_update_time > 8000: # update at 120hz
        last_update_time = now
        update_leds(led_val)
        update_display(rpm_num)

        led_val = (rpm_num/150)*100.0


    
