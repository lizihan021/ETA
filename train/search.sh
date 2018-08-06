search_dir="gen_XY_results_9_9_2_15_0.75"
i=0
for entry in "$search_dir"/*
do
  i=$i+1
  echo "$i : $entry"
  /usr/local/bin/python mainnmt.py $entry
done