#!/usr/bin/env python3

import config as CONFIG

import requests

if CONFIG.DLL:
    import util_dll as UTIL
else:
    import util as UTIL
import serial
import time
import math
import serial.tools.list_ports
import os
import json
import substring
from datetime import datetime
from datetime import timedelta
import random

ser = {}
current_totalizer = 0
send_com_error = True
starttime = time.time()
current_path = CONFIG.FILE_PATH
is_expired = False
http_verify = CONFIG.HTTP_VERIFY
deleyed_modbus_error = CONFIG.DELAYED_MODBUS_ERROR
deleyed_serial_error = CONFIG.DELAYED_SERIAL_ERROR
delay_modbus_count = {}
delay_serial_count = {}
previous_modbus_data = {}
previous_serial_data = {}

test_count = 0


def connectToDevice():
    global ser, current_totalizer, send_com_error
    paramValue = 0

    for i in range(len(CONFIG.COMPORT)):
        try:
            if ser[CONFIG.COMPORT[i]].isOpen():
                ser[CONFIG.COMPORT[i]].close()
        except Exception:
            pass

    for i in range(len(CONFIG.COMPORT)):
        try:
            ser[CONFIG.COMPORT[i]] = serial.Serial(port=CONFIG.COMPORT[i], baudrate=CONFIG.COMPORT_BAUD_RATE[i],
                                                   parity=CONFIG.COMPORT_PARITY[i],
                                                   bytesize=CONFIG.COMPORT_BYTE_SIZE[i],
                                                   stopbits=CONFIG.COMPORT_STOP_BIT[i],
                                                   timeout=CONFIG.COMPORT_TIMEOUT)
            if ser[CONFIG.COMPORT[i]].isOpen():
                message = ser[CONFIG.COMPORT[i]].name + ' is open--------------------------------------------'
                print_debugging(message)
            send_com_error = True
        except Exception as e:
            code = 'E0001'
            message = 'Comport Error ' + str(e)
            error_location = 'connectToDevice1()'
            print_error(code, error_location, message)
            if send_com_error:
                try:
                    sendErrorRequest(code, message, "", CONFIG.STATION_LIST[0]['STATION_NAME'])
                    send_com_error = False
                except Exception as e:
                    code = 'E1000'
                    message = 'Network Error' + str(e)
                    create_error_file(code, message)
    time.sleep(1)
    try:
        for station_index in range(len(CONFIG.STATION_LIST)):
            selected_station = CONFIG.STATION_LIST[station_index]
            selected_station_name = selected_station["STATION_NAME"]
            selected_station['PARAM_VALUE'] = []
            selected_station['IS_EXCEEDED'] = []
            parameter_index = 0
            while parameter_index < len(selected_station['PARAMS_LIST']):
                # for parameter_index in range(len(selected_station['PARAMS_LIST'])):
                print_debugging("param_index*********************" + str(parameter_index))
                paramValueArray = []
                num_of_loops = 0
                selected_comport = selected_station['COMPORT'][parameter_index]
                selected_modbus_device_id = selected_station['MODBUS_DEVICE_ID'][parameter_index]
                selected_modbus_register = selected_station['MODBUS_REGISTER'][parameter_index]
                selected_param_address = selected_station['PARAM_ADDRESS'][parameter_index]
                selected_length = selected_station['BYTES_TO_READ'][parameter_index]
                selected_out_type = selected_station['OUT_TYPE'][parameter_index]
                selected_param_name = selected_station['PARAMS_LIST'][parameter_index]
                selected_protocol = selected_station['PROTOCOL'][parameter_index]
                selected_continuous_readings_flag = 0
                try:
                    selected_continuous_readings = selected_station['CONTINUOUS_READING'][parameter_index]
                except Exception:
                    selected_continuous_readings = 0

                try:
                    selected_zero_value = selected_station['ZERO_VALUE'][parameter_index]
                except Exception:
                    selected_zero_value = False

                try:
                    selected_custom_length = selected_station['CUSTOM_LENGTH_FOR_MODBUS_ERROR'][parameter_index]
                except Exception:
                    selected_custom_length = 0

                todays_date = datetime.today()

                if selected_continuous_readings == 1:
                    selected_continuous_readings_flag = 1
                    num_of_loops = 1
                elif selected_continuous_readings > 1:
                    num_of_loops = selected_continuous_readings
                    selected_length = 0
                    selected_continuous_readings_flag = 2
                    for continuous_readings_count in range(selected_continuous_readings):
                        selected_length = selected_length + selected_station['BYTES_TO_READ'][
                            parameter_index + continuous_readings_count]
                if selected_param_name == 'parameter_93':
                    try:
                        if not os.path.exists(str(current_path) + '/Totalizer'):
                            os.makedirs(str(current_path) + '/Totalizer')
                        if os.path.exists(
                                str(current_path) + '/Totalizer/totalizer_value' + str(station_index) + '.txt'):
                            file1 = open(
                                str(current_path) + "/Totalizer/totalizer_value" + str(station_index) + ".txt", "r")
                            totalizer_read_val = file1.readlines()
                            if totalizer_read_val[1].strip() != str(todays_date.strftime("%Y-%m-%d")):
                                paramValue = 0
                            else:
                                if current_totalizer == 0:
                                    paramValue = 0
                                else:
                                    paramValue = current_totalizer - float(totalizer_read_val[0])
                                file1.close()
                        else:
                            paramValue = 0

                        paramValueArray.append(paramValue)
                    except Exception as e:
                        paramValue = 0
                        code = 'E1001'
                        message = 'Totalizer Fetching Error ' + str(e)
                        error_location = 'connectToDevice1()'
                        print_error(code, error_location, message)
                elif selected_protocol == "MODBUS":
                    try:
                        paramValueArray = readModbusData(selected_comport, selected_modbus_device_id,
                                                         selected_modbus_register,
                                                         selected_param_address, selected_length, selected_out_type,
                                                         selected_param_name, selected_station,
                                                         selected_continuous_readings,
                                                         selected_continuous_readings_flag,
                                                         selected_custom_length, parameter_index)
                    except Exception as e:
                        pass
                elif selected_protocol == "SERIAL":
                    try:
                        paramValueArray = serialProtocolRead(selected_comport, selected_param_address,
                                                             selected_continuous_readings,
                                                             selected_continuous_readings_flag, parameter_index,
                                                             selected_station, selected_param_name)
                    except Exception as e:
                        pass
                elif selected_protocol == "RANDOM":
                    paramValue = float(format(random.uniform(selected_station['RANDOM_VALUE_MIN'][parameter_index],
                                                             selected_station['RANDOM_VALUE_MAX'][parameter_index]),
                                              '.3f'))
                    paramValueArray.append(paramValue)
                else:
                    if CONFIG.ERROR_REPORTING:
                        print_debugging("invalid protocol")
                for loopCount in range(num_of_loops):

                    if loopCount > 0:
                        parameter_index = parameter_index + 1
                    print_debugging("#######" + str(parameter_index))
                    try:
                        paramValue = paramValueArray[loopCount]
                    except Exception as e:
                        paramValue = ''
                    selected_param_name = selected_station['PARAMS_LIST'][parameter_index]

                    print_debugging("\nObtained Raw Value:::" + str(paramValue) + "\n")

                    try:
                        if selected_station['MAX_PARAM_RANGE'][parameter_index] != 0:
                            print_debugging("count before conversion::::" + str(paramValue))
                            paramValue = float(paramValue) * (
                                    float(selected_station['MAX_PARAM_RANGE'][parameter_index])
                                    / float(CONFIG.FULL_COUNT)
                            ) - float(selected_station['COUNT_TO_SUB'][parameter_index])
                            print_debugging("count converted::::" + str(paramValue))
                    except Exception as e:
                        code = 'E1002'
                        message = 'Count Error ' + str(e)
                        error_location = 'connectToDevice1()'
                        print_error(code, error_location, message)

                    try:
                        if selected_param_name == 'parameter_3' or selected_param_name == 'parameter_94':
                            current_totalizer = paramValue
                            if not os.path.exists(str(current_path) + '/Totalizer'):
                                os.makedirs(str(current_path) + '/Totalizer')
                            if os.path.exists(
                                    str(current_path) + '/Totalizer/totalizer_value' + str(station_index) + '.txt'):
                                file1 = open(
                                    str(current_path) + "/Totalizer/totalizer_value" + str(station_index) + ".txt",
                                    "r")
                                totalizer_read_val = file1.readlines()
                                if totalizer_read_val[1].strip() != str(todays_date.strftime("%Y-%m-%d")):
                                    file1.close()
                                    create_totalizer_file(paramValue, todays_date, str(station_index))
                                else:
                                    file1.close()
                            else:
                                create_totalizer_file(paramValue, todays_date, str(station_index))

                    except Exception as e:
                        code = 'E1003'
                        message = 'Totalizer Assigning Error ' + str(e)
                        error_location = 'connectToDevice1()'
                        print_error(code, error_location, message)

                    try:
                        # change here
                        if paramValue == '':
                            if selected_zero_value:
                                selected_station['PARAM_VALUE'].append(float(format(float('0.000'), '.3f')))
                            else:
                                selected_station['PARAM_VALUE'].append(None)
                            selected_station['IS_EXCEEDED'].append(False)
                        else:
                            if selected_station['DEVICE_RANGE_MIN'][parameter_index] <= float(paramValue) <= \
                                    selected_station['DEVICE_RANGE_MAX'][parameter_index]:
                                selected_station['PARAM_VALUE'].append(float(format(float(paramValue), '.3f')))
                                if float(paramValue) > float(selected_station['EXCEEDANCE_LIMIT'][parameter_index]):
                                    selected_station['IS_EXCEEDED'].append(True)
                                else:
                                    selected_station['IS_EXCEEDED'].append(False)
                            else:
                                paramValue = 0
                                selected_station['PARAM_VALUE'].append(float(format(float(paramValue), '.3f')))
                                selected_station['IS_EXCEEDED'].append(False)

                    except Exception as e:
                        code = 'E1004'
                        message = 'Exceedance Error ' + str(e)
                        error_location = 'connectToDevice1()'
                        print_error(code, error_location, message)
                parameter_index = parameter_index + 1
            try:
                sendRequest(selected_station['PARAM_VALUE'], selected_station)
            except Exception as e:
                code = 'E1006'
                message = 'Vasthi Send Request error ' + str(e)
                error_location = 'connectToDevice1()'
                print_error(code, error_location, message)
                create_error_file(code, message)
            if is_expired:
                code = 'E1011'
                message = 'License Expired'
                error_location = 'connectToDevice1()'
                print_error(code, error_location, message)
                create_error_file(code, message)

    except Exception as e:
        code = 'E0002'
        message = 'Modbus/Serial Error ' + str(e)
        error_location = 'connectToDevice1()'
        print_error(code, error_location, message)
        sendErrorRequest(code, message, "", CONFIG.STATION_LIST[0]['STATION_NAME'])
        time.sleep(10)

        # print("Param Value: ", paramValue)


def create_totalizer_file(paramValue, todays_date, station_num):
    if not os.path.exists(str(current_path) + '/Totalizer'):
        os.makedirs(str(current_path) + '/Totalizer')
    file1 = open(str(current_path) + "/Totalizer/totalizer_value" + station_num + ".txt", "w")
    L = [str(paramValue) + "\n", str(todays_date.strftime("%Y-%m-%d")) + "\n"]
    file1.writelines(L)
    file1.close()


def create_error_file(code, message):
    read_line_arr = []
    try:
        todays_date = datetime.today()
        time_minus_16 = datetime.now()
        timestamp1 = str(time_minus_16)[0:17]
        timestamp = timestamp1 + "00"
        file_name = "error_" + str(todays_date.strftime("%Y-%m-%d")) + ".txt"
        if not os.path.exists(str(current_path) + '/Error'):
            os.makedirs(str(current_path) + '/Error')
        try:
            file2 = open(str(current_path) + "/Error/" + file_name, "r")
            read_line_arr = file2.readlines()
            file2.close()
        except Exception as e:
            pass

        if len(read_line_arr) < 50:
            file1 = open(str(current_path) + "/Error/" + file_name, "a")
            L = [str(code) + "::::::" + str(message) + ":::datetime::::" + timestamp + "\n"]
            file1.writelines(L)
            file1.close()
    except Exception as e:
        code = 'E1011'
        message = 'create_error_file ' + str(e)
        error_location = 'create_error_file()'
        print_error(code, error_location, message)


def print_error(code, error_location, message):
    if CONFIG.ERROR_REPORTING:
        todays_date = datetime.today()
        time_minus_16 = datetime.now()
        timestamp1 = str(time_minus_16)[0:17]
        timestamp = timestamp1 + "00"
        file_name = "debugging_" + str(todays_date.strftime("%Y-%m-%d")) + ".txt"
        if not os.path.exists(str(current_path) + '/Debugging'):
            os.makedirs(str(current_path) + '/Debugging')
        file1 = open(str(current_path) + "/Debugging/" + file_name, "a")
        L = ['Error: {}'.format(str(message)),
             'MODBUS--' + code + 'Error Occurred In :' + error_location + ' in main.py file' + "----" + timestamp + "\n"]
        file1.writelines(L)
        file1.close()
        # print('Error: {}'.format(str(message)))
        # print('MODBUS--' + code + 'Error Occurred In :' + error_location + ' in main.py file')
        # print(os.path.abspath(os.getcwd()))


def print_debugging(message):
    if CONFIG.DEBUGGING:
        todays_date = datetime.today()
        time_minus_16 = datetime.now()
        timestamp1 = str(time_minus_16)[0:17]
        timestamp = timestamp1 + "00"
        file_name = "debugging_" + str(todays_date.strftime("%Y-%m-%d")) + ".txt"
        if not os.path.exists(str(current_path) + '/Debugging'):
            os.makedirs(str(current_path) + '/Debugging')
        file1 = open(str(current_path) + "/Debugging/" + file_name, "a")
        L = [str(message) + "----" + timestamp + "\n"]
        file1.writelines(L)
        file1.close()
        # print(message)


def readModbusData(selectedComport, selectedModbusDeviceId, selectedModbusRegister, selectedParamAddress,
                   selectedLength, selectedOutType, selectedParamName, selectedStation, selected_continuous_readings,
                   selected_continuous_readings_flag, selected_custom_length, parameter_index):
    global ser, delay_modbus_count, previous_modbus_data

    paramValue = ''
    out = ''
    paramValueArray = []


    try:
        outData = []
        inputString = ''

        try:
            inputString = UTIL.generateInputString(selectedModbusDeviceId, selectedModbusRegister,
                                                   selectedParamAddress, selectedLength)
        except Exception as e:
            code = 'E0003'
            message = 'Input String Generation Error ' + str(e)
            error_location = 'readModbusData()'
            print_error(code, error_location, message)
            time.sleep(10)

        print_debugging("modbus device id : " + str(selectedModbusDeviceId))
        print_debugging("modbus register : " + str(selectedModbusRegister))
        print_debugging("select param address : " + str(selectedParamAddress))
        print_debugging("select length : " + str(selectedLength))
        print_debugging("Output type : " + str(selectedOutType))
        print_debugging("input code:::" + str(inputString))

        ser[selectedComport].write(inputString)
        time.sleep(1)
        out = ser[selectedComport].read_all()

        if deleyed_modbus_error:
            index_name = str(selectedStation['DELAY_NAME'])
            try:
                delay_modbus_count[index_name]
            except Exception as e:
                delay_modbus_count[index_name] = 0

            try:
                previous_modbus_data[index_name]
            except Exception as e:
                previous_modbus_data[index_name] = ''

            try:
                out = out.decode("utf-8").strip()
            except Exception as e:
                out = out.strip()

            if not str(out):
                if delay_modbus_count[index_name] < CONFIG.DELAYED_MODBUS_COUNT:
                    out = previous_modbus_data[index_name]
                    delay_modbus_count[index_name] = delay_modbus_count[index_name] + 1
                else:
                    previous_modbus_data[index_name] = ""
            else:
                delay_modbus_count[index_name] = 0
                previous_modbus_data[index_name] = out

        for byte in out:
            if CONFIG.DLL:
                outData.append(ord(byte))
            else:
                outData.append(byte)

        if outData:
            # delay_modbus_count[index_name] = 0
            print_debugging("output : " + str(outData))
            if isOutputAligned(outData):
                print_debugging("CRC verification successful!")
                paramValueArray = extractData(selectedOutType, outData, selectedParamName, selectedStation,
                                              selected_continuous_readings, selected_continuous_readings_flag,
                                              selected_custom_length, parameter_index)
            else:
                code = 'E0007'
                message = 'Output Error:: Receive invalid response  from Device'
                error_location = 'readModbusData()'
                print_error(code, error_location, message)
                try:
                    sendErrorRequest(code, message, selectedParamName, selectedStation)
                except Exception as e:
                    code = 'E1007'
                    message = 'Network Error' + str(e)
                    create_error_file(code, message)
        else:

            code = 'E0008'
            message = 'Receive empty output from Device'
            error_location = 'readModbusData()'
            print_error(code, error_location, message)
            try:
                sendErrorRequest(code, message, selectedParamName, selectedStation)
            except Exception as e:
                code = 'E1008'
                message = 'Network Error' + str(e)
                create_error_file(code, message)
    except Exception as e:
        code = 'E0009'
        message = 'ReadModbus Error ' + str(e)
        error_location = 'readModbusData()'
        print_error(code, error_location, message)
        try:
            sendErrorRequest(code, message, selectedParamName, selectedStation)
        except Exception as e:
            code = 'E1009'
            message = 'Network Error' + str(e)
            create_error_file(code, message)
        time.sleep(10)

    return paramValueArray


def isOutputAligned(outData):
    try:
        print_debugging('checking isOutputAligned....')
        interimOutString = outData[0:-2]
        outCrc = outData[-2:]
        print_debugging(str(interimOutString) + '----CRC---' + str(outCrc))
        if outData[0] == interimOutString[0] and outData[1] == interimOutString[1] and UTIL.verifyOutCRC(
                interimOutString, outCrc):
            return True
        else:
            return False

    except Exception as e:
        code = 'E0006'
        message = 'CRC Verification Error ' + str(e)
        error_location = 'isOutputAligned()'
        print_error(code, error_location, message)
        time.sleep(10)


def extractData(selectedOutType, outData, selectedParamName, selectedStation, selected_continuous_readings,
                selected_continuous_readings_flag, selected_custom_length, parameter_index):
    paramValue = ''
    paramValueArray = []
    dataBytesStartIndex = 3
    if selected_custom_length != 0:
        NumberOfOutDataBytesReceived = selected_custom_length
    else:
        NumberOfOutDataBytesReceived = outData[2]
    paramCount = 1  # len(PARAMS_LIST)
    bytesPerParam = int(NumberOfOutDataBytesReceived / paramCount)
    start = dataBytesStartIndex
    end = dataBytesStartIndex + bytesPerParam

    val = []
    for param_count_continuous_readings in range(selected_continuous_readings):
        selectedOutType = selectedStation['OUT_TYPE'][parameter_index + param_count_continuous_readings]
        try:
            for i in range(start, end):
                val.append(format(outData[i], '#04x').replace('0x', ''))  # convert to HEX and remove 0x
            hexvaltoconvert = ""
            popCount = 0
            if selectedOutType == "INTEGER" or selectedOutType == "DECIMAL":
                hexvaltoconvert = str(val[0]) + str(val[1])
                popCount = 2
            if selectedOutType == "LONG_INTEGER":
                hexvaltoconvert = str(val[0]) + str(val[1]) + str(val[2]) + str(val[3])
                popCount = 4
            elif selectedOutType == "SWAPPED_FLOAT":
                hexvaltoconvert = str(val[0]) + str(val[1]) + str(val[2]) + str(val[3])
                popCount = 4
            elif selectedOutType == "FLOAT":
                hexvaltoconvert = str(val[2]) + str(val[3]) + str(val[0]) + str(val[1])
                popCount = 4
            elif selectedOutType == "SWAPPED_DOUBLE":
                hexvaltoconvert = str(val[6]) + str(val[7]) + str(val[4]) + str(val[5]) + str(val[2]) + str(
                    val[3]) + str(val[0]) + str(val[1])
                popCount = 8

            for popCountRemove in range(popCount):
                val.pop(0)

            print_debugging("hexvaltoconvert::" + str(hexvaltoconvert))
            if math.isnan(UTIL.getConvertedData(hexvaltoconvert, selectedOutType)):
                paramValue = 0
            else:
                paramValue = UTIL.getConvertedData(hexvaltoconvert, selectedOutType)
        except Exception as e:
            code = 'E0005'
            message = 'Extract data  Error ' + str(e) + " modbus received :::" + outData
            error_location = 'extractData()'
            print_error(code, error_location, message)
            try:
                sendErrorRequest(code, message, selectedParamName, selectedStation)
            except Exception as e:
                code = 'E1005'
                message = 'Network Error' + str(e)
                create_error_file(code, message)
            time.sleep(10)
        paramValueArray.append(paramValue)

    return paramValueArray


def serialProtocolRead(selectedComport, selectedParamNumber, selected_continuous_readings,
                       selected_continuous_readings_flag, parameter_index, selectedStation, selected_param_name):
    global ser, delay_serial_count, previous_serial_data
    paramValue = ''
    paramValueArray = []


    if CONFIG.CALIBRATION != "":
        ser[selectedComport].write(bytes(CONFIG.CALIBRATION.encode('utf-8')))
    out = ser[selectedComport].read(200)
    time.sleep(2)

    if deleyed_serial_error:
        index_name = str(selectedStation['DELAY_NAME'])
        try:
            delay_serial_count[index_name]
        except Exception as e:
            delay_serial_count[index_name] = 0

        try:
            previous_serial_data[index_name]
        except Exception as e:
            previous_serial_data[index_name] = ''

        try:
            out = out.decode("utf-8").strip()
        except Exception as e:
            out = out.strip()


        if not str(out):
            if delay_serial_count[index_name] < CONFIG.DELAYED_SERIAL_COUNT:
                out = previous_serial_data[index_name]
                delay_serial_count[index_name] = delay_serial_count[index_name] + 1
            else:
                previous_serial_data[index_name] = ""
        else:
            delay_serial_count[index_name] = 0
            previous_serial_data[index_name] = out

        print_debugging(str('Serial Output Received::') + str(out))
        print_debugging(str('Serial Output backup::') + str(previous_serial_data[index_name]))

    try:
        result = out.decode("utf-8")
    except Exception as e:
        result = out

    print_debugging(str('Serial Output Received Result::') + str(result))
    # data_read = (result.split(CONFIG.SERIAL_START_STRING, 0)[0]).split(',')

    data_read = []
    try:
        data_read = (substring.substringByChar(str(result), startChar="#", endChar="$").replace("$", "")).split(',')
    except Exception as e:
        code = 'E0010'
        message = 'Serial Response error' + str(e)
        error_location = 'serialProtocolRead()'
        print_error(code, error_location, message)
        paramValue = ''

    for param_count_continuous_readings in range(selected_continuous_readings):
        try:
            selectedParamNumber = selectedStation['PARAM_ADDRESS'][parameter_index + param_count_continuous_readings]
            paramValue = data_read[selectedParamNumber]
        except Exception as e:
            code = 'E0010'
            message = 'Serial Response error' + str(e)
            error_location = 'serialProtocolRead()'
            print_error(code, error_location, message)
            paramValue = ''
        paramValueArray.append(paramValue)

    return paramValueArray


def sendRequest(parameter_values, station_details):
    global is_expired
    print_debugging("sending parameter array:::" + str(parameter_values))
    time_minus_16 = datetime.now()
    timestamp1 = str(time_minus_16)[0:17]
    timestamp = timestamp1 + "00"
    url = CONFIG.VASTHI_URL
    data = {
        "industry_id": CONFIG.SITE_ID,
        "station_id": station_details['STATION_NAME'],
        "reading": station_details['PARAM_VALUE'],
        "parameter_id": station_details['PARAMS_LIST'],
        "exceedance": station_details['IS_EXCEEDED'],
        "datentime": str(timestamp),
        "cmd": "31",
        "license": station_details['LICENSE']
    }
    if CONFIG.PROXY:
        proxyDict = {
            CONFIG.PROXY_PROTOCOL: CONFIG.PROXY_IP
        }
        resp = requests.post(url, json=data, proxies=proxyDict, verify=http_verify, timeout=CONFIG.HTTP_TIMEOUT)
    else:
        resp = requests.post(url, json=data, verify=http_verify, timeout=CONFIG.HTTP_TIMEOUT)

    print_debugging(data)
    # resp = requests.post(url, json=data, timeout=CONFIG.HTTP_TIMEOUT, verify=http_verify)
    print_debugging(resp.text)

    json_Response = json.loads(resp.text)
    if json_Response['status'] == "expired":
        is_expired = True
    elif json_Response['status'] == "success":
        is_expired = False


def sendErrorRequest(code, message, parameter, selectedStation):
    time_minus_16 = datetime.now()
    timestamp1 = str(time_minus_16)[0:17]
    timestamp = timestamp1 + "00"
    data = {
        "industry_id": CONFIG.SITE_ID,
        "station_id": selectedStation['STATION_NAME'],
        "parameter_id": parameter,
        "datentime": str(timestamp),
        "code": code,
        "message": message,
        "cmd": "32",
        "license": selectedStation['LICENSE']
    }
    url = CONFIG.VASTHI_URL
    print_debugging(data)

    # resp = requests.post(url, json=data, timeout=CONFIG.HTTP_TIMEOUT, verify=http_verify)
    # print_debugging(resp.text)


if __name__ == '__main__':
    testing_count = 0
    while True:
        try:
            connectToDevice()
        except Exception:
            pass
        if not CONFIG.TESTING or testing_count > 1:
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        else:
            testing_count = testing_count + 1
