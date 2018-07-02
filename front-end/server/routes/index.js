var express = require('express');
var router = express.Router();
var path = require('path');

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
});


module.exports = router;
