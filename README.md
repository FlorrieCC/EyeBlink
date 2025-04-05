## FLIR Lepton 3.5

### Details

- **Name (CN)**: Miniature LWIR (Long-wave Infrared) Thermal Imaging Sensor thermal camera
- **Model**: FLIR Lepton 3.5 ([Official Website](https://www.flir.asia/products/lepton/?model=500-0771-01&vertical=microcam&segment=oem))
- **Operating Principle**: LWIR microbolometer array.
- **Video Stream Support**: Outputs infrared thermal video stream.
- **Temperature Range**: -10°C to 140°C
- **Resolution**: 160×120
- **Field of View (FOV)**:
  - Horizontal: 57°, Diagonal: 71°, Vertical Field of View (VFOV): 46.34° (Calculated)
- **Frame Rate**: 8.6Hz
- **Thermal Sensitivity (NETD)**: ≤50mK
- **Data Format**: User-selectable 14-bit, 8-bit (AGC applied), or 24-bit RGB (AGC and colorization applied)
- **Price**: 1,337.99 HKD (Module included: 3,989 HKD)
- **Data Reading**: [Data Reading Example](https://book.openmv.cc/example/27-Lepton/lepton-get-object-temp.html)

### Experiment

OpenmMV development board is also a usb device, put the [main file](https://github.com/FlorrieCC/EyeBlink/blob/main/FLIR_LEPTON/main.py), when the OpenMV device is connected to the computer through the usb interface, the device will run its own main script. We use a [controller](https://github.com/FlorrieCC/EyeBlink/blob/main/FLIR_LEPTON/controller.py) to listen to the script to run the device manually, and detach from the plugin provided by OpenMV as well as the IDE, use the command line to run mutiple devices at one time.


## Seek Thermal Micro Core M2

- **Name (CN)**: Consumer and Industrial Infrared Thermal Imaging Device thermal camera
- **Model**: Micro Core M2 ([Official Website](https://www.thermal.com/uploads/1/0/1/3/101388544/micro_core_specification_sheet.pdf))
- **Operating Principle**: Uncooled Vanadium Oxide Microbolometer (7.8 - 14 µm)
- **Video Stream Support**: Supported (limited to <9Hz)
- **Temperature Range**: -20°C to 300°C
- **Resolution**: 200×150
- **Field of View (FOV)**: 81°×61°
- **Frame Rate**: <9Hz
- **Thermal Sensitivity (NETD)**: 75 mK
- **Data Format**: 16-bit RAW data, 32-bit ARGB processed data, supports floating-point or fixed-point thermal imaging temperature units (°C, °F, K)
- **Price**: 5,088.86 HKD
- **Data Reading**: [seekcamera-python SDK](https://github.com/seekcamera/seekcamera-python)


### The complete readme: https://possible-calf-de9.notion.site/Thermal-Duo-One-Truth-Building-a-Reliable-Deployment-for-Comparative-Thermal-Sensing-1c7208d1fa5780f2997dd9ca39009ebf?pvs=4