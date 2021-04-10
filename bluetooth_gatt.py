import bluetooth
from ble_advertising import advertising_payload
import utime

CSC_SERVICE_UUID        = 0x1816
CSC_MEASUREMENT_UUID    = 0x2A5B
CSC_FEATURE_UUID        = 0x2A5C


_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)


# Define the service
CSC_UUID = bluetooth.UUID(CSC_SERVICE_UUID)

# Define the characteristic
CSC_MEASUREMENT_CHAR = ( bluetooth.UUID(CSC_MEASUREMENT_UUID), bluetooth.FLAG_NOTIFY)
CSC_FEATURE_CHAR =  (bluetooth.UUID(CSC_FEATURE_UUID), bluetooth.FLAG_READ)

CSC_SERVICE = (CSC_UUID, (CSC_MEASUREMENT_CHAR, CSC_FEATURE_CHAR),)
PROFILE = (CSC_SERVICE,)


class BLEGattServer:
    def __init__(self, ble, name="MicroPy"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._csc_msr_handle, self._csc_ftr_handle),) = self._ble.gatts_register_services(PROFILE)
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[CSC_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._csc_msr_handle, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


def demo():
    ble = bluetooth.BLE()
    p = BLEGattServer(ble)
    num_revs = 0

    while True:
        if p.is_connected():
            # Short burst of queued notifications.

            ## CSC Measurement Buffer
            # https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.csc_measurement.xml
            # 
            # Features:
            #   [Flags] 8 bit
            #   [Cumulative Wheel Revolutions] uint32
            #   [Last Wheel Event Time]  uint16
            #   [Cumulative Crank Revolutions] uint16
            #   [Last Crank Event Time] uint16

            num_revs += 1
            contains_data = "{0:08b}".format(2)
            cum_crank_revolutions = "{0:016b}".format(num_revs)
            last_event_time = "{0:016b}".format(int(1024*utime.ticks_us()/(1e6)))
            package = int(last_event_time + cum_crank_revolutions + contains_data,2).to_bytes(5, 'little')

            p.send(package)
            print('Writing: ', package)
            utime.sleep(1)

            ## Feature Characteristic
            # https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.csc_feature.xml
            #
            # Features:
            #   [CSC Feature] 16bit

            # csc_feature_buffer = b'0000000000000001'
            
            # p.send(str(rpm))
        # time.sleep_ms(100)


if __name__ == "__main__":
    demo()