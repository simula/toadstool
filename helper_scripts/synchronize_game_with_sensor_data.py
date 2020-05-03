import os
import csv
import json
import glob
import argparse

argument_parser = argparse.ArgumentParser(description="A script used to match the sensor data to the game session")

argument_parser.add_argument("-d", "--dataset-path", type=str, default=None)
argument_parser.add_argument("-p", "--participant-path", type=str, default=None)

def synchronize_game_with_sensor_data(signal_path, session_path, output_file_path):

    with open(session_path) as json_file:
        session = json.load(json_file)

    session_start = session['start_time']
    session_stop = session['stop_time']
    timestep = 1 / 60

    ibi = []

    with open(signal_path, newline='') as csvfile:
        rd = csv.reader(csvfile)
        for row in rd:
            ibi.append(row)

    ibi_start = float(ibi[0][0])
    ibi_time = ibi_start
    pruned_ibi = []

    i = 0

    while ibi_time < session_start:
        i +=1
        ibi_time = ibi_start + float(ibi[i][0])

    skipped_time = float(ibi[i][0]) - float(ibi[i][1])


    pruned_ibi.append([ibi_time - float(ibi[i][1]), 'IBI'])

    while ibi_time < session_stop and i < len(ibi):
        pruned_ibi.append([float(ibi[i][0])-skipped_time, ibi[i][1]])
        i += 1

    with open(output_file_path, 'w') as f:
        for line in pruned_ibi:
            f.write("%s," % line[0])
            f.write("%s\n" % line[1])

def match_sensor_data_to_game_session(signal_path, session_path, gap_path, output_file_path):
    
    e4 = []

    with open(session_path) as json_file:
        session = json.load(json_file)

    with open(signal_path, newline='') as csvfile:
        rd = csv.reader(csvfile)
        for row in rd:
            e4.append(row)

    with open(gap_path) as json_file:
        gap_info = json.load(json_file)

    e4_type = os.path.basename(os.path.splitext(signal_path)[0])

    e4_pr_sec = float(e4[1][0])
    e4_start = float(e4[0][0])

    session_start = session['start_time']
    session_stop = session['stop_time']

    n_frames = len(session['obs'])
    missing = gap_info['missing']
    gap_indices = gap_info['indices']
    n_gaps = len(gap_indices)
    avg_gap = int(missing/n_gaps)
    extra = missing % n_gaps
    frame_pr_sek = 60
    
    timestep = 1 / e4_pr_sec
    j = 2

    while e4_start < session_start-timestep/2:
        e4_start += timestep
        j +=1

    k = j
    e4_end = e4_start

    while e4_end < session_stop-timestep/2:
        e4_end += timestep
        k +=1

    synched_e4 = []
    for i in range(j,k):
        synched_e4.append(e4[i])
        
    if e4_type == "BVP" or e4_type == "ACC":
        pruned_e4 = []
        for i in range(len(synched_e4)):
            if i % 16 != 0:
                pruned_e4.append(synched_e4[i])
        synched_e4 = pruned_e4
        e4_pr_sec = 60
        if e4_type == "ACC":
            e4_pr_sec = 30

    frames_pr_e4 = int(frame_pr_sek / e4_pr_sec)
    transformed_e4 = []
    times = []

    for i in range(j,k):
        for l in range(frames_pr_e4):
            transformed_e4.append(e4[i])
            times.append(0 + (1/60)*(i-j))

    matching_e4 = []
    n = 0
    for i in range(n_frames):
        matching_e4.append(transformed_e4[n])

        if i in gap_indices:
            n += avg_gap
            if extra > 0:
                n += 1
                extra -= 1

        i += 1
        n += 1

    with open(output_file_path, "w") as f:
        for value in matching_e4:
            f.write("%s\n" % " ".join(value))

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

    sensor_file_names = [
        "ACC.csv",
        "BVP.csv",
        "EDA.csv",
        "HR.csv",
        "TEMP.csv",
        "IBI.csv"
    ]

    for participant_path in participants:

        for sensor_file in sensor_file_names:

            participant_id = os.path.basename(participant_path).split("_")[ -1 ]

            sensor_path = os.path.join(participant_path, "participant_%s_sensor_raw" % participant_id, sensor_file)

            if not os.path.exists(sensor_path):
                print("Skipped %s..." % participant_path)
                continue

            session_path = os.path.join(participant_path, "participant_%s_session.json" % participant_id)
            gap_path = os.path.join(participant_path, "participant_%s_gap_info.json" % participant_id)
            output_file_path = os.path.join(participant_path, "participant_%s_sensor" % participant_id, sensor_file)

            if sensor_file == "IBI.csv":
                synchronize_game_with_sensor_data(sensor_path, session_path, output_file_path)
            else:
                match_sensor_data_to_game_session(sensor_path, session_path, gap_path, output_file_path)