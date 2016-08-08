var app = angular.module('SFHomelessnessApp', ['nvd3']);

app.controller('MainCtrl', function($scope, $http) {

    $scope.options = {
        chart: {
            type: 'scatterChart',
            height: 450,
            color: ['#00e3e5', '#29d500', '#c67800', '#bf0000'],
            scatter: {
                onlyCircles: false
            },
            noData: 'Loading data and calculating stuff ... This will take about a minute.',
            showDistX: true,
            showDistY: true,
            useInteractiveGuideline: false,
            interactive: true,
            tooltips: true,
            tooltip: {
              contentGenerator: function(d) {
                return '<p>Subjectivity index: ' + d.point.subjectivity + ' ('+ d.series[0].key + ')</p>' +
                '<p>Seen before: ' + d.point.size + ' times</p>' +
                '<p>Sentiment polarity: ' + d.series[0].value + '</p>' +
                '<p>Tweeted text: ' + d.point.text + '</p>';
              }
            },
            duration: 350,
            xAxis: {
                axisLabel: 'Date',
                tickFormat: function(date){
                    return d3.time.format('%b %e, %Y')(new Date(date));
                }
            },
            yAxis: {
                axisLabel: 'Sentiment Polarity',
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

    $scope.data = [];
    getData();

    function getData(){
        var tweets;
        var processedData = [];

        $http.get("/processed")
        .then(function(response){
            tweets = response.data;
            var i = 0
            // Memoization to speed up this computation
            var timesSeen = {};
            timesSeen[tweets[i].text] = 0;
            var seenTweetsText = Object.keys(timesSeen);
            while ( tweets[i] ) {
                var notSeen = true;
                for (var j = 0; j < seenTweetsText.length; j++) {
                    var l = new Levenshtein( tweets[i].text, seenTweetsText[j] )
                    var fractionalDistance = l.distance / Math.max(tweets[i].text.length, seenTweetsText[j].length)
                    if (fractionalDistance < 0.5) {
                        timesSeen[seenTweetsText[j]] += 1;
                        notSeen = false;
                        processedData.push([
                            new Date(tweets[i].created_at),
                            tweets[i].polarity,
                            tweets[i].subjectivity,
                            timesSeen[seenTweetsText[j]],
                            tweets[i].text,
                        ]);
                        break;
                    }
                }

                if (notSeen) {
                    timesSeen[tweets[i].text] = 0;
                    seenTweetsText = Object.keys(timesSeen);
                    processedData.push([
                        new Date(tweets[i].created_at),
                        tweets[i].polarity,
                        tweets[i].subjectivity,
                        timesSeen[tweets[i].text],
                        tweets[i].text,
                    ]);
                }

                i += 1;
                $scope.tweetsAnalyzed = i;
            }
            $scope.data = [0.25, 0.5, 0.75, 1.0].map(function(cutoff, idx){
                return {
                    key: ["Highly Objective", "Slightly Objective", "Slightly Subjective", "Highly Subjective"][idx],
                    values: processedData.filter(function(d){
                        return (d[2] < cutoff) && (d[2] >= cutoff - 0.25)
                    }).map(function(d){
                        return {
                          x: d[0]
                          , y: d[1]
                          , size: d[3]
                          , shape: 'circle'
                          , subjectivity: d[2]
                          , text: d[4]
                        }
                    })
                }
            })
        });
    }
});
