import os
import csv
import json
import glob
import argparse
import numpy as np

argument_parser = argparse.ArgumentParser(description="A script is used to extract the BVP amplitudes from the BVP.csv filw")

argument_parser.add_argument("-d", "--dataset-path", type=str, default=None)
argument_parser.add_argument("-p", "--participant-path", type=str, default=None)

def average_bvp(bvp_path, output_file_path):
    
    averages = [ ]

    with open(bvp_path, newline='') as csvfile:
        bvp = [ float(value) for value in f.readlines() ]
        for row in rd:
            bvp.append(row[0])

    bvp = np.array(bvp)
    
    for i in range(0, len(bvp), 64):
        averages.append(np.mean(bvp[ i : i + 64 ]))

    with open(output_file_path, "w") as f:
        for value in averages:
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

        bvp_path = os.path.join(participant_path, "participant_%s_sensor" % participant_id, "BVP_AMP.csv")

        if not os.path.exists(bvp_path):
            print("Skipped %s..." % participant_path)
            continue

        output_file_path = os.path.join(participant_path, "participant_%s_sensor" % participant_id, "BVP_AMP_AVG.csv")

        synch_bvp(bvp_path, output_file_path)