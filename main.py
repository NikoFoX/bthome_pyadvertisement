import ustruct, bluetooth
from bthome_pyadvertisement import BTHomeAdvertisementData
from utime import sleep_ms


ble = bluetooth.BLE()
ble.active(True)
print(
    bytes(ble.config("mac")[1])
)  # get the address of your transmitter to put into the receiver code

# set advertising interval to 500 ms
advertisingInterval_us = 100000  # 100 ms
loopIterationDuration_ms = 1000  # 1 second

bthome = BTHomeAdvertisementData(advertisement_name="zordon")

measurements = [
    ("temperature_2", -10.2),
    # ("temperature_2", 3.62),
    ("humidity", 33.66),
    ("count", 36),
    # ("count_2", 33777),
]
measurements_2 = [
    ("battery", 33),
]

# adv_data = bthome.get_advertisement_data(**{name: value for name, value in measurements})
# adv_data_2 = bthome.get_advertisement_data(**{name: value for name, value in measurements_2})

count = 0
temp = 0.00
humidity = 0.00
pressure = 0.00


def advertise_measurements():
    global count, temp, humidity, pressure

    count += 1
    temp += 0.01
    humidity += 0.01
    pressure += 0.01
    measurement_value = {
        "temperature_2": temp,
        "humidity": humidity,
        "count_2": count,
        "pressure": pressure,
    }
    adv_data = bthome.get_advertisement_data(**measurement_value)
    ble.gap_advertise(
        advertisingInterval_us, adv_data, connectable=False
    )  # not connectable because this is just to send the data
    sleep_ms(loopIterationDuration_ms)


while True:
    advertise_measurements()
#     ble.gap_advertise(advertisingInterval_us,adv_data=adv_data, connectable=False) #not connectable because this is just to send the data
#     sleep_ms(loopIterationDuration_ms)
#     ble.gap_advertise(advertisingInterval_us,adv_data=adv_data_2, connectable=False) #not connectable because this is just to send the data
#     sleep_ms(loopIterationDuration_ms)
#     counter += 1
#     if counter == 30:
#         break
