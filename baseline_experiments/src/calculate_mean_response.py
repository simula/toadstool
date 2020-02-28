import os
import math
import argparse

from collections import defaultdict
from sklearn import metrics

from utils import split_data_into_equal_parts
from utils import read_sensor_data

import numpy as np

argument_parser = argparse.ArgumentParser(description="")

argument_parser.add_argument("-i", "--input-paths", nargs='+', default=["/Users/steven/github/toadstool/baseline_experiments/data/participant_0/sensor/HR.csv"])
argument_parser.add_argument("-o", "--output-path", type=str, default="test.txt")

def calculate_mean_response_for_participants(sensor_data_paths, output_path, n_folds):

    split_data = defaultdict(list)

    if not os.path.exists(os.path.dirname(output_path)) and len(os.path.dirname(output_path)) != 0:
        os.makedirs(os.path.dirname(output_path))
    
    for sensor_data_path in sensor_data_paths:

        split_fold_data = split_data_into_equal_parts(
            data=read_sensor_data(sensor_data_path),
            number_of_parts=n_folds
        )

        for fold_index in range(n_folds):
            split_data[ fold_index ].extend(split_fold_data[ fold_index ])

    split_data = [np.array(data, dtype=np.float32) for data in split_data.values() ]

    calculate_mean_response(split_data, output_path, n_folds)

def calculate_mean_response(split_data, output_path, n_folds):

    metrics_file = open(output_path, "w")

    average_mse = []
    average_mae = []
    average_rmse = []

    for fold_index in range(n_folds):

        train_data = []

        for n in range(n_folds):
            if n != fold_index:
                train_data.extend(split_data[ n ])
        test_data = split_data[ fold_index ]

        metrics_file.write("Metrics for fold %s\n" % fold_index)

        y_pred = [ np.mean(train_data) for _ in range(len(test_data)) ]

        mse = metrics.mean_squared_error(test_data, y_pred)
        mae = metrics.mean_absolute_error(test_data, y_pred)
        rmse = math.sqrt(mse)

        average_mse.append(mse)
        average_mae.append(mae)
        average_rmse.append(rmse)

        metrics_file.write("Mean Squared Error: %s\n" % mse)
        metrics_file.write("Mean Absolute Error: %s\n" % mae)
        metrics_file.write("Root Mean Squared Error: %s\n\n" % rmse)

    metrics_file.write("Average across all folds\n")
    metrics_file.write("Mean Squared Error: %s\n" % np.mean(average_mse))
    metrics_file.write("Mean Absolute Error: %s\n" % np.mean(average_mae))
    metrics_file.write("Root Mean Squared Error: %s\n\n" % np.mean(average_rmse))

if __name__ == "__main__":

    args = argument_parser.parse_args()

    input_path = args.input_paths
    output_path = args.output_path

    calculate_mean_response_for_participants( input_path, output_path, 3 )