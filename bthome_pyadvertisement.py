import json
import struct
import utime

DEBUG = True
LOG_TO_FILE = False


def log(message):
    timestamp = utime.localtime()
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        timestamp[0],
        timestamp[1],
        timestamp[2],
        timestamp[3],
        timestamp[4],
        timestamp[5],
    )
    if DEBUG:
        print(f"{formatted_time} - {message}")
    if LOG_TO_FILE:
        with open("log.txt", "a") as log_file:
            log_file.write(f"{formatted_time} - {message}\n")


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
    def float_to_uint_bytes(
        value: float, byte_length: int, factor: float = 1.0
    ) -> bytes:
        """Convert float to bytes as unsigned integer with given byte length and factor."""
        # Scale the value back by the factor and round to get the original integer value
        int_value = round(value / factor)

        if int_value < 0:
            raise ValueError("Value cannot be negative for unsigned integer conversion")

        # Check if the integer fits within the specified byte length
        max_int_value = 2 ** (8 * byte_length) - 1
        if int_value > max_int_value:
            raise ValueError(
                f"Value {int_value} exceeds maximum for {byte_length}-byte unsigned integer"
            )

        # Convert the integer to bytes
        return int_value.to_bytes(byte_length, "little", False)

    @staticmethod
    def float_to_int_bytes(
        value: float, byte_length: int, factor: float = 1.0
    ) -> bytes:
        """Convert float to bytes as unsigned integer with given byte length and factor."""
        # Scale the value back by the factor and round to get the original integer value
        int_value = round(value / factor)

        # Check if the integer fits within the specified byte length
        max_int_value = 2 ** (8 * byte_length) - 1
        if int_value > max_int_value:
            raise ValueError(
                f"Value {int_value} exceeds maximum for {byte_length}-byte unsigned integer"
            )

        # Convert the integer to bytes
        return int_value.to_bytes(byte_length, "little", True)

    @staticmethod
    def float_to_bytes(value: float, byte_length: int, factor: float = 1.0) -> bytes:
        """Convert float to bytes with a given byte length and factor."""
        value /= factor  # Scale the value back by the factor

        if byte_length == 2:
            return struct.pack("e", value)
        elif byte_length == 4:
            return struct.pack("f", value)
        elif byte_length == 8:
            return struct.pack("d", value)
        else:
            raise ValueError(
                f"Only 2, 4, or 8 byte long floats are supported. {byte_length} is not supported."
            )

    def get_sensor_data_bytes(self, sensor_data: dict):
        """
        :param sensor_data: dict with sensor data
        :return: bytearray with sensor data
        """
        bthome_sensor_data = json.load(open("bthome_sensor_data.json"))
        measurement_bytes = []

        log(f"Sensor data: {sensor_data}")

        # Measurement data
        for key, value in sensor_data.items():
            measurement = bthome_sensor_data[key]
            log(f"Processing measurement: {key}: {value}")

            if key == "text":  # Text sensor
                text_bytes = value.encode("utf-8")
                text_length = len(text_bytes)
                measurement_bytes.extend(
                    [int(measurement["service_data_byte"], 16), text_length]
                )
                measurement_bytes.extend(text_bytes)
                continue
            elif key == "raw":  # Raw sensor
                raw_length = len(value)
                measurement_bytes.extend(
                    [int(measurement["service_data_byte"], 16), raw_length]
                )
                measurement_bytes.extend(value.encode("utf-8"))
                continue

            conversion_method = {
                "uint": self.float_to_uint_bytes,
                "uint8": self.float_to_uint_bytes,
                "uint16": self.float_to_uint_bytes,
                "uint24": self.float_to_uint_bytes,
                "uint32": self.float_to_uint_bytes,
                "uint48": self.float_to_uint_bytes,
                "int": self.float_to_int_bytes,
                "sint8": self.float_to_int_bytes,
                "sint16": self.float_to_int_bytes,
                "float": self.float_to_bytes,
                "see below": self.float_to_bytes,
            }[measurement["data_type"]]

            measurement_bytes_value = conversion_method(
                value, measurement["data_bytes_count"], measurement["factor"]
            )

            measurement_bytes.extend([int(measurement["service_data_byte"], 16)])
            measurement_bytes.extend(measurement_bytes_value)

        log(f"Measurement bytes: {measurement_bytes}")
        return measurement_bytes

    def get_advertisement_data(self, **kwargs) -> bytes:
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
        service_data_bytes_length_array = [service_data_bytes_length]

        service_data_with_length = service_data_bytes_length_array + service_data_bytes

        service_data_bytes = bytearray(service_data_with_length)

        # Local name
        local_name = self.adv_local_name

        advertisement_data = advertisement_flags_bytes + service_data_bytes + local_name
        log(f"Advertisement data: {advertisement_data}")
        return advertisement_data
