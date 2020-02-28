dataset_path=$1;
for i in 0 1 2 3 4 5 7 8 9
do
    python ./src/extract_video_and_game_state.py \
        -p $dataset_path/participant_$i \
        -o data/participant_$i/frames;
done