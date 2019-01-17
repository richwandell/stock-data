import React from "react";
import Chart from "./Chart";
import Table from "./Table";
import PortfolioManagement from "./PortfolioManagement";
import {PAGES} from "../constants";


export default class Main extends React.Component {

    constructor(props) {
        super(props);
        this.portfolios = props.config.portfolios;
        this.state = {
            page: PAGES.PORTFOLIO,
            selected_portfolio: props.config.portfolios[0],
            symbol_selected: false,
            selected_symbol: props.config.portfolios[0].symbols[0]
        };
        this.actions = {
            portfolioClicked: (p) => this.portfolioClicked(p)
        };
    }


    portfolioClicked(p) {
        let portfolio = $.extend({}, this.state.selected_portfolio, p);
        this.setState({
            selected_portfolio: portfolio
        });
    }

    symbolClicked(s) {
        this.setState({
            symbol_selected: true,
            selected_symbol: s
        });
    }

    render() {
        const config = this.props.config;

        let nav = []
        for(let p of config.portfolios){
            nav.push(<li className={"nav-item"} onClick={(e) => this.portfolioClicked(p)} >
                <a href="#" className={"nav-link " + (this.state.selected_portfolio.name === p.name ? "active" : "")} >{p.name}</a>
            </li>)
        }

        let leftNav = [];
        if(this.state.selected_portfolio) {
            let selectedPortfolio = this.state.selected_portfolio;
            for(let i = 0; i < selectedPortfolio.symbols.length; i++){
                let symbol = selectedPortfolio.symbols[i];
                let value = 0;
                if(typeof(selectedPortfolio.allocations) !== "undefined") {
                    value = (selectedPortfolio.allocations[i] * 100).toFixed(2);
                }

                leftNav.push(
                    <div className="form-group row">
                        <label className="col-sm-2 col-form-label">{symbol}</label>
                        <div className="col-sm-10">
                            <input
                                id={symbol + "_input"}
                                value={value}
                                type={"number"}
                                className="form-control" />
                        </div>
                    </div>
                );
            }
        }



        return (
            <div className="container-fluid">
                <div className={"row"}>
                    <ul className="nav nav-pills">
                        {nav}
                    </ul>
                </div>
                <div className="row">

                    {this.state.page === PAGES.PORTFOLIO &&
                    <PortfolioManagement
                        actions={this.actions}
                        selected_portfolio={this.state.selected_portfolio} />}

                </div>
            </div>

        );
    }
}