import gym
import gym_xplane.xpc as xp
import gym_xplane.parameters as parameters
import gym_xplane.space_definition as envSpaces
import numpy as np
import itertools
from time import sleep, clock
import math

class initial:
    ### Calls xpc.py to set connection using XplaneConnect plugin
    def connect( xpHost, xpPort , timeout ):
            return xp.XPlaneConnect(xpHost, xpPort , timeout )

class XplaneEnv(gym.Env):

    def __init__(self, xpHost, xpPort  , timeout):
        XplaneEnv.CLIENT = None
        envSpace = envSpaces.xplane_space()
        self.ControlParameters = parameters.getParameters()
        self.action_space = envSpace._action_space()
        self.observation_space = envSpace._observation_space()
        self.ControlParameters.episodeStep =0
        self.max_episode_steps = 500
        self.max_sim_time = 62.35
        self.statelength = 10
        self.actions = [0,0,0,0,0]
        self.test= False
        try:
            XplaneEnv.CLIENT = initial.connect(xpHost = '127.0.0.1',xpPort = 49009, timeout = 1000)
        except:
            print("connection error. Check your paramters")
        print('I am client', XplaneEnv.CLIENT )
    

    def close(self):
        XplaneEnv.CLIENT.close()
    

    def rewardCalcul(self,sigma=0.45):
        '''
        input : 
        output: 
        '''
        ### G_force Reward
        '''
        if XplaneEnv.CLIENT.getDREFs(self.ControlParameters.gforce)[0][0] < 1.5:
            g_reward = 1
        else:
            g_reward = np.tanh(1-(XplaneEnv.CLIENT.getDREFs(self.ControlParameters.gforce)[0][0]/7.5))
        '''
        ### Altitude Reward
        reward_velocity = 0 
        reward_altitude = np.tanh(1-((1*self.ControlParameters.state14['delta_altitude'])/245))
        
        ### Heading Reward
        if self.ControlParameters.state14['delta_heading'] < 180:
            reward_heading = 1 - (self.ControlParameters.state14['delta_heading']/90)
        else:
            reward_heading = -1 + ((self.ControlParameters.state14['delta_heading'] - 180)/90)
        
        ### Stability Reward 
        sum_rates = abs(self.P) + abs(self.Q)
        reward_stability = np.tanh(2 - 2 * (sum_rates)/50)

        ### Speed Reward 
        if self.ControlParameters.state14['delta_altitude'] < 60:
            reward_velocity = np.tanh(1 - self.raw_velocity/50)
        print(reward_stability)
        ### Total reaward 
        reward = reward_heading + (2 * reward_altitude) + reward_stability + (2 * reward_velocity) - 1.5 # time based punishment
        #print(reward_heading, reward_altitude, reward_stability, reward_velocity)
        return np.array(reward)


    def step(self, actions):

        self.test=False # if true, only test paramters returned. for Model tesing 
        self.ControlParameters.flag = False # for synchronisation of training
        self.reward = 0.
        actions_ = []
        
        j=0  # getting simulaion timing measurement
        
        try:
        
            #############################################
            i=clock() # get the time up till now
            # Pass a dummy value -998 to bypass gear and controll airbrakes
            actions = np.concatenate((actions[:4],[-998],actions[4:]),axis = 0) 
            XplaneEnv.CLIENT.sendCTRL(actions) # send action

            sleep(0.0003)  # sleep for a while so that action is executed
            self.actions = actions  # set the previous action to current action. 


            j=clock() # get the time now, i-j is the time at which the simulation is unpaused and action exeuted
            ################################################# 
            
            #################################################
            # tenporary variable for holding stae values
            state = [];
            state14 = []
            ################################################
            
            #################################################
            # get the state variables here . The parameter file has all the required variables
            # we only need to call the client interface and get parameters defined as stateVariable
            # in parameter file as below
            stateVariableTemp = XplaneEnv.CLIENT.getDREFs(self.ControlParameters.stateVariable) 
            # the client interface automaically gets the position parameters
            self.ControlParameters.stateAircraftPosition = list(XplaneEnv.CLIENT.getPOSI());
            # Remove brackets from state variable and store in the dictionary
            self.ControlParameters.stateVariableValue = [i[0] for i in stateVariableTemp]
            # combine the position and other state parameters in temporary variable here
            state =  self.ControlParameters.stateAircraftPosition + self.ControlParameters.stateVariableValue
            ########################################################

            ########################################################
            # **********************************************reward parametera**********************
            #self.headingReward = 213.5 # the heading target (headingTrue)
            self.headingReward = 143.76 #Landing
            self.minimumAltitude= 0 # Target Altitude (Meters) 
            # ****************************************************************************************

            # *******************************other training parameters ******************
            # consult https://www.siminnovations.com/xplane/dataref/index.php for full list of possible parameters
            self.P = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/P")[0][0] # moment P
            self.Q = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/Q")[0][0] # moment Q
            self.R = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/R")[0][0]  # moment R
            hstab = XplaneEnv.CLIENT.getDREF("sim/flightmodel/controls/hstab1_elv2def")[0][0] # horizontal stability : not use for now
            vstab = XplaneEnv.CLIENT.getDREF("sim/flightmodel/controls/vstab2_rud1def")[0][0] # vertical stability : not used for now
            
            self.gforce_normal = XplaneEnv.CLIENT.getDREF("sim/flightmodel2/misc/gforce_normal")[0][0] # vertical stability : not used for now
            self.gforce_axil = XplaneEnv.CLIENT.getDREF("sim/flightmodel2/misc/gforce_axil")[0][0] # vertical stability : not used for now
            self.gforce_side = XplaneEnv.CLIENT.getDREF("sim/flightmodel2/misc/gforce_side")[0][0] # vertical stability : not used for now
            self.gforce_overG = XplaneEnv.CLIENT.getDREF("sim/flightmodel2/misc/has_crashed")[0][0] # vertical stability : not used for now
            self.distance = XplaneEnv.CLIENT.getDREF("sim/cockpit/radios/gps_dme_dist_m")[0][0]
            self.raw_velocity = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/groundspeed")[0][0]
            self.ground_contact = XplaneEnv.CLIENT.getDREF("sim/flightmodel2/gear/on_ground")[0][0]
            self.plugAlt = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/y_agl")[0][0]
            self.simtime = XplaneEnv.CLIENT.getDREF("sim/time/total_running_time_sec")[0][0]
            # ******************************************************************************
            ################################################################################

            ##############################################################################
            # check that all parameters have been collected. This is done by checking the legth of list
            # It is possible because of network failure that all parameters are not retrieved on UDP
            # In that case previous state / last full state will be used. check the except of this try.
            if len(state) == self.statelength: # this should be true if len(state) is 10

                self.ControlParameters.state14['roll_rate'] = self.P #  The roll rotation rates (relative to the flight)
                self.ControlParameters.state14['pitch_rate']= self.Q    # The pitch rotation rates (relative to the flight)
                self.ControlParameters.state14['yaw_rate']= self.R # The yaw rotation rates (relative to the flight)
                self.ControlParameters.state14['altitude']= state[2] #  Altitude 
                self.ControlParameters.state14['Pitch']= state[3] # pitch 
                self.ControlParameters.state14['Roll']= state[4]  # roll
                self.ControlParameters.state14['velocity_x']= state[6] # local velocity x  OpenGL coordinates
                self.ControlParameters.state14['velocity_y']= state[7] # local velocity y  OpenGL coordinates              
                self.ControlParameters.state14['velocity_z']= state[8] # local velocity z   OpenGL coordinates
                self.ControlParameters.state14['delta_altitude']= abs(state[2] - self.minimumAltitude) # difference in altitude
                self.ControlParameters.state14['delta_heading']= abs(state[5] - self.headingReward) # difference in heading
                if self.test :
                    # if testing use append longitude and latitude as  the state variable
                    # The intuition for this is that during testing we need lat and long to be able to project the position of the
                    # aircarft in space. Thus [lat,long,altitude will be relevant]. Lat Long are not relevant during training
                    state.append(R) # if connection fails append R to make sure state is not empty
                    state14 = state # state variable this inclue lat long for ploting 

                else:
                    # lat long have been overriden. The dictionary above is used as normal during training
                    state14 = [i for i in self.ControlParameters.state14.values()]
            ######################################################################
            
            ###########################################################################
            # *******************************reward computation ******************
            timer =  XplaneEnv.CLIENT.getDREF(self.ControlParameters.timer2)[0][0] # running time of simulation
            self.reward = self.rewardCalcul()
            self.ControlParameters.episodeReward += self.reward
            self.ControlParameters.episodeStep += 1
            ### Check Point implementation ###
            
            #############################################################################

            ###########################################################################
            # end of episode setting

            ''' #KeepHeading Reset
            if self.ControlParameters.state14['altitude'] <= 880.2760009765625:
                self.ControlParameters.flag = True # end of episode flag
            '''

            # landing Reset 
            if abs(self.gforce_normal) >= 5 or abs(self.gforce_side) >= 5 or abs(self.gforce_axil) >= 5 or self.gforce_overG == 1:
                self.ControlParameters.flag = True
                self.reward -= 25 # end of episode flag
                self.ControlParameters.episodeStep = 0

            elif (self.raw_velocity <= 5 and self.plugAlt <= 5): #or self.ground_contact == 1):
                print("landed")
                landed = 50 * (self.max_sim_time - self.simtime)
                self.reward += landed
                self.ControlParameters.flag = True

            elif self.simtime >= self.max_sim_time:
                self.ControlParameters.flag = True

            ###########################################################################

            ###########################################################################
            # reset the episode paameters if Flag is true. (since episode has terminated)
            # flag marks end of episode
            if self.ControlParameters.flag:
                self.ControlParameters.episodeStep = 0
                print('reward',self.reward , 'episodeReward', self.ControlParameters.episodeReward, 'episodeSteps:', self.ControlParameters.episodeStep)
                self.reset()

            else:
                reward = self.ControlParameters.episodeReward
            ###########################################################################
        
            
        except:
            reward = self.ControlParameters.episodeReward
            self.ControlParameters.flag = False
            self.ControlParameters.state14 =  self.ControlParameters.state14
            if self.test:
                state.append(0)
                state14 = state
            else:
                state14 = [i for i in self.ControlParameters.state14.values()]
        
        q=clock() # end of loop timer 
        #rint("pause estimate", q-j)
        print("Reward:", self.reward, "delta_altitude:", self.ControlParameters.state14['delta_altitude'], "delta_heading:", self.ControlParameters.state14['delta_heading'],"Episode:",self.ControlParameters.episodeStep)
        #print("G_normal:",self.gforce_normal,"G_axil:",self.gforce_axil,"G_side:",self.gforce_side,"OverG:",self.gforce_overG)
        #print(self.ControlParameters.state14)
        sleep(0.1)

        return  state14,self.reward,self.ControlParameters.flag,{} #self._get_info() #self.ControlParameters.state14
  

    def _get_info(self):
        """Returns a dictionary contains debug info"""
        return {'control Parameters':self.ControlParameters, 'actions':self.action_space }

    def render(self, mode='human', close=False):
        pass


    def reset(self):
        """
        Reset environment and setup for new episode.
        Returns:
            initial state of reset environment.
        """
        print("reset")
        self.actions = [0,0,0,0] 
        self.ControlParameters.stateAircraftPosition = []
        self.ControlParameters.stateVariableValue = []
        self.ControlParameters.episodeReward  = 0.
        self.ControlParameters.totalReward  = 0.
        #self.ControlParameters.flag = False
        self.ControlParameters.episodeStep = 0
        self.ControlParameters.state14 = dict.fromkeys(self.ControlParameters.state14.keys(),0)
        state = np.zeros(11)
        
        return state # self.ControlParameters.state14
