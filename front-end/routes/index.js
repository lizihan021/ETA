var express = require('express');
var router = express.Router();
var path = require('path');
var fs = require('fs');

/* GET home page. */
router.get('/', function(req, res, next) {
  // res.render('index', { title: 'Express' });
  res.render('index');
  // res.sendFile(path.join(__dirname, '../views/index.html'));
});

router.post('/upload', function(req, res, next) {
  console.log(req.body.srclat);
  console.log(req.body.srclon);
  console.log(req.body.dstlat);
  console.log(req.body.dstlon);
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
      filenames.forEach(function(filename) {
        var oldfilename = filename;
        filename = path.join(__dirname, '../../data-process/' + req.body.dir + '/' + filename);
        console.log(filename);
        fs.readFile(filename, {encoding: 'utf-8'}, function (err, data) {
          if (!err) {
            obj = JSON.parse(data);
            obj.id = oldfilename;
            console.log(obj);
            objs.push(obj);
            if (objs.length == filenames.length) {
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

module.exports = router;
