'use strict'

let currentFrame = -1
let maxFrame = -1
let frameData = {}
let carsLoading = []

function loadGameData(url) {
  init()

  var request = new XMLHttpRequest();

  request.open('GET', url, true);

  request.onload = function() {
    if (request.status >= 200 && request.status < 400) {
      frameData = JSON.parse(request.responseText);

      maxFrame = Object.keys(frameData).length
      currentFrame = 0
    }
  };

  request.send();
}

function positionReplayObjects() {
  if (carsLoading.length > 0) {
    console.warn(`Still rendering ${carsLoading}`)
  }

  frameData[currentFrame].actors.forEach(function(actor, index) {
    // Does this car already exist in the scene.
    const objectName = `car-${actor.id}`
    const carObject = scene.getObjectByName(objectName)

    if (carObject === undefined) {
      // Add the car.
      if (carsLoading.indexOf(objectName) === -1) {
        carsLoading.push(objectName)

        console.log(`[${objectName}] Calling addCar`)
        if (actor.type === 'player') {
          addCar(objectName, actor)
        } else if (actor.type === 'ball') {
          addBall(objectName, actor)
        }
      }
    } else {
      // Reposition the car based on the latest data.
      if (actor.z < 0) {
        console.error('Z value below 0 at frame', currentFrame)
      }

      carObject.position.set(
        actor.x * -1,
        actor.y,
        1
      )

      // If actor.z is 18, we want scaleFactor to be 1
      // if actor.z is 2048 we want scaleFactor to be 2
      // const scaleFactor = 4 - (((2048 - (actor.z - 18)) / 2048) / 4)

      const scaleFactor = (
          1 +  // Base scale, required to stop objects disappearing (by being scaled to 0 at ground level)
          (2.75 * // Max scale factor.
            (actor.z - 18) / 2048) // Currenct z value as a percentage of the arena height.
          )

      carObject.scale.set(
        scaleFactor,
        scaleFactor,
        scaleFactor
      )

      // Looks close.
      carObject.rotation.set(
        0,
        0,
        r(90) + actor.pitch * Math.PI * -1
      )
    }
  });
}
