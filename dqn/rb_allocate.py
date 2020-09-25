import tensorflow as tf
import random
import numpy as np
from collections import deque


class DeepQNetwork:
    r = np.array([[0, 1],
                  [0, 2],
                  [0, 4]])
    r_all = []  # 统计所获收益
    slices = [0, 0, 0]  # 统计各类切片在系统中运作的数量
    state_num = 0
    action_num = 2 
    state_space = []
    action_space = None
    state_list = None
    action_list = None
    slice_max = 4  # 系统运作最大切片数量
    gamma = 0.7

    initial_epsilon = 1
    final_epsilon = 0.1
    epsilon = 0
    Explore = 3000000

    Observe = 1000
    Batch = 64
    step_index = 0
    learn_step = 0  # 迭代次数

    memory_size = 10000
    memory_counter = 0
    replay_memory_store = deque()

    # primary_QNetwork参数
    q_eval_input = None
    action_input = None
    q_eval_output = None
    q_value = None
    q_target = None
    loss = None
    train_op = None
    learning_rate = 0.01  # 0.1/0.01/0.001

    # target_QNetwork参数
    target_q_eval_input = None
    target_q_eval_output = None

    sess = None

    # 初始化
    def __init__(self):
        self.create_state_space()
        self.action_space = np.array([[0, 1]])  # 动作空间,1 x 2
        # 初始化状态和动作列表为对角方阵
        self.state_list = np.identity(self.state_num)
        self.action_list = np.identity(self.action_num)
        # 创建神经网络
        self.create_target_q_network()
        self.create_q_network()
        # 初始话对话
        self.sess = tf.InteractiveSession()  # 对话必须在这里面初始化
        self.sess.run(tf.initialize_all_variables())

    # 创建状态空间
    def create_state_space(self):
        for slice_sum in range(self.slice_max + 1):
            if slice_sum == 0:
                state = [0, 0, 0]
                self.state_space.append(state)
                self.state_num += 1
            elif slice_sum == 1:
                for index in range(3):
                    state = [0, 0, 0]
                    state[index] = 1
                    self.state_space.append(state)
                    self.state_num += 1
            elif slice_sum == 2:
                for index in range(3):
                    state = [0, 0, 0]
                    state[index] = 2
                    self.state_space.append(state)
                    self.state_num += 1
                for index in range(3):
                    state = [1, 1, 1]
                    state[index] = 0
                    self.state_space.append(state)
                    self.state_num += 1
            elif slice_sum == 3:
                state = [1, 1, 1]
                self.state_space.append(state)
                self.state_num += 1
                for index in range(3):
                    state = [0, 0, 0]
                    state[index] = 3
                    self.state_space.append(state)
                    self.state_num += 1
                for index in range(3):
                    state = [1, 1, 1]
                    state[index] = 2
                    for i in range(3):
                        s = []
                        for j in range(3):
                            s.append(state[j])
                        if i != index:
                            s[i] = 0
                            self.state_space.append(s)
                            self.state_num += 1
            elif slice_sum == 4:
                for index in range(3):
                    state = [0, 0, 0]
                    state[index] = 4
                    self.state_space.append(state)
                    self.state_num += 1
                for index in range(3):
                    state = [1, 1, 1]
                    state[index] = 3
                    for i in range(3):
                        s = []
                        for j in range(3):
                            s.append(state[j])
                        if i != index:
                            s[i] = 0
                            self.state_space.append(s)
                            self.state_num += 1
                for index in range(3):
                    state = [1, 1, 1]
                    state[index] = 2
                    self.state_space.append(state)
                    self.state_num += 1
                for index in range(3):
                    state = [2, 2, 2]
                    state[index] = 0
                    self.state_space.append(state)
                    self.state_num += 1
        self.state_space = np.array(self.state_space)
        print('系统状态数:', self.state_num)
        print('系统状态空间:')
        print(self.state_space)

    # 创建target_q_network
    def create_target_q_network(self):
        # 定义节点op
        self.target_q_eval_input = tf.placeholder(shape=[None, self.state_num], dtype=tf.float32)  # [None,35]
        # 定义网络层,得到当前状态下可执行的动作的Q表
        neural_layer = 3
        in_size = self.state_num
        out_size = self.action_num
        w1 = tf.Variable(tf.random_normal(shape=[in_size, neural_layer]))  # [35,3]
        b1 = tf.Variable(tf.zeros(shape=[1, neural_layer]) + 0.1)  # [1,3]
        l1 = tf.matmul(self.target_q_eval_input, w1) + b1  # [None,3]
        w2 = tf.Variable(tf.random_normal(shape=[neural_layer, out_size]))  # [3,2]
        b2 = tf.Variable(tf.zeros(shape=[1, out_size]) + 0.1)  # [1,2]
        self.target_q_eval_output = tf.nn.relu(tf.matmul(l1, w2) + b2)  # [None,2]

    # 创建primary_q_network
    def create_q_network(self):
        # 定义节点op
        self.q_eval_input = tf.placeholder(shape=[None, self.state_num], dtype=tf.float32)  # [None,35]
        self.action_input = tf.placeholder(shape=[None, self.action_num], dtype=tf.float32)  # [None,2]
        self.q_target = tf.placeholder(shape=None, dtype=tf.float32)  # [None]
        # 定义网络层,得到当前状态下可执行的动作的Q表
        neural_layer = 3
        in_size = self.state_num
        out_size = self.action_num
        w1 = tf.Variable(tf.random_normal(shape=[in_size, neural_layer]))  # [35,3]
        b1 = tf.Variable(tf.zeros(shape=[1, neural_layer]) + 0.1)  # [1,3]
        l1 = tf.matmul(self.q_eval_input, w1) + b1  # [None,3]
        w2 = tf.Variable(tf.random_normal(shape=[neural_layer, out_size]))  # [3,2]
        b2 = tf.Variable(tf.zeros(shape=[1, out_size]) + 0.1)  # [1,2]
        self.q_eval_output = tf.nn.relu(tf.matmul(l1, w2) + b2)  # [None,2]
        # 计算当前动作下的Q值
        self.q_value = tf.reduce_sum(tf.multiply(self.q_eval_output, self.action_input),
                                     reduction_indices=[1])  # [None]
        self.loss = tf.reduce_mean(tf.square(self.q_target - self.q_value))
        # StochasticGradientDescent
        self.train_op = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self.loss)


    # 寻找状态标号
    def search_state_index(self, state):
        for i in range(0, self.state_num):
            flag = 1
            for j in range(0, 3):
                if state[j] != self.state_space[i][j]:
                    flag = 0
                    break
            if flag == 1:
                break
        state_index = i
        return state_index

    # 在一定概率下，事件表示两类切片请求到达系统，此时系统做出选择接收一类
    def create_event_in_pay(self,current_state_index):
        n1 = 0.3  # 两类切片请求到达系统的概率
        n2 = 0.7
        slice_index = []
        event = [0, 0, 0]
        current_state = self.state_space[current_state_index]
        n = np.random.uniform()
        if n < n1:
            index1 = None
            index2 = None
            while index1 == index2:
                index1 = np.random.randint(0, 3)
                index2 = np.random.randint(0, 3)
            slice_index.append(index1)
            slice_index.append(index2)
            event[slice_index[0]] = 1
            event[slice_index[1]] = 1
        else:
            slice_index.append(np.random.randint(0, 3))
            # 避免切片数量为0还让离开系统的事件发生
            if current_state[slice_index[0]] == 0:
                event[slice_index[0]] = np.random.randint(0, 2)
            else:
                event[slice_index[0]] = np.random.randint(0, 3) - 1
        return slice_index, event

    # 在训练时，只生成某类切片请求到达的事件
    def create_event_in_train(self):
        event = [0, 0, 0]
        slice_index = np.random.randint(0, 3)
        event[slice_index] = 1
        return slice_index, event

    # 选择动作
    def select_action(self, current_state_index):
        # 当系统切片数量饱和时，直接拒绝
        current_state = self.state_space[current_state_index]
        slice_sum = 0
        for i in range(len(current_state)):
            slice_sum += current_state[i]
        if slice_sum == self.slice_max:
            current_action_index = 0
        elif slice_sum < self.slice_max:
            n = np.random.uniform()
            if n < self.epsilon:
                current_action_index = np.random.randint(0, 2)
            else:
                state = self.state_list[current_state_index:current_state_index + 1]  # [1,35]
                action_values = self.sess.run(self.q_eval_output, feed_dict={self.q_eval_input: state})
                current_action_index = np.argmax(action_values)
        # 更新epsilon
        if self.epsilon > self.final_epsilon and self.step_index > self.Observe:
            self.epsilon -= (self.initial_epsilon - self.final_epsilon) / self.Explore
        return current_action_index

    # 执行动作
    def take_action(self, current_state_index, current_action_index, slice_index):
        reward = self.r[slice_index][current_action_index]
        next_state = []
        if current_action_index == 0:
            next_state_index = current_state_index
        elif current_action_index == 1:
            current_state = self.state_space[current_state_index]
            for index in range(3):
                next_state.append(current_state[index])
            next_state[slice_index] += 1
            next_state_index = self.search_state_index(next_state)

        return next_state_index, reward

    # 存储记忆
    def memory_store(self, current_state_index, current_action_index, reward, next_state_index):
        current_state = self.state_list[current_state_index:current_state_index + 1]  # [1,35]
        current_action = self.action_list[current_action_index:current_action_index + 1]  # [1,2]
        next_state = self.state_list[next_state_index:next_state_index + 1]
        # 四个量一组进行存放
        self.replay_memory_store.append((current_state, current_action, reward, next_state))
        if len(self.replay_memory_store) > self.memory_size:
            self.replay_memory_store.popleft()
        self.memory_counter += 1

    # 记忆回放
    def experience_replay(self):
        # 采样
        if self.memory_counter > self.Batch:
            batch = self.Batch
        else:
            batch = self.memory_counter
        minibatch = random.sample(self.replay_memory_store, batch)
        # 分别存放不同的记忆
        batch_state = None
        batch_action = None
        batch_reward = None
        batch_next_state = None
        for i in range(len(minibatch)):
            if batch_state is None:
                batch_state = minibatch[i][0]
            elif batch_state is not None:
                batch_state = np.vstack((batch_state, minibatch[i][0]))  # [batch,35]
            if batch_action is None:
                batch_action = minibatch[i][1]
            elif batch_action is not None:
                batch_action = np.vstack((batch_action, minibatch[i][1]))  # [batch,2]
            if batch_reward is None:
                batch_reward = minibatch[i][2]
            elif batch_reward is not None:
                batch_reward = np.vstack((batch_reward, minibatch[i][2]))  # [batch]
            if batch_next_state is None:
                batch_next_state = minibatch[i][3]
            elif batch_next_state is not None:
                batch_next_state = np.vstack((batch_next_state, minibatch[i][3]))  # [batch,35]
        # 将下一状态集合输入target_q_network得到下一状态对应动作集合batch_next_action
        action_values = self.sess.run(self.target_q_eval_output, feed_dict={self.target_q_eval_input: batch_next_state})
        batch_next_action = None  # [64,2]
        for index in range(batch):
            action_index = np.argmax(action_values[index])
            if batch_next_action is None:
                batch_next_action = self.action_list[action_index:action_index+1]
            elif batch_next_action is not None:
                batch_next_action = np.vstack((batch_next_action, self.action_list[action_index:action_index+1]))
        y = []
        # 将下一状态集合和下一状态对应动作集合输入primary_q_network得到Q值集合
        q_values = self.sess.run(self.q_value, feed_dict={self.q_eval_input: batch_next_state,
                                                          self.action_input: batch_next_action})
        for index in range(batch):
            y.append(batch_reward[index]+self.gamma*q_values[index])

        # 将y值输入primary_q_network进行训练得到loss值
        trainer, loss = self.sess.run([self.train_op, self.loss], feed_dict={self.q_eval_input: batch_state,
                                                                             self.action_input: batch_action,
                                                                             self.q_target: y})
        if self.learn_step % 1000 == 0:
            print('loss:', loss)

    # 训练
    def train(self):
        # 初始化状态
        current_state_index = np.random.randint(35)
        self.epsilon = self.initial_epsilon
        while True:
            slice_index, event = self.create_event_in_train()
            slice_sum = 0
            current_state = self.state_space[current_state_index]
            for i in range(len(current_state)):
                slice_sum += current_state[i]

            if slice_sum < self.slice_max:
                current_action_index = self.select_action(current_state_index)
                next_state_index, reward = self.take_action(current_state_index, current_action_index, slice_index)
                self.memory_store(current_state_index, current_action_index, reward, next_state_index)
                current_state_index = next_state_index
            elif slice_sum == self.slice_max:
                current_state_index = 0

            self.step_index += 1
            if self.step_index > self.Observe:
                self.experience_replay()
                self.learn_step += 1
            # 迭代次数一定后结束训练
            if self.learn_step == 5000:
                break

    # 测试
    def pay(self):
        # 训练神经网络
        self.train()
        # 初始化状态
        current_state_index = 0
        current_state = self.state_space[current_state_index]
        print('>>>系统初始状态：', current_state, '<<<')
        print()
        event_num = 50  # 生成事件数量/系统运作总周期event_num*T
        # 创建event_num个事件
        for i in range(event_num):
            next_state = []
            reward = 0
            slice_index, event = self.create_event_in_pay(current_state_index)
            # 只对一个切片进行处理
            if len(slice_index) == 1:
                if event[slice_index[0]] == 0:
                    next_state_index = current_state_index
                    next_state = self.state_space[next_state_index]
                    reward = 0
                    print('###既没有新的切片请求到达系统，也没有切片离开系统###')
                    print('——>系统当前状态：', next_state)
                    print()
                elif event[slice_index[0]] == -1 and current_state[slice_index[0]] > 0:
                    for index in range(3):
                        next_state.append(current_state[index])
                    next_state[slice_index[0]] -= 1
                    next_state_index = self.search_state_index(next_state)
                    reward = 0
                    print('###第', slice_index[0]+1, '类切片离开系统###')
                    print('——>系统当前状态：', next_state)
                    print()
                else:
                    print('###第', slice_index[0] + 1, '类切片请求到达系统###')
                    # 系统运作切片数量饱和时拒绝请求
                    slice_sum = 0
                    for index in range(3):
                        slice_sum += current_state[index]
                    if slice_sum == self.slice_max:
                        next_state_index = current_state_index
                        next_state = self.state_space[next_state_index]
                        reward = 0
                        print('###当前系统中正在运作的切片数量饱和，拒绝第', slice_index[0]+1, '类切片请求###')
                        print('——>系统当前状态：', next_state)
                        print()
                    else:
                        state = self.state_list[current_state_index:current_state_index+1]
                        action_values = self.sess.run(self.q_eval_output,feed_dict={self.q_eval_input:state})
                        current_action_index = np.argmax(action_values)
                        next_state_index,reward = self.take_action(current_state_index,current_action_index,slice_index[0])
                        next_state = self.state_space[next_state_index]
                        if current_action_index == 0:
                            print('###系统拒绝第', slice_index[0]+1, '类切片请求，获得即时奖励', reward, '###')
                            print('——>系统当前状态：', next_state)
                            print()
                        else:
                            self.slices[slice_index[0]] += 1
                            print('###系统接受第', slice_index[0]+1, '类切片请求，获得即时奖励', reward, '###')
                            print('——>系统当前状态：', next_state)
                            print()
            # 两个切片请求同时到达
            elif len(slice_index) == 2:
                print('###第',slice_index[0]+1,'和第',slice_index[1]+1,'类切片请求同时到达系统###')
                # 系统运作切片数量饱和时拒绝请求
                slice_sum = 0
                for index in range(3):
                    slice_sum += current_state[index]
                if slice_sum == self.slice_max:
                    next_state_index = current_state_index
                    next_state = self.state_space[next_state_index]
                    reward = 0
                    print('###当前系统中正在运作的切片数量饱和，拒绝第', slice_index[0]+1, '和第',slice_index[1]+1,'类切片请求###')
                    print('——>系统当前状态：', next_state)
                    print()
                else:
                    state = self.state_list[current_state_index:current_state_index + 1]
                    action_values = self.sess.run(self.q_eval_output, feed_dict={self.q_eval_input: state})
                    current_action_index = np.argmax(action_values)
                    rewards = [0,0]
                    next_state_index1,rewards[0] = self.take_action(current_state_index,current_action_index,slice_index[0])
                    next_state_index2,rewards[1] = self.take_action(current_state_index,current_action_index,slice_index[1])
                    if current_action_index == 0:
                        next_state_index = current_state_index
                        next_state = self.state_space[next_state_index]
                        reward = 0
                        print('###系统拒绝第', slice_index[0]+1, '和第',slice_index[1]+1,'类切片请求###')
                        print('——>系统当前状态：', next_state)
                        print()
                    else:
                        if rewards[0] > rewards[1]:
                            next_state_index = next_state_index1
                            reward_No = 0
                            slice_No = slice_index[0] + 1
                        else:
                            next_state_index = next_state_index2
                            reward_No = 1
                            slice_No = slice_index[1] + 1
                        next_state = self.state_space[next_state_index]
                        reward = rewards[reward_No]
                        self.slices[slice_No-1] += 1
                        print('###系统接受第', slice_No, '类切片请求，获得即时奖励', rewards[reward_No], '###')
                        print('——>系统当前状态：', next_state)
                        print()
            # 更新状态积累收益
            self.r_all.append(reward)
            current_state_index = next_state_index
            current_state = self.state_space[current_state_index]
        # 计算长期平均收益
        r_average = 0
        for j in range(len(self.r_all)):
            r_average += self.r_all[j]
        r_average = r_average/event_num
        print('系统长期平均收益：', r_average)
        # 统计系统中各类切片运作总数
        class_1 = self.slices[0]
        class_2 = self.slices[1]
        class_3 = self.slices[2]
        class_all = class_1+class_2+class_3
        print('第1类在系统中运作的切片总数量：', class_1, '个')
        print('第2类在系统中运作的切片总数量：', class_2, '个')
        print('第3类在系统中运作的切片总数量：', class_3, '个')
        proportion_1 = class_1 / class_all
        proportion_2 = class_2 / class_all
        proportion_3 = 1 - proportion_1 - proportion_2
        print('第1类切片在系统中运作数目占比：', round(proportion_1 * 100, 0), '%')
        print('第2类切片在系统中运作数目占比：', round(proportion_2 * 100, 0), '%')
        print('第3类切片在系统中运作数目占比：', round(proportion_3 * 100, 0), '%')


if __name__ == "__main__":
    q_network = DeepQNetwork()
    q_network.pay()
