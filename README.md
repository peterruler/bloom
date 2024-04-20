# Work is based on this tutorial
https://towardsdatascience.com/run-bloom-the-largest-open-access-ai-model-on-your-desktop-computer-f48e1e2a9a32
- need 700GB of free space use M.2 NVMe external memory
# Github lfs "large file storage" install with brew macos m1
- from https://brew.sh install via:
- `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage
- once brew is installed, install large file system: `brew install git-lfs`
# installation of python conda env
- install miniconda first https://docs.conda.io/en/latest/miniconda.html
- `conda create --name torch python=3.9`
- `conda activate torch`
- `pip install transformers==4.20.0`
- `conda install torch`
- `python -m ipykernel install --user --name torch --display-name "Python 3.9 (torch)"`
- you can leave torch and transformers installed only
- more info on https://github.com/jeffheaton/app_deep_learning/blob/main/install/pytorch-install-aug-2023.ipynb
 # configure path to model in app.py
 - `model_path = "/Volumes/Volume/bloom/new/bloom" # replace with your local folder path`
# run (note: takes about 30 minutes for each token without gpu acceleration)
- `python app.py`