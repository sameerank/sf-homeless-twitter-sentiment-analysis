var app = angular.module('SFHomelessnessApp', ['nvd3']);

app.controller('MainCtrl', function($scope, $http, $timeout) {

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
                '<p>Count of previous similar tweets: ' + d.point.size + '</p>' +
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
    $scope.countingSimilarTweets = false;

    $scope.testTest = "5";

    $scope.$watch(function(scope){return scope.countingSimilarTweets;}, function(newValue, oldValue) {
            if (newValue) {
                // Not sure if this is the best way, but pausing before changing the data seems to give d3 a change to plot the data
                $timeout(countSeen, 500);
            }
        }
    );

    getData();

    function getData(){
        var tweets;
        var processedData = [];

        $http.get("/processed")
        .then(function(response){
            tweets = response.data;
            var i = 0
            while ( tweets[i] ) {

                processedData.push([
                    new Date(tweets[i].created_at),
                    tweets[i].polarity,
                    tweets[i].subjectivity,
                    NaN,
                    tweets[i].text,
                ]);

                i += 1;

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
            });

            $scope.countingSimilarTweets = true;
        })
    }

    function countSeen(){

        // Memoization to speed up this computation
        var timesSeen = {};
        timesSeen[$scope.data[0].values[0].text] = 0;
        var seenTweetsText = Object.keys(timesSeen);

        $scope.data.forEach(function(category){
            category.values.forEach(function(point){
                var notSeen = true;
                for (var j = 0; j < seenTweetsText.length; j++) {
                    var l = new Levenshtein( point.text, seenTweetsText[j] )
                    var fractionalDistance = l.distance / Math.max(point.text.length, seenTweetsText[j].length)
                    if (fractionalDistance < 0.5) {
                        timesSeen[seenTweetsText[j]] += 1;
                        notSeen = false;
                        point.size = timesSeen[seenTweetsText[j]];
                        break;
                    }
                }
                if (notSeen) {
                    timesSeen[point.text] = 0;
                    seenTweetsText = Object.keys(timesSeen);
                    point.size = timesSeen[point.text];
                }
            })
        })

        $scope.countingSimilarTweets = false;
    }
});
