import psycopg2

if __name__ == '__main__':
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    stmt = ''' SELECT CONCAT(
                    'INSERT INTO ', t.table_name, ' (osm_id, source_id, target_id, predict_speed) ',
                    'SELECT -1,-1,-1, avg(predict_speed*3.6/maxspeed_forward) FROM ways AS w JOIN ',
                    t.table_name, ' AS t ON w.osm_id = t.osm_id AND ',
                    '((w.source_osm = t.source_id AND w.target_osm = t.target_id) OR ',
                    '(w.source_osm = t.target_id AND w.target_osm = t.source_id)) ;'
                ) AS stmt
                FROM information_schema.tables t
                WHERE t.table_schema = 'public'
                AND t.table_name LIKE 'time%'            
                ORDER BY t.table_name; '''
    cur = conn.cursor()
    cur.execute(stmt)
    for i, line in enumerate(cur):
        if i%100 == 9:
            print "processed {} time table".format(i + 1)
        #print line
        #exit(0)
        cur = conn.cursor()
        cur.execute(line[0])
        conn.commit()
    conn.close()