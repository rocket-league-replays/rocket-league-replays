/*global init, formatTime, scene, addCar, addBall, r*/
'use strict'

let currentFrame = -1
let maxFrame = -1
let frameData = {}
let goalData = []
let boostData = {}
let secondsData = {}
let carsLoading = []
let actorData = {}
let teamData = {}

function loadGameData (url) {
  init()

  const request = new XMLHttpRequest()

  request.open('GET', url, true)

  request.onload = function () {
    if (request.status >= 200 && request.status < 400) {
      const response_data = JSON.parse(request.responseText)

      if (response_data.frame_data !== undefined) {
        frameData = response_data.frame_data
      }

      if (response_data.goals !== undefined) {
        goalData = response_data.goals
      }

      if (response_data.boost !== undefined) {
        boostData = response_data.boost
      }

      if (response_data.seconds_mapping !== undefined) {
        secondsData = response_data.seconds_mapping
      }

      if (response_data.actors !== undefined) {
        actorData = response_data.actors
      }

      if (response_data.teams !== undefined) {
        teamData = response_data.teams
      }

      maxFrame = Object.keys(frameData).length
      currentFrame = 0
    }
  }

  request.send()
}

function positionReplayObjects () {
  if (carsLoading.length > 0) {
    console.warn(`Still rendering ${carsLoading}`)
  }

  if (secondsData[currentFrame] !== undefined) {
    document.querySelector('.sim-Timer_Value').innerHTML = formatTime(secondsData[currentFrame])
  }

  // Is there any boost data for this frame?
  Object.keys(boostData.values).forEach(function (item) {
    if (boostData.values[item][currentFrame] !== undefined) {
      // Which player is this?
      const player_id = boostData.cars[boostData.actors[item]]

      // Current in-game (and %) value.
      const value = Math.ceil(boostData.values[item][currentFrame] * (100 / 255))

      const boostEl = document.querySelector(`.sim-Boost_Inner-player${player_id}`)

      if (boostEl) {
        boostEl.style.backgroundSize = `${value}% 100%`;
        boostEl.innerHTML = value

        if (value < 15) {
          boostEl.style.color = '#000'
        } else {
          boostEl.style.color = ''
        }
      }
    } else {
      // Search for boost values within the next 74 frames.
      let searchLength = 1

      for (let i=currentFrame; i<currentFrame+74; i++) {
        if (boostData.values[item][i] !== undefined) {
          // Which player is this?
          const player_id = boostData.cars[boostData.actors[item]]
          const boostEl = document.querySelector(`.sim-Boost_Inner-player${player_id}`)

          if (boostEl) {
            const frameDiff = i - currentFrame
            // Boost decreases at a rate of ~255/74 per frame.
            const currentValue = boostEl.innerText / (100 / 255)
            const nextValue = boostData.values[item][i]

            // We only care about boost values going down.
            if (nextValue < currentValue) {

              // Is this the right time to start moving this boost value? We don't to use
              // a full 74 frames for a tiny burst of boost, only for a full range, so ensure
              // we're not being premature.
              //
              // Diff | Frame lookahead
              // 255  | 74
              //
              // Take the diff and check how many frames before we should start to move the gauge.

              const frameDiffRequired = (currentValue - nextValue) / (255 / 74)

              if (frameDiff > frameDiffRequired) {
                continue
              }

              const rawValue = boostData.values[item][i] + (frameDiff * (255/74))

              if (rawValue < 0 || rawValue > 255) {
                throw new Error("BoostRangeError")
              }

              const value = Math.ceil(rawValue * (100 / 255))

              boostEl.style.backgroundSize = `${value}% 100%`;
              boostEl.innerHTML = value

              if (value < 15) {
                boostEl.style.color = '#000'
              } else {
                boostEl.style.color = ''
              }

              break
            }
          }
        }
      }
    }
  })

  // Figure out what the score is.
  let team_0_score = 0
  let team_1_score = 0

  goalData.forEach(function (item) {
    if (currentFrame >= item.frame) {
      if (item.PlayerTeam === 0) {
        team_0_score++
      } else if (item.PlayerTeam === 1) {
        team_1_score++
      }
    }
  })

  document.querySelector('.sim-Timer_Score-0').innerHTML = team_0_score
  document.querySelector('.sim-Timer_Score-1').innerHTML = team_1_score

  document.querySelector('.sim-Timeline_Inner').style.width = `${currentFrame / maxFrame * 100}%`;

  // Do any actors get removed in this frame?
  Object.keys(actorData).forEach(function (item) {
    if (actorData[item].left <= currentFrame) {
      const objectName = `car-${item}`
      const carObject = scene.getObjectByName(objectName)

      if (carObject !== undefined) {
        scene.remove(carObject)
      }

      const boostEl = document.querySelector(`.sim-Boost_Outer-actor${item}`)

      if (boostEl) {
        boostEl.remove()
      }
    }
  })

  frameData[currentFrame].actors.forEach(function (actor, index) {
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
  })
}
