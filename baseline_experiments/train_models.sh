dataset_path=$1

for i in 0 1 2 3 4 5 6 7 8 9
do
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