---------
##### gym-xplane
---------
gym_xplane is an  environment bundle for OpenAI Gym. It allows an agent to interact seamlessly with the XPlane Simulation environment 


-------------
##### Installation
---------

1. Install [Stable-baselines Gym](https://github.com/hill-a/stable-baselines) and its dependencies.
2. Install the package itself:
    ```
    git clone  PASTE HTTPS OR SSH HERE // if you have not cloned the repo before
    cd gym_xpalne_final_version/gym_xplane
    pip install -e .
    ```
-----------------
##### Usage
--------------------

1. Start Xplane 
2. Change the directory to gym_xplane:
   ```
    cd ../gym_xplane
    ```
2. Run examples:

    ``` 
    sudo  /path/to/anaconda/python3.6  random_agent.py 
    ```
   
### To Load Tensorboard
   tensorboard -- logdir 'path to file'
   
### To Load Model
   Paste the name and directory of the model into XPilot.py
   Run X Plane 
   Run XPilot.py
   
### TO DO
   Look into GLX accelerated rendering in nvidi-docker
   Train the model with current reward function
   (You could define your reward function for your custom scenario too)
    
