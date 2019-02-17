// @flow
import React from "react";
import PortfolioManagement from "./PortfolioManagement";
import {PAGES} from "../constants";
import {Nav1, Nav2} from "./Nav";
import TechnicalAnalysis from "./TechnicalAnalysis";
import type {MainProps, MainState, Portfolio, Actions} from "../types";
declare var $;

export default class Main extends React.Component<MainProps, MainState> {

    portfolios: Array<Portfolio>;
    actions: Actions;

    constructor(props: MainProps) {
        super(props);
        this.portfolios = props.config.portfolios;
        this.state = {
            page: PAGES.PORTFOLIO,
            selected_portfolio: props.config.portfolios[0],
            selected_symbol: props.config.portfolios[0].symbols[0]
        };

        this.actions = {
            setPortfolio: (p) => this.setPortfolio(p),
            pageClicked: (p) => this.pageClicked(p),
            portfolioSelected: (p) => this.portfolioSelected(p)
        };
    }

    portfolioSelected(portfolio: string) {
        let p = this.portfolios.find((i) => i.name === portfolio);
        this.setState({
            selected_portfolio: p
        });
    }

    pageClicked(p: string) {
        this.setState({
            page: p
        })
    }


    setPortfolio(p: Portfolio) {
        let portfolio = $.extend({}, this.state.selected_portfolio, p);

        this.setState({
            selected_portfolio: portfolio
        });
    }

    render() {
        return (
            <div className="container-fluid">
                <Nav1
                    selected_portfolio={this.state.selected_portfolio}
                    actions={this.actions}
                    config={this.props.config}
                    page={this.state.page}/>

                <Nav2
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