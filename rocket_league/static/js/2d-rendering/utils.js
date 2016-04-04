/*global THREE*/
'use strict';

var loader = new THREE.JSONLoader();
var textureLoader = new THREE.TextureLoader();
textureLoader.crossOrigin = '';

// Convert degrees to radians
function r(d) {
  return d * (Math.PI / 180);
}

// Convert radians to degrees
function d(r) {
  return r * (180 / Math.PI);
}

function formatTime(time) {
  time = Math.ceil(time);

  // Minutes and seconds
  var mins = ~ ~(time / 60);
  var secs = time % 60;

  // Hours, minutes and seconds
  var hrs = ~ ~(time / 3600);
  mins = ~ ~(time % 3600 / 60);
  secs = time % 60;

  // Output like "1:01" or "4:03:59" or "123:03:59"
  var ret = '';

  if (hrs > 0) {
    ret += hrs + ':' + (mins < 10 ? '0' : '');
  }

  ret += mins + ':' + (secs < 10 ? '0' : '');
  ret += '' + secs.toFixed(0);
  return ret;
}
