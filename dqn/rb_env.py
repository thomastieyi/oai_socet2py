"""
Reinforcement learning maze example.

Red rectangle:          explorer.
Black rectangles:       hells       [reward = -1].
Yellow bin circle:      paradise    [reward = +1].
All other states:       ground      [reward = 0].

This script is the environment part of this example.
The RL is in RL_brain.py.

View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""
import numpy as np
import time
import sys
if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk

from rate_computer import Rate
UNIT = 40   # pixels
MAZE_H = 10 # grid height
MAZE_W = 10 # grid width
UE1_RATE = 11
UE2_RATE = 47
UE3_RATE = 33
UE4_RATE = 25
RATES =np.array([UE1_RATE,UE2_RATE,UE3_RATE,UE4_RATE])
colors = '''#696969 DimGray 暗淡灰
#FF0000 Red 纯红
#FAEBD7 AntiqueWhite 古董白
#FFFF00 Yellow 纯黄
#006400 DarkGreen 暗绿色
#BDB76B DarkKhaki 暗黄褐色/深卡叽布
#FFFACD LemonChiffon 柠檬绸
'''

cooler_arr= np.array(['#FF69B4'])

for color in colors.split('\n'):
    sp = color.split(' ')   
    cooler_arr = np.append(cooler_arr,sp[0])





class RB(tk.Tk,object):
    def __init__(self):
        super(RB,self).__init__()
        self.action_space = ['a1','a2','a3','a4',]
        #4个UE的资源在一个TTI的PRB占用
        self.state_space = np.array([0,0,0,0])
        self.n_actions = len(self.action_space)
        self.n_features = 4
        self.title('RB_Allocated in one subframe')
        self.geometry('{0}x{1}'.format(MAZE_H * UNIT, MAZE_H * UNIT))
        self.getRates = Rate()
        self._build_RB()
        self._prbs=[]
    
    def _build_RB(self):
        self.canvas = tk.Canvas(self, bg='white',
                           height=MAZE_H * UNIT,
                           width=MAZE_W * UNIT)

        # create grids
        for c in range(0, MAZE_W * UNIT, UNIT):
            x0, y0, x1, y1 = c, 0, c, MAZE_H * UNIT
            self.canvas.create_line(x0, y0, x1, y1)
        for r in range(0, MAZE_H * UNIT, UNIT):
            x0, y0, x1, y1 = 0, r, MAZE_W * UNIT, r
            self.canvas.create_line(x0, y0, x1, y1)

        # create origin
        origin = np.array([20, 20])


        # 定义100个PRB的坐标
        self.rbs_posis = np.array([[20, 20]])
        for i in range(10):
            x=UNIT*(i)
            for j in range(10):
                y=UNIT*(j)
                buffer= origin + np.array([x, y])
                self.rbs_posis = np.concatenate((self.rbs_posis,[buffer]))
            
        self.canvas.pack()

    def _draw_state(self,state_space):
        self.update()
        self.state_space = state_space
        
        allocated=1
        for ue in range(4):
            for prbs in range(state_space[ue]):
                self._prbs.append('UE_'+str(ue)+"_"+str(prbs))
                setattr(self,'UE_'+str(ue)+"_"+str(prbs), self.canvas.create_rectangle(
                                                               self.rbs_posis[allocated][0] - 15, self.rbs_posis[allocated][1] - 15,
                                                               self.rbs_posis[allocated][0] + 15, self.rbs_posis[allocated][1] + 15,
                                                               fill=cooler_arr[ue]))
                allocated+=1

        self.canvas.pack()

        # reward function
    
    def _allocate(self,action):
        self.already_all=0
        rates=np.array(self.getRates._all_ue_rate(self.state_space))
       # print(action)
        for i in self.state_space:
            self.already_all+=i
        if action == 0:     # ue1
            if ((self.state_space[0]<=100) and (self.already_all<100) and (rates[0]<=RATES[0])):
                self.state_space[0]+=1
        elif action == 1:   # ue2
            if  ((self.state_space[1]<=100) and (self.already_all<100) and (rates[1]<=RATES[1])):
                self.state_space[1]+=1
        elif action == 2:   # ue3
            if  ((self.state_space[2]<=100) and (self.already_all<100) and (rates[2]<=RATES[2])):
                self.state_space[2]+=1
        elif action == 3:   # ue4
            if  ((self.state_space[3]<=100) and (self.already_all<100) and (rates[3]<=RATES[3])):
                self.state_space[3]+=1

        self._delete_draw()
        self._draw_state(self.state_space)
        #print(self.state_space)
        print(rates)
        print("Utiliztion:  "+str( self.already_all/100.0))
        # reward function
        delta = (np.array(rates) - np.array(RATES)  )/np.array(RATES)
        reward= 0
        if((rates[action]>=RATES[action])):
            reward = -1
        elif((rates[action]<=RATES[action])):
            reward = 1
        elif ((delta[0]>=0) or (delta[1]>=0) or (delta[2]>=0) or (delta[3]>=0)):
            reward = 10      
        elif ((delta[0]<0) and (delta[1]<0) and (delta[2]<0) and (delta[3]<0)):
            reward = 0
        elif ((delta[0]>=0) and (delta[1]>=0) and (delta[2]>=0) and (delta[3]>=0)):
            reward = 100

        print(reward)
        if((rates[0]>=RATES[0]) and (rates[1]>=RATES[1])  and (rates[2]>=RATES[2])  and  (rates[3]>=RATES[3])  ):
            done = True
        else:
            done = False
        
        return delta, reward, done

    def _delete_draw(self):
        self.update()
        #time.sleep(0.001)
        for i in self._prbs:
            self.canvas.delete(getattr(self,i))
           
    def reset(self):
        self.update()
        #time.sleep(0.001)
        try:
            for i in self._prbs:
                self.canvas.delete(getattr(self,i))
        finally:
            pass
       
        rates=np.array(self.getRates._all_ue_rate(self.state_space))
        # reward function
        delta = (np.array(rates) - np.array(RATES)  )/np.array(RATES)
        self.state_space = np.array([0,0,0,0])
        return delta
