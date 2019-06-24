import gym_xplane
import xpc 
import gym
import os
import time

from stable_baselines.common.policies import MlpPolicy,LstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.bench import Monitor

log_dir = "/home/datalab-student/Desktop/Results"
def plot_results('/home/datalab-student/Desktop/Results', title ='Monitor'):

   	x, y = ts2xy(load_results(log_folder), 'timesteps')
   	y = moving_average(y, window=50)
   	# Truncate x
   	x = x[len(x) - len(y):]
   	fig = plt.figure(title)
   	plt.plot(x, y)
   	plt.xlabel('Number of Timesteps')
   	plt.ylabel('Rewards')
   	plt.title(title + " Smoothed")
   	plt.show()

plot_results(log_dir)

