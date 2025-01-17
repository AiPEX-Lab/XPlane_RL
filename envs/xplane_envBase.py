import gym
import gym_xplane.xpc as xp
import gym_xplane.parameters as parameters
import gym_xplane.space_definition as envSpaces
import numpy as np
import itertools
from time import sleep, clock



class initial:

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
        self.max_episode_steps = 1000
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
        ### Altitude Reward 

        reward_altitude = np.tanh(1-((2*self.ControlParameters.state14['delta_altitude'])/1524))
        
        ### Heading Reward

        if self.ControlParameters.state14['delta_heading'] < 180:
            reward_heading = 1 - (self.ControlParameters.state14['delta_heading']/90)
        else:
            reward_heading = -1 + ((self.ControlParameters.state14['delta_heading'] - 180)/90)
        
        ### G_force Reward
        '''
        if XplaneEnv.CLIENT.getDREFs(self.ControlParameters.gforce)[0][0] < 1.5:
            g_reward = 1
        else:
            g_reward = np.tanh(1-(XplaneEnv.CLIENT.getDREFs(self.ControlParameters.gforce)[0][0]/7.5))
        '''


        reward = reward_heading + reward_altitude
        return np.array(reward)


    def step(self, actions):
     

        self.test=False # if true, only test paramters returned. for Model tesing 
        self.ControlParameters.flag = False # for synchronisation of training
        checkStep = 0
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
            # get the state variabls here . The parameter file has all the required variables
            # we only need to call the client interface and get parameters defined as stateVariable
            # in parameter file as below
            stateVariableTemp = XplaneEnv.CLIENT.getDREFs(self.ControlParameters.stateVariable) 
            # the client interface automaically gets the position paameters
            self.ControlParameters.stateAircraftPosition = list(XplaneEnv.CLIENT.getPOSI());
            # Remove brackets from state variable and store in the dictionary
            self.ControlParameters.stateVariableValue = [i[0] for i in stateVariableTemp]
            # combine the position and other state parameters in temporary variable here
            state =  self.ControlParameters.stateAircraftPosition + self.ControlParameters.stateVariableValue
            ########################################################

            ########################################################
            # **********************************************reward parametera**********************
            self.headingReward = 213.5 # the heading target for keepHeadingAW1 (headingTrue)
            self.minimumAltitude= 1524 # Target Altitude (Meters) keepHeadings
            minimumRuntime = 210.50 # Target runtime ????
            # ****************************************************************************************

            # *******************************other training parameters ******************
            # consult https://www.siminnovations.com/xplane/dataref/index.php for full list of possible parameters
            P = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/P")[0][0] # moment P
            Q = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/Q")[0][0] # moment Q
            R = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/R")[0][0]  # moment R
            hstab = XplaneEnv.CLIENT.getDREF("sim/flightmodel/controls/hstab1_elv2def")[0][0] # horizontal stability : not use for now
            vstab = XplaneEnv.CLIENT.getDREF("sim/flightmodel/controls/vstab2_rud1def")[0][0] # vertical stability : not used for now
            
            self.gforce_normal = XplaneEnv.CLIENT.getDREF("sim/flightmodel2/misc/gforce_normal")[0][0] # vertical stability : not used for now
            self.distance = XplaneEnv.CLIENT.getDREF("sim/cockpit/radios/gps_dme_dist_m")[0][0]
            self.rew_velocity = XplaneEnv.CLIENT.getDREF("sim/flightmodel/position/groundspeed")[0][0]

            # ******************************************************************************
            ################################################################################

            ##############################################################################
            # check that all parameters have been collected. This is done by checking the legth of list
            # It is possible because of network failure that all parameters are not retrieved on UDP
            # In that case previous state / last full state will be used. check the except of this try.
            if len(state) == self.statelength: # this should be true if len(state) is 10

                self.ControlParameters.state14['roll_rate'] = P #  The roll rotation rates (relative to the flight)
                self.ControlParameters.state14['pitch_rate']= Q    # The pitch rotation rates (relative to the flight)
                self.ControlParameters.state14['yaw_rate']= R # The yaw rotation rates (relative to the flight)
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
            # parameters required for reward
            timer =  XplaneEnv.CLIENT.getDREF(self.ControlParameters.timer2)[0][0] # running time of simulation
            #target_state = [abs(XplaneEnv.CLIENT.getDREFs(self.ControlParameters.on_ground)[0][0])),self.minimumAltitude,0.25]  # taget situation -heading, altitude, and distance 
            #target_state = XplaneEnv.CLIENT.getDREFs(self.ControlParameters.on_ground)[0][0]
            #xplane_state = [ abs(state[5]),state[2],rewardVector]  # present situation -heading, altitude, and distance 
            self.reward = self.rewardCalcul()
            self.ControlParameters.episodeReward += self.reward
            self.ControlParameters.episodeStep += 1
            ### Check Point implementation ###
            
            #############################################################################

            ###########################################################################
            # end of episode setting
            # detect crash and penalize the agênt
            # if crash add -3 otherwose reward ramin same
            print(self.ControlParameters.state14['altitude'])
            if self.ControlParameters.state14['altitude'] <= 880.2760009765625:
                self.ControlParameters.flag = True # end of episode flag
            elif self.ControlParameters.episodeStep > self.max_episode_steps:
                self.ControlParameters.flag = True

            ###########################################################################

            ###########################################################################
            # reset the episode paameters if Flag is true. (since episode has terminated)
            # flag is synchonised with XPlane enviroment
            if self.ControlParameters.flag:
                print('reward',self.reward , 'episodeReward', self.ControlParameters.episodeReward, 'episodeSteps:', self.ControlParameters.episodeStep)
                #self.ControlParameters.flag = True
                print("Flag")
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
