import React from "react";
import {perc} from "../Utils";


export default class Chart extends React.Component {

    shouldComponentUpdate(newProps, newState) {
        if (this.props.portfolio.name !== newProps.portfolio.name) {
            return true;
        }
        return false;
    }

    async componentDidMount() {
        this.res = {};
        this.res[this.props.portfolio.name] = await this.getData();
        this.renderChart(this.res[this.props.portfolio.name]);
        this.props.actions.portfolioClicked(this.sharpePortfolio);
    }

    async componentDidUpdate() {
        if (typeof(this.res[this.props.portfolio.name]) !== "undefined") {
            this.renderChart(this.res[this.props.portfolio.name]);
        } else {
            this.res[this.props.portfolio.name] = await this.getData();
            this.renderChart(this.res[this.props.portfolio.name]);
            this.props.actions.portfolioClicked(this.sharpePortfolio);
        }
    }

    createChart() {
        this.chart = new Highcharts.Chart({
            credits: {
                enabled: false
            },
            chart: {
                plotBackgroundColor: "rgb(234, 234, 242)",
                renderTo: 'highcharts-container'
            },
            title: {
                text: ''
            },
            yAxis: {
                gridLineWidth: 1,
                minorGridLineWidth: 0,
                labels: {
                    formatter: function () {
                        return (this.value * 100).toFixed(1) + "%";
                    }
                },
                title: {
                    enabled: true,
                    text: "Annualized Monthly Return"
                }
            },
            xAxis: {
                gridLineWidth: 1,
                labels: {
                    formatter: function () {
                        return (this.value * 100).toFixed(1) + "%";
                    }
                },
                title: {
                    enabled: true,
                    text: "Annualized Monthly Risk"
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [],

            plotOptions: {
                scatter: {
                    dataLabels: {
                        format: "{point.name}",
                        enabled: true
                    }
                }
            },
            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500
                    },
                    chartOptions: {
                        legend: {
                            align: 'center',
                            verticalAlign: 'bottom',
                            layout: 'horizontal'
                        },
                        yAxis: {
                            labels: {
                                align: 'left',
                                x: 0,
                                y: -5
                            },
                            title: {
                                text: null
                            }
                        },
                        subtitle: {
                            text: null
                        },
                        credits: {
                            enabled: false
                        }
                    }
                }]
            }
        });
    }

    async getData() {
        let dfd = $.Deferred();
        let p = this.props.portfolio;
        $.ajax({
            url: "/portfolios/get/" + p.name,
            dataType: "json",
            method: "post",
            success: (res) => {
                dfd.resolve(res);
            }
        });
        return dfd;
    }

    async renderChart(res) {
        this.createChart();



        let data = [];
        let assets = res.assets;

        for (let i = 0; i < assets.assets.length; i++) {
            data.push({
                name: assets.assets[i],
                y: assets.asset_reward[i],
                x: assets.asset_risk[i]
            })
        }
        let data1 = [];
        let portfolios = res.efficient.portfolios;
        let efficientSymbols = res.efficient.symbols;
        let maxSharpeValue = 0.0;
        let maxSharpePoint = [];
        let sharpePortfolio = [];
        let efficientPortfolioStrings = [];
        let minVariance = Infinity;
        let minVarianceIndex = Infinity;
        for(let i = 0; i < portfolios.length; i++){
            if(portfolios[i][0] < minVariance) {
                minVarianceIndex = i;
                minVariance = portfolios[i][0];
            }
        }
        portfolios = portfolios.slice(minVarianceIndex, portfolios.length);
        for (let i = 0; i < portfolios.length; i++) {
            data1.push({
                name: 'Portfolio ' + i,
                x: portfolios[i][0],
                y: portfolios[i][1]
            });
            let portfolioString = "";
            for (let j = 3; j < portfolios[i].length; j++) {
                if ((portfolios[i][j] * 100).toFixed(2) > 0) {
                    portfolioString += efficientSymbols[j - 3] + ": " + perc(portfolios[i][j]) + "% <br>";
                }
            }
            efficientPortfolioStrings.push(portfolioString);
            if (portfolios[i][2] > maxSharpeValue) {
                maxSharpePoint = {
                    name: "Maximum Sharpe Ratio",
                    x: portfolios[i][0],
                    y: portfolios[i][1]
                };
                maxSharpeValue = portfolios[i][2];
                sharpePortfolio = portfolios[i].slice(0);
                let risk = sharpePortfolio.shift();
                let ret = sharpePortfolio.shift();
                let sharpe = sharpePortfolio.shift();
                this.sharpePortfolio = {
                    risk_return_sharpe: [risk, ret, sharpe],
                    allocations: sharpePortfolio,
                    symbols: efficientSymbols,
                    name: this.props.portfolio.name
                };
            }
        }
        let sharpePortfolioString = "";
        for (let i = 0; i < sharpePortfolio.length; i++) {
            if ((sharpePortfolio[i] * 100).toFixed(2) > 0) {
                sharpePortfolioString += efficientSymbols[i] + ": " + perc(sharpePortfolio[i]) + "% <br>";
            }
        }


        this.chart.addSeries({
            name: "Assets",
            data: data,
            type: "scatter",
            marker: {
                enabled: true,
                radius: 5,
                symbol: "triangle"
            },
            dataLabels: {
                enabled: true
            },
            states: {
                hover: {
                    enabled: false
                }
            }
        });
        let actions = this.props.actions;
        let portfolio = this.props.portfolio;
        this.chart.addSeries({
            name: 'Efficient Frontier',
            data: data1,
            type: "spline",
            color: "rgb(124, 181, 236)",
            marker: {
                enabled: true,
                radius: 3
            },
            tooltip: {
                pointFormatter: function () {
                    return efficientPortfolioStrings[this.index];
                }
            },
            cursor: 'pointer',
            point: {
                events: {
                    click: function () {
                        portfolio.symbols = efficientSymbols;
                        portfolio.allocations = portfolios[this.index].slice(3);
                        portfolio.risk_return_sharpe = portfolios[this.index].slice(0, 3);
                        actions.portfolioClicked(portfolio);
                    }
                }
            }
        });

        this.chart.addSeries({
            name: 'Maximum Sharpe Ratio',
            data: [maxSharpePoint],
            type: "scatter",
            color: "red",
            marker: {
                enabled: true,
                radius: 10,
            },
            tooltip: {
                pointFormatter: function () {
                    return sharpePortfolioString;
                }
            },
        });
    }

    render() {
        return (
            <div id="highcharts-container" className={"highcharts-container"}>

            </div>
        );
    }
}