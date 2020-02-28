for i in 0 1 2 3 4 5 7 8 9
do
    python ./src/calculate_mean_response.py \
        -i data/participant_$i/sensor/BVP_AMP_AVG.csv \
        -o results/participant_$i/mean_response_bvp.txt;
done
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