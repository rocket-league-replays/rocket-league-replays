var gulp         = require('gulp'),
    bower        = require('gulp-bower'),
    browserSync  = require('browser-sync'),
    autoPrefixer = require('gulp-autoprefixer'),
    changed      = require('gulp-changed'),
    gulpIf       = require('gulp-if'),
    pxtorem      = require('gulp-pxtorem'),
    sass         = require('gulp-sass'),
    size         = require('gulp-size'),
    sourceMaps   = require('gulp-sourcemaps'),
    runSequence  = require('run-sequence'),
    rename       = require('gulp-rename'),
    reload       = browserSync.reload;

var AUTOPREFIXER_BROWSERS = [
    'last 2 versions',
    'ie >= 9'
];

var staticFolder = 'rocket_league/static/';
var templateFolder = 'rocket_league/templates/';

var config = {
    bower: {
        folder: 'bower_components/'
    },
    css: {
        folder: staticFolder + 'css'
    },
    js: {
        src: [
            staticFolder + '*.js',
            staticFolder + '/**/*.js'
        ]
    },
    html: {
        src: [
            templateFolder + '*.html',
            templateFolder + '/**/*.html'
        ]
    },
    sass: {
        folder: staticFolder + 'scss/',
        src: [
            staticFolder + 'scss/*.scss',
            staticFolder + 'scss/**/*.scss'
        ]
    }
};

gulp.task('styles', function() {
    return gulp.src(config.sass.src)
        // .pipe(changed('styles', {extension: '.scss'}))
        .pipe(sass({
            // TODO: Find a way to iterate over each .scss file for csscomb
            // errLogToConsole stops sass errors breaking the task
            errLogToConsole: true,
            precision: 10,
            includePaths: [
                config.sass.folder
            ],
            sourceComments: true,
            stats: true
        }))
        .on('error', function(e) {
            console.log(e);
        })
        .pipe(autoPrefixer({
            browsers: AUTOPREFIXER_BROWSERS
        }))
        .pipe(pxtorem())
        .pipe(gulp.dest(config.css.folder))
        .pipe(reload({
            stream: true
        }))
        .pipe(size({
            title: 'styles'
        }));
});

gulp.task('watch', function() {
    gulp.watch(config.sass.src, ['styles']);
});

gulp.task('serve', function() {
    browserSync({
        // Do we want the notifications in the top right when things update?
        notify: false,
        // The prefix in the console for browserSync events
        logPrefix: 'rocket_league',
        // Inject the changes instead of a reload
        injectChanges: true,
        // The directory to serve HTML files from
        // server: ['./']
        // Uncomment this and comment the above line if you want to tie
        // browserSync to an already existing server
        proxy: '0.0.0.0:8000'
    });

    gulp.watch(config.sass.src, ['styles']);
    gulp.watch(config.html.src, reload);
    gulp.watch(config.js.src, reload);
});

gulp.task('bower', function() {
    return bower()
        .pipe(gulp.dest(config.bower.folder));
});

gulp.task('bowerFiles', function() {
    gulp.src([
            'bower_components/fastclick/lib/fastclick.js',
            'bower_components/jquery/dist/jquery.js',
            'bower_components/jquery-placeholder/jquery.placeholder.js',
            'bower_components/jquery.cookie/jquery.cookie.js',
            'bower_components/modernizr/modernizr.js',
            'bower_components/modernizr/modernizr.js',
        ])
        .pipe(gulp.dest('rocket_league/static/js/vendor/'));


    gulp.src('bower_components/foundation/js/foundation/*')
        .pipe(gulp.dest('rocket_league/static/js/vendor/foundation/'));


    gulp.src([
            'bower_components/foundation/scss/normalize.scss',
            'bower_components/foundation/scss/**/*',
            '!bower_components/foundation/scss/foundation.scss',
        ])
        .pipe(gulp.dest('rocket_league/static/scss/'));


    gulp.src('bower_components/foundation/scss/foundation.scss')
        .pipe(rename({
            basename: 'screen'
        }))
        .pipe(gulp.dest('rocket_league/static/scss'));
});

gulp.task('initialise', function(callback) {
        return runSequence(
        // Install the project dependancies from `bower.json`
        'bower',

        // Move the bower files to their final destination.
        'bowerFiles',

        callback
    );
})

gulp.task('default', function(callback) {
    return runSequence(
        // Perform the initial compilation of the SCSS files.
        'styles',

        // Start watching for changes to SCSS files.
        'serve',

        callback
    );
});
