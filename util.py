from ctypes import cast, pointer, c_int, c_float, POINTER
from builtins import str
import struct


INITIAL_MODBUS = 0xFFFF
INITIAL_DF1 = 0x0000

table = (
    0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
    0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
    0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
    0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
    0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
    0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
    0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
    0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
    0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
    0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
    0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
    0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
    0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
    0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
    0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
    0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
    0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
    0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
    0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
    0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
    0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
    0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
    0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
    0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
    0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
    0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
    0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
    0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
    0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
    0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
    0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
    0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040)


def CRC16_Byte(ch, crc):
    """Given a new Byte and previous CRC, Calculate a new CRC-16"""
    if type(ch) == type("c"):
        by = ord(ch)
    else:
        by = ch
    crc = (crc >> 8) ^ table[(crc ^ by) & 0xFF]
    return (crc & 0xFFFF)


def CRC16_String(st, crc):
    """Given a binary string and starting CRC, Calculate a final CRC-16 """
    for ch in st:
        crc = (crc >> 8) ^ table[(crc ^ ord(ch)) & 0xFF]
    return crc


def CRC16_BIG_INDIAN(st):
    crc = format(CRC16_String(st, INITIAL_MODBUS), '#04x').replace('0x', '')

    if len(crc) % 2 == 0:
        if crc[2:] == '':
            return crc[0:2] + '00'
        if crc[0:2] == '':
            return crc[2:] + '00'
        return crc[2:] + crc[0:2]  # Returning in BIG INDIAN Format
    else:
        crc = '0' + crc
        return crc[2:] + crc[0:2]


def rawStringToCRCInput(inp):
    return bytes.fromhex(inp).decode('utf-8')


def init_table():  # Use only if required
    # Initialize the CRC-16 table,
    #   build a 256-entry list, then convert to read-only tuple
    global table
    a1st = []
    for i in range(256):
        data = i << 1
        crc = 0
        for j in range(8, 0, -1):
            data >>= 1
            if (data ^ crc) & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

        a1st.append(crc)

    table = tuple(a1st)
    return

def getConvertedData(val, dtype):
    # start V0
    # if dtype == DATA_TYPE[0]:     #INTEGER
    # end V0
    # start V1.4
    if dtype == "INTEGER" or dtype == "LONG_INTEGER":
        return int(val, 16)
    elif dtype == "DECIMAL":
        return int(val, 16) / 100

    elif dtype == "SWAPPED_DOUBLE":
        return struct.unpack('!d', bytes.fromhex(val))[0]
    # end V1.4

    elif dtype == "SWAPPED_FLOAT" or dtype == "FLOAT" or dtype == "BIG_I":  # ABCD - BIG_I
        return hexToFloat(val)

    elif dtype == "LITTLE_I":  # DCBA - LITTLE_I
        val_arr = [val[6:8], val[4:6], val[2:4], val[0:2]]
        strval = ''
        for item in val_arr:
            strval = strval + item
        return hexToFloat(strval)

    elif dtype == "MID_BIG_I":  # BADC - MID_BIG_I
        val_arr = [val[2:4], val[0:2], val[6:8], val[4:6]]
        strval = ''
        for item in val_arr:
            strval = strval + item
        return hexToFloat(strval)

    elif dtype == "MID_LITTLE_I":  # CDAB - MID_LITTLE_I
        val_arr = [val[4:6], val[6:8], val[0:2], val[2:4]]
        strval = ''
        for item in val_arr:
            strval = strval + item
        return hexToFloat(strval)

    # end V1.4


def hexToFloat(s):
    i = int(s, 16)  # convert from hex to a Python int
    cp = pointer(c_int(i))  # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    return fp.contents.value  # dereference the pointer, get the float


def handleByteAbove255(val):
    if len(val) < 4:
        val = '0' + val
    return val


def generateInputString(selected_modbus_device_id, selected_modbus_register, selected_param_address, selected_length):
    slaveId = format(selected_modbus_device_id, '#04x').replace('0x', '')
    holdingRegister = format(selected_modbus_register, '#04x').replace('0x', '')
    start = ''
    bytesToRead = ''
    if selected_param_address > 255:
        start = handleByteAbove255(format(selected_param_address, '#04x').replace('0x', ''))
    else:
        start = start + '00' + format(selected_param_address, '#04x').replace('0x', '')

    if selected_length > 255:
        bytesToRead = handleByteAbove255(format(selected_length, '#04x').replace('0x', ''))
    else:
        bytesToRead = bytesToRead + '00' + format(selected_length, '#04x').replace('0x', '')

    interimn_input_string = slaveId + holdingRegister + start + bytesToRead

    final_input_string = interimn_input_string + CRC16_BIG_INDIAN(
        bytes.fromhex(interimn_input_string).decode('latin-1'))
    return bytes.fromhex(final_input_string)
    # End


def verifyOutCRC(out, outCRC):
    outStr = getStringFromList(out)
    oCRC = getStringFromList(outCRC)
    myCRC = CRC16_BIG_INDIAN(bytes.fromhex(outStr).decode('latin-1'))
    # print('My CRC -- ', myCRC, ', CRC from modbus --', oCRC)
    if myCRC == oCRC:
        return True
    else:
        return False


def getStringFromList(lis):
    outStr = ''
    for item in lis:
        outStr += format(item, '#04x').replace('0x', '')
    return outStr


if __name__ == '__main__':
    pass
