if ($('#chartContainer').length == 1 && (
    duels.length > 0 ||
    doubles.length > 0 ||
    solo_standard.length > 0 ||
    standard.length > 00
)) {

    var chart = new CanvasJS.Chart("chartContainer",
    {
        zoomEnabled: true,
        title:{
            text: "Historical ratings per playlist",
            fontSize: 14,
        },
        axisX: {
            title: "Date / Time",
            labelFontSize: 14,
            titleFontSize: 14,
            // labelFormatter: function(e) {
            //     return "Update ", e.value, "DD/MM/YYYY");
            // },
            valueFormatString: " "
        },
        axisY: {
            title: "Rating",
            labelFontSize: 14,
            titleFontSize: 14,
        },
        legend: {},
        data: [
            {
                name: "Duels",
                type: "line",
                // xValueType: "dateTime",
                dataPoints: duels,
            },
            {
                name: "Doubles",
                type: "line",
                // xValueType: "dateTime",
                dataPoints: doubles,
            },
            {
                name: "Solo Standard",
                type: "line",
                // xValueType: "dateTime",
                dataPoints: solo_standard,
            },
            {
                name: "Standard",
                type: "line",
                // xValueType: "dateTime",
                dataPoints: standard,
            }
        ],
        toolTip: {
            shared: true,
        }
    });

    chart.render();
}
