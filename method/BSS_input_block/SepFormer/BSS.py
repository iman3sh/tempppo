import subprocess
import os
import json
from scipy.io import wavfile
from speechbrain.pretrained import SepformerSeparation as separator
# In[]

import torchaudio
import os
from tqdm import tqdm


from speechbrain.pretrained import SepformerSeparation as separator
import torchaudio
import os
from tqdm import tqdm

from os import path
import os
import sys
SepFormer_root = os.path.dirname(os.path.abspath(__file__))
wd = os.getcwd()
sys.path.append(SepFormer_root)
os.chdir(SepFormer_root)


model = separator.from_hparams(source="speechbrain/sepformer-wsj02mix", savedir='./pretrained_models/sepformer-wsj02mix')

# tmpdir = getfixture("tmpdir")
# model = SepformerSeparation.from_hparams(
#     ...     source="speechbrain/sepformer-wsj02mix",
#                    ...     savedir=tmpdir)
# mix = torch.randn(1, 400)
# est_sources = model.separate_batch(mix)
# print(est_sources.shape)
# torch.Size([1, 400, 2])

# for custom file, change path
# root_path='pretrained_models/sepformer-wsj02mix'
# root_path='/home/iman/storage/code/project/PERSONAL/military/Finalize/dataset/demo/record/recorded_voice_ss'
# root_path='/home/iman/storage/code/project/PERSONAL/military/Finalize/dataset/complete/BSS_8kHz/test/mix'
root_path = '/home/iman/storage/code/project/PERSONAL/military/Finalize/Projects/results/2_finalize_BSS8_BWE_ASR/BSS/mix'

in_dir = os.path.abspath(root_path)
wav_list = os.listdir(in_dir)
qq=0
for wav_file in tqdm(wav_list):
    if not wav_file.endswith('.wav'):
        continue
    qq+=1
    if qq==3:
        break
    wav_path = os.path.join(in_dir, wav_file)
    est_sources = model.separate_file(path=wav_path, savedir='outputs')
    torchaudio.save(f"./outputs/{wav_file.split('.')[0]}"+"_spk1.wav", est_sources[:, :, 0].detach().cpu(), 8000)
    torchaudio.save(f"./outputs/{wav_file.split('.')[0]}"+"_spk2.wav", est_sources[:, :, 1].detach().cpu(), 8000)

SAMPLE_RATE = 8000
class ss:
    def __init__(self):
        svoice_root = os.path.dirname(os.path.abspath(__file__))
        self.model_path =os.path.join(svoice_root, f'pretrained_models/checkpoint.th')

    def run(self, save_root, input, device='cpu'):
        if input.split('.')[-1]=='wav':
            self._run(save_root, mix_wav_file=input, device=device)
        elif input.split('.')[-1]=='json':
            self._run(save_root, mix_wav_json=input, device=device)
        else:
            self._run(save_root, mix_wav_root=input, device=device)

    def _run(self, save_root, mix_wav_file=None, mix_wav_root=None, mix_wav_json=None, device='cpu', sample_rate=SAMPLE_RATE):
        wd = os.getcwd()

        if not os.path.isabs(save_root):
            save_root = os.path.join(wd, save_root)
        else:
            save_root = os.path.join(save_root)
        os.makedirs(save_root,exist_ok=True)

        if mix_wav_file!=None:
            if not os.path.isabs(mix_wav_file):
                mix_wav_file = os.path.join(wd, mix_wav_file)
            sr, wav = wavfile.read(mix_wav_file)
            if sr!=SAMPLE_RATE:
                print(f'sr != {SAMPLE_RATE}')

            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            L = []
            L.append([mix_wav_file,len(wav)])
            json_file = os.path.join(save_root,'temp.json')
            with open(json_file, 'w') as f:
                json.dump(L, f)

            cmd = ['python', '-m', 'svoice.separate', self.model_path, save_root, '--mix_json', json_file,
                   '--device', device, '--sample_rate', str(sample_rate)]

            subprocess.call((cmd))
            cmd = ['rm', json_file]
            subprocess.call((cmd))


        elif mix_wav_root!=None:
            if not os.path.isabs(mix_wav_root):
                mix_wav_root = os.path.join(wd, mix_wav_root)

            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            cmd = ['python', '-m', 'svoice.separate', self.model_path, save_root, '--mix_dir', mix_wav_root,
                   '--device', device, '--sample_rate', str(sample_rate)]
            subprocess.call((cmd))

        elif mix_wav_json!=None:
            if not os.path.isabs(mix_wav_json):
                mix_wav_json = os.path.join(wd, mix_wav_json)

            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            cmd = ['python', '-m', 'svoice.separate', self.model_path, save_root, '--mix_json', mix_wav_json,
                   '--device', device, '--sample_rate', str(sample_rate)]
            subprocess.call((cmd))
        else:
            print('Input does not set!')

        os.chdir(wd)
        print('SUCCESS!')
        return ('done!')

BSS_class = ss()
# In[]
if __name__=='__main__':
    # check each test at a time or change the save root
    # use
    #BSS_class.run(save_root, input, device='cpu')
    from os import path
    import os
    import sys
    svoice_root = os.path.dirname(os.path.abspath(__file__))
    wd = os.getcwd()
    sys.path.append(svoice_root)
    os.chdir(svoice_root)

    print('TEST 1 : separate single file')
    input = './test_set/R000016-S000121-P001099_R000020-S036520-P327233.wav'
    save_root = f'./outputs/ss_wave'
    BSS_class.run(save_root, input, device='cpu')
    #
    print('TEST 2 : separate directory')
    input = './test_set'
    save_root = f'./outputs/ss_root'
    BSS_class.run(save_root, input, device='cpu')

    print('TEST 3 : record and separate')
    from utils.mic_record import record_class
    record_path = './outputs/ss_record/record_1.wav'
    os.makedirs(os.path.split(record_path)[0],exist_ok=True)
    record_class.run(record_path, record_time=5, sr=SAMPLE_RATE)
    save_root = f'./outputs/ss_record'
    BSS_class.run(save_root, record_path, device='cpu')

    print('TEST 4 : separate json file')
    input = './test_set/mix.json'
    save_root = f'./outputs/ss_json'
    BSS_class.run(save_root, input, device='cpu')

