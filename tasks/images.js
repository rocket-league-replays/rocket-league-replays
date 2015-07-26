/*****************************************************************************/
/* Imports */
/*****************************************************************************/
// - Main
import gulp from 'gulp';

// - Gulp modules
import gulpLoadPlugins from 'gulp-load-plugins';
const $ = gulpLoadPlugins();

// - Project config
import config from './_config';

export default () => {
  return gulp.src(config.images.src)
    // Filter out previously done images
    .pipe($.cache($.imagemin({
      progressive: true,
      interlaced: true
    })))

    // Place our nice new images
    .pipe(gulp.dest(config.images.path))

    // Let the console know what we did
    .pipe($.size({title: 'images'}));
}
