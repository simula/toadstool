for i in 0 1 2 3 4 5 6 7 8 9
do
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