

This module was created to easily create BTHome advertisement data for further use in bluetooth advertising.
It is based on BTHome v2 format documentation (https://bthome.io/format/).

Please note that the module is not fully tested and may not work as expected.
All contributions, suggestions and bug reports are welcome.

### Motivation
There was no actual ready-to-use, simple module/package which, by passing measurement data to it, 
would parse the data to BTHome v2 format. 
Every example of BTHome use I found was for specific measurements and mostly mixed up with 
some bluetooth library, which not always worked with used hardware and software.


### How to use
Because the module is just 2 files, you can just copy them to your project and use it as you want.

First you need to initialize the class with your device name:
```python
from bthome_pyadvertisement import BTHomeAdvertisementData

bthome = BTHomeAdvertisementData(advertisement_name="MyDevice")
```

Then you can get the advertisement data by passing your measurements to the class:
```python
adv_data = bthome.get_advertisement_data(temperature=28)
```

The `get_advertisement_data` method can be called with many kwargs, which will be parsed to BTHome format.
All available kwargs are listed in `bthome_sensor_data.json` file and the code uses this file.

### Example
```python
from bthome_pyadvertisement import BTHomeAdvertisementData

bthome = BTHomeAdvertisementData(advertisement_name="MyDevice")
adv_data = bthome.get_advertisement_data(temperature=28)

# pass adv_data to your bluetooth library to advertise it
```


### Todo
- [ ] Add support for BTHome binary sensors
- [ ] Add support for encrypted BTHome data
- [ ] Add CircuitPython and MicroPython bluetooth libraries and create examples for them


### License: MIT License