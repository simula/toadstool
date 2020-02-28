import json
import time
import glob
import cv2
import os
import argparse

import gym
import gym_super_mario_bros

argument_parser = argparse.ArgumentParser(description="A script used to extract synchronized video and game session frames.")

argument_parser.add_argument("-d", "--dataset-path", type=str, default=None)
argument_parser.add_argument("-p", "--participant-path", type=str, default=None)

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

def replay_game_from_session(session_filepath, video_filepath, video_info_filepath, output_path):

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(video_info_filepath) as f:
        video_info = json.load(f)

    with open(session_filepath) as json_file:
        data = json.load(json_file)

    cap = None

    if os.path.exists(video_filepath):
        cap = cv2.VideoCapture(video_filepath)
    else:
        print("Video file does not exist!")

    first_world = "SuperMarioBros-1-1-v0"
    env = gym_super_mario_bros.make(first_world)

    next_state = env.reset()

    world = 1
    stage = 1
    stage_num = 0

    video_frame_length = 1 / 30

    video_start = video_info["start_time"]
    video_stop = video_info["stop_time"]
    game_start = data["start_time"]
    game_stop = data["stop_time"]

    print("Frame: %s" % str(video_frame_length))
    print("VT: %s" % str(video_stop - video_start))
    print("GT: %s" % str(game_stop - game_start))
    print("VS: %s" % str(video_start))
    print("GS: %s" % str(game_start))

    if cap is not None:

        skipped_frames = 0

        while video_start < game_start:
            ret, frame = cap.read()
            video_start += video_frame_length
            skipped_frames += 1

        print("Skipped: %s" % str(skipped_frames))
        print("VS: %s" % str(video_start))
        print("GS: %s" % str(game_start))

    states = []

    is_first = True
    frame_number = 1

    steps = 0

    for action in data["obs"]:
        
        next_state, reward, done, info = env.step(action)
        steps += 1

        if is_first:
            is_first = False
        else:
            
            if cap is not None:
                ret, frame = cap.read()
                cv2.imwrite(os.path.join(output_path, "face_%s.png" % frame_number), frame)

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

    dataset_path = args.dataset_path
    participant_path = args.participant_path

    if dataset_path is None and participant_path is None:
        raise Exception("Please provide either the dataset path or a participant!")

    if participant_path is not None:
        if participant_path[-1] == "/":
            participant_path = participant_path[:-1]
        participants = [ participant_path ]
    else:
        participants = list(glob.glob(os.path.join(dataset_path, "participants", "*")))

    for participant_path in participants:

        participant_id = os.path.basename(participant_path).split("_")[ -1 ]

        print("Extracting frames for participant %s..." % participant_id)

        action_path = os.path.join(participant_path, "participant_%s_session.json" % participant_id)
        video_path = os.path.join(participant_path, "participant_%s_video.avi" % participant_id)
        video_info_path = os.path.join(participant_path, "participant_%s_video_info.json" % participant_id)

        output_path = os.path.join(participant_path, "participant_%s_frames" % participant_id)

        replay_game_from_session(action_path, video_path, video_info_path, output_path)