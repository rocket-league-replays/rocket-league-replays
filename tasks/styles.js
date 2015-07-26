/*****************************************************************************/
/* Imports */
/*****************************************************************************/
// - Main
import gulp from 'gulp';

// - Gulp modules
import gulpLoadPlugins from 'gulp-load-plugins';
const $ = gulpLoadPlugins();

// - Browser Sync
import browserSync from 'browser-sync';
const reload = browserSync.reload;

// - Project config
import config from './_config';

export default () => {
  // Browsers we support
  const autoprefixerBrowsers = [
    'last 2 versions',
    'ie >= 9'
  ];

  return gulp.src(config.sass.src)
    // Only pass through changed files
    .pipe($.changed(config.css.path, {extension: '.css'}))

    // Initialise source maps
    .pipe($.sourcemaps.init())

    // Process our SCSS to CSS
    .pipe($.sass({
      precision: 10,
      stats: true
    }).on('error', $.sass.logError))

    // PostCSS our vendor prefixes
    .pipe($.autoprefixer(autoprefixerBrowsers))

    // Convert viable px units to REM
    .pipe($.pxtorem())

    // Place our compiled CSS in a tmp folder
    .pipe(gulp.dest('.tmp'))

    // Minify our CSS in the temp folder
    .pipe($.if('*.css', $.minifyCss()))

    // Write our source map, the root is needed for Django funnyness
    .pipe($.sourcemaps.write('./', {
      includeContent: false,
      sourceRoot: () => {
        return '../../static'
      }
    }))

    // Place our CSS in the location we link to
    .pipe(gulp.dest(config.css.path))

    // Stream the changes to Browser Sync
    .pipe(browserSync.stream({match: '**/*.css'}))

    // Spit out the size to the console
    .pipe($.size({title: 'styles'}));
}
