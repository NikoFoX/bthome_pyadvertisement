

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


### Example
```python
from upy_bthome import BTHomeAdvertisementData

bthome = BTHomeAdvertisementData(advertisement_name="MyDevice")
adv_data = bthome.get_advertisement_data(temperature=28)

# pass adv_data to your bluetooth library to advertise it
```


### Todo
- [ ] Add support for BTHome binary sensors
- [ ] Add support for encrypted BTHome data
- [ ] Add CircuitPython and MicroPython bluetooth libraries and create examples for them


### License: MIT License