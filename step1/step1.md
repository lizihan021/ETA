##Map range: 

104-104.2

30.6-30.8

##All the project that I searched

#### 1.

Mapbox route matching for **front end**

<https://github.com/mapbox/mapbox-match.js>

#### 2.

<https://github.com/simonscheider/mapmatching>

Cons: the software requires .shp file. Not sure whether there are loss if we convert .osm to .shp.

#### 3. 
This is simple, requires PSQL 

<https://github.com/mapillary/map_matching> 

<https://github.com/pgRouting/osm2pgrouting> 

How to create a user in PSQL data base:
```
CREATE USER tom WITH PASSWORD 'myPassword';
CREATE DATABASE jerry;
GRANT ALL PRIVILEGES ON DATABASE jerry to tom;
```
Change user to connect to database:

`sudo -i -u postgres`

Some of the dependences (not all) please follow the instruction in the two repos
```
sudo apt-get install postgresql
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgis
sudo apt-get install expat
sudo apt install libpqxx-dev
sudo apt-get install postgresql-10-pgrouting
```
Useless (don’t use this) (just for reference)

`osm2pgsql --create --database gis -C 6000 china-latest.osm.pbf`

##### If you try to test the system with data of the country Andorra:

**Step 1:**

Follow instructions in <https://github.com/pgRouting/osm2pgrouting> and:

`osm2pgrouting --f andorra-latest.osm --conf mapconfig.xml --dbname routing --username tom --password myPassword --clean`

**Step 2:**

Follow instructions in <https://github.com/mapillary/map_matching> and:

`python ./examples/map_matcher.py "host=localhost port=5432 dbname=routing user=tom password=myPassword" ways < path_psql.json`

**Results:**


```
zihanli@ubuntu:~/Desktop/450/map_matching$ python ./examples/map_matcher.py "host=localhost port=5432 dbname=routing user=tom password=myPassword" ways < a.txt

/home/zihanli/.local/lib/python2.7/site-packages/psycopg2/__init__.py:144: UserWarning: The psycopg2 wheel package will be renamed from release 2.8; in order to keep installing from binary please use "pip install psycopg2-binary" instead. For details see: <http://initd.org/psycopg/docs/install.html#binary-install-from-pypi>.

  """)

         Measurement ID: 0
             Coordinate: 1.512735 42.500891
    Matche d coordinate: 1.512735 42.500891
        Matched edge ID: 3379
Location along the edge: 0.80
               Distance: 0.00 meters

         Measurement ID: 1
             Coordinate: 1.513547 42.501933
    Matche d coordinate: 1.513547 42.501933
        Matched edge ID: 4386
Location along the edge: 0.71
               Distance: 0.00 meters

         Measurement ID: 2
             Coordinate: 1.499084 42.494258
    Matche d coordinate: 1.499084 42.494258
        Matched edge ID: 2954
Location along the edge: 0.39
               Distance: 0.00 meters

         Measurement ID: 3
             Coordinate: 1.499586 42.494155
    Matche d coordinate: 1.499586 42.494155
        Matched edge ID: 280
Location along the edge: 0.68
               Distance: 0.00 meters

         Measurement ID: 4
             Coordinate: 1.499859 42.494123
    Matche d coordinate: 1.499859 42.494123
        Matched edge ID: 280
Location along the edge: 0.41
               Distance: 0.00 meters
               
         Measurement ID: 5
             Coordinate: 1.500262 42.494109
    Matche d coordinate: 1.500262 42.494109
        Matched edge ID: 3001
Location along the edge: 1.00
               Distance: 0.00 meters

         Measurement ID: 6
             Coordinate: 1.500521 42.494082
    Matche d coordinate: 1.500521 42.494082
        Matched edge ID: 1844
Location along the edge: 0.00
               Distance: 0.00 meters

         Measurement ID: 7
             Coordinate: 1.500461 42.494105
    Matche d coordinate: 1.500461 42.494105
        Matched edge ID: 4412
Location along the edge: 0.43
               Distance: 0.00 meters

```

#### 4.

Online GPS match api (haven’t look into that)

https://mapmatching.3scale.net

Problems that we meet
---

现在的问题在于，openstreetmap 没有重庆的地图，只有全中国的 然后这个地图有5G，根据小国家25M 地图用了200M 内存来看我们至少要50G 内存，所以我想用交大的高性能计算， 

我用的两个工具是 <https://github.com/mapillary/map_matching> 

<https://github.com/pgRouting/osm2pgrouting>

先用第二个生成一个 psql 数据库，里面有 edge 的信息，然后再用第一个，把 GPS map 到 edge 上 

所以接下来有这么几件事可以做，1.了解一下openstreetmap 的画框取地图生成的文件如何使得 osm2pgrouting works，2.如果1失败了，了解一下交大的高性能计算，然后写个小报告给马成斌问问他的意见 3. 确认一下 map_matching 用的是HMM 算法。 4. 这个工具似乎只把 gps map 到了 edge 上，我们怎么根据这个拿到这辆车经过了那些 edge？

复现成功！
---

1. Put on your vpn

```
git clone git@github.com:lizihan021/ETA.git

sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt-get update
#sudo apt-get install postgis
sudo apt-get install libboost-all-dev
sudo apt-get install expat
sudo apt-get install libexpat1-dev
sudo apt-get install libboost-dev
sudo apt-get install libboost-program-options-dev
sudo apt install libpqxx-dev
wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-10-pgrouting
sudo apt-get install postgresql-10 postgresql-server-dev-10
sudo apt-get install postgresql-9.6-pgrouting
sudo apt-get install postgresql-9.5-pgrouting

git clone https://github.com/pgRouting/osm2pgrouting
cd osm2pgrouting/
cmake -H. -Bbuild
cd build/
make
sudo make install

## here you will be as user postgres
sudo -i -u postgres
createdb routing
psql --dbname routing -c 'CREATE EXTENSION postgis'
psql --dbname routing -c 'CREATE EXTENSION pgRouting'
## make sure there is no error on the above two command.

psql
CREATE USER tom WITH PASSWORD 'myPassword';
\q

## you need to 'su' back to your origin user
## example: su ubuntu-user

cd ETA
cd step1
osm2pgrouting --f andorra-latest.osm --conf mapconfig.xml --dbname routing --username tom --password myPassword --clean

cd map_matching/
sudo python setup.py install
python ./examples/map_matcher.py "host=localhost port=5432 dbname=routing user=tom password=myPassword" ways < a.txt

```



