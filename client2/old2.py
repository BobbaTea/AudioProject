import websocket
import pyaudio
import wave
import numpy as np
import json
import time
import sys
import pygame
import subprocess
import sounddevice as sd
import soundfile as sf


SPEAKER = True
BROADCASTER = True
HOSTNAME = "ws://127.0.0.1:5000"
USER = "Akash"
FORMAT = pyaudio.paInt32
RATE = 44100
CHUNK = 1024

audio = pyaudio.PyAudio()


def serialize(msgtype, **kwargs):
    formattedtype = "{:<10}".format(str(msgtype)[:10])
    if msgtype == "connection":
        name = "{:<10}".format(str(kwargs['name'])[:10])
        return bytes(formattedtype+name, "utf8")+bytes([int(kwargs['broadcaster'])])+bytes([int(kwargs['speaker'])])
    if msgtype == "audio":
        return kwargs['data']
    if msgtype == "ping":
        return bytes(formattedtype, "utf8")+bytes([0]*int(kwargs['bytes']))

def list_to_bytes(data):
    res = b""
    for i in data:
        res += i.to_bytes(4, 'big')
    return res

def ping(ws, num, numbytes = CHUNK * 4):
    tot = 0
    for i in range(num):
        start = time.time()
        ws.sock.send_binary(serialize("ping", bytes = numbytes))
        result = ws.sock.recv()
        end = time.time()
        tot += end-start
    return tot/num

def on_close(ws):
    print("Connection closed")

def on_error(ws, error):
    print(error)

def on_message(ws, message):
    ws.out.write(message)
    print(end())

    # ws.out.play()

gstart = 0
def start():
    global gstart
    gstart = time.time()
def end():
    global gstart
    return time.time() - gstart


def on_open(ws):
    ws.sock.send_binary(serialize("connection", broadcaster = BROADCASTER, speaker = SPEAKER, name = USER))
    print("Latency: " + str(ping(ws, 10)))
    if SPEAKER:
        # out = audio.open(format=FORMAT, channels=1, rate=RATE, frames_per_buffer=CHUNK, output=True, output_device_index = 1)
        # ws.out = out
        ws.out = sd.RawOutputStream(samplerate = RATE, blocksize = CHUNK*4, channels = 1, dtype="int32", latency = 0)
        ws.out.start()

    if BROADCASTER:
        def callback(in_data, frame_count, time_info, status):
            # print(ws.out.get_output_latency())
            start()
            ws.sock.send_binary(in_data)
            return (in_data, pyaudio.paContinue)
        mic = audio.open(format=FORMAT, channels=1,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK, stream_callback=callback)
        ws.mic = mic
        mic.start_stream()

        # while stream.is_active():
        #     time.sleep(0.1)
        # mic.stop_stream()
    print("Connection opened")





# websocket.enableTrace(True)
ws = websocket.WebSocketApp(HOSTNAME, on_message = on_message, on_close = on_close, on_open = on_open, on_error = on_error)
ws.run_forever()





# print("recording...")
# frames = []
# for i in range(0, int(RATE / CHUNK * 2)):
#     data = stream.read(CHUNK)
#     ws.send_binary(serialize(USER, "audio", data=list_to_bytes(data)))
#     frames.append(data)
# print("finished recording")




