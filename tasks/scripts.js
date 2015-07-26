/*****************************************************************************/
/* Imports */
/*****************************************************************************/
// - Main
import gulp from 'gulp';

// - Gulp modules
import gulpLoadPlugins from 'gulp-load-plugins';
const $ = gulpLoadPlugins();

// - Node modules
import browserify from 'browserify';
import watchify from 'watchify';
import babelify from 'babelify';
import source from 'vinyl-source-stream';
import buffer from 'vinyl-buffer';

// - Browser Sync
import browserSync from 'browser-sync';
const reload = browserSync.reload;

// - Project config
import config from './_config';

function compile(watch) {
  // Create our browserify instance
  const bundler = watchify(browserify(config.watchify.fileIn, {debug: true}).transform(babelify));

  function rebundle() {
    bundler.bundle()
      .on('error', function (err) {
        console.error(err);
        this.emit('end');
      })
      // Grab our entry file
      .pipe(source(config.watchify.fileOut))

      // Buffer it.. (?)
      .pipe(buffer())

      // Initialise source maps, load the maps from browserify
      .pipe($.sourcemaps.init({loadMaps: true}))

      // Write the source maps, need to provide the source for Browser Sync
      .pipe($.sourcemaps.write({includeContent: false, sourceRoot: config.watchify.folderIn}))

      // Place our nice new JS file
      .pipe(gulp.dest(config.watchify.folderOut));
  }

  if (watch) {
    bundler.on('update', function () {
      // Success message
      console.log('BUNDLED JS! ᕦ(ò_ó)ᕤ');

      // Bundle the JS
      rebundle();

      // Reload browser
      reload();
    });
  }

  rebundle();
}

export default () => compile(true);
