// @flow
import React from "react";
import Chart from "./Chart";
import Table from "./Table";
import {perc} from "../Utils";
import PieChart from "./PieChart";
import type {PMProps, PMState} from "../types";
declare var $;

export default class PortfolioManagement extends React.Component<PMProps, PMState> {

    actions: {
        portfolioPercChanged: Function
    };

    constructor(props: PMProps) {
        super(props);
        this.state = {
            error: false,
            error_message: "",
            portfolio_perc: 100
        };
        this.actions = {
            portfolioPercChanged: (perc) => this.portfolioPercChanged(perc)
        };
    }

    portfolioPercChanged(perc: number) {
        this.setState({
            portfolio_perc: perc
        });
    }


    render() {
        let tableData = [];
        let risk = 0;
        let ret = 0;
        let sharpe = 0;
        if (
            this.props.selected_portfolio !== false
            && typeof(this.props.selected_portfolio.allocations) !== "undefined"
        ) {
            for (let i = 0; i < this.props.selected_portfolio.symbols.length; i++) {
                tableData.push({
                    asset: this.props.selected_portfolio.symbols[i],
                    allocation: this.props.selected_portfolio.allocations[i]
                })
            }
            risk = perc(this.props.selected_portfolio.risk_return_sharpe[0]) + "%";
            ret = perc(this.props.selected_portfolio.risk_return_sharpe[1]) + "%";
            sharpe = this.props.selected_portfolio.risk_return_sharpe[2].toFixed(2);
        }

        let sharpeColor = sharpe > 2 ? {
            color: "lime",
            "textShadow": "1px 1px 1px black"
        } : {
            color: "red",
            "textShadow": "1px 1px 1px black"
        };

        return (
            <div className={"page-portfolio-management"}>
                <div className={"row"}>
                    <div className={"col-4"}>
                        Risk <span id={"current-risk"}>{risk}</span>
                    </div>
                    <div className={"col-4"}>
                        Return <span id={"current-return"}>{ret}</span>
                    </div>
                    <div className={"col-4"}>
                        Sharpe Ratio <span style={sharpeColor} id={"current-sharpe"}>{sharpe}</span>
                    </div>
                </div>
                <div className={"row"}>
                    <div id={"table-container"} className={"col-5"}>
                        <Table
                            actions={$.extend({}, this.props.actions, this.actions)}
                            data={tableData}/>

                        <div id={"right-stats"}>
                            <ul>
                                <li>
                                    <PieChart tableData={tableData} />
                                </li>
                                <li>
                                    <div className="btn-group-vertical">
                                        <button
                                            type={"button"}
                                            className={"btn btn-primary"}>Show Max Sharpe Ratio</button>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <div id={"chart-container"} className={"col-7"}>
                        <Chart
                            actions={this.props.actions}
                            portfolio={this.props.selected_portfolio}/>
                    </div>
                </div>
            </div>
        )
    }
}