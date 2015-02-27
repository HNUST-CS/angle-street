// 引入 gulp
var gulp = require('gulp');

// 引入 Plugins
var compass = require('gulp-compass');
var prettify = require('gulp-html-prettify');
var combineCSS = require('combine-css');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
gulp.task('format', function() {
    function to(src,dest){
        gulp.src(src)
        .pipe(prettify({indent_char: ' ', indent_size: 2}))
        .pipe(gulp.dest(dest))
    }
    to('./*.html','./')
    to('static/template/*.html','static/template/')
    to('static/template/admin/*.html','static/template/admin/')
});

gulp.task('combinelib', function() {
    var src=[
    "static/js/lib/underscore.js ",
    "static/js/lib/jquery.min.js ",
    "static/js/lib/angular.min.js ",
    "static/js/lib/iScroll.js ",
    "static/js/lib/angular-animate.min.js ",
    "static/js/lib/angular-route.min.js ",
    "static/js/lib/angular-cookies.min.js ",
    "static/js/lib/bootstrap.min.js "]
    return gulp.src(src)
        .pipe(concat("lib.js"))
        .pipe(uglify())
        .pipe(gulp.dest('static/js/'))
});

gulp.task('combineall',function(cb){
    return gulp.src([
    "static/js/main.js",
    "static/js/config.js ",
    ])
    .pipe(concat('all.js'))
    .pipe(gulp.dest('static/js/dest/'))
})

gulp.task('combine',['combinelib','combineall'])

// 创建 Compass 任务
gulp.task('compass', function() {
  gulp.src('static/css/*.css')
    .pipe(compass({
        comments: false,
        css: 'css',
    }).pipe(gulp.dest('static_min/css')));
});

// 默认任务
gulp.task('default', function() {
    // gulp.run('compass');

    // gulp.watch([
    //     './scss/**',
    //     './img/**'
    //     ], function(event) {
    //     gulp.run('compass');
    // });
});

