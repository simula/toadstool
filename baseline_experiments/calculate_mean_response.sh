for i in 0 1 2 3 4 5 6 7 8 9
do
    python ./src/calculate_mean_response.py \
        -i $dataset_path/participant_${i}_sensor/BVP_AMP_AVG.csv \
        -o results/participant_${i}/mean_response_bvp.txt;
done

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