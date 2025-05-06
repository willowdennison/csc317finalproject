import pyaudio
import wave

#args needed: video fps, input frame, audio path
fps = 25 #test. will be passed in


CHUNK = 1764
start = 0
end = start + CHUNK

wf = wave.open("audio.wav", 'rb')
p = pyaudio.PyAudio()
out_stream = p.open(format=p.get_format_from_width(2),channels=2,rate=44100,output=True,frames_per_buffer=CHUNK)

framerate = wf.getframerate()
print(framerate)
for i in range(100):
    wf.setpos(int(start))
    data = wf.readframes(int((end - start)))
    data = wf.readframes(CHUNK)
    out_stream.write(data)
    start +=CHUNK
    end+= CHUNK

def getAudioFrame(fps, inputFrame, audioPath):
    wf = wave.open(audioPath, 'rb')
    framewf.getframerate()

    return