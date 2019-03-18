// @flow
import React from "react";
import type {StockHistory, TAProps} from "../types";

declare var $;
declare var Highcharts;

export default class TechnicalAnalysis extends React.Component<TAProps> {

    chart: Highcharts.StockChart;

    async getData(): StockHistory {
        let dfd = $.Deferred();
        $.ajax({
            url: `/stocks/get/${this.props.selected_symbol}`,
            dataType: "json",
            method: "post",
            success: (res) => {
                dfd.resolve(res);
            }
        });
        return dfd;
    }

    async renderStock() {
        let data = await this.getData();
        let ohlc = data.ohlc;
        let volume = data.volume;
        this.setTheme();
        this.chart = new Highcharts.StockChart('highstock-container', {
            yAxis: [{
                labels: {
                    align: 'left'
                },
                height: '80%',
                resize: {
                    enabled: true
                }
            }, {
                labels: {
                    align: 'left'
                },
                top: '80%',
                height: '20%',
                offset: 0
            }],
            tooltip: {
                shape: 'square',
                headerShape: 'callout',
                borderWidth: 0,
                shadow: false,
                positioner: function (width, height, point) {
                    var chart = this.chart,
                        position;

                    if (point.isHeader) {
                        position = {
                            x: Math.max(
                                // Left side limit
                                chart.plotLeft,
                                Math.min(
                                    point.plotX + chart.plotLeft - width / 2,
                                    // Right side limit
                                    chart.chartWidth - width - chart.marginRight
                                )
                            ),
                            y: point.plotY
                        };
                    } else {
                        position = {
                            x: point.series.chart.plotLeft,
                            y: point.series.yAxis.top - chart.plotTop
                        };
                    }

                    return position;
                }
            },
            series: [{
                type: 'candlestick',
                id: `${this.props.selected_symbol}-ohlc`,
                name: `${this.props.selected_symbol} Stock Price`,
                data: ohlc
            }, {
                type: 'column',
                id: `${this.props.selected_symbol}-volume`,
                name: `${this.props.selected_symbol} Volume`,
                data: volume,
                yAxis: 1
            }],
            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 800
                    },
                    chartOptions: {
                        rangeSelector: {
                            inputEnabled: false
                        }
                    }
                }]
            }
        });
    }

    setTheme() {
        Highcharts.theme = {
            colors: ['#f45b5b', '#8085e9', '#8d4654', '#7798BF', '#aaeeee',
                '#ff0066', '#eeaaee', '#55BF3B', '#DF5353', '#7798BF', '#aaeeee'],
            chart: {
                backgroundColor: null,
                style: {
                    fontFamily: 'Signika, serif'
                }
            },
            title: {
                style: {
                    color: 'black',
                    fontSize: '16px',
                    fontWeight: 'bold'
                }
            },
            subtitle: {
                style: {
                    color: 'black'
                }
            },
            tooltip: {
                borderWidth: 0
            },
            legend: {
                itemStyle: {
                    fontWeight: 'bold',
                    fontSize: '13px'
                }
            },
            xAxis: {
                labels: {
                    style: {
                        color: '#6e6e70'
                    }
                }
            },
            yAxis: {
                labels: {
                    style: {
                        color: '#6e6e70'
                    }
                }
            },
            plotOptions: {
                series: {
                    shadow: true
                },
                candlestick: {
                    lineColor: '#404048'
                },
                map: {
                    shadow: false
                }
            },

            // Highstock specific
            navigator: {
                xAxis: {
                    gridLineColor: '#D0D0D8'
                }
            },
            rangeSelector: {
                buttonTheme: {
                    fill: 'white',
                    stroke: '#C0C0C8',
                    'stroke-width': 1,
                    states: {
                        select: {
                            fill: '#D0D0D8'
                        }
                    }
                }
            },
            scrollbar: {
                trackBorderColor: '#C0C0C8'
            },

            // General
            background2: '#E0E0E8'

        };

        // Apply the theme
        Highcharts.setOptions(Highcharts.theme);
    }

    componentDidMount() {
        this.renderStock();
    }

    componentWillUpdate() {
        this.renderStock();
    }

    render() {
        return (
            <div id={"highstock-container"}/>
        );
    }
}

// $.getJSON('https://www.highcharts.com/samples/data/aapl-ohlcv.json', function (data) {
//
//     // split the data set into ohlc and volume
//     var ohlc = [],
//         volume = [],
//         dataLength = data.length,
//         i = 0;
//
//     for (i; i < dataLength; i += 1) {
//         ohlc.push([
//             data[i][0], // the date
//             data[i][1], // open
//             data[i][2], // high
//             data[i][3], // low
//             data[i][4] // close
//         ]);
//
//         volume.push([
//             data[i][0], // the date
//             data[i][5] // the volume
//         ]);
//     }
//
//     Highcharts.stockChart('container', {
//         yAxis: [{
//             labels: {
//                 align: 'left'
//             },
//             height: '80%',
//             resize: {
//                 enabled: true
//             }
//         }, {
//             labels: {
//                 align: 'left'
//             },
//             top: '80%',
//             height: '20%',
//             offset: 0
//         }],
//         tooltip: {
//             shape: 'square',
//             headerShape: 'callout',
//             borderWidth: 0,
//             shadow: false,
//             positioner: function (width, height, point) {
//                 var chart = this.chart,
//                     position;
//
//                 if (point.isHeader) {
//                     position = {
//                         x: Math.max(
//                             // Left side limit
//                             chart.plotLeft,
//                             Math.min(
//                                 point.plotX + chart.plotLeft - width / 2,
//                                 // Right side limit
//                                 chart.chartWidth - width - chart.marginRight
//                             )
//                         ),
//                         y: point.plotY
//                     };
//                 } else {
//                     position = {
//                         x: point.series.chart.plotLeft,
//                         y: point.series.yAxis.top - chart.plotTop
//                     };
//                 }
//
//                 return position;
//             }
//         },
//         series: [{
//             type: 'ohlc',
//             id: 'aapl-ohlc',
//             name: 'AAPL Stock Price',
//             data: ohlc
//         }, {
//             type: 'column',
//             id: 'aapl-volume',
//             name: 'AAPL Volume',
//             data: volume,
//             yAxis: 1
//         }],
//         responsive: {
//             rules: [{
//                 condition: {
//                     maxWidth: 800
//                 },
//                 chartOptions: {
//                     rangeSelector: {
//                         inputEnabled: false
//                     }
//                 }
//             }]
//         }
//     });
// });