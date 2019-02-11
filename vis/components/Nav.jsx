import React, {Component} from "react";
import {PAGES} from "../constants";

export default class Nav extends Component {
    render() {

        let nav = [];
        for(let p of this.props.config.portfolios){
            nav.push(<li className={"nav-item"} onClick={(e) => this.props.actions.portfolioClicked(p)} >
                <a href="#" className={"nav-link " + (this.props.selected_portfolio.name === p.name ? "active" : "")} >{p.name}</a>
            </li>)
        }

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
                {[PAGES.PORTFOLIO, PAGES.TECHNICAL].indexOf(this.props.page) > -1 &&
                <ul className="nav nav-pills">
                    {nav}
                </ul>}
            </div>
        )
    }
}