import pyaudio
import wave

import numpy as np

import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)

########################################################
#######################################################
########################################################
import os
import openai
import subprocess

openai.api_key = 'TYPE_YOUR_OPENAI_API_KEY_HERE'



# Initialize conversation with a system message
messages = [{'role': 'system', 'content': 'You are Cookie Monster from Sesame Street.'}]

def text_to_speech(text):
    # Use the 'text2wave' Festival command to generate WAV audio from text
    process = subprocess.Popen(["text2wave", "-o", "output.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.communicate(input=text.encode())

    # Use 'aplay' to play the generated audio
    subprocess.run(["aplay", "output.wav"])
####################
def contains_audio(audio_file_path, threshold_energy=0.0000000008):
    CHUNK = 1000  # Size of each audio chunk

    wf = wave.open("/home/pi/test1.wav", "rb")
    sample_width = wf.getsampwidth()

    p = pyaudio.PyAudio()

    stream = p.open(
        format=p.get_format_from_width(sample_width),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        input=True,
        frames_per_buffer=CHUNK
    )

    audio_data = wf.readframes(CHUNK)
    audio_energy = 0

    while audio_data:
        audio_data_np = np.frombuffer(audio_data, dtype=np.int16)
        audio_energy += np.mean(audio_data_np ** 2) / 32767.0 ** 2

        audio_data = wf.readframes(CHUNK)

    audio_energy /= wf.getnframes()

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("audio energy: ")
    print(audio_energy)
    return audio_energy > threshold_energy
#############3

while True:
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 1024 # 2^12 samples for buffer
    record_secs = 4 # seconds to record
    dev_index = 2 # device index found by p.get_device_info_by_index(ii)
    wav_output_filename = 'test1.wav' # name of .wav file

    THRESHOLD = 200  # Adjust this threshold to your desired audio level

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    GPIO.output(18,GPIO.HIGH) #TURN ON LED TO LET YOU KNOW COOKIE MONSTER IS LISTENING/RECORDING
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)

    volume = max(data)
    #if volume > THRESHOLD:
    print(volume)
                


    print("finished recording")
    GPIO.output(18,GPIO.LOW) #TURN OFF LED TO LET YOU KNOW RECORDING IS DONE
    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
        
    audio_file = open("/home/pi/test1.wav", "rb")
    
    ################
    audio_file_path = "/home/pi/test1.wav"
    is_audio = contains_audio(audio_file_path)

    if is_audio:
        print("The audio file contains meaningful audio.")
    
    
    ################
        user_text = openai.Audio.transcribe(model="whisper-1",file=audio_file,response_format="text")
            
            #user_text = input('Bucky: ')

            # Add the user message to the conversation history
        messages.append({'role': 'user', 'content': user_text})

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            temperature=0.5,
            max_tokens=1024
            )

        granny_response = response.choices[0].message.content
        print(f'Cookie Monster: {granny_response}')

            # Add grandmas message to the conversation history
        messages.append({'role': 'system', 'content': granny_response})

        if __name__ == "__main__":
            text = response.choices[0].message.content
            text_to_speech(text)

    else:
        print("The audio file is likely empty or contains silence.")
#print(response)
#print()
#print(response.choices[0].message.content)


#END TEXT TO SPEECH
