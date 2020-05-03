dataset_path = $1

for i in 0 1 2 3 4 5 6 7 8 9
do
    python extract_synchronized_video_and_game_state.py \
        -p $dataset_path/participant_${i} \
        -o data/participant_${i};

    python extract_synchronized_bvp_amplitude.py \
        -p $dataset_path/participant_${i} \
        -o data/participant_${i}/participant_${i}_sensor;

    python average_bvp_by_second.py \
        -p $dataset_path/participant_${i} \
        -o data/participant_${i}/participant_${i}_sensor;

    python ./src/calculate_mean_response.py \
        -i $dataset_path/participant_${i}_sensor/BVP_AMP_AVG.csv \
        -o results/participant_${i}/mean_response_bvp.txt;

    python ./src/train.py \
        -s BVP_AMP_AVG.csv \
        -p $dataset_path/participant_${i} \
        -o results/participant_${i}/results_cnn;
done

python ./src/train.py \
        -s BVP_AMP_AVG.csv \
    -i  $dataset_path/participant_0 \
        $dataset_path/participant_1 \
        $dataset_path/participant_2 \
        $dataset_path/participant_3 \
        $dataset_path/participant_4 \
        $dataset_path/participant_5 \
        $dataset_path/participant_6 \
        $dataset_path/participant_7 \
        $dataset_path/participant_8 \
        $dataset_path/participant_9 \
    -o  results/all/results_cnn;

python ./src/calculate_mean_response.py \
    -i  $dataset_path/participant_0/participant_0_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_1/participant_1_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_2/participant_2_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_3/participant_3_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_4/participant_4_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_5/participant_5_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_6/participant_6_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_7/participant_7_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_8/participant_8_sensor/BVP_AMP_AVG.csv \
        $dataset_path/participant_9/participant_9_sensor/BVP_AMP_AVG.csv \
    -o  results/all/mean_response_bvp.txt;