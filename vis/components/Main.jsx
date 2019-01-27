import React from "react";
import Chart from "./Chart";
import Table from "./Table";
import PortfolioManagement from "./PortfolioManagement";
import {PAGES} from "../constants";
import Nav from "./Nav";
import TechnicalAnalysis from "./TechnicalAnalysis";


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
            portfolioClicked: (p) => this.portfolioClicked(p),
            pageClicked: (p) => this.pageClicked(p)
        };
    }

    pageClicked(p) {
        this.setState({
            page: p
        })
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
        return (
            <div className="container-fluid">
                <Nav
                    selected_portfolio={this.state.selected_portfolio}
                    actions={this.actions}
                    config={this.props.config}
                    page={this.state.page}/>
                <div className="row">

                    {this.state.page === PAGES.PORTFOLIO &&
                    <PortfolioManagement
                        actions={this.actions}
                        selected_portfolio={this.state.selected_portfolio} />}
                    {this.state.page === PAGES.TECHNICAL &&
                    <TechnicalAnalysis
                        actions={this.actions}
                        selected_portfolio={this.state.selected_portfolio}/> }
                </div>
            </div>

        );
    }
}