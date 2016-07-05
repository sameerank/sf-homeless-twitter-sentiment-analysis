var app = angular.module('SFHomelessnessApp', ['nvd3']);

app.controller('MainCtrl', function($scope) {
    $scope.options = {
        chart: {
            type: 'scatterChart',
            height: 450,
            color: d3.scale.category10().range(),
            scatter: {
                onlyCircles: false
            },
            showDistX: true,
            showDistY: true,
            tooltipContent: function(key) {
                return '<h3>' + key + '</h3>';
            },
            duration: 350,
            xAxis: {
                axisLabel: 'Datetime',
                tickFormat: function(date){
                    return d3.time.format('%H:%M:%S')(new Date(date));
                }
            },
            yAxis: {
                axisLabel: 'Sentiment',
                tickFormat: function(d){
                    return d3.format('.02f')(d);
                },
                axisLabelDistance: -5
            },
            zoom: {
                //NOTE: All attributes below are optional
                enabled: false,
                scaleExtent: [1, 10],
                useFixedDomain: false,
                useNiceScale: false,
                horizontalOff: false,
                verticalOff: false,
                unzoomEventType: 'dblclick.zoom'
            }
        }
    };

    $scope.data = getData();

    /* Random Data Generator (took from nvd3.org) */
    function getData(){
        var data = [],
            groups = 1,
            points = sfHomelessData.length;

        for (var i = 0; i < groups; i++) {
            data.push({
                key: 'Group ' + i,
                values: []
            });

            for (var j = 0; j < points; j++) {
                data[i].values.push({
                    x: sfHomelessData[j][0]
                    , y: sfHomelessData[j][1]
                    , size: sfHomelessData[j][2]
                    , shape: 'circle'
                });
            }
        }
        return data;
    }
});
