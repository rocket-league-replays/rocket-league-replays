'use strict'

function renderRect(width, height) {
  var rectShape = new THREE.Shape()
  rectShape.moveTo(-(width / 2), -(height / 2))
  rectShape.lineTo(width / 2, -(height / 2))
  rectShape.lineTo(width / 2, height / 2)
  rectShape.lineTo(-(width / 2), height / 2)
  rectShape.lineTo(-(width / 2), -(height / 2))

  return new THREE.ShapeGeometry(rectShape)
}

// Load the stadium outline.
function addStadium() {
  var materials = [
    new THREE.MeshLambertMaterial({
      map: textureLoader.load('/static/img/2d-rendering/arena_fieldlines.png'),
      transparent: true,
      opacity: 0.5,
      color: 0xffffff,
    }),
    new THREE.MeshLambertMaterial({
      map: textureLoader.load('/static/img/2d-rendering/arena_overlay2.png'),
      transparent: true,
      opacity: 0.7,
      color: 0xffffff,
    }),
    new THREE.MeshLambertMaterial({
      map: textureLoader.load('/static/img/2d-rendering/arena_boost.png'),
      transparent: true,
      color: 0xffffff,
      opacity: 0.5
    })
  ]

  var mesh = new THREE.SceneUtils.createMultiMaterialObject(
    new THREE.PlaneGeometry(8240, 12000),
    materials
  );

  mesh.name = 'stadium'
  mesh.castShadow = false;
  mesh.receiveShadow = false;

  scene.add(mesh);
}

// Cached meshes to improve load speed.
let carMesh;
let wheelMesh;

function addCar(name, actor) {
  console.log(`[${name}] Adding car`)
  let color = 0xff0000

  if (actor.y < 0) {
    console.log('Team 0')
    color = 0x6086e5
  } else {
    console.log('Team 1')
    color = 0xffae7f
  }

  const mesh = new THREE.Mesh(
    renderRect(74, 144),
    new THREE.MeshBasicMaterial({ color })
  );

  mesh.name = name
  mesh.matrixAutoUpdate = true;
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  console.log(`[${name}] Adding to scene`)

  // Fix the rotation point.
  var box = new THREE.Box3().setFromObject(mesh);
  box.center(mesh.position); // this re-sets the mesh position
  mesh.position.multiplyScalar(-1);

  scene.add(mesh);

  // Reposition the car based on the latest data.
  console.log(`[${name}] Setting initial position`)

  mesh.position.set(
    actor.x * -1,
    actor.y,
    actor.z
  )

  mesh.rotation.set(
    0,
    0,
    r(90) + actor.pitch * Math.PI * -1
  )

  console.log(`[${name}] Render complete`)
  carsLoading = carsLoading.filter(function(e){ return e !== name })
}

function addBall(name, actor) {
  console.log(`[${name}] Adding ball`)

  const mesh = new THREE.Mesh(
    new THREE.CircleGeometry(91, 32),
    new THREE.MeshLambertMaterial({
      map: textureLoader.load('/static/img/2d-rendering/ball.png')
    })
  );

  mesh.name = name
  mesh.matrixAutoUpdate = true;
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  console.log(`[${name}] Adding to scene`)

  // Fix the rotation point.
  var box = new THREE.Box3().setFromObject(mesh);
  box.center(mesh.position); // this re-sets the mesh position
  mesh.position.multiplyScalar(-1);

  scene.add(mesh);

  // Reposition the car based on the latest data.
  console.log(`[${name}] Setting initial position`)

  mesh.position.set(
    actor.x * -1,
    actor.y,
    actor.z
  )

  mesh.rotation.set(
    0,
    0,
    actor.yaw * Math.PI
  )

  // mesh.rotation.set(
  //   (actor.roll * Math.PI * - 1) + r(-90),
  //   actor.pitch * Math.PI * -1,
  //   (actor.yaw * Math.PI * - 1) + r(180)
  // )

  // XYZ XZY YXZ YZX ZXY ZYX

  console.log(`[${name}] Render complete`)
  carsLoading = carsLoading.filter(function(e){ return e !== name })
}
