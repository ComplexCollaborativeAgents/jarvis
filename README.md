# JARVIS 
(Just an Augmented Reality/Virtual Instruction System)


## Install and Build
### Prerequisites
* Anaconda
* Python 2 
* Soar cognitive architecture

### Steps
* Download Soar9.6 from [here](https://soar.eecs.umich.edu/Downloads) and extract the files to a preferred location on the local file system.
* Clone this repository  
   `git clone https://gitlab-external.parc.com/augmented-reality-assistant-2017/jarvis`
* Edit the `Soar`  `path` element in `config.json` to point to your `/local/soar/installation/bin/linux64`
* Configure a Python2 conda environment

       `conda create --name jarvis_env python=2.7`

       `conda install coloredlogs`
    
    
## Usage
* Activate the conda environment
  
      `source activate jarvis_env`
      
* Run jarvis

      `python jarvis.py`
      
* Inspect jarvis' state and interact with it

      `python jarvis_interface.py`