import os
import sys
import gym
import time
import torch
import torch.nn as nn
import pickle
import numpy as np
import glog as log
import subprocess
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import gym_unrealcv
import real_lsd

from PPOagent import PPOAgent

# TODO: change data save path

'''------------------------Hyperparameters------------------------'''
hidden_size      = 256
lr               = 3e-4
num_steps        = 20
mini_batch_size  = 5
ppo_epochs       = 5
max_frames       = 15000
threshold_reward = -100

'''----------------------------------------------------------------'''


'''---------------------------Helper functions--------------------'''
def save_obj(obj, filename, timestamp):
    dir = timestamp
    # path = os.getcwd()
    PATH = '/media/scratch2/plr_project/PLR/data/eval_test'  #'/home/plr/PLR'    # '/media/scratch2/plr_project/PLR'
    
    if dir not in os.listdir(PATH):
        PATH =  os.path.join(PATH, dir)
        os.mkdir(PATH)
    else:
        PATH =  os.path.join(PATH, dir)
    
    abs_file_path = PATH + '/' + filename + '.pkl'
    print("1")
    with open(abs_file_path, 'wb') as f:
        print("2")

        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

        print("3")

    return filename

def save_train(obj, filename, timestamp):
    dir = timestamp
    # path = os.getcwd()
    PATH = '/media/scratch2/plr_project/PLR/data/data_train'  #'/home/plr/PLR'    # '/media/scratch2/plr_project/PLR'
    
    if dir not in os.listdir(PATH):
        PATH =  os.path.join(PATH, dir)
        os.mkdir(PATH)
    else:
        PATH =  os.path.join(PATH, dir)
    
    abs_file_path = PATH + '/' + filename + '.pkl'
    print("1")
    with open(abs_file_path, 'wb') as f:
        print("2")

        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

        print("3")

    return filename

def load_obj(filename):
    dir = 'data'
    path = os.getcwd()
    assert dir in os.listdir(path)
    path = path + '/' + dir + '/'
    with open(path + filename + '.pkl', 'rb') as f:
        return pickle.load(f)

# get activation of layers in model
def get_activation(name):
    def hook(model, input, output):
        activation[name] = output.detach()
    return hook

def plot(train_timestamp,frame_idx, rewards):
#     clear_output(True)
     PATH = "/media/scratch2/plr_project/PLR/data/train_rewards"
     if train_timestamp not in os.listdir(PATH):
         PATH =  os.path.join(PATH, train_timestamp)
         os.mkdir(PATH)
     else:
         PATH =  os.path.join(PATH, train_timestamp)
     plt.figure(figsize=(20,5))
     plt.subplot(131)
     plt.title('frame %s. reward: %s' % (frame_idx, rewards[-1]))
     plt.plot(rewards)
     out_plot = PATH + '/' + "{}_training_rewards_{}.png".format(train_timestamp,frame_idx)
     plt.savefig(out_plot, format='png')
     #plt.show()

def plot_trajectory(poses_x, poses_y, poses_z, test, episode_count, info, timestamp):
    PATH = "/media/scratch2/plr_project/PLR/data/test_traj"
    if timestamp not in os.listdir(PATH):
        PATH =  os.path.join(PATH, timestamp)
        os.mkdir(PATH)
    else:
        PATH =  os.path.join(PATH, timestamp)
    plt.figure(figsize=(20,5))
    plt.subplot(111, projection='3d')
    plt.title('Trajectory')
    plt.plot(poses_x, poses_y, poses_z)
    if info['Success']:
        out_plottraj= PATH + '/' + "{}_{}_{}_succ.png".format(timestamp,test,episode_count)
    elif info['Max Step']:
        out_plottraj=PATH + '/' + "{}_{}_{}_max.png".format(timestamp,test,episode_count)
    elif info['Collision']:
        out_plottraj=PATH + '/' + "{}_{}_{}_coll.png".format(timestamp,test,episode_count)
    elif info['Out_of_boundaries']:
        out_plottraj=PATH + '/' + "{}_{}_{}_out.png".format(timestamp,test,episode_count)
    else:
        out_plottraj=PATH + '/' + "{}_{}_{}_fail.png".format(timestamp,test,episode_count)
    plt.savefig(out_plottraj, format='png')


def test_env():
    state = env.reset()
    done = False
    steps = 0
    total_reward = 0
    while not done:
        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        dist, _ = agent.model(state)
        next_state, reward, done, _, = env.step(dist.sample().cpu().numpy()[0])
        state = next_state
        steps +=1
        total_reward += reward

    mean_reward = total_reward / steps
    return [total_reward, mean_reward]

'''---------------------------------------------------------------'''

# LOG LEVEL: Set to INFO for debugging
log.setLevel("WARN")


# Copy settings file to data folder
json_abs_path = os.path.dirname(real_lsd.__file__) + '/envs/settings/landing/gorner.json'
lan_abs_path = os.path.dirname(real_lsd.__file__) + '/../agents/ppo_agent/lander.py'
rew_abs_path = os.path.dirname(real_lsd.__file__) + '/envs/landing/reward.py'
un_abs_path = os.path.dirname(real_lsd.__file__) + '/envs/unrealcv_landing_base.py'

PATH = '/home/nicloi/plr_project/PLR/data/snap'

train_timestamp = time.strftime("%Y%m%d_%H%M%S")
if train_timestamp not in os.listdir(PATH):
    PATH =  os.path.join(PATH, train_timestamp)
    os.mkdir(PATH)
else:
    PATH =  os.path.join(PATH, train_timestamp)

json_cp_path  = PATH +"/"+ train_timestamp + '_gorner.json' #'/home/plr/PLR/data/json' # '/home/nicloi/plr_project/data'
lan_cp_path  = PATH + "/"+train_timestamp + '_lander.py'
rew_cp_path  = PATH + "/"+train_timestamp + '_reward.py'
un_cp_path  = PATH + "/"+train_timestamp + '_unrealcv_landing_base.py'

list_files = subprocess.run(["cp", json_abs_path, json_cp_path])
log.warn("The exit code was: %d" % list_files.returncode)
list_files = subprocess.run(["cp", lan_abs_path, lan_cp_path])
log.warn("The exit code was: %d" % list_files.returncode)
list_files = subprocess.run(["cp", rew_abs_path, rew_cp_path])
log.warn("The exit code was: %d" % list_files.returncode)
list_files = subprocess.run(["cp", un_abs_path, un_cp_path])
log.warn("The exit code was: %d" % list_files.returncode)

log.warn("Starting...")
print("\n\n")
log.warn("TIMESTAMP:   {}\n\n".format(train_timestamp))

# Check cuda availability/set device
use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")


# Initialising environment
#env = gym.make('MyUnrealLand-cpptestFloorGood-DiscreteHeightFeatures-v0')
env = gym.make('MyUnrealLand-gornerFloorGood-Discrete-v0')
num_inputs  = env.observation_space.shape[0]
num_outputs = env.action_space.n
log.info("Observation Space:", env.observation_space, "dimension of observation:", env.observation_space.shape[0])
log.info("Action Space:", env.action_space, "Number of actions:", env.action_space.n)


# Initialise agent
agent = PPOAgent(num_inputs,
                num_outputs,
                hidden_size,
                lr,
                num_steps,
                mini_batch_size,
                ppo_epochs,
                threshold_reward,
                std=0.0,
                device=device)

# print(agent.model)
# print(agent.model.actor)
# print(agent.model.actor[0])
# print(type(agent.model.actor[0]))


# set model train mode
agent.model.train()


# Register hooks for actor layer activations
for name, layer in agent.model.actor.named_modules():
    if isinstance(layer, nn.ReLU) or isinstance(layer, nn.Linear) or isinstance(layer, nn.LogSoftmax) or isinstance(layer, nn.LeakyReLU):
        print(name, layer)
        layer.register_forward_hook(get_activation('actor_layer_{}'.format(name)))


# Define and initialise auxiliary variables
frame_idx  = 0
test_rewards = []
test_mean_rewards = []
episode_count = 0
episode_now = 0
values_at_beginning = []
prior_action = 0
activation = {}
training_data = dict()
early_stop = False


# Reset environment and load starting state into state
state = env.reset()


# Training loop
while frame_idx < max_frames and not early_stop:
    log.warn("\n\n\n")
    log.warn("Training Timestamp: {}".format(train_timestamp))
    log.warn("\n\n\n")
    log.warn("Frame: {} of {} \n\n\n".format(frame_idx, max_frames))

    log_probs = []
    values    = []
    states    = []
    actions   = []
    rewards   = []
    masks     = []
    entropy = 0

    for st in range(num_steps):
        action = None
        state = torch.FloatTensor(state).to(device)
        log.info("Model Input: {}".format(state))

        assert torch.sum(torch.isnan(state)) == 0, "State contains NANs!"
        log.info("state SIZE: {}".format(state.size()))

        dist, value = agent.model(state)
        log.info("Forward pass distribution: {}, forward pass value: {}".format(dist, value))

        if (episode_now != episode_count):
            values_at_beginning.append(value)
        episode_now = episode_count

        # Output all layer activations to logstream
        #for i in range(5):
        #    log.warn("actor layer {} activation: {}".format(i, activation['actor_layer_'+str(i)]))

        state = state.unsqueeze(1)
        state = torch.transpose(state, 0, 1)
        log.info("state post unsqueeze and transpose SIZE: {}".format(state.size()))

        value = value.unsqueeze(1)
        log.info("Value: {}".format(value))

        action = dist.sample()
        log.warn("Sampled Action: {}".format(action))
        log.info("Action TYPE: {}, SHAPE: {}".format(type(action), action.shape))

        action_not_same = not (action == prior_action)
        #log.warn("Sampled Action is not same as prior action: {}".format(action_not_same))
        prior_action = action

        next_state, reward, done, info = env.step(action.cpu().numpy())
        #log.warn("Step REWARD: {} DONE: {}".format(reward, done))

        #log.warn("Distance to mesh: {}".format(info['Mesh_dists']))

        log_prob = dist.log_prob(action)
        log.info("Step LOG_PROB: {}".format(log_prob))
        log.info("LOG_PROB TYPE: {}, SHAPE: {}".format(type(log_prob), log_prob.shape))

        entropy += dist.entropy().mean()

        # Append data to arrays
        log_prob = log_prob.unsqueeze(0)
        log_prob = log_prob.unsqueeze(1)
        log_prob = log_prob.to(device)
        log_probs.append(log_prob)

        values.append(value)

        interim = torch.FloatTensor([np.float(reward)])
        interim = interim.unsqueeze(1)
        reward  = interim.to(device)
        rewards.append(reward)

        mask = float(1-done)
        mask = torch.FloatTensor([mask])
        mask = mask.unsqueeze(1)
        masks.append(mask.to(device))

        states.append(state)

        action = action.unsqueeze(0)
        action = action.unsqueeze(1)
        action = action.to(device)
        actions.append(action)

        # collect data on training progress
        if frame_idx % 1000 == 0:
            test_ep_total_rewards = []
            test_ep_mean_rewards = []
            for _ in range(15):
                test_res = test_env()
                test_ep_total_rewards.append(test_res[0])
                test_ep_mean_rewards.append(test_res[1])

            test_mean_reward = np.mean(test_ep_mean_rewards)
            test_reward = np.mean(test_ep_total_rewards)
            log.warn("Test results -> Total reward: {}, Mean reward: {}".format(test_reward, test_mean_reward))

            test_mean_rewards.append(test_mean_reward)
            test_rewards.append(test_reward)
            plot(train_timestamp, frame_idx, test_rewards)
            if test_reward > threshold_reward: early_stop = True

        # next state logic
        if done:
            episode_count += 1
            log.warn(info)
            log.warn("Resetting")          
            state = env.reset()
        else:
            state = next_state

        frame_idx += 1

        ### END for loop

    next_state = torch.FloatTensor(next_state).to(device)

    assert torch.sum(torch.isnan(next_state)) == 0

    _, next_value = agent.model(next_state)

    next_state = next_state.unsqueeze(1)
    next_state = torch.transpose(next_state, 0, 1)

    # compute returns for advantage function
    returns = agent.compute_gae(next_value,
                                rewards,
                                masks,
                                values)

    returns   = torch.cat(returns).detach()
    log_probs = torch.cat(log_probs).detach()
    values    = torch.cat(values).detach()
    states    = torch.cat(states)
    actions   = torch.cat(actions)
    advantage = returns - values

    # log.info("Returns before CAT: {}".format(len(returns)))
    log.info("Returns   SIZE after CAT: {}".format(returns.size()))
    log.info("log probs SIZE after CAT: {}".format(log_probs.size()))
    log.info("Values    SIZE after CAT: {}".format(values.size()))
    log.info("States    SIZE after CAT: {}".format(states.size()))
    log.info("Actions   SIZE after CAT: {}".format(actions.size()))
    log.info("Advantage SIZE after CAT: {}".format(advantage.size()))

    log.warn("Calling PPO update.")
    agent.ppo_update(ppo_epochs, mini_batch_size, states, actions, log_probs, returns, advantage)

    ### END while loop

# Save data collected during training
plot(train_timestamp, frame_idx,'all')
training_data['test_rewards'] = test_rewards
training_data['test_mean_rewards'] = test_mean_rewards
training_data['values_at_beginning'] = values_at_beginning
_ = save_train(training_data, train_timestamp + '_training_data', train_timestamp)

# Delete training data once data is saved! Free up Memory
del training_data
del test_rewards
del test_mean_rewards
del values_at_beginning

# Save model
log.warn("Saving the model.")
agent.save_model()

log.warn("Training completed.")


'''------------------- Testing the policy after training --------------------'''
# Testing parameters
num_tests = 5
episodes_per_test = np.array([10,20,30,40,50])
tot_successful_episodes = 0
successful_episodes = 0

log.warn("Setting model to eval, setup for testing.")
agent.model.eval()

test_timestamp = train_timestamp #time.strftime("%Y%m%d_%H%M%S")

with torch.no_grad():
    for test in range(num_tests):
        episode_count = 0
        num_test_episodes = episodes_per_test[test]

        episodes = {}
        state = env.reset()

        while episode_count < num_test_episodes:

            done = False
            episode = {}

            poses_x, poses_y, poses_z     = [], [], []
            states    = [state]
            dists     = []
            values    = []
            actions   = []
            rewards   = []
            log_probs = []
            traj      = []
            mesh_dists = []

            while not done:
                action = 0
                #states.append(state)

                state = torch.FloatTensor(state).to(device)
                dist, value = agent.model(state)  

                action = dist.sample()
                log.info("action type: {}".format(action))
                #log_prob = dist.log_prob(action)

                next_state, reward, done, info = env.step(action.cpu().numpy())

                #log.warn("Step REWARD: {} DONE: {}".format(reward, done))
                #log.warn("Distance to mesh: {}".format(info['Mesh_dists']))

                poses_x.append(info['Pose'][0])
                poses_y.append(info['Pose'][1])
                poses_z.append(info['Pose'][2])
                #poses = np.concatenate((poses,info['Pose'].np), axis=1)
                #dists.append(dist)
                #values.append(value.cpu().numpy())
                actions.append(action.cpu().numpy())
                #log_probs.append(log_prob.cpu().numpy())
                rewards.append(reward)
                mesh_dists.append(info['Mesh_dists'])

                # next state logic
                if done:
                    if info['Success']:
                        successful_episodes += 1
                        tot_successful_episodes += 1
                    traj = info['Trajectory']
                    log.warn(info)
                    state = env.reset()
                    episode_count += 1
                else:
                    state = next_state

            #episode['poses']    = poses
            #episode['states']   = states
            #episode['dists']    = dists
            #episode['values']   = values
            episode['actions']  = actions
            episode['rewards']  = rewards
            #episode['log_probs'] = log_probs
            episode['trajectory']= traj
            episode['mesh_dists'] = mesh_dists

            key = 'episode_{}'.format(episode_count)
            episodes[key] = episode

            log.warn("Successes out of {}: {}".format(episode_count, successful_episodes))
            log.warn("Timestamp: {}".format(train_timestamp))
            plot_trajectory(poses_x, poses_y, poses_z, test, episode_count, info, train_timestamp)
        filename = test_timestamp + str(test) +'_'+ str(num_test_episodes)+'-' +str(successful_episodes)
        log.warn("Successes out of {}: {}".format(num_test_episodes, successful_episodes))
        log.warn("Timestamp: {}".format(train_timestamp))
        log.warn("About to save the test data.")
        file = save_obj(episodes, filename, train_timestamp)
        del episodes
        # print(load_obj(file))
        successful_episodes = 0


log.warn("Total Successes out of {}: {}".format(episodes_per_test[0:test].sum(), tot_successful_episodes))

log.warn("Done Testing.")

env.close()

sys.exit('Training and testing completed.')
