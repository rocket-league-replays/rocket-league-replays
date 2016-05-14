/*global h337 replay_file_url*/
'use strict'

if ($('#chartContainer').length === 1 && (
    typeof duels !== 'undefined' && duels.length > 0 ||
    typeof doubles !== 'undefined' && doubles.length > 0 ||
    typeof solo_standard !== 'undefined' && solo_standard.length > 0 ||
    typeof standard !== 'undefined' && standard.length > 0
  )) {
  const chart = new CanvasJS.Chart('chartContainer',
    {
      zoomEnabled: true,
      title: {
        text: 'Historical ratings per playlist',
        fontSize: 14
      },
      axisX: {
        title: 'Date / Time',
        labelFontSize: 14,
        titleFontSize: 14,
        valueFormatString: ' '
      },
      axisY: {
        title: 'Rating',
        labelFontSize: 14,
        titleFontSize: 14
      },
      legend: {},
      data: [
        {
          name: 'Duels',
          type: 'line',
          // xValueType: 'dateTime',
          dataPoints: duels
        },
        {
          name: 'Doubles',
          type: 'line',
          // xValueType: 'dateTime',
          dataPoints: doubles
        },
        {
          name: 'Solo Standard',
          type: 'line',
          // xValueType: 'dateTime',
          dataPoints: solo_standard
        },
        {
          name: 'Standard',
          type: 'line',
          // xValueType: 'dateTime',
          dataPoints: standard
        }
      ],
      toolTip: {
        shared: true
      }
    })

  chart.render()
}

function render_heatmap (data) {
  const elements = document.querySelectorAll('.heatmap')
  for (const index in elements) {
    if (!elements.hasOwnProperty(index)) {
      return
    }

    const el = elements[index]

    let radius = 20
    let blur

    const heatmap = h337.create({
      container: el,
      radius,
      blur,
      minOpacity: 0.1,
      maxOpacity: 1,
      backgroundColor: '#fff'
    })

    // el.parentNode.querySelector('.heatmap-download').classList.add('hide')
    const selected_actor = el.getAttribute('data-actor-id')

    // Rework the data to work with the heatmap library.
    const formatted_data = []
    let min_value = null
    let max_value = null

    let max_x = null
    let max_y = null
    let min_x = null
    let min_y = null

    Object.keys(data[selected_actor]).forEach(function (item) {
      const value = data[selected_actor][item]
      let x = parseInt(item.split(',')[0], 10)
      let y = parseInt(item.split(',')[1], 10)

      // Rotate the points -90deg
      const rotation = (Math.PI / 2) * -1
      const rotatedX = Math.cos(rotation) * x - Math.sin(rotation) * y
      const rotatedY = Math.sin(rotation) * x + Math.cos(rotation) * y

      x = rotatedX
      y = rotatedY

      formatted_data.push({
        x,
        y,
        value
      })

      if (min_value === null || value < min_value) {
        min_value = value
      }

      if (max_value === null || value > max_value) {
        max_value = value
      }

      if (min_x === null || x < min_x) {
        min_x = x
      }

      if (min_y === null || y < min_y) {
        min_y = y
      }

      if (max_x === null || x > max_x) {
        max_x = x
      }

      if (max_y === null || y > max_y) {
        max_y = y
      }
    })

    // Re-work all of the values to be positive. 🌝
    min_x = Math.abs(min_x)
    min_y = Math.abs(min_y)
    max_x += min_x
    max_y += min_y

    const reformatted_data = []

    const canvas_width = el.offsetWidth
    const canvas_height = el.offsetHeight

    const stats = {}
    const quadrantData = {
      'topLeft': 0,
      'topRight': 0,
      'bottomLeft': 0,
      'bottomRight': 0
    }

    const thirdData = {
      'left': 0,
      'middle': 0,
      'right': 0
    }

    formatted_data.forEach(function (item) {
      // Rework the x values to be between 0 and `canvas width`.
      let offsetX = item.x + min_x
      offsetX /= max_x / canvas_width

      // Rework the y values to be between 0 and `canvas height`.
      let offsetY = item.y + min_y
      offsetY /= max_y / canvas_height

      // Which quadrant is this data point in?
      let quadrant = ''

      if (offsetX <= canvas_width / 2) {
        if (offsetY <= canvas_height / 2) {
          quadrant = 'topLeft'
        } else {
          quadrant = 'bottomLeft'
        }
      } else {
        if (offsetY <= canvas_height / 2) {
          quadrant = 'topRight'
        } else {
          quadrant = 'bottomRight'
        }
      }

      quadrantData[quadrant] += item.value

      // Which third is this data point in?
      let third = ''

      if (offsetX <= canvas_width / 3) {
        third = 'left'
      } else if (offsetX >= canvas_width / 3 && offsetX <= canvas_width / 3 * 2) {
        third = 'middle'
      } else {
        third = 'right'
      }

      thirdData[third] += item.value

      // Determine the value distribution.
      if (stats[item.value] === undefined) {
        stats[item.value] = 1
      } else {
        stats[item.value] += 1
      }

      // Push the data into the final array.
      reformatted_data.push({
        x: offsetX,
        y: offsetY,
        value: item.value
      })
    })

    heatmap.setData({
      min: Object.keys(stats).shift(),
      max: Object.keys(stats).pop(),
      data: reformatted_data
    })

    const quadrants = document.querySelector(`.quadrants[data-actor-id="${selected_actor}"]`)

    // Sum all of the quadrant data.
    const quadrantSum = Object.keys(quadrantData).reduce(function (sum, key) {
      return sum + parseInt(quadrantData[key], 10)
    }, 0)

    quadrants.querySelector('.top-left').innerHTML = `${(quadrantData.topLeft / quadrantSum * 100).toFixed(2)}%`
    quadrants.querySelector('.top-right').innerHTML = `${(quadrantData.topRight / quadrantSum * 100).toFixed(2)}%`
    quadrants.querySelector('.bottom-left').innerHTML = `${(quadrantData.bottomLeft / quadrantSum * 100).toFixed(2)}%`
    quadrants.querySelector('.bottom-right').innerHTML = `${(quadrantData.bottomRight / quadrantSum * 100).toFixed(2)}%`

    const thirds = document.querySelector(`.thirds[data-actor-id="${selected_actor}"]`)

    // Sum all of the quadrant data.
    const thirdSum = Object.keys(thirdData).reduce(function (sum, key) {
      return sum + parseInt(thirdData[key], 10)
    }, 0)

    thirds.querySelector('.left').innerHTML = `${(thirdData.left / thirdSum * 100).toFixed(2)}%`
    thirds.querySelector('.middle').innerHTML = `${(thirdData.middle / thirdSum * 100).toFixed(2)}%`
    thirds.querySelector('.right').innerHTML = `${(thirdData.right / thirdSum * 100).toFixed(2)}%`
  }
}

// Load up the JSON file.
if (typeof replay_file_url !== 'undefined') {
  const request = new XMLHttpRequest()
  request.open('GET', replay_file_url, true)

  request.onload = function () {
    if (this.status >= 200 && this.status < 400) {
      // Success!
      const data = JSON.parse(this.response)
      render_heatmap(data)
    } else {
      // We reached our target server, but it returned an error
      console.error(this.status)
    }
  }

  request.onerror = function (e) {
    // There was a connection error of some sort
    console.error(`Error Status: ${e.target.status}`)
  }

  request.send()
}
