#!/bin/bash
# install macos m1 https://brew.sh/
brew install git-lfs
git lfs install

# installation
export GIT_LFS_SKIP_SMUDGE=1
git clone https://huggingface.co/bigscience/bloom
cd bloom
git lfs fetch origin 2a3d62e
git lfs checkout
# pyhton env
conda create --name torch2 python=3.9
conda activate torch2
# https://pypi.org/project/transformers/4.2.0/
conda install -c huggingface transformers==4.20.0
conda install torchvision pytoch torchaudio
python -m ipykernel install --user --name pytorch --display-name "Python 3.9 (torch)"

python app.py









