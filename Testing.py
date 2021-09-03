import unittest
import asyncio
import logging
import websockets
from smbus2 import SMBus, i2c_msg
import json
import arduino_controller


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

def testJsonServo():
    """Тестовый метод, который формирует JSON и отправляет его в метод приема сообщений с сервера"""
    servo = {
        "type": "cmd",
        "body": {
            "id": "201",
            "data": [
                "100",
            ]
        }
    }
    messagePack = json.dumps(servo)

    id = arduino_controller.parse_id(messagePack)
    arduino_controller.writeBlockData(arduino_controller.strToCode(id))
    data = arduino_controller.parse_json(messagePack)
    arduino_controller.writeBlockData(arduino_controller.strToCode(data))


def testJsonMotorsDelay():
    """Тестовый метод, который формирует JSON и отправляет его в метод приема сообщений с сервера"""
    # id = parse_id(testJsonMotors())
    # writeString(id)
    # data = parse_data(testJsonMotors())
    # writeString(data)
    motors = {
        "type": "cmd",
        "body": {
            "id": "100",
            "data": [
                "120",
                "120",
                "5000",
            ]
        }
    }
    return json.dumps(motors)


def testJsonJoystick():
    """Тестовый метод, который формирует JSON и отправляет его в метод приема сообщений с сервера"""

    joystick = {
        "type": "cmd",
        "body": {
            "id": "10",
            "data": [
                "120",
                "120",
            ]
        }
    }
    messagePack = json.dumps(joystick)

    id = arduino_controller.parse_id(messagePack)
    arduino_controller.writeBlockData(arduino_controller.strToCode(id))
    data = arduino_controller.parse_json(messagePack)
    arduino_controller.writeBlockData(arduino_controller.strToCode(data))

def testJsonLight():
    """Тестовый метод, который формирует JSON и отправляет его в метод приема сообщений с сервера"""
    light = {
        "type": "cmd",
        "body": {
            "id": "401",
            "data": [
                "true",
                "5000",
            ]
        }
    }
    return json.dumps(light)

def testJsonAudio():
    """Тестовый метод, который формирует JSON и отправляет его в метод приема сообщений с сервера"""
    light = {
        "type": "cmd",
        "body": {
            "id": "13",
            "data": [
                "0",
                "400",
                "5000",
            ]
        }
    }
    messagePack = json.dumps(light)

    id = arduino_controller.parse_id(messagePack)
    arduino_controller.writeBlockData(arduino_controller.strToCode(id))
    data = arduino_controller.parse_json(messagePack)
    arduino_controller.writeBlockData(arduino_controller.strToCode(data))

async def test():
    """Тестовый метод для генерации различных тестовых данных"""
    # cmd_to_i2c(bytearray.fromhex('FFFE01FF'))


if __name__ == '__main__':
    testJsonAudio()
