for i in 0 1 2 3 4 5 6 7 8 9
do
    python extract_synchronized_video_and_game_state.py.py.py \
        -p $1/participant_$i \
        -o data/participant_$i;

    python extract_synchronized_bvp_amplitude.py \
        -p $1/participant_$i \
        -o data/participant_$i/sensor;

    python average_bvp_by_second.py \
        -p $1/participant_$i \
        -o data/participant_$i/sensor;

    python ./src/calculate_mean_response.py \
        -i data/participant_$i/sensor/BVP_AMP_AVG.csv \
        -o results/participant_$i/mean_response_bvp.txt;

    python ./src/train.py \
        -s BVP_AMP_AVG.csv \
        -p participant_$i \
        -o results/participant_$i/results_cnn;
done

python ./src/train.py \
        -s BVP_AMP_AVG.csv \
    -i  data/participant_0 \
        data/participant_1 \
        data/participant_2 \
        data/participant_3 \
        data/participant_4 \
        data/participant_5 \
        data/participant_6 \
        data/participant_7 \
        data/participant_8 \
        data/participant_9 \
    -o  results/all/all_results_cnn;

python ./src/calculate_mean_response.py \
    -i  data/participant_0/sensor/BVP_AMP_AVG.csv \
        data/participant_1/sensor/BVP_AMP_AVG.csv \
        data/participant_2/sensor/BVP_AMP_AVG.csv \
        data/participant_3/sensor/BVP_AMP_AVG.csv \
        data/participant_4/sensor/BVP_AMP_AVG.csv \
        data/participant_5/sensor/BVP_AMP_AVG.csv \
        data/participant_6/sensor/BVP_AMP_AVG.csv \
        data/participant_7/sensor/BVP_AMP_AVG.csv \
        data/participant_8/sensor/BVP_AMP_AVG.csv \
        data/participant_9/sensor/BVP_AMP_AVG.csv \
    -o  results/all/mean_response_bvp.txt;