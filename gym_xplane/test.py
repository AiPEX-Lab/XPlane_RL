import gym
from scipy.spatial.distance import pdist, squareform

import gym_xplane.xpc as xp
import gym_xplane.parameters as parameters
import gym_xplane.space_definition as envSpaces
import numpy as np
import itertools
from time import sleep, clock
import socket



client = xp.XPlaneConnect(xpHost = "localhost",xpPort =49009,timeout = 3000)
dref = "sim/flightmodel2/misc/gforce_normal"
out = client.getDREF(dref)
i = 0
while True:
	out = client.getDREF(dref) 
	print(out)
	sleep(.1)
