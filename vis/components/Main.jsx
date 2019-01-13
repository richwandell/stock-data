import React from "react";
import Chart from "./Chart";


export default class Main extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            selected_portfolio: props.config.portfolios[0],
            symbol_selected: false,
            selected_symbol: props.config.portfolios[0].symbols[0]
        };
        this.actions = {
            portfolioClicked: (p) => this.portfolioClicked(p)
        };
    }


    portfolioClicked(p) {
        this.setState({
            selected_portfolio: p
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
                if(value > 0) {
                    leftNav.push(<li className={"nav-item"}>
                        <label>
                            <a href="#" onClick={(e) => this.symbolClicked(symbol)}>{symbol}</a>
                        </label>
                        <input
                            id={symbol + "_input"}
                            value={value}
                            type={"number"}/>
                    </li>)
                }
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
                    <div className="col-2">
                        <div className={"scrollable"}>
                            <ul className={"nav nav-pills"}>
                                {leftNav}
                            </ul>
                        </div>
                    </div>
                    <div className="col-10">
                        <div className={"scrollable"}>
                        {this.state.selected_portfolio !== false && <Chart
                            actions={this.actions}
                            portfolio={this.state.selected_portfolio}/>}
                        </div>
                    </div>
                </div>
            </div>

        );
    }
}