// @flow
import React, {Component} from "react";
import {PAGES} from "../constants";
import type {NavProps} from "../types";

export class Nav1 extends Component<NavProps> {
    render() {
        return (
            <div className={"row"}>
                <ul className={"nav nav-tabs"}>
                    <li className={"nav-item"}>
                        <a href="#"
                           onClick={() => this.props.actions.pageClicked(PAGES.PORTFOLIO)}
                           className={"nav-link " + (this.props.page === PAGES.PORTFOLIO ? "active" : "")}> Portfolio Optimization</a>
                    </li>
                    <li className={"nav-item"}>
                        <a href="#"
                           onClick={() => this.props.actions.pageClicked(PAGES.TECHNICAL)}
                           className={"nav-link " + (this.props.page === PAGES.TECHNICAL ? "active" : "")}> Technical Analysis</a>
                    </li>
                </ul>
            </div>
        )
    }
}

export class Nav2 extends Component<NavProps> {
    render() {
        return (
            <div className={"row"}>
                {[PAGES.PORTFOLIO, PAGES.TECHNICAL].indexOf(this.props.page) > -1 &&
                [
                    <label key="nav2-label1" htmlFor="portfolio-type-selector" className={"col-1 col-form-label"}>
                        Type:
                    </label>,
                    <div key="nav2-div1" className={"col-2"}>
                        <select
                            id={"portfolio-type-selector"}
                            onChange={(e) => this.props.actions.portfolioTypeSelected(e.target.value)}
                            className={"form-control"}>
                            <option value={"mine"}>My Portfolios</option>
                            <option value={"snp500"}>S&P 500</option>
                        </select>
                    </div>,
                    <label key="nav2-label2" htmlFor={"portfolio-selector"} className={"col-1 col-form-label"}>
                        Portfolio:
                    </label>,
                    <div key="nav2-div2" className={"col-8"}>
                        <select
                            id={"portfolio-type-selector"}
                            onChange={(e) => this.props.actions.portfolioSelected(e.target.value)}
                            className="form-control">
                            {this.props.config.portfolios.map((p, i) => <option
                                key={"nav-" + p + i}
                                className={"nav-item"}
                                value={p.name} >{p.name}</option>)}
                        </select>
                    </div>
                ]}
            </div>
        );
    }
}