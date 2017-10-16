require('expose?ReplayPlayback!./replay.js')

import {init} from './main'
import {
  // Helper functions
  setFrameData,
  setGoalData,
  setBoostData,
  setSecondsData,
  setActorData,
  setTeamData,
  setMaxFrame,
  setCurrentFrame,

  // Actual variables
  frameData,
  goalData,
  boostData,
  secondsData,
  actorData,
  maxFrame,
  currentFrame,
  scene
} from './variables'

import {addBall, addCar} from './objects'
import {formatTime, calculatePitch} from './utils'

export function loadGameData (url) {  // eslint-disable-line no-unused-vars
  init()

  const request = new XMLHttpRequest()

  request.open('GET', url, true)

  request.onload = function () {
    if (request.status >= 200 && request.status < 400) {
      const response_data = JSON.parse(request.responseText)

      if (response_data.frame_data !== undefined) {
        setFrameData(response_data.frame_data)
      }

      if (response_data.goals !== undefined) {
        setGoalData(response_data.goals)
      }

      if (response_data.boost !== undefined) {
        if (Object.keys(response_data.boost).indexOf('values') !== -1) {
          const newBoostData = {}

          // Rework this old-style data to look like the new data.
          Object.keys(response_data.boost.values).forEach((item) => {
            // Get the player ID.
            const player_id = response_data.boost.cars[response_data.boost.actors[item]].toString()

            if (Object.keys(newBoostData).indexOf(player_id) === -1) {
              newBoostData[player_id] = {}
            }

            Object.keys(response_data.boost.values[item]).forEach((value_item) => {
              newBoostData[player_id][value_item] = response_data.boost.values[item][value_item]
            })
          })

          response_data.boost = newBoostData
        }

        setBoostData(response_data.boost)
      }

      if (response_data.seconds_mapping !== undefined) {
        setSecondsData(response_data.seconds_mapping)
      }

      if (response_data.actors !== undefined) {
        setActorData(response_data.actors)
      }

      if (response_data.teams !== undefined) {
        setTeamData(response_data.teams)
      }

      setMaxFrame(Object.keys(frameData).length)
      setCurrentFrame(0)
    }
  }

  request.send()
}

export function positionReplayObjects () {
  if (secondsData[currentFrame] !== undefined) {
    document.querySelector('.sim-Timer_Value').innerHTML = formatTime(secondsData[currentFrame])
  }

  // Is there any boost data for this frame?
  // console.log(boostData)
  Object.keys(boostData).forEach(function (item) {
    if (boostData[item][currentFrame] !== undefined) {
      // Which player is this?
      const player_id = item

      // Current in-game (and %) value.
      const value = Math.ceil(boostData[item][currentFrame] * (100 / 255))

      const boostEl = document.querySelector(`.sim-Boost_Inner-player${player_id}`)

      if (boostEl) {
        boostEl.style.backgroundSize = `${value}% 100%`
        boostEl.innerHTML = value

        if (value < 15) {
          boostEl.style.color = '#000'
        } else {
          boostEl.style.color = ''
        }
      }
    } else {
      // Search for boost values within the next 74 frames.
      for (let i = currentFrame; i < currentFrame + 74; i++) {
        if (boostData[item][i] !== undefined) {
          // Which player is this?
          const player_id = item
          const boostEl = document.querySelector(`.sim-Boost_Inner-player${player_id}`)

          if (boostEl) {
            const frameDiff = i - currentFrame
            // Boost decreases at a rate of ~255/74 per frame.
            const currentValue = boostEl.innerText / (100 / 255)
            const nextValue = boostData[item][i]

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

              const rawValue = boostData[item][i] + (frameDiff * (255 / 74))

              if (rawValue < 0 || rawValue > 255) {
                throw new RangeError(`BoostRangeError: Value of ${rawValue} is not within the range of 0-255`)
              }

              const value = Math.ceil(rawValue * (100 / 255))

              boostEl.style.backgroundSize = `${value}% 100%`
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

  document.querySelector('.sim-Timeline_Inner').style.width = `${currentFrame / maxFrame * 100}%`

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

  let frame_actor_iterator = frameData[currentFrame]
  if (frameData[currentFrame].actors !== undefined) {
    frame_actor_iterator = frameData[currentFrame].actors
  }

  frame_actor_iterator.forEach(function (actor, index) {
    // Does this car already exist in the scene.
    const objectName = `car-${actor.id}`
    const carObject = scene.getObjectByName(objectName)

    if (carObject === undefined) {
      // Add the car.
      console.log(`[${objectName}] Calling addCar`)
      if (actor.type === 'player' || actorData[actor.id] !== undefined) {
        addCar(objectName, actor)
      } else if (actor.type === 'ball' || actorData[actor.id] === undefined) {
        addBall(objectName, actor)
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

      const full_min = 0
      const full_max = 65536
      const full_range = full_max - full_min

      const deg_min = 0
      const deg_max = 360
      const deg_range = deg_max - deg_min

      let pitch = (((actor.pitch - full_min) * deg_range) / full_range) + deg_min
      pitch += 90

      // Looks close.
      carObject.rotation.set(
        0,
        0,
        calculatePitch(actor.pitch)
      )
    }
  })
}
