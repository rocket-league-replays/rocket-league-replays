"use strict";

if (!Detector.webgl) Detector.addGetWebGLMessage();
var clock = new THREE.Clock();

var camera, controls, scene, renderer;

var animData;
var mesh;
var stats;
var bottomSpacing = 100;


function init() {

  scene = new THREE.Scene();

  renderer = new THREE.WebGLRenderer();
  renderer.setClearColor(0xffffff);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize('1248', '702', false);
  renderer.shadowMap.enabled = true;

  var container = document.querySelector('.sim-Outer');
  container.appendChild(renderer.domElement);
  renderer.domElement.style.width = '100%'

  camera = new THREE.PerspectiveCamera(2 * Math.atan( 8240 / ( 2 * 5000 ) ) * ( 180 / Math.PI ), 1248 / 702, 1, 30000);
  camera.position.set(0, 0, 5000);
  camera.rotation.set(0, 0, r(90))

  // Add stats module.
  stats = new Stats();
  stats.domElement.style.position = 'absolute';
  stats.domElement.style.bottom = '0px';
  stats.domElement.style.zIndex = 100;
  container.appendChild(stats.domElement);

  // Add lighting.
  const light = new THREE.DirectionalLight(0xffffff);
  light.castShadow = true;
  light.shadow.camera.left = -5000;
  light.shadow.camera.right = 5000;
  light.shadow.camera.top = 5000;
  light.shadow.camera.bottom = -5000;
  light.position.set(0, 0, 5000);
  scene.add(light);

  document.querySelector('.sim-Timeline_Outer').addEventListener('mousemove', function(e) {
    if (document.querySelector('.sim-Timeline_Outer') !== e.target) {
      return;
    }

    document.querySelector('.sim-Timeline_Cursor').style.left = `${e.offsetX}px`
  })

  document.querySelector('.sim-Timeline_Outer').addEventListener('mousedown', function(e) {
    if (document.querySelector('.sim-Timeline_Outer') !== e.target) {
      return;
    }

    // Convert the current position into a frame.
    const percentage = e.offsetX / e.target.offsetWidth

    currentFrame = Math.floor(maxFrame * percentage)
  })

  addStadium()
  animate()
}

function animate() {
  if (typeof scene === 'undefined') {
    return
  }

  stats.update();

  if (typeof currentFrame !== 'undefined' && currentFrame >= 0) {
    positionReplayObjects()

    if (currentFrame === maxFrame - 1) {
      currentFrame = 0
    } else {
      currentFrame += 1
    }
  }

  render();

  let fpsLimit = 30 // Cap at 30 FPS.
  let timeoutDelay = 1000 / fpsLimit

  setTimeout(function() {
    requestAnimationFrame(animate);
  }, timeoutDelay)
}

function render() {
  renderer.render(scene, camera);
}
