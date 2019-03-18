var webpack = require('webpack');

module.exports = function (grunt) {

    function wConfig(options) {
        var config = {
            module: {
                loaders: [{
                    exclude: /node_modules/,
                    loader: 'babel-loader'
                }]
            },
            resolve: {
                extensions: ['.es6', '.js', '.jsx']
            },
            stats: {
                colors: true
            },
            progress: false,
            inline: false,
            devtool: 'source-map',
            plugins: [
                // new webpack.optimize.UglifyJsPlugin({
                //     compress: {
                //         warnings: false
                //     },
                //     output: {
                //         comments: false
                //     },
                //     sourceMap: true
                // })
            ]
        };

        for (var k in options) {
            config[k] = options[k];
        }
        return config;
    }

    grunt.initConfig({
        less: {
            vis: {
                options: {
                    paths: ['./static'],
                    sourceMap: true,
                    sourceMapURL: '/static/style.css.map',
                },
                files: {
                    './static/style.css': './static/style.less'
                }
            },
        },
        webpack: {
            vis: wConfig({
                entry: ['babel-polyfill', './vis/Vis.jsx'],
                output: {filename: './static/dist/Vis.js'}
            })
        },
        watch: {
            vis: {
                files: ['vis/*.*', 'vis/components/*.*'],
                tasks: ['webpack:vis']
            },
            vis_less: {
                files: ['static/**/*.less'],
                tasks: ['less:vis']
            }
        },
        copy: {
            dependencies: {
                files: [{
                    cwd: 'node_modules/handsontable/dist/',
                    src: ['handsontable.full.js', 'handsontable.full.css'],
                    dest: 'static/scripts/handsontable/',
                    expand: true
                },{
                    cwd: 'node_modules/gist-async/js/',
                    src: 'gist-async.min.js',
                    dest: 'static/scripts/',
                    expand: true
                },{
                    cwd: 'node_modules/numeric/',
                    src: 'numeric-1.2.6.min.js',
                    dest: 'static/scripts/',
                    expand: true
                },{
                    cwd: 'node_modules/jquery/dist/',
                    src: 'jquery.min.js',
                    dest: 'static/scripts/',
                    expand: true
                }, {
                    cwd: 'node_modules/highcharts/themes/',
                    src: '*',
                    dest: 'static/scripts/highcharts/themes/',
                    expand: true
                }, {
                    cwd: 'node_modules/highcharts/',
                    src: ['highcharts.js', 'highstock.js'],
                    dest: 'static/scripts/highcharts/',
                    expand: true
                }, {
                    cwd: 'node_modules/mathjs/dist/',
                    src: 'math.js',
                    dest: 'static/scripts/',
                    expand: true
                }]
            },
        },
        exec: {
            run_api: {
                cmd: "python cron/run_api.py"
            },
            download_snp: {
                cmd: "python cron/download_snp.py"
            },
            compute_snp: {
                cmd: "python cron/compute_snp500.py"
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-webpack');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-exec');

};