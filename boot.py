# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)


# # Connect to the local network
# import network
# import passwords

# sta_if = network.WLAN(network.STA_IF)
# if not sta_if.isconnected():
#     print('connecting to network...')
#     sta_if.active(True)
#     sta_if.connect(passwords.SSID, passwords.PASSWORD)
#     while not sta_if.isconnected():
#         pass
# print('network config:', sta_if.ifconfig())


# ## Start the webrepl so we can interface with the ESP over wifi
# import webrepl
# webrepl.start()


# ## Run the main code 
import blink
if __name__ == "__main__":
    blink.main()
