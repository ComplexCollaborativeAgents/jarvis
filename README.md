# Coach AR 


## Install and Build
### Prerequisites
* Anaconda
* Python 2 
* Soar cognitive architecture

### Steps
* Download Soar9.6 from [here](https://soar.eecs.umich.edu/Downloads) and extract the files to a preferred location on the local file system.
* Clone this repository  
  > `git clone https://gitlab-external.parc.com/augmented-reality-assistant-2017/ARTaskAssistant`
* Edit the `Soar`  `path` element in `config.json` to point to your local soar installation
* Configure a Python2 conda environment

       conda create --name soarpy2 python=2.7
       conda install coloredlogs, tk
    
    
## Usage
* Activate the conda environment
  
      source activate soarpy2
      
* Run the state reasoning, planning agent

      python soar_runner.py
      
* Inspect agent state

      python soar_state_monitor_gui.py