from smbus2 import SMBus, i2c_msg
import json

"""
    Ожидаемый приход с клиента:
                    {"body":{"id":"10","data":["-226","-22"]},"type":"cmd"}
    Сообщения с сервера принимаются по стандарту json в формате указанном в тестовых json методах типа 
    def testJsonMotors().
    
    Протокол обмена между Малиной и Ардуино "RPINO" Версия протокола 2.0
    Описание протокола обмена между Raspberry и Arduino 
    Все данные отправляются в виде строк. Каждое сообщение, будь то id команды или просто знак "," пакуется как ячейка 
    массива и рассматривается на принимающей стороне как единая команда. 
    В начале сообщение приходит нулевой байт
    Пакет это сообщение внутри скобок [], т.е. по сути массив байтов.
    Разделитель команд внутри пакета два символа идушие подряд - "," и " ", 
    Окончание пакета - "]".  
    Пример отправки: [101] [120,120]
    Пример приемки: 00_91_49_48_49_93_00_91_49_50_48_44_32_49_50_48_93
    В примере выше отправляется всего два пакета id и data. ID отправляется отдельной строкой и сразу после него 
    следует строка с параметрами для исполняемой функции.
"""

def parse_id(data):
    """
    Метод парсит id команды из json и готовит его для отправки на Ардуину.
    """
    dat = json.loads(data)
    id = dat['body']['id']  # достаем из json id
    id = f'[{id}]'
    return id

def parse_json(json = None):
    if json == None:
        return None
    data = json.loads(json)
    body = data['body']['data']
    body = str(body).replace('\'', '')  # убираем кавычки из json схемы
    return body

def parse_list_jsons(jsons = None):
    """
    Перегоняем json в массив из строк
    Ожидаемый вход пример: {'id': 100, 'spdL': 100, 'spdR': 100, 'delay': 1000}
    """
    if jsons == None:
        return None
    ardumsg = []
    for i in jsons:
        gson = json.loads(i)
        str(gson).replace('\'', '') # убираем кавычки из json
        ardumsg.append(gson)
    return ardumsg


def writeByte(data):
    """
    Передать на шину i2c 1 байт данных.
    :param data: int
    """
    with SMBus(1) as bus:
        bus.write_byte(8, data)

def writeBlockData(data):
    """
    Метод отправляет пакет данных на шину i2c
    :param data: str
    Запакованные данные на стороне приемщика выглядят следующим образом:
    Строка на входе - [120, 120]
    Отправляется по i2c - 0
    """

    with SMBus(1) as bus:
        bus.write_i2c_block_data(8, 0, data)
        # bus.write_(8, 0, data)

def strToCode(data):
    """
    метод принемает строку и возвращает массив символов представленных как коды из ASCII
    """
    data = [ord(i) for i in list(data)]
    return data

def toPackMessage(arr):
    with SMBus(1) as bus:
        for i in arr:
            writeString(str(i))
            writeString(',')  # запятая значит продолжаем передачу

def writeString(data):
    """
    метод пишет в буфер строку как последовательность байтов каждый байт как отдельный пакет
    """
    msg = data.encode('utf-8')
    print(msg.__class__)
    for i in msg:
        writeByte(i)

def controller(data):
    ardumsg = parse_list_jsons(data)
    writeBlockData(ardumsg)
