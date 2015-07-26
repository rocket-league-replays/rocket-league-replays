/*****************************************************************************/
/* Imports */
/*****************************************************************************/
// - Main
import gulp from 'gulp';

// - Gulp modules
import gulpLoadPlugins from 'gulp-load-plugins';
const $ = gulpLoadPlugins();

// - Browser Sync from base Gulpfile
import browserSync from 'browser-sync';
const reload = browserSync.reload;

// - Project config
import config from './_config';

export default () => {
  // Initialise Browser Sync
  browserSync.init({
    injectChanges: true,
    logFileChanges: true,
    logPrefix: 'text',
    notify: false,
    open: false,
    proxy: '0.0.0.0:8000'
  });

  process.on('exit', () => {
    browserSync.exit();
  });

  /***********/
  /* Watches */
  /***********/
  // - Pass SASS to the Styles task
  gulp.watch(config.sass.src, ['styles', 'clean:temp']);

  // - HTML and Images don't need to be processed
  gulp.watch(config.html.src, reload);
  gulp.watch(config.images.src, reload);

  // - We don't need a JS watch as that's handled in it's own task (Watchify)
}
