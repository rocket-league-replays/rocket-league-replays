'use strict'

const loader = new THREE.JSONLoader();
const textureLoader = new THREE.TextureLoader()


// Convert degrees to radians
function r(d) {
  return d * (Math.PI / 180)
}

// Convert radians to degrees
function d(r) {
  return r * (180 / Math.PI)
}
