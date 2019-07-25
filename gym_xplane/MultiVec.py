import gym_xplane
import xpc 
import gym
import os
import time
from gym.envs.registration import register
from stable_baselines.common.policies import MlpPolicy,LstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.bench import Monitor


def callback(_locals, _globals):

    global n_steps

    # Print stats every 1000 calls
    if (n_steps + 1) % 100 == 0:

        model.save(log_dir+"/{}".format(int(time.time())))        
    
    n_steps += 1 
    return True



if __name__ == '__main__':

    env_id = 'gymXplane-v2'
    log_dir = "./gym/{}".format(int(time.time()))
    os.makedirs(log_dir, exist_ok=True)


    def make_env(env_id, port, rank, seed=0):
        """
        Utility function for multiprocessed env.

        :param env_id: (str) the environment ID
        :param num_env: (int) the number of environments you wish to have in subprocesses
        :param seed: (int) the inital seed for RNG
        :param rank: (int) index of the subprocess
        """
        def _init():
            env = gym.make(env_id)
            env.seed(seed + rank)
            env.xpPort = port
            env.clientAddr = "0.0.0.0"
            env.xpHost = '127.0.0.1'
            env.xpPort = 49009
            env.clientPort = 0
            env = Monitor(env, log_dir, allow_early_resets=True)
            return env
        #set_global_seeds(seed)
        return _init
 
     #tensorboard --logdir 


    n_steps = 0
    num_cpu = 4

    env = SubprocVecEnv([make_env(env_id, 49009 + i, i) for i in range(num_cpu)])  # The algorithms require a vectorized environment to run
   
    
    
    #model = PPO2(MlpPolicy, env, verbose=1, tensorboard_log = log_dir)
    model = PPO2.load('0_Throttle2.pkl', env, tensorboard_log = log_dir)
    model.learn(total_timesteps=5000000, callback = callback)

    ##### Final Save 

    model.save("PPO2_landingAW2")
    #PPO2('MlpPolicy', env, verbose=1).learn(1000)
   

