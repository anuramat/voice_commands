#!/usr/bin/env python3

import os
import queue
import sounddevice as sd
import vosk
import sys
import json

import arduino_controller
from voice_parser import parse

q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def listen(return_callback = None, filename = None, samplerate = None, model = None, device = None):
    # str filename : file for the audio recording
    # str model : path to the model
    # int/str device : input device (numeric ID or substring)
    # int samplerate

    if not return_callback:
        return_callback = print
    if model is None:
        model = "model"
    if not os.path.exists(model):
        print ("Please download a model for your language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")
        return
    if samplerate is None:
        device_info = sd.query_devices(device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(model)

    if filename:
        dump_fn = open(filename, "wb")
    else:
        dump_fn = None
    
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16',
                            channels=1, callback=callback):

            words = "едь вперёд назад поверни направо налево стоп один два три четыре пять шесть семь восемь девять десять секунд секунды до препятствия включи выключи свет проиграй мелодию подожди нажатие кнопки кто такой ваня"
            words = words.split(' ')
            rec = vosk.KaldiRecognizer(model, samplerate, f'["{" ".join(words)}", "[unk]"]')
            print('loaded')
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    text = json.loads(rec.Result())['text']
                    if text:
                        cmds = parse(text)
                        return_callback(cmds)
                else:
                    pass
                    #print(rec.PartialResult())
                if dump_fn is not None:
                    dump_fn.write(data)

if __name__ == '__main__':
    try:
        print(sd.query_devices()) # list the devices together with their ID's
        listen(arduino_controller.controller)
    except KeyboardInterrupt:
        print('done')