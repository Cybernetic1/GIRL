for x in {1..100}
do
    python3 genetic-programming.py
    if [ $? != 0 ]
    then
        beep -f 900 -l 1000
        break
    fi
done
