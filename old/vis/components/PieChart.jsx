import React from "react";

export default class PieChart extends React.Component {

    makeSeries(){
        let series = [];
        for(let row of this.props.tableData){
            if((Number(row.allocation) * 100).toFixed(2) > 0){
                series.push({
                    y: row.allocation,
                    name: row.asset
                })
            }
        }
        return {'id': 'one', data: series};
    }

    componentDidMount() {
        this.createChart();
        this.chart.addSeries(this.makeSeries());
    }

    componentDidUpdate(){
        this.chart.get('one').remove();
        this.chart.addSeries(this.makeSeries());
    }

    createChart() {
        let pieColors = (function () {
            let colors = [],
                base = "#0074e4",
                i;

            for (i = 0; i < 10; i += 1) {
                // Start out with a darkened base color (negative brighten), and end
                // up with a much brighter color
                colors.push(Highcharts.Color(base).brighten((i - 3) / 7).get());
            }
            base = "#ef1515";
            for (i = 0; i < 10; i += 1) {
                // Start out with a darkened base color (negative brighten), and end
                // up with a much brighter color
                colors.push(Highcharts.Color(base).brighten((i - 3) / 7).get());
            }
            return colors;
        }());


        this.chart = new Highcharts.Chart('highcharts-container-1', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            credits: {
                enabled: false
            },
            title: {
                text: ''
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    colors: pieColors,
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b><br>{point.percentage:.1f} %',
                        distance: -50,
                        filter: {
                            property: 'percentage',
                            operator: '>',
                            value: 4
                        }
                    }
                }
            },
            series: []
        });
    }

    render() {
        return (
            <div id={"highcharts-container-1"}/>
        );
    }
}