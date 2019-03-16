// @flow
import React from "react";
import PortfolioManagement from "./PortfolioManagement";
import {PAGES, PORTFOLIO_TYPES as PF} from "../constants";
import {Nav1, Nav2} from "./Nav";
import TechnicalAnalysis from "./TechnicalAnalysis";
import type {MainProps, MainState, Portfolio, Actions, PortfolioAllocation} from "../types";
declare var $;

export default class Main extends React.Component<MainProps, MainState> {

    portfolios: Array<Portfolio>;
    snpPortfolios: Array<Portfolio>;
    actions: Actions;

    constructor(props: MainProps) {
        super(props);
        this.portfolios = props.config.portfolios;
        this.snpPortfolios = props.snpPortfolios;
        this.state = {
            page: PAGES.PORTFOLIO,
            selected_portfolio: props.config.portfolios[0],
            selected_symbol: props.config.portfolios[0].symbols[0],
            selected_portfolio_type: PF.MINE
        };

        this.actions = {
            setPortfolio: (p: Portfolio) => this.setPortfolio(p),
            pageClicked: (p: string) => this.pageClicked(p),
            portfolioSelected: (p: string) => this.portfolioSelected(p),
            portfolioTypeSelected: (type: string) => this.portfolioTypeSelected(type),
            symbolClicked: (pa: PortfolioAllocation) => this.symbolClicked(pa)
        };
    }

    symbolClicked(pa: PortfolioAllocation) {
        this.setState({
            page: PAGES.TECHNICAL
        });
    }

    portfolioTypeSelected(type: string) {
        let selected = this.portfolios[0];
        if(type === PF.SNP) {
            selected = this.snpPortfolios[0];
        }
        this.setState({
            selected_portfolio_type: type,
            selected_portfolio: selected
        });
    }

    portfolioSelected(portfolio: string) {
        let p;
        if(this.state.selected_portfolio_type === PF.MINE) {
            p = this.portfolios.find((i) => i.name === portfolio);
        } else {
            p = this.snpPortfolios.find((i) => i.name === portfolio);
        }
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
                    portfolios={this.state.selected_portfolio_type === PF.MINE ?
                    this.portfolios : this.snpPortfolios}
                    page={this.state.page}/>

                {this.state.page === PAGES.PORTFOLIO &&
                <Nav2
                    selected_portfolio={this.state.selected_portfolio}
                    actions={this.actions}
                    portfolios={this.state.selected_portfolio_type === PF.MINE ?
                    this.portfolios : this.snpPortfolios}
                    page={this.state.page}/>}

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