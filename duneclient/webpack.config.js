var webpack = require('webpack');
var path = require('path');
var WebpackNotifierPlugin = require('webpack-notifier');

var BUILD_DIR = path.resolve(__dirname, 'app')
var APP_DIR = path.resolve(__dirname, 'src')

var config = {
    entry: APP_DIR + '/main.js',
    output: {
        path: BUILD_DIR,
        filename: 'main.js'
    },
    module: {
        loaders: [
            {
                test: /\.jsx?/,
                include: APP_DIR,
                loader: 'babel-loader',
                query: {
                    presets: ['es2015', 'react', 'stage-2']
                }
            }
        ]
    },
    plugins: [
        new WebpackNotifierPlugin(),
        // new webpack.DefinePlugin({
        //     'process.env' : {
        //         NODE_ENV: JSON.stringify('production')
        //     }
        // }),
        // new webpack.optimize.UglifyJsPlugin(),
    ]
};

module.exports = config;
