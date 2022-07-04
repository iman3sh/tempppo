# In[]
if __name__ == '__main__':
    import os
    import argparse
    import subprocess
    import torch
    wd = os.getcwd()
    BSS_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BSS_root)


    parser = argparse.ArgumentParser("BSS train")
    parser.add_argument('--conf_yaml', type=str, default='hparams/sepformer-customdataset-GPU.yaml', help='config yaml file')
    if not torch.cuda.is_available():
        parser.add_argument('--device', type=str, default='cpu' , help='')
    args = parser.parse_args()

    cmd = ['python', '-m', 'SepFormer.train']

    cmd.append(vars(args)['conf_yaml'])
    for arg in vars(args):
        if arg != 'conf_yaml':
            cmd.append('--'+arg)
            cmd.append(vars(args)[arg])
    subprocess.call(cmd)
    os.chdir(wd)
