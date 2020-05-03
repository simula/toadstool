
dataset_path=$1

python synchronize_game_with_face_data.py \
    -d $dataset_path;

python synchronize_game_with_sensor_data.py \
    -d $dataset_path;