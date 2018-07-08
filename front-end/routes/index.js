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
  var filePath = path.join(__dirname, '../public/fake/path_psql.json');
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


module.exports = router;
