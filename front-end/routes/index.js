var express = require('express');
var router = express.Router();
var path = require('path');
var fs = require('fs');
var PythonShell = require('python-shell');

/* GET home page. */
router.get('/', function(req, res, next) {
  // res.render('index', { title: 'Express' });
  res.render('index');
  // res.sendFile(path.join(__dirname, '../views/index.html'));
});

router.post('/upload', function(req, res, next) {
  // TODO call a python function with the two points as input
  var filePath = path.join(__dirname, '../../data-process/mapmatching-data/9f2f5a3972df52464e93495dbd528c80.json');
  // TODO need to check whether the file exist.
  fs.readFile(filePath, {encoding: 'utf-8'}, function(err,data){
    if (!err) {
      //console.log('received data: ' + data);
      res.send(data);
    } else {
      console.log(err);
      res.status(404).send("Oh uh, something went wrong");
    }
  });
});

router.post('/getfakedata', function(req, res, next) {
  var filePath = path.join(__dirname, '../../data-process/mapmatching-data/9f2f5a3972df52464e93495dbd528c80_result.json');
  // TODO need to check whether the file exist.
  fs.readFile(filePath, {encoding: 'utf-8'}, function(err,data){
    if (!err) {
      //console.log('received data: ' + data);
      res.send(data);
    } else {
      console.log(err);
      res.status(404).send("Oh uh, something went wrong");
    }
  });
});

router.post('/draw', function(req, res, next) {
  var filePath = path.join(__dirname, '../../data-process/' + req.body.dir);


  fs.readdir(filePath, function(err, filenames) {
    if (!err) {
      var objs = [];
      var valid_file_count = 0;
      filenames.forEach(function(filename) {
        if (filename.split('.').pop() !== "json") {
          return;
        }
        valid_file_count = valid_file_count + 1;
      });

      filenames.forEach(function(filename) {
        var oldfilename = filename;
        if (filename.split('.').pop() !== "json") {
          return;
        }
        filename = path.join(__dirname, '../../data-process/' + req.body.dir + '/' + filename);
        fs.readFile(filename, {encoding: 'utf-8'}, function (err, data) {
          if (!err) {
            console.log(filename);
            obj = JSON.parse(data);
            obj.id = oldfilename;
            objs.push(obj);
            if (objs.length == valid_file_count) {
              console.log("send " + req.body.dir);
              res.send(objs);
            }
          } else {
            console.log(err);
            res.status(404).send("Oops, something went wrong");
          }
        });
      });
    } else {
      console.log(err);
      throw err;
      res.status(404).send("Oops, something went wrong");
    }
  });
});

router.post('/drawastarsbatch', function(req, res, next) {
  var filePath = path.join(__dirname, '../../data-process/' + req.body.dir);
  var batchidx = req.body.batch;


  fs.readdir(filePath, function(err, filenames) {
    if (!err) {
      var objs = [];
      var valid_file_count = 0;
      filenames.forEach(function(filename) {
        if (filename.split('.').pop() !== "json") {
          return;
        }
        var check_filename_tmp = filename.split('-');
        if (check_filename_tmp[0] === "astar"
            && check_filename_tmp[1] === "pt"
            && check_filename_tmp[2] === batchidx.toString()) {
          valid_file_count = valid_file_count + 1;
          console.log(valid_file_count);
        }
      });

      filenames.forEach(function(filename) {
        var oldfilename = filename;
        if (filename.split('.').pop() !== "json") {
          return;
        }
        var check_filename_tmp = filename.split('-');
        if (check_filename_tmp[0] !== "astar"
            || check_filename_tmp[1] !== "pt"
            || check_filename_tmp[2] !== batchidx.toString()) {
          return;
        }
        filename = path.join(__dirname, '../../data-process/' + req.body.dir + '/' + filename);
        fs.readFile(filename, {encoding: 'utf-8'}, function (err, data) {
          if (!err) {
            console.log(filename);
            obj = JSON.parse(data);
            obj.id = oldfilename;
            objs.push(obj);
            if (objs.length == valid_file_count) {
              console.log("send " + req.body.dir);
              res.send(objs);
            }
          } else {
            console.log(err);
            throw err;
            res.status(404).send("Oops, something went wrong");
          }
        });
      });
    } else {
      console.log(err);
      throw err;
      res.status(404).send("Oops, something went wrong");
    }
  });
});

router.post('/getpath', function(req, res, next) {
  console.log(req.body.srclat);
  console.log(req.body.srclon);
  console.log(req.body.dstlat);
  console.log(req.body.dstlon);
  if (!(req.body.srclat && req.body.srclon && req.body.dstlat && req.body.dstlon)) {
    return;
  }

  var options = {
    mode: 'text',
    pythonOptions: ['-u'], // get print results in real-time
    scriptPath: path.join(__dirname, "../../get-path/pgrouting-test"),
    args: [req.body.srclon, req.body.srclat, req.body.dstlon, req.body.dstlat]
  };

  PythonShell.run("astar_visualize.py", options, function (err, results) {
    if (err) {
      console.log('Error: python error ' + err);
      //res.status(404).send("Oh uh, something went wrong");
    }
    else {
      console.log('results: %j', results);
    }

    // TODO call a python function with the two points as input
    var filePath = path.join(__dirname, '../../data-process/frontend-path/astar-path.json');
    // TODO need to check whether the file exist.
    fs.readFile(filePath, {encoding: 'utf-8'}, function(err,data){
      if (!err) {
        obj = JSON.parse(data);
        obj.id = "astarpath.json";
        res.send([obj]);
      } else {
        console.log(err);
        res.status(404).send("Oh uh, something went wrong");
      }
    });
  });


});

module.exports = router;
