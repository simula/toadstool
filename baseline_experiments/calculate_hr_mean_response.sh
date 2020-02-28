for i in 0 1 2 3 4 5 7 8 9
do
    python ./src/calculate_mean_response.py \
        -i data/participant_$i/sensor/HR.csv \
        -o results/participant_$i/mean_response_hr.txt;
done

python ./src/calculate_mean_response.py \
    -i  data/participant_0/sensor/HR.csv \
        data/participant_1/sensor/HR.csv \
        data/participant_2/sensor/HR.csv \
        data/participant_3/sensor/HR.csv \
        data/participant_4/sensor/HR.csv \
        data/participant_5/sensor/HR.csv \
        data/participant_6/sensor/HR.csv \
        data/participant_7/sensor/HR.csv \
        data/participant_8/sensor/HR.csv \
        data/participant_9/sensor/HR.csv \
    -o  results/all/mean_response_hr.txt;