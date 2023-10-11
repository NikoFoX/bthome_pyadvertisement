import json


class BTHomeAdvertisementData:
    BT_HOME_FLAGS = [0x02, 0x01, 0x06]
    BT_HOME_SERVICE_DATA_BYTE = 0x16
    BT_HOME_UUID_BYTES = [0xD2, 0xFC]
    BT_HOME_DEVICE_INFORMATION_BYTE = 0x40

    def __init__(self, advertisement_name: str):
        self.adv_local_name = self._name2adv(advertisement_name)

    @staticmethod
    def _name2adv(local_name):
        adv_element = bytearray([len(local_name) + 1, 0x09])
        adv_element.extend(bytes(local_name, "utf-8"))
        return adv_element

    @staticmethod
    def value_to_little_endian(
        measurement: float, measurement_factor: float, bytes_count: int
    ):
        # Calculate the integer value by dividing the temperature by the factor
        integer_value = int(measurement / measurement_factor)

        bytes_array = []
        # Extract the lower and upper bytes for little-endian representation
        for i in range(bytes_count):
            lower_byte = integer_value & 0xFF
            bytes_array.append(lower_byte)
            integer_value = integer_value >> 8

        # Reverse the order of the bytes
        bytes_array.reverse()

        little_endian_bytes = bytes(bytes_array)
        return little_endian_bytes

    def get_sensor_data_bytes(self, sensor_data: dict):
        """
        :param sensor_data: dict with sensor data
        :return: bytearray with sensor data
        """
        bthome_sensor_data = json.load(open("bthome_sensor_data.json"))
        measurement_bytes = []

        # Measurement data
        for key, value in sensor_data.items():
            # find measurement in bthome_sensor_data
            measurement = bthome_sensor_data[key]
            measurement_bytes_value = self.value_to_little_endian(
                measurement=value,
                measurement_factor=measurement["factor"],
                bytes_count=measurement["bytes"],
            )
            measurement_bytes.extend(measurement_bytes_value)
        return measurement_bytes

    def get_advertisement_data(self, **kwargs):
        """
        :param kwargs: one of bthome sensor or binary sensor data, which can be found in bthome_sensor_data.json
        :return: advertisement data (bytes)
        """
        if not kwargs:
            raise ValueError("No data to advertise")

        # Flags
        advertisement_flags_bytes = bytearray(BTHomeAdvertisementData.BT_HOME_FLAGS)

        # Service data
        measurement_bytes = self.get_sensor_data_bytes(sensor_data=kwargs)

        service_data_bytes = (
            [BTHomeAdvertisementData.BT_HOME_SERVICE_DATA_BYTE]
            + BTHomeAdvertisementData.BT_HOME_UUID_BYTES
            + [BTHomeAdvertisementData.BT_HOME_DEVICE_INFORMATION_BYTE]
            + measurement_bytes
        )

        # We need to add 1 byte which is the length of the service data
        service_data_bytes_length = len(service_data_bytes)
        service_data_bytes = bytearray([service_data_bytes_length]) + service_data_bytes

        # Local name
        local_name = self.adv_local_name

        advertisement_data = advertisement_flags_bytes + service_data_bytes + local_name
        return advertisement_data


bthome = BTHomeAdvertisementData(advertisement_name="ESP32")
adv_data = bthome.get_advertisement_data(temperature=28)
