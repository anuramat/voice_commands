#!/usr/bin/env python3

import os
import queue
import sounddevice as sd
import vosk
import sys
import json
from time import time
import re
import arduino_controller
from voice_parser import parse

q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def listen(name_to_cmd, activator, timeout, deactivator, return_callback, filename = None, samplerate = None, model = None, device = None, verbose = False):
    # str filename : file for the audio recording
    # str model : path to the model
    # int/str device : input device (numeric ID or substring)
    # int samplerate

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

    # TODO update numbers_dict when parser is updated
    numbers_dict = set('одна две три четыре пять шесть семь восемь девять десять'.split())
    cmd_dict = set()
    for name in name_to_cmd:
        cmd_dict = cmd_dict.union(set(name.split()))
    lang_dict = numbers_dict.union(cmd_dict).union([activator, deactivator])

    model = vosk.Model(model)

    if filename:
        dump_fn = open(filename, "wb")
    else:
        dump_fn = None
    
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16',
                            channels=1, callback=callback):

        rec = vosk.KaldiRecognizer(model, samplerate, f'["{" ".join(lang_dict)}", "[unk]"]')
        print('Listener started')
        words = ''
        activated = False
        activator_regexp = re.compile(activator + r'\b')
        deactivator_regexp = re.compile(deactivator + r'\b')
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result())['text']
                if text:
                    print(f'>>> "{text}"')
                    last_time = time()
                    if not activated:
                        activator_match = activator_regexp.search(text)
                        if activator_match:
                            print('Activated')
                            text = text[activator_match.end()+1:]
                            activated = True
                        
                    if activated:
                        deactivator_match = deactivator_regexp.search(text)
                        if deactivator_match:
                            print('Deactivated manually')
                            words += ' ' + text[:deactivator_match.start()]
                            activated = False
                            cmds = parse(words, name_to_cmd)
                            return_callback(cmds)
                            words = ''
                        else:
                            words += ' ' + text


                elif activated:
                    if time() - last_time > timeout:
                        print('Deactivated automatically due to timeout')
                        activated = False
                        cmds = parse(words, name_to_cmd)
                        return_callback(cmds)
                        words = ''
            
            else:
                pass
                # print(rec.PartialResult())
                # might be useful for the stop command
            if dump_fn is not None:
                dump_fn.write(data)

if __name__ == '__main__':
    name_to_cmd = {
            'едь вперёд': {'id': 100, 'body': [100, 100, 1000]},
            'едь назад': {'id': 100, 'body': [-100, -100, 1000]},
            'поверни налево': {'id': 100, 'body': [-100, 100, 1000]},
            'поверни направо': {'id': 100, 'body': [100, -100, 1000]},
            'включи свет': {'id': 401, 'body': [1]},
            'выключи свет': {'id': 401, 'body': [0]},
            }
    # TODO нормальные команды
    activator = 'робот'
    deactivator = 'поехали'
    timeout = 3
    try:
        print(sd.query_devices()) # list the devices together with their ID's
        listen(name_to_cmd, activator, timeout, deactivator, arduino_controller.controller)
    except KeyboardInterrupt:
        print('done')
