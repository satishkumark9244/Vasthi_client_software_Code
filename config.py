from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

SITE_ID = ""
CODE_VERSION = "v4.0.0"

VASTHI_URL = "https://api.vasthienviro.com"

FILE_PATH = ""

ERROR_REPORTING = True
DEBUGGING = True
TOTALIZER_FLOW = True

HTTP_VERIFY = True
HTTP_TIMEOUT = 10
TESTING = True

DLL = False

#-------------PROXY------------------------#
PROXY = True
PROXY_PROTOCOL = "https"
PROXY_IP = ""
#-------------PROXY------------------------#

DELAYED_MODBUS_ERROR = True
DELAYED_MODBUS_COUNT = 5

DELAYED_SERIAL_ERROR = True
DELAYED_SERIAL_COUNT = 5

COMPORT = ["COM5"]
COMPORT_PARITY = [PARITY_NONE]
COMPORT_BAUD_RATE = [9600]
COMPORT_BYTE_SIZE = [EIGHTBITS]
COMPORT_STOP_BIT = [STOPBITS_ONE]
COMPORT_PROTOCOL = ["MODBUS"]
COMPORT_TIMEOUT = 5

CALIBRATION = ""
FULL_COUNT = 10457

STATION_1 = {
    "STATION_NAME": "",
    "COMPORT": ["COM5", "COM5", "COM5"],
    # "DATA_BYTES_START_INDEX": 3,
    "MODBUS_DEVICE_ID": [2, 2, 2],
    "MODBUS_REGISTER": [3, 3, 3],  # 3-HOLDING REGISTER #4-INPUT REGISTER
    "BYTES_TO_READ": [2, 1, 1],
    "PARAMS_LIST": ["parameter_2", "parameter_94", "parameter_93","parameter_5"],
    "OUT_TYPE": ["FLOAT", "INTEGER", "INTEGER"],
    "PARAM_ADDRESS": [99, 107, 107],
    # for modbus write modbus address for serial write parameter position starting from 1
    "PROTOCOL": ["RANDOM", "MODBUS", "MODBUS"],
    "PARAM_VALUE": [],
    "IS_EXCEEDED": [],
    "MAX_PARAM_RANGE": [0, 0, 0],
    "EXCEEDANCE_LIMIT": [100, 100000, 10000],
    "LICENSE": "052b8f68c55196523319bc306b60d995",

    "DEVICE_RANGE_MIN": [0, 0, 0, 0, 0],
    "DEVICE_RANGE_MAX": [1000, 100000, 1000, 1000],

    "COUNT_TO_SUB": [0, 0, 0, 0, 0],
    "CONTINUOUS_READING": [1, 1, 1, 1, 1, 1, 1],
    "RANDOM_VALUE_MIN": [0, 0, 0, 0, 0, 0],
    "RANDOM_VALUE_MAX": [10, 100000, 1000, 1000, 1000, 1000],
    "ZERO_VALUE": [False, False, False, False, False],
    "CUSTOM_LENGTH_FOR_MODBUS_ERROR": [0, 0, 0, 0, 0, 0],
    "DELAY_NAME": ['1', '1', '1', '1', '1', '1', '1']
}

STATION_2 = {
    "STATION_NAME": "",
    "COMPORT": ["COM5", "COM5", "COM5"],
    # "DATA_BYTES_START_INDEX": 3,
    "MODBUS_DEVICE_ID": [1, 1, 1],
    "MODBUS_REGISTER": [3, 3, 3],  # 3-HOLDING REGISTER #4-INPUT REGISTER
    "BYTES_TO_READ": [2, 1, 1],
    "PARAMS_LIST": ["parameter_2", "parameter_94", "parameter_93"],
    "OUT_TYPE": ["FLOAT", "INTEGER", "INTEGER"],
    "PARAM_ADDRESS": [99, 107, 107],
    # for modbus write modbus address for serial write parameter position starting from 1
    "PROTOCOL": ["MODBUS", "MODBUS", "MODBUS"],
    "PARAM_VALUE": [],
    "IS_EXCEEDED": [],
    "MAX_PARAM_RANGE": [0, 0, 0],
    "EXCEEDANCE_LIMIT": [100, 100000, 10000],
    "LICENSE": "e62f0e4c2edbf4b5374cc9208e7f2949",
    "DEVICE_RANGE_MIN": [0, 0, 0, 0, 0],
    "DEVICE_RANGE_MAX": [1000, 100000, 1000, 1000],
    "COUNT_TO_SUB": [0, 0, 0, 0, 0],
    "CONTINUOUS_READING": [1, 1, 1, 1, 1, 1, 1],
    "RANDOM_VALUE_MIN": [0, 0, 0, 0, 0, 0],
    "RANDOM_VALUE_MAX": [100, 1000, 1000, 1000, 1000, 1000],
    "ZERO_VALUE": [False, False, False, False, False],
    "CUSTOM_LENGTH_FOR_MODBUS_ERROR": [0, 0, 0, 0, 0, 0],
    "DELAY_NAME": ['1', '1', '1', '1', '1', '1', '1']
}

STATION_LIST = [STATION_1, STATION_2]
