import os
import csv
import json
import glob
import argparse

from scipy.signal import find_peaks

argument_parser = argparse.ArgumentParser(description="A script is used to extract the BVP amplitudes from the BVP.csv filw")

argument_parser.add_argument("-d", "--dataset-path", type=str, default=None)
argument_parser.add_argument("-p", "--participant-path", type=str, default=None)

def process_bvp_signal(signal_path, session_path, output_file_path):

    session_name = os.path.splitext(os.path.basename(session_path))[0]
    
    with open(session_path) as json_file:
        session = json.load(json_file)

    session_start = session["start_time"]
    session_stop = session["stop_time"]

    bvp_values = []

    with open(signal_path, newline="") as f:
        bvp_values = [ row[ 0 ] for row in csv.reader(f) ]

    e4_start = float(bvp_values[ 0 ])
    samples_per_second = bvp_values[ 1 ]

    x = []
    y = []

    timestep = 1 / 64

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
        if i % 1 == 0 and i < len(bvp_values) - 2:
            y.append(float(bvp_values[ i ]))
            x.append(0 + timestep * (i - j))

    max_y = max(y)
    min_y = min(y)
    
    range_y = max_y - min_y

    normalized_y = []

    for i in range(len(y)):
        if y[ i ] < min_y:
            normalized_y.append(-1)
        else:
            norm_val = y[ i ] / max_y
            normalized_y.append(norm_val)

    normalized_y_positive = []

    for i in range(len(normalized_y)):
        if normalized_y[ i ] > 0 :
            normalized_y_positive.append(normalized_y[ i ])
        else:
            normalized_y_positive.append(0)

    peaks, _ = find_peaks(normalized_y, distance=40)

    single_peak_values = []
    single_peak_values_with_min = []

    cur_val = 0.5
    start = 0

    for i in range(len(normalized_y)):

        if i in peaks:

            new_val = normalized_y[ i ]

            if new_val > 0.1:
                cur_val = new_val
                
            for j in range(start, i + 1):
                single_peak_values_with_min.append(cur_val)

            start = i + 1
            
        if i == len(normalized_y) - 1:
            for j in range(start, i + 1):
                single_peak_values_with_min.append(cur_val)

    with open(output_file_path, "w") as f:
        for value in single_peak_values_with_min:
            f.write("%s\n" % value)

if __name__ == "__main__":

    args = argument_parser.parse_args()

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

        print("Extracting BVP amplitudes for participant %s..." % participant_id)

        bvp_path = os.path.join(participant_path, "participant_%s_sensor_source" % participant_id, "BVP.csv")

        if not os.path.exists(bvp_path):
            print("Skipped %s..." % participant_path)
            continue

        session_path = os.path.join(participant_path, "participant_%s_video_info.json" % participant_id)
        output_file_path = os.path.join(participant_path, "participant_%s_sensor" % participant_id, "BVP_AMP.csv")

        process_bvp_signal(bvp_path, session_path, output_file_path)