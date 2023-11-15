import json
import struct


class BTHomeAdvertisementData:
    # Based on documentation: https://bthome.io/format/
    BT_HOME_FLAGS = [0x02, 0x01, 0x06]  # per documentation Flags
    BT_HOME_SERVICE_DATA_SPECIAL_BYTE = 0x16
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
    def value_to_bytes(value, data_type: str, factor: float, bytes_count: int):
        # Determine the byte length based on the data type
        if data_type in ["uint", "uint8"]:
            struct_format = "B"
            if bytes_count == 2:
                struct_format = "H"
        elif data_type == "uint16":
            struct_format = "H"
        elif data_type == "uint24":
            struct_format = "I"
        elif data_type == "sint16":
            struct_format = "h"
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        # Add the byte order to the struct format (big endian)
        struct_format = ">" + struct_format

        byte_length = bytes_count

        # Convert float value to the integer representation based on the factor
        integer_value = int(value / factor)

        # Pack the integer value into bytes
        packed_bytes = bytearray(struct.pack(struct_format, integer_value))

        # Return the bytes
        packed_bytes = packed_bytes[:byte_length]
        return packed_bytes

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
            measurement_bytes_value = self.value_to_bytes(
                value=value,
                data_type=measurement["data_type"],
                factor=measurement["factor"],
                bytes_count=measurement["data_bytes_count"],
            )
            measurement_bytes.extend([int(measurement["service_data_byte"], 16)])
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
            [BTHomeAdvertisementData.BT_HOME_SERVICE_DATA_SPECIAL_BYTE]
            + BTHomeAdvertisementData.BT_HOME_UUID_BYTES
            + [BTHomeAdvertisementData.BT_HOME_DEVICE_INFORMATION_BYTE]
        )
        service_data_bytes.extend(measurement_bytes)

        # We need to add 1 byte which is the length of the service data
        service_data_bytes_length = len(service_data_bytes)
        service_data_bytes = bytearray([service_data_bytes_length] + service_data_bytes)

        # Local name
        local_name = self.adv_local_name

        advertisement_data = advertisement_flags_bytes + service_data_bytes + local_name
        return advertisement_data
