from sys import byteorder
from array import array
from struct import pack
import pyaudio
import wave
import os

THRESHOLD = 1000
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16

# In[]
class record():
    def __init__(self):
        self.format = FORMAT
        self.chunk_size = CHUNK_SIZE
        self.threshold = THRESHOLD

    def is_silent(self, snd_data):
        "Returns 'True' if below the 'silent' threshold"
        return max(snd_data) < self.threshold


    def normalize(self, snd_data):
        "Average the volume out"
        MAXIMUM = 16384
        times = float(MAXIMUM)/max(abs(i) for i in snd_data)

        r = array('h')
        for i in snd_data:
            r.append(int(i*times))
        return r


    def trim(self, snd_data):
        "Trim the blank spots at the start and end"
        def _trim(snd_data):
            snd_started = False
            r = array('h')
            s = array('h')
            frame_Nu = 0
            for i in snd_data:
                if not snd_started and abs(i)>self.threshold:
                    snd_started = True
                    r.append(i)
                elif snd_started:
                    r.append(i)
                else:
                    s.append(i)
                frame_Nu += 1
            return r,s

        # Trim to the left
        snd_data, start_noise_data = _trim(snd_data)
        return snd_data
        # Trim to the right
        # snd_data.reverse()
        # snd_data, end_noise_data = _trim(snd_data)
        # end_noise_data.reverse()
        # snd_data.reverse()
        # return snd_data, end_noise_data


    def add_silence(self, snd_data, seconds , SAMPLE_RATE):
        "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
        silence = [0] * int(seconds * SAMPLE_RATE)
        r = array('h', silence)
        r.extend(snd_data)
        r.extend(silence)
        return r


    def record(self, record_time, sr):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=1, rate=sr,
                        input=True, output=True,
                        frames_per_buffer=self.chunk_size)

        num_silent = 0
        snd_started = False

        r = array('h')
        num_chunk = 1
        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(self.chunk_size))
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            num_chunk += 1
            if sr*record_time < self.chunk_size*num_chunk:
                break

        sample_width = p.get_sample_size(self.format)
        stream.stop_stream()
        stream.close()
        p.terminate()

        # r = self.normalize(r)
        # r = self.trim(r)
        # if len(r)>20000:
        #     r = self.add_silence(r[160:], 0.0, sr)
        # else:
        #     r = self.add_silence(r, 0.0, sr)
        return sample_width, r

    def run(self, path, record_time=5, sr=8000):
        "Records from the microphone and outputs the resulting data to 'path'"
        print("please speak a word into the microphone")
        sample_width, data = self.record(record_time, sr)

        data = pack('<' + ('h'*len(data)), *data)
        # plt.plot(data)
        # plt.show()
        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(sr)
        wf.writeframes(data)
        wf.close()

        print("done - result written to "+ os.path.basename(path))

record_class = record()
if __name__ == '__main__':
    temp_path = './temp.wav'
    SAMPLE_RATE = 8000
    record_class.run(temp_path, record_time=3, sr=SAMPLE_RATE)
