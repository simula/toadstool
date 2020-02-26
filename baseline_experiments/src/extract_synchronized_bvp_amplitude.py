import os
import csv
import json
import glob
import argparse

from scipy.signal import find_peaks

argument_parser = argparse.ArgumentParser(description="A script is used to extract the BVP amplitudes from the BVP.csv filw")

argument_parser.add_argument("-d", "--dataset-path", type=str, default=None)
argument_parser.add_argument("-p", "--participant-path", type=str, default=None)

def normalize_bvp(x, y):

    max_y = max(y)
    min_y = min(y)

    #Normalize positive and negative values relative to 0    
    normalized_y = []
    for i in range(len(y)):
        if y[i] < 0:
            norm_val = y[i] / (min_y*-1)
            normalized_y.append(norm_val)
        else:
            norm_val = y[i] / max_y
            normalized_y.append(norm_val)

    #Extract only positive
    normalized_y_positive = []
    for i in range(0, len(normalized_y)):
        if normalized_y[i] >= 0 :
            normalized_y_positive.append(normalized_y[i])
        else:
            normalized_y_positive.append(0)

    peaks, _ = find_peaks(normalized_y, distance=40)

    single_peak_values = []
    single_peak_values_with_min = []
    cur_val = 0.5
    start = 0

    for i in range(0, len(normalized_y)):
        if i in peaks:
            for j in range(start, i+1):
                cur_val  = normalized_y[i]
                single_peak_values.append(normalized_y[i])     
            start = i+1

        if i == len(normalized_y)-1:
            for j in range(start, i+1):
                single_peak_values.append(cur_val)
            
    cur_val = 0.1
    start = 0
    for i in range(0, len(normalized_y)):
        if i in peaks:
            new_val = normalized_y[i]
            if new_val >= 0.1:
                cur_val = new_val
                
            for j in range(start, i+1):
                single_peak_values_with_min.append(cur_val)
            start = i+1
            
        if i == len(normalized_y)-1:
            for j in range(start, i+1):
                single_peak_values_with_min.append(cur_val)

    return single_peak_values_with_min

def synch_bvp(bvp_path, session_path, gap_path, output_file_path, halve=False, normalize=False):
    
    bvp = []

    with open(bvp_path, newline='') as csvfile:
        rd = csv.reader(csvfile)
        for row in rd:
            bvp.append(row[0])

    with open(session_path) as json_file:
        session = json.load(json_file)

    with open(gap_path) as json_file:
        gap_info = json.load(json_file)

    e4_start = float(bvp[0])
    samples_pr_sec = bvp[1]

    session_start = session['start_time']
    session_stop = session['stop_time']

    timestep = 1 / 64
    j = 2

    while e4_start < session_start-timestep/2:
        e4_start += timestep
        j +=1

    k = j
    e4_end = e4_start

    while e4_end < session_stop-timestep/2:
        e4_end += timestep
        k +=1

    synched_bvp = []
    times = []

    for i in range(j,k):
        synched_bvp.append(float(bvp[i]))
        times.append(0 + timestep*(i-j))

    if normalize:
        print("Normalizing values")
        synched_bvp = normalize_bvp(times, synched_bvp)
        
    frames = len(session['obs'])

    # Prune bvp to match 60 fps
    pruned_bvp = []
    for i in range(len(synched_bvp)):
        if i % 16 != 0:
            pruned_bvp.append(synched_bvp[i])

    #Skipping gaps to deal with issue of inconsistent number of observations/frames in session
    missing = gap_info['missing']
    gap_indices = gap_info['indices']
    n_gaps = len(gap_indices)

    avg_gap_len = int(missing / n_gaps)
    extra = missing % n_gaps

    print('Matching bvp datapoints with game frames')
    i = 0
    j = 0

    matching_bvp = []
    for i in range(frames):
        matching_bvp.append(pruned_bvp[j])
        if i in gap_indices:      
            j += int(avg_gap_len)
            if extra > 0:
                j += 1
                extra -= 1
        i += 1
        j += 1

    # Remove every 2. datapoint to match current number of frames
    halved_bvp = []
    if halve:
        for i in range(len(matching_bvp)):
            if i % 2 != 0:
                halved_bvp.append(matching_bvp[i])

        matching_bvp = halved_bvp

    with open(output_file_path, "w") as f:
        for value in matching_bvp:
            f.write("%s\n" % value)

if __name__ == "__main__":

    args = argument_parser.parse_args()

    participant_path = args.participant_path
    dataset_path = args.dataset_path

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

        bvp_path = os.path.join(participant_path, "participant_%s_sensor_raw" % participant_id, "BVP.csv")

        if not os.path.exists(bvp_path):
            print("Skipped %s..." % participant_path)
            continue

        session_path = os.path.join(participant_path, "participant_%s_session.json" % participant_id)
        gap_path = os.path.join(participant_path, "participant_%s_gap_info.json" % participant_id)
        output_file_path = os.path.join(participant_path, "participant_%s_sensor" % participant_id, "BVP_AMP.csv")

        synch_bvp(bvp_path, session_path, gap_path, output_file_path, True, True)