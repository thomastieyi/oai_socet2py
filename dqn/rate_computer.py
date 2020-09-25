"""
模拟OAI-LTE之中的下行速率计算函数
1 frame = 10ms
1 subframe = 1ms
1 subframe = 2 slots = (0.5ms)*2
1 RB = 180kHz(frequency domain,被12个Subcarrier平分) * 0.5ms(time domain，总共有7个OFDMA符号)
    一个RB中共有 12*7 = 84 个RE（无无线承载元素）
    最小调度时间TTI = 1ms = 2 slots，最小调度单位有两个RB构成的（RB Pair）
1 PRB（物理） 一个TTI 内的调度（调度PDSCH 和PUSCH 资源）的最小单位实际上由同一子帧上时间上相连的2 个RB（每个slot 对应一个RB）组成，并被称为RB pair
    一个PRB实际上有 84 * 2 = 168 个RE
    时频分布：180kHZ*1ms（TTI）

现做如下假设：
    1. 采用 band7 20 MHz 100PRB 的LTE制式，即每个TTI内传输100个PRB
    2. 每个PRB在一个TTI内只能被分配到一个UE上
    3. 现假设信道为理想信道（rf-sim）,下行MCS-index均为最大28，调制指数6（64QAM）
    4. 每次调度计算个UE的速率，仅由 State_n=[R1,R2,R3,R4] {∑R<=100}，以及各个R_n对应查表得出TBS计算速率
    5. 2x2 MIMO 双流传输

计算公式：
        子帧 n：
            UE_n计算速率 = （UE_n占用子频带数目SC_n*调制指数(6)*OFDMA符号数(7)*2）/ TTI ==>单位(bps)
            SC_n = R_n*12 (每个PRB占用了12个子频带)
            TTI = 1 ms = 0.001 s
            故：
                V_n = ((R_n*12*6*7*2*2)/0.001)*0.75, 有0.25的估计下行系统开销

"""
import numpy as np

class Rate():
    def __init__(self):
        self.rate_arr=[0.0,0.0,0.0,0.0]
    def _get_rate(self,R_n):
        return (((R_n*12*6*7*2*2)/0.001)*0.75)/1000000
    
    def _all_ue_rate(self,state_space):
        for index,value in enumerate(state_space):
            self.rate_arr[index]=self._get_rate(value)
        return self.rate_arr
        
