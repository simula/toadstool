import os
import csv
import json
import glob
import argparse

argument_parser = argparse.ArgumentParser(description="A script used to match the sensor data to the game session")

argument_parser.add_argument("-d", "--dataset-path", type=str, default=None)
argument_parser.add_argument("-p", "--participant-path", type=str, default=None)
argument_parser.add_argument("-o", "--output-path", type=str, default=None)

def match_ibi_to_game_session(signal_path, session_path, output_file_path):

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

def match_sensor_data_to_game_session(signal_path, session_path, output_file_path):

    session_name = os.path.splitext(os.path.basename(session_path))[0]

    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path))
    
    with open(session_path) as json_file:
        session = json.load(json_file)

    session_start = session["start_time"]
    session_stop = session["stop_time"]

    raw_signal_values = []

    with open(signal_path) as f:
        raw_signal_values = [ row for row in f.read().splitlines() ]

    e4_start = float(raw_signal_values[ 0 ].split(",")[0])
    samples_per_second = float(raw_signal_values[ 1 ].split(",")[0])

    matched_signal_values = []

    timestep = 1 / samples_per_second

    j = 2

    while e4_start < session_start - timestep / 2:
        e4_start += timestep
        j += 1

    k = j
    e4_end = e4_start

    while e4_end < session_stop - timestep / 2:
        e4_end += timestep
        k += 1

    for i in range(j, k):
        if i % 1 == 0 and i < len(raw_signal_values) - 2:
            matched_signal_values.append(raw_signal_values[ i ])

    with open(os.path.join(output_file_path), "w") as f:
        for value in matched_signal_values:
            f.write("%s\n" % value)

if __name__ == "__main__":

    args = argument_parser.parse_args()

    dataset_path = args.dataset_path
    participant_path = args.participant_path
    output_path = args.output_path

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

            session_path = os.path.join(participant_path, "participant_%s_video_info.json" % participant_id)
            output_file_path = os.path.join(output_path, "participant_%s_sensor" % participant_id, sensor_file)

            if sensor_file == "IBI.csv":
                match_ibi_to_game_session(sensor_path, session_path, output_file_path)
            else:
                match_sensor_data_to_game_session(sensor_path, session_path, output_file_path)