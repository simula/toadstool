"""A method to play gym environments using human IO inputs. This program is a modified version of the one found in the nes-py site-package"""

import gym
import gym_super_mario_bros
from pyglet import clock
from _image_viewer import ImageViewer
import numpy as np
import json
import os
import time
from random import randint

# Contains the custom stage order as well as methods for transitioning to next stage
import stages 

# the sentinel value for "No Operation"
_NOP = 0

# Play time based on frames (60fps)

#play_time = 5 #
#play_time = 300
#play_time = 60 # 1min
#play_time = 600 # 10min
play_time = 2100 # 35min

time_limit = 16000 # Time on a single stage before switching to new one


def play_human_record(callback=None):
    """
    Play the environment using keyboard as a human.

    Returns:
        None

    """
    # Start on the first world
    first_world = 'SuperMarioBros-1-1-v0'
    env = gym_super_mario_bros.make(first_world)

    observations = [] #For Storing observations
    
    # set the frame rate for pyglet
    clock.set_fps_limit(env.metadata['video.frames_per_second'])
    # ensure the observation space is a box of pixels
    assert isinstance(env.observation_space, gym.spaces.box.Box)
    # ensure the observation space is either B&W pixels or RGB Pixels
    obs_s = env.observation_space
    is_bw = len(obs_s.shape) == 2
    is_rgb = len(obs_s.shape) == 3 and obs_s.shape[2] in [1, 3]
    assert is_bw or is_rgb
    # get the mapping of keyboard keys to actions in the environment
    if hasattr(env, 'get_keys_to_action'):
        keys_to_action = env.get_keys_to_action()
    elif hasattr(env.unwrapped, 'get_keys_to_action'):
        keys_to_action = env.unwrapped.get_keys_to_action()
    else:
        raise ValueError('env has no get_keys_to_action method')
    
    # create the image viewer
    from tkinter import Tk
    root = Tk()
    
    # Determining screen size
    height = root.winfo_screenheight()
    width = int(((height/240) * 256))

    viewer = ImageViewer(
        env.spec.id if env.spec is not None else env.__class__.__name__,

        #env.observation_space.shape[0], # height
        #env.observation_space.shape[1], # width
        height,
        width,
        monitor_keyboard=True,
        relevant_keys=set(sum(map(list, keys_to_action.keys()), []))
    )
    # create a done flag for the environment
    done = False
    state = env.reset()
    viewer.show(env.unwrapped.screen)
    
    # for keeping score
    score = 0
    level_score = 1000
    death_score = -100
    cur_level_score = level_score
    min_score = 200

    # start the main game loop        
    finish = False
    start = None
    try:
        world = 1
        stage = 1
        stage_num = 0
        steps = 0
        start = time.time() # timestamp for start of game
        
        while True:
            # clock tick
            clock.tick()

            # reset if the environment is done
            if done:
                done = False
                
                if cur_level_score > min_score:
                    cur_level_score += death_score
                      
                # Go to new stage if flag/axe reached or time-limit is up 
                if finish or steps >= time_limit:
                    if finish:
                        score += cur_level_score
                    cur_level_score = level_score
                    
                    stage_num += 1
                    world, stage, new_world = stages.make_next_stage(world, stage, stage_num)
                    env.close()
                    env = gym_super_mario_bros.make(new_world)
                    finish = False
                    steps = 0

                state = env.reset()
                viewer.show(env.unwrapped.screen)
                
            # unwrap the action based on pressed relevant keys
            action = keys_to_action.get(viewer.pressed_keys, _NOP)
            next_state, reward, done, info = env.step(action)
            steps += 1

            if info['flag_get']:
                finish = True

            # Adding observation to list           
            observations.append(action)
            
            viewer.show(env.unwrapped.screen)
            # pass the observation data through the callback
            if callback is not None:
                callback(state, action, reward, done, next_state)
            state = next_state
            # shutdown if the escape key is pressed
            if viewer.is_escape_pressed:
                break
            # shutdown if playtime is up
            now = time.time() 
            if now - start > play_time:
                break
            
            
    except KeyboardInterrupt:
        pass
    
    end = time.time()
    #Storing the data
    data = {}
    data['obs'] = observations
    data['obs_n'] = len(observations)
    data['start_time'] = start
    data['stop_time'] = end
    data['score'] = score

    folder_path = './DATA/sessions/'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    
    path, dirs, files = next(os.walk(folder_path))
    file_count = len(files)

    file_path = folder_path + 'session' + str(file_count)
 
    print('Saving observations to file')
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)
    
    viewer.close()
    env.close()


play_human_record()
print('Finished play session')
