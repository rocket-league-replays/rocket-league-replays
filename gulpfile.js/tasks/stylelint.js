var config = require('../config')
if (!config.tasks.css) return

var gulp = require('gulp')
var postcss = require('gulp-postcss')
var path = require('path')
var reporter = require('postcss-reporter')

var paths = {
  src: path.join(config.root.src, '/**/*.' + config.tasks.css.extensions),
  dest: path.join(config.root.dest, config.tasks.css.dest)
}

var styleLintTask = function () {
  var processors = [
    require('stylelint'),
    reporter({clearMessages: true})
  ]

  return gulp.src(paths.src)
    .pipe(postcss(processors))
}

gulp.task('stylelint', styleLintTask)
module.exports = styleLintTask
