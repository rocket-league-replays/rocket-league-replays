/*global Detector, THREE, r, Stats, currentFrame:true, maxFrame, positionReplayObjects, addStadium*/
'use strict'

if (!Detector.webgl) {
  Detector.addGetWebGLMessage()
}

let camera
let scene
let renderer
let stats
let playState = 1

function init () {
  scene = new THREE.Scene()

  renderer = new THREE.WebGLRenderer()
  renderer.setClearColor(0xffffff)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.setSize('1248', '702', false)
  renderer.shadowMap.enabled = true

  const container = document.querySelector('.sim-Outer')
  container.appendChild(renderer.domElement)
  renderer.domElement.style.width = '100%'

  camera = new THREE.PerspectiveCamera(2 * Math.atan(8240 / (2 * 5000)) * (180 / Math.PI), 1248 / 702, 1, 30000)
  camera.position.set(0, 0, 5000)
  camera.rotation.set(0, 0, r(90))

  // Add lighting.
  const light = new THREE.DirectionalLight(0xffffff)
  light.castShadow = true
  light.shadow.camera.left = -5000
  light.shadow.camera.right = 5000
  light.shadow.camera.top = 5000
  light.shadow.camera.bottom = -5000
  light.position.set(0, 0, 5000)
  scene.add(light)

  document.querySelector('.sim-Timeline_Outer').addEventListener('mousemove', function (e) {
    if (document.querySelector('.sim-Timeline_Outer') !== e.target) {
      return
    }

    document.querySelector('.sim-Timeline_Cursor').style.left = `${e.offsetX}px`
  })

  document.querySelector('.sim-Timeline_Outer').addEventListener('mousedown', function (e) {
    if (document.querySelector('.sim-Timeline_Outer') !== e.target) {
      return
    }

    // Convert the current position into a frame.
    const percentage = e.offsetX / e.target.offsetWidth

    currentFrame = Math.floor(maxFrame * percentage)
  })

  // Add Play / Pause controls.
  document.querySelector('.sim-Timeline_Controls').addEventListener('mousedown', function (e) {
    const pausedClass = 'sim-Timeline_Controls-paused'

    if (e.target.classList.contains(pausedClass)) {
      e.target.classList.remove(pausedClass)
      playState = 1
    } else {
      e.target.classList.add(pausedClass)
      playState = 0
    }
  })

  addStadium()
  animate()
}

function animate () {
  if (typeof scene === 'undefined') {
    return
  }

  if (typeof currentFrame !== 'undefined' && currentFrame >= 0) {
    positionReplayObjects()

    if (playState === 1) {
      if (currentFrame === maxFrame - 1) {
        currentFrame = 0
      } else {
        currentFrame += 1
      }
    }
  }

  render()

  const fpsLimit = 30 // Cap at 30 FPS.
  const timeoutDelay = 1000 / fpsLimit

  setTimeout(() => {
    requestAnimationFrame(animate)
  }, timeoutDelay)
}

function render () {
  renderer.render(scene, camera)
}
