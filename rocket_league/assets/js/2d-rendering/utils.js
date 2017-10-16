// Convert degrees to radians
export function r (d) {
  return d * (Math.PI / 180)
}

// Convert radians to degrees
export function d (r) {
  return r * (180 / Math.PI)
}

export function formatTime (time) {
  time = Math.ceil(time)

  // Minutes and seconds
  let mins = ~~(time / 60)
  let secs = time % 60

  // Hours, minutes and seconds
  const hrs = ~~(time / 3600)
  mins = ~~((time % 3600) / 60)
  secs = time % 60

  // Output like "1:01" or "4:03:59" or "123:03:59"
  let ret = ''

  if (hrs > 0) {
    ret += `${hrs}:${(mins < 10 ? '0' : '')}`
  }

  ret += `${mins}:${(secs < 10 ? '0' : '')}`
  ret += `${secs.toFixed(0)}`
  return ret
}

export function calculatePitch (actor_pitch) {
  const full_min = 0
  const full_max = 65536
  const full_range = full_max - full_min

  const deg_min = -1
  const deg_max = 1
  const deg_range = deg_max - deg_min

  let pitch = (((actor_pitch - full_min) * deg_range) / full_range) + deg_min

  // r(90) + actor.pitch * Math.PI * -1
  pitch += r(90)
  pitch *= Math.PI
  pitch *= -1

  return pitch
}
