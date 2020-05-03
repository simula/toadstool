import json
import time
import glob
import cv2
import os
import argparse

import gym
import gym_super_mario_bros

argument_parser = argparse.ArgumentParser(description="")

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

def synchronize_game_with_face_data(action_filepath, video_filepath, video_info_filepath, gap_path, output_dir):

    stage_order_len = len(_STAGE_ORDER)

    with open(video_info_filepath) as json_file:
        video_info =  json.load(json_file)

    cap = cv2.VideoCapture(video_filepath)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(action_filepath) as json_file:
        data = json.load(json_file)

    first_world = 'SuperMarioBros-1-1-v0'
    env = gym_super_mario_bros.make(first_world)

    next_state = env.reset()
    start = time.time()

    world = 1
    stage = 1
    stage_num = 0

    video_frame_length = 1 / 30
    video_start = video_info['start_time']
    video_stop = video_info['stop_time']
    game_start = data['start_time']
    game_stop = data['stop_time']

    video_time = video_stop - video_start
    game_time = game_stop - game_start

    print('Frame: ' + str(video_frame_length))
    print('VT:' + str(video_time))
    print('GT:' + str(game_time))
    print('VS:' + str(video_start))
    print('GS:' + str(game_start))

    skipped_frames = 0
    
    while video_start < game_start:
        ret, frame = cap.read()
        video_start += video_frame_length
        skipped_frames += 1
    
    print('Skipped: ' + str(skipped_frames))
    print('VS:' + str(video_start))
    print('GS:' + str(game_start))

    is_first = True
    no = 0
    finish = False

    steps = 0

    total_steps = 0
    gap_indices = []

    counter = 1

    for action in data['obs']:
        
        # env.render()
        
        next_state, reward, done, info = env.step(action)
        steps += 1
        total_steps += 1

        #Capture 1 game-frames for each video-frame by skipping every 2nd frame
        cvt_state = cv2.cvtColor(next_state, cv2.COLOR_BGR2RGB)
        if is_first:
            is_first = False
        else:
            # cv2.imwrite(os.path.join(output_dir, "game_" + str(no) + ".png"), cvt_state)
            is_first = True
            no += 1
            counter += 1
        
        if info['flag_get']:
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
                gap_indices.append(total_steps)

            next_state = env.reset()
        
    #Extract video
    n_gaps = len(gap_indices)

    n_actions = len(data['obs'])
    missing = 126000 - n_actions
    video_frames_to_skip = missing/2
    avg_gap_len = int(video_frames_to_skip / n_gaps)
    extra = video_frames_to_skip % n_gaps

    skips = 0
    counter = 1

    first = True
    print('Extracting video')
    for i in range(n_actions):    
        if first:
            first = False
            i += 1
        else:
            first = True
            ret, frame = cap.read()
            if not ret:
                break
            # cv2.imwrite(os.path.join(output_dir, "face_" + str(counter - 1) + ".png"), frame)
            i += 1
            counter += 1
        if i in gap_indices:
            skips += 1
            for j in range(int(avg_gap_len)):
                ret, frame = cap.read()
            if extra > 0:
                ret, frame = cap.read()
                extra -= 1
        i += 1

    print('Saving gap_info')
    gap_info = {}
    gap_info['indices'] = gap_indices
    gap_info['missing'] = missing

    print('Saving gaps to file')
    with open(gap_path, 'w') as outfile:
        json.dump(gap_info, outfile)

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

        session_path = os.path.join(participant_path, "participant_%s_session.json" % participant_id)
        video_path = os.path.join(participant_path, "participant_%s_video.avi" % participant_id)
        video_info_path = os.path.join(participant_path, "participant_%s_video_info.json" % participant_id)
        gap_path = os.path.join(participant_path, "participant_%s_gap_info.json" % participant_id)

        synchronize_game_with_face_data(session_path, video_path, video_info_path, gap_path, participant_path)