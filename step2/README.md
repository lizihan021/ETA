1. generate road network from map matching results

   ```
   python create_table_step1_ways.py
   ```

   This script assumes map matching results are stored in `DB_NAME/TABLE_NAME`, and user tom has privilege to the table. If not, grant tom privilege by

   ```
   sudo -i -u postgres
   psql
   \c DB_NAME
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tom;
   ```

   The script also assumes the new empty table has been created. If not, create the table by:

   ```
   sudo -i -u postgres
   psql
   \c DB_NAME
   CREATE NEW_TABLE_NAME(
       gid 		bigint,
       source 		bigint,
       target 		bigint,
       osm_id     	bigint,
       source_osm 	bigint,
       target_osm 	bigint,
   );
   ```

2. Conduct random walks

   ```
   python random_walk.py walk_num step_num_in_one_walk [uri] [table_name]
   ```

   Check comments on the top of `random_walk.py` to learn about meaning and default values of input arguments.

   Results will be stored in directory `/random_walk_results_[walk_num]_[step_num_in_one_walk]`

3. (Optional) Show random walk results on the front end

   ```
   python show_rw_res.py path_to_random_walk_result_file
   ```

   Check comments on the top of `random_walk.py` to learn about how to adjust parameters on the top, as well as where results are stored

4. Generate Xs and Ys for CNN training

   ```
   python gen_matrix.py x_rn x_cn y_len time_itv q_rate rw_wn rw_sn uri table_name
   ```

   Again check the comments

