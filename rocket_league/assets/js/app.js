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
