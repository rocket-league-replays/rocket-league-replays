/*global THREE, textureLoader, scene, r, teamData, actorData, carsLoading:true*/
'use strict'

function renderRect (width, height) {
  const rectShape = new THREE.Shape()
  rectShape.moveTo(-(width / 2), -(height / 2))
  rectShape.lineTo(width / 2, -(height / 2))
  rectShape.lineTo(width / 2, height / 2)
  rectShape.lineTo(-(width / 2), height / 2)
  rectShape.lineTo(-(width / 2), -(height / 2))

  return new THREE.ShapeGeometry(rectShape)
}

// Load the stadium outline.
function addStadium () {
  const materials = [
    new THREE.MeshLambertMaterial({
      map: textureLoader.load(resource__arena_fieldlines),
      transparent: true,
      opacity: 0.5,
      color: 0xffffff
    }),
    new THREE.MeshLambertMaterial({
      map: textureLoader.load(resource__arena_overlay),
      transparent: true,
      opacity: 0.7,
      color: 0xffffff
    }),
    new THREE.MeshLambertMaterial({
      map: textureLoader.load(resource__arena_boost),
      transparent: true,
      color: 0xffffff,
      opacity: 0.5
    })
  ]

  const mesh = new THREE.SceneUtils.createMultiMaterialObject(
    new THREE.PlaneGeometry(8240, 12000),
    materials
  )

  mesh.name = 'stadium'
  mesh.castShadow = false
  mesh.receiveShadow = false

  scene.add(mesh)
}

function addCar (name, actor) {
  console.log(`[${name}] Adding car`)
  let texture

  if (actor.y < 0) {
    texture = textureLoader.load(resource__Car_Body_0)
  } else {
    texture = textureLoader.load(resource__Car_Body_1)
  }

  const mesh = new THREE.Mesh(
    // renderRect(74, 144),
    new THREE.BoxGeometry(90, 175, 1),
    new THREE.MeshLambertMaterial({
      map: texture,
      transparent: true,
      opacity: 1
    })
  )

  mesh.name = name
  mesh.matrixAutoUpdate = true
  mesh.castShadow = true
  mesh.receiveShadow = true

  console.log(`[${name}] Adding to scene`)

  // Fix the rotation point.
  const box = new THREE.Box3().setFromObject(mesh)
  box.center(mesh.position) // this re-sets the mesh position
  mesh.position.multiplyScalar(-1)

  scene.add(mesh)

  // Reposition the car based on the latest data.
  console.log(`[${name}] Setting initial position`)

  mesh.position.set(actor.x * -1, actor.y, actor.z)
  mesh.rotation.set(0, 0, r(90) + actor.pitch * Math.PI * -1)

  // Add the boost gauge.
  /*
  <div class="boost-outer boost-player-{{ player.actor_id }}">
      {{ player.player_name }}

      <div class="boost-inner" data-team="{{ player.team }}">34</div>
  </div>
  */

  if (actorData[actor.id] !== undefined) {
    const team = teamData[actorData[actor.id].team]

    const outerElement = document.createElement('div')
    outerElement.classList.add('sim-Boost_Outer')
    outerElement.classList.add(`sim-Boost_Outer-actor${actor.id}`)

    const playerName = document.createElement('span')
    playerName.innerHTML = actorData[actor.id].name
    playerName.classList.add('sim-Boost_Text')
    outerElement.appendChild(playerName)

    const innerElement = document.createElement('div')
    innerElement.innerHTML = '34'
    innerElement.classList.add('sim-Boost_Inner')
    innerElement.classList.add(`sim-Boost_Inner-team${team}`)
    innerElement.classList.add(`sim-Boost_Inner-player${actor.id}`)
    outerElement.appendChild(innerElement)

    document.querySelector(`.sim-Boost-team${team}`).appendChild(outerElement)
  }

  console.log(`[${name}] Render complete`)
  carsLoading = carsLoading.filter(function (e) { return e !== name })
}

function addBall (name, actor) {
  console.log(`[${name}] Adding ball`)

  const mesh = new THREE.Mesh(
    new THREE.CircleGeometry(91, 32),
    new THREE.MeshLambertMaterial({
      map: textureLoader.load(resource__ball)
    })
  )

  mesh.name = name
  mesh.matrixAutoUpdate = true
  mesh.castShadow = true
  mesh.receiveShadow = true
  mesh.renderOrder = 1

  console.log(`[${name}] Adding to scene`)

  // Fix the rotation point.
  const box = new THREE.Box3().setFromObject(mesh)
  box.center(mesh.position) // this re-sets the mesh position
  mesh.position.multiplyScalar(-1)

  scene.add(mesh)

  // Reposition the car based on the latest data.
  console.log(`[${name}] Setting initial position`)

  mesh.position.set(actor.x * -1, actor.y, actor.z)
  mesh.rotation.set(0, 0, actor.yaw * Math.PI)

  console.log(`[${name}] Render complete`)
  carsLoading = carsLoading.filter(function (e) { return e !== name })
}
