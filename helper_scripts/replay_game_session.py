import json
import time
import cv2
import os
import argparse

import gym
import gym_super_mario_bros

argument_parser = argparse.ArgumentParser(description="A script used to replay the game session.")

argument_parser.add_argument("-i", "--input-path", type=str, default=None)
argument_parser.add_argument("-o", "--output-path", type=str, default= None)
argument_parser.add_argument("-r", "--render-screen", type=bool, default=True)

_STAGE_ORDER = [
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 2),
    (1, 4),
    (3, 1),
    (4, 1),
    (2, 1),
    (2, 3),
    (2, 4),
    (3, 2),
    (3, 3),
    (3, 4),
    (4, 2)
]

def make_next_stage(world, stage, num):

    if num < len(_STAGE_ORDER):
        world = _STAGE_ORDER[num][0]
        stage = _STAGE_ORDER[num][1]

    else:
        if stage >= 4:
            stage = 1
            if world >= 8:
                world = 1
            else:
                world += 1
        else:
            stage += 1

    return world, stage, "SuperMarioBros-%s-%s-v0" % (str(world), str(stage))

def replay_game_from_actions(session_path, output_path=None, render_screen=False):

    if output_path is not None and not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(session_path) as json_file:
        data = json.load(json_file)

    first_world = "SuperMarioBros-1-1-v0"
    env = gym_super_mario_bros.make(first_world)

    next_state = env.reset()

    world = 1
    stage = 1
    stage_num = 0

    frame_number = 1

    steps = 0

    for action in data["obs"]:
        
        if render_screen:
            env.render()
        
        next_state, reward, done, info = env.step(action)
        steps += 1

        if output_path is not None:
            cvt_state = cv2.cvtColor(next_state, cv2.COLOR_BGR2RGB)
            cv2.imwrite(os.path.join(output_path, "game_%s.png" % frame_number), cvt_state)

        is_first = True
        frame_number += 1
        
        if info["flag_get"]:
            finish = True

        if done:
            done = False
            end = time.time()
            
            if finish or steps >= 16000:
                stage_num += 1
                world, stage, new_world = make_next_stage(world, stage, stage_num)
                env.close()
                env = gym_super_mario_bros.make(new_world)
                finish = False
                steps = 0

            next_state = env.reset()

if __name__ == "__main__":

    args = argument_parser.parse_args()

    input_path = args.input_path
    render_screen = args.render_screen
    output_path = args.output_path

    if input_path is None:
        raise Exception("Please provide the path to a game session!")

    replay_game_from_actions(
        session_path=input_path,
        output_path=output_path,
        render_screen=render_screen
    )