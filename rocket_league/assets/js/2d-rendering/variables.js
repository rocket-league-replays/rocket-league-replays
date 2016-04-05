import THREE from 'three'

// From main.js
export let scene

// From objects.js
export let currentFrame = -1
export let maxFrame = -1
export let frameData = {}
export let goalData = []
export let boostData = {}
export let secondsData = {}
export let actorData = {}
export let teamData = {}

// From utils.js
export const loader = new THREE.JSONLoader()
export const textureLoader = new THREE.TextureLoader()
textureLoader.crossOrigin = ''

// Helper functions to allow us to update these values.
export function setCurrentFrame (value) {
  currentFrame = value
}

export function setMaxFrame (value) {
  maxFrame = value
}

export function setScene (value) {
  scene = value
}

export function setFrameData (value) {
  frameData = value
}

export function setGoalData (value) {
  goalData = value
}

export function setBoostData (value) {
  boostData = value
}

export function setSecondsData (value) {
  secondsData = value
}

export function setActorData (value) {
  actorData = value
}

export function setTeamData (value) {
  teamData = value
}

