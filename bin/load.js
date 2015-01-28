var page = require('webpage').create();
var fs = require('fs');

var system = require('system');
var args = system.args;

// args.forEach(function(arg, i) {
//   console.log(i + ': ' + arg);
// });

var url = args[1]
var output = args[2]

var t = Date.now();
page.open(url, function(status) {
    console.log("open Status: " + status);
    if(status === "success") {
        fs.write(output, page.content, "w")
        t = Date.now() - t;
        console.log('Loading time ' + t + ' msec');
    }
    phantom.exit();
});
