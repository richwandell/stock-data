import React from "react";
import Chart from "./Chart";
import Table from "./Table";
import {perc} from "../Utils";
import PieChart from "./PieChart";

export default class PortfolioManagement extends React.Component {

    constructor(props) {
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

    portfolioPercChanged(perc) {
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
            risk = perc(this.props.selected_portfolio.risk_return_sharpe[0]);
            ret = perc(this.props.selected_portfolio.risk_return_sharpe[1]);
            sharpe = perc(this.props.selected_portfolio.risk_return_sharpe[2]);
        }



        return (
            <div className={"scrollable container-fluid"}>
                <div className={"row"}>
                    <div id={"chart-container"}>
                        <Chart
                            actions={this.props.actions}
                            portfolio={this.props.selected_portfolio}/>
                    </div>
                </div>
                <div className={"row"}>
                    <div id={"table-container"}>
                        <Table
                            actions={$.extend({}, this.props.actions, this.actions)}
                            data={tableData}/>

                        <div id={"right-stats"}>
                            <ul>
                                <li>
                                    <PieChart tableData={tableData} />
                                </li>
                                <li>
                                    Risk <span id={"current-risk"}>{risk}</span>
                                </li>
                                <li>
                                    Return <span id={"current-return"}>{ret}</span>
                                </li>
                                <li>
                                    Sharpe Ratio <span id={"current-sharpe"}>{sharpe}</span>
                                </li>

                                <li>
                                    <div className="btn-group-vertical">
                                        <button
                                            type={"button"}
                                            className={"btn btn-primary"}>Show Max Sharpe Ratio</button>
                                        <button
                                            type="button"
                                            className="btn btn-primary">Calculate Portfolio</button>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}