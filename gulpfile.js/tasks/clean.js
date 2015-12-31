var gulp   = require('gulp')
var del    = require('del')
var config = require('../config')
var path   = require('path')
var gutil  = require("gulp-util")

var cleanTask = function (cb) {
  var files = [ path.join(config.root.dest, 'rev-manifest.json') ]

  for(var key in config.tasks) {
    var task = config.tasks[key]
    if(task.dest) {
      var glob = '**/*' + (task.extensions ? ('.{' + task.extensions.join(',') + ',map}') : '')
      files.push(path.join(config.root.dest, task.dest, glob))
    }
  }

  // Don't touch node_modules or source files!
  files.push('!node_modules/**/*')
  files.push('!' + path.join(config.root.src, '/**/*'))

  del(files).then(function (paths) {
    // console.log(paths)
    cb()
  })
}

gulp.task('clean', cleanTask)
module.exports = cleanTask
