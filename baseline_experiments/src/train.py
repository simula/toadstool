import os
import pickle
import argparse
import math

from tensorflow.keras.optimizers import Adam

from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model

from models import build_resnet50
from utils import load_data

argument_parser = argparse.ArgumentParser(description="")

argument_parser.add_argument("-p", "--participant-paths", nargs="+", required=True)
argument_parser.add_argument("-s", "--signal-file-name", type=str, required=True)
argument_parser.add_argument("-o", "--output-dir", type=str, required=True)

def train_model(x_path, y_path, output_path):

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for fold_index, (train_generator, test_generator) in enumerate(load_data(x_path, y_path)):
        
        model_save_path = os.path.join(output_path, "model_%i.h5" % fold_index)
        history_path = os.path.join(output_path, "history_%i.pkl" % fold_index)
        metrics_log = os.path.join(output_path, "metrics_%i.txt" % fold_index)

        model = build_resnet50((224, 224, 3))

        callbacks = [
            EarlyStopping(monitor="val_loss", patience=10),
            ModelCheckpoint(model_save_path, monitor="val_loss"),
        ]
    
        model.compile(
            loss="mean_squared_error",
            optimizer=Adam(lr=0.001),
            metrics=[ "mse", "mae" ]
        )

        history = model.fit_generator(
            epochs=1000,
            generator=train_generator,
            callbacks=callbacks,
            validation_data=test_generator
        )
        
        model = load_model(model_save_path)

        evaluation = model.evaluate_generator(test_generator)

        mse = str(evaluation[1])
        mae = str(evaluation[2])

        with open(history_path, "wb") as f:
            pickle.dump(history.history, f)

        with open(metrics_log, "w") as f:
            f.write("Mean Squared Error: %s\n" % mse)
            f.write("Mean Absolute Error: %s\n" % mae)

if __name__ == "__main__":

    args = argument_parser.parse_args()

    participant_paths = args.participant_paths
    signal_file_name = args.signal_file_name
    output_dir = args.output_dir

    x_path = [ os.path.join(participant, "frames") for participant in participant_paths ]
    y_path = [ os.path.join(participant, "sensor", signal_file_name) for participant in participant_paths ]

    train_model(
        x_path=x_path,
        y_path=y_path,
        output_path=output_dir
    )