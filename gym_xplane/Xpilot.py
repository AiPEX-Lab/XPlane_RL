import gym_xplane
import xpc 
import gym
import os
from time import sleep,clock

from stable_baselines.common.policies import MlpPolicy,LstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.bench import Monitor

env = gym.make('gymXplane-v2')
env.clientAddr = "0.0.0.0" 
env.xpHost = '127.0.0.1'
env.xpPort = 49009
env.clientPort = 0

n_cpu = 1

env = DummyVecEnv([lambda: env])  # The algorithms require a vectorized environment to run

model = PPO2.load('X_Pilot_run3')

obs = env.reset()
for i in range(5000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()
    sleep(.01)