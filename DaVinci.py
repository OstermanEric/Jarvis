#!/usr/bin/env python3

import json
import boto3
import openai
import os
import pvcobra
import pvleopard
import pvporcupine
import pyaudio
import random
import struct
import sys
import textwrap
import threading
import time
from datetime import datetime

import base64
import requests

import requests

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from colorama import Fore, Style
from openai import OpenAI
from pvleopard import *
from pvrecorder import PvRecorder
from threading import Thread, Event
from time import sleep


audio_stream = None
cobra = None
pa = None
polly = boto3.client('polly')
porcupine = None
recorder = None
wav_file = None



audio_stream = None
cobra = None
pa = None
polly = boto3.client('polly')
porcupine = None
recorder = None
wav_file = None



# OpenAI and API credentials
GPT_model = "gpt-3.5-turbo"
openai.api_key = ""
pv_access_key = ""

# Meteomatics API constants
NYC_lat = 40.730610
NYC_long = -74.0060
temp_type = "t_2mc"
times = "now"
# Initialize OpenAI client
client = OpenAI(api_key=openai.api_key)

# Prompt options
prompt = [
    "How may I assist you?",
    "How may I help?",
    "What can I do for you?",
    "Ask me anything.",
    "Yes?",
    "I'm here.",
    "I'm listening.",
    "What would you like me to do?"
]

# Initial chat log
chat_log = [
    {"role": "system", "content": "Your name is Jarvis. You are a helpful assistant. If asked about yourself, you include your name in your response."},
]



# Credentials
username = ''
password = ''

def get_access_token():
    auth_url = 'https://login.meteomatics.com/api/v1/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
    }

    try:
        print("Authenticating to get access token...")  # Debug statement
        response = requests.get(auth_url, headers=headers)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"Access token obtained: {token}")  # Debug statement
            return token
        else:
            print(f"Failed to authenticate: {response.text}")  # Debug statement
            return None
    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        return None


def get_weather(lat=NYC_lat, long=NYC_long, _type=temp_type, times=times, output="json", access_token=None):
    base_url = "https://api.meteomatics.com"
    endpoint = f"/{times}/{_type}/{lat},{long}/{output}"
    full_url = f"{base_url}{endpoint}?access_token={access_token}"

    print(f"get_weather called with arguments: lat={NYC_lat}, long={NYC_long}, _type={temp_type}, times={times}, output={output}")  # Debug statement

    try:
        print(f"Requesting weather data from: {full_url}")  # Debug statement
        response = requests.get(full_url)  # Add authentication if required

        print(f"Response Status Code: {response.status_code}")  # Debug statement

        if response.status_code == 200:
            weather_data = response.json()  # Assuming JSON output
            print(f"Weather Data: {weather_data}")  # Debug statement

            # Parsing the weather data
            parsed_data = {}
            for data_entry in weather_data.get("data", []):
                parameter = data_entry.get("parameter")
                coordinates_data = data_entry.get("coordinates", [])

                for coord in coordinates_data:
                    coord_lat = coord.get("lat")
                    coord_lon = coord.get("lon")
                    if coord_lat == lat and coord_lon == long:
                        print(f"Matching coordinates found: lat={coord_lat}, long={coord_lon}")  # Debug statement
                        # For now, we'll just grab the first date entry, but this could be expanded
                        first_date_entry = coord.get("dates", [])[0]
                        parsed_data[parameter] = {
                            "date": first_date_entry.get("date"),
                            "value": first_date_entry.get("value")
                        }
                        print(f"Extracted data for {parameter}: {parsed_data[parameter]}")  # Debug statement

            print(f"Parsed Weather Data: {parsed_data}")  # Debug statement
            return parsed_data
        else:
            print(f"Failed to retrieve weather data: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred in get_weather: {e}")
        return None


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "times": {
                        "type": "string",
                        "description": "Time of the weather data, e.g., 'now' or a specific date-time",
                    },
                    "_type": {
                        "type": "string",
                        "description": "Type of weather data, e.g., 't_2m:C' for temperature",
                    },
                    "lat": {
                        "type": "number",
                        "description": "Latitude of the location",
                    },
                    "long": {
                        "type": "number",
                        "description": "Longitude of the location",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output format, e.g., 'json'",
                    }
                },
                "required": ["times", "_type", "lat", "long"],
                "additionalProperties": False
            }
        }
    }
]


def ChatGPT(query, access_token):
    print(f"ChatGPT called with query: {query}")  # Debug statement
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,  # Passing the tools here
        )
        
<<<<<<< HEAD
        response_message = response.choices[0].message
        print(f"OpenAI response received: {response_message}")  # Debug statement
        messages.append(response_message)

        # get if any tool calls have been called 
        tool_calls = response_message.tool_calls
        # if true, the model will return the name of the tool / function to call and arguments
        if tool_calls:
            tool_call_id = tool_calls[0].id
            tool_function_name = tool_calls[0].function.name
            tool_function_lat = json.loads(tool_calls[0].function.arguments)['lat']
            print('lat: {tool_function_lat}')
        

        tool_call = response.choices[0].message.tool_calls[0]
        print(f"tool calls:{tool_call}") # this works
=======
        message = response.choices[0].message
        print(f"OpenAI response received: {message}")  # Debug statement
        
        tool_call = response.choices[0].message.tool_calls[0]
        print(f"tool calls:{tool_call}")
>>>>>>> 71002ba20681952dd39e237f23226eb7b3cbef42
        arguments = json.loads(tool_call['function']['arguments'])
        print(arguments)
        
        # Check if a tool call was made
        if 'tool_calls' in message:
            tool_call = message['tool_calls'][0]  # Assuming we're dealing with the first tool call
            print(f"Tool call detected: {tool_call}")  # Debug statement
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])  # Load the arguments
            print(f"Tool call arguments: {arguments}")  # Debug statement
            
            if function_name == "get_weather":
                # Extract arguments and call the get_weather function
                times = arguments.get("times", "now")
                _type = arguments.get("_type", "t_2m:C")
                lat = float(arguments.get("lat", NYC_lat))
                long = float(arguments.get("long", NYC_long))
                output = arguments.get("output", "json")
                
                print(f"Calling get_weather with: times={times}, _type={_type}, lat={lat}, long={long}, output={output}, access_token={access_token}")  # Debug statement
                # Call the get_weather function and return the result
                weather_data = get_weather(lat=lat, long=long, _type=_type, times=times, output=output, access_token=access_token)
                if weather_data:
                    print(f"Weather data retrieved: {weather_data}")  # Debug statement
                    return f"The current temperature is {weather_data['t_2m:C']['value']}°C."
                else:
                    print("Weather data retrieval failed.")  # Debug statement
                    return "Sorry, I couldn't retrieve the weather information."
        
        # If no tool call was made, return the regular response
        print("No tool call made, returning regular response.")  # Debug statement
        return message.get('content', 'Sorry, there was no content in the response.')

    except openai.BadRequestError as e:
        print(f"An error occurred in ChatGPT: {e}")
        return "Sorry, there was an error processing your request."




def append_clear_countdown():
    sleep(300)  # Wait for 5 minutes (300 seconds)
    global chat_log
    chat_log.clear()
    chat_log = [
        {"role": "system", "content": "Your name is Jarvis. You are a helpful assistant. If asked about yourself, you include your name in your response."},
    ]
    print("Chat log cleared after 5 minutes.")  # Debug statement



def responseprinter(chat):
   wrapper = textwrap.TextWrapper(width=70)  # Adjust the width to your preference
   paragraphs = res.split('\n')
   wrapped_chat = "\n".join([wrapper.fill(p) for p in paragraphs])
   for word in wrapped_chat:
      time.sleep(0.06)
      print(word, end="", flush=True)
   print()



# Function to handle voice response
def voice(chat):
    voiceResponse = polly.synthesize_speech(Text=chat, OutputFormat="mp3", VoiceId="Matthew")
    if "AudioStream" in voiceResponse:
        with voiceResponse["AudioStream"] as stream:
            output_file = "speech.mp3"
            try:
                with open(output_file, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                print(error)
    else:
        print("Voice synthesis failed.")
    
    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    sleep(0.2)
    
    
def wake_word():
    keywords = ["computer", "jarvis"]
    porcupine = pvporcupine.create(
        keywords=keywords,
        access_key=pv_access_key,
        sensitivities=[1.0, 1.0]  # High sensitivity for better detection
    )
    
    wake_pa = pyaudio.PyAudio()
    porcupine_audio_stream = wake_pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        while True:
            porcupine_pcm = porcupine_audio_stream.read(porcupine.frame_length)
            porcupine_pcm = struct.unpack_from("h" * porcupine.frame_length, porcupine_pcm)

            porcupine_keyword_index = porcupine.process(porcupine_pcm)

            if porcupine_keyword_index >= 0:
                print(f"\nKeyword '{keywords[porcupine_keyword_index]}' detected\n")
<<<<<<< HEAD
=======
                GPIO.output(led1_pin, GPIO.HIGH)
                GPIO.output(led2_pin, GPIO.HIGH)
>>>>>>> 71002ba20681952dd39e237f23226eb7b3cbef42
                break
    finally:
        porcupine_audio_stream.stop_stream()
        porcupine_audio_stream.close()
        porcupine.delete()


def listen():
    cobra = pvcobra.create(access_key=pv_access_key)

    listen_pa = pyaudio.PyAudio()
    listen_audio_stream = listen_pa.open(
        rate=cobra.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=cobra.frame_length
    )

    print("Listening...")

    try:
        while True:
            listen_pcm = listen_audio_stream.read(cobra.frame_length)
            listen_pcm = struct.unpack_from("h" * cobra.frame_length, listen_pcm)

            if cobra.process(listen_pcm) > 0.3:
                print("Voice detected")
                break
    finally:
        listen_audio_stream.stop_stream()
        listen_audio_stream.close()
        cobra.delete()


def detect_silence():
    cobra = pvcobra.create(access_key=pv_access_key)

    silence_pa = pyaudio.PyAudio()
    cobra_audio_stream = silence_pa.open(
        rate=cobra.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=cobra.frame_length
    )

    last_voice_time = time.time()

    while True:
        cobra_pcm = cobra_audio_stream.read(cobra.frame_length)
        cobra_pcm = struct.unpack_from("h" * cobra.frame_length, cobra_pcm)

        if cobra.process(cobra_pcm) > 0.2:
            last_voice_time = time.time()  # Update the last voice detected time
        else:
            silence_duration = time.time() - last_voice_time  # Calculate the duration of silence
            if silence_duration > 1.3:
                print("End of query detected\n")
<<<<<<< HEAD
=======
                GPIO.output(led1_pin, GPIO.LOW)
                GPIO.output(led2_pin, GPIO.LOW)
                
>>>>>>> 71002ba20681952dd39e237f23226eb7b3cbef42
                cobra_audio_stream.stop_stream()
                cobra_audio_stream.close()
                cobra.delete()
                break




class Recorder(Thread):
    def __init__(self):
        super().__init__()
        self._pcm = []
        self._is_recording = False
        self._stop = False

    def is_recording(self):
        return self._is_recording

    def run(self):
        self._is_recording = True

        recorder = PvRecorder(device_index=-1, frame_length=512)
        recorder.start()

        while not self._stop:
            self._pcm.extend(recorder.read())
        recorder.stop()

        self._is_recording = False

    def stop(self):
        self._stop = True
        while self._is_recording:
            pass

        return self._pcm


# Additional functions (fade_leds, wake_word, listen, detect_silence, Recorder class)
# These remain the same as in the original code, with added print statements for debugging where necessary

# Main loop with integrated weather function calling
try:
    # Obtain the access token before starting the loop
    access_token = get_access_token()
    
    if not access_token:
        print("Failed to obtain access token. Exiting.")
        sys.exit(1)  # Exit the program if the token couldn't be obtained

    o = create(
        access_key=pv_access_key,
        enable_automatic_punctuation=True,
    )
    
    event = threading.Event()
    count = 0

    while True:
        try:
            if count == 0:
                t_count = threading.Thread(target=append_clear_countdown)
                t_count.start()
            count += 1

            wake_word()
            voice(random.choice(prompt))
            recorder = Recorder()
            recorder.start()
            listen()
            detect_silence()
            transcript, words = o.process(recorder.stop())
            recorder.stop()
            print(transcript)  # Debug statement, prints the transcript or voice request
            
            # Use the ChatGPT function, passing the access token for the weather API
            res = ChatGPT(transcript, access_token)
            print("\nChatGPT's response is:\n")
            t1 = threading.Thread(target=voice, args=(res,))
            t2 = threading.Thread(target=responseprinter, args=(res,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            event.set()       
            recorder.stop()
            o.delete
            recorder = None

        except openai.APIError as e:
            print("\nThere was an API error. Please try again in a few minutes.")
            print(e)
            voice("\nThere was an A P I error. Please try again in a few minutes.")
            event.set()
            recorder.stop()
            o.delete
            recorder = None
            sleep(1)

        except openai.RateLimitError as e:
            print("\nYou have hit your assigned rate limit.")
            voice("\nYou have hit your assigned rate limit.")
            event.set()
            recorder.stop()
            o.delete
            recorder = None
            break

        except openai.APIConnectionError as e:
            print("\nI am having trouble connecting to the API. Please check your network connection and then try again.")
            voice("\nI am having trouble connecting to the A P I. Please check your network connection and try again.")
            event.set()
            recorder.stop()
            o.delete
            recorder = None
            sleep(1)

        except openai.AuthenticationError as e:
            print("\nYour OpenAI API key or token is invalid, expired, or revoked. Please fix this issue and then restart my program.")
            voice("\nYour Open A I A P I key or token is invalid, expired, or revoked. Please fix this issue and then restart my program.")
            event.set()
            recorder.stop()
            o.delete
            recorder = None
            break

except KeyboardInterrupt:
    print("\nExiting ChatGPT Virtual Assistant")
<<<<<<< HEAD
    o.delete
=======
    o.delete
>>>>>>> 71002ba20681952dd39e237f23226eb7b3cbef42
