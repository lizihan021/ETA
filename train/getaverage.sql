SELECT CONCAT(
	'INSERT INTO ', t.table_name, ' (osm_id, source_id, target_id, predict_speed) ',
	'SELECT -1,-1,-1, avg(predict_speed*3.6/maxspeed_forward) FROM ways AS w JOIN ',
	t.table_name, ' AS t ON w.osm_id = t.osm_id AND ',
	'((w.source_osm = t.source_id AND w.target_osm = t.target_id) OR ',
	'(w.source_osm = t.target_id AND w.target_osm = t.source_id)) ;'
) AS stmt
FROM information_schema.tables t
WHERE t.table_schema = 'public'
AND t.table_name LIKE 'time%'            
ORDER BY t.table_name;


INSERT INTO time_1480145400  (osm_id, source_id, target_id, predict_speed)
SELECT -1,-1,-1, avg(predict_speed*3.6/maxspeed_forward) 
FROM ways AS w JOIN time_1480145400  AS t ON w.osm_id = t.osm_id AND 
((w.source_osm = t.source_id AND w.target_osm = t.target_id) OR 
(w.source_osm = t.target_id AND w.target_osm = t.source_id));

GROUP BY w.osm_id, w.source_osm, w.target_osm ;


select table_name, pg_relation_size(quote_ident(table_name))
from information_schema.tables
where table_schema = 'public'
order by 2 desc;