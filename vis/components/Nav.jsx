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
                        <a href="#" className={"nav-link active"}> Portfolio Optimization</a>
                    </li>
                    <li className={"nav-item"}>
                        <a href="#" className={"nav-link"}> Fundamental Analysis</a>
                    </li>
                    <li className={"nav-item"}>
                        <a href="#" className={"nav-link"}> Technical Analysis</a>
                    </li>
                </ul>
                {this.props.page === PAGES.PORTFOLIO &&
                <ul className="nav nav-pills">
                    {nav}
                </ul>}
            </div>
        )
    }
}