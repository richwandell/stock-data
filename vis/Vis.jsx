// @flow
import Main from "./components/Main"
import React from "react"
import ReactDOM from 'react-dom';
import type {Config, Portfolio} from "./types";
declare var $;

new class Vis {

    config: Config;

    constructor() {
        $.when(
            this.getConfig(),
            this.getSnP500(),
            this.getSnpPortfolios()
        ).then((config: Config, snp: Portfolio, snpPortfolios: Array<Portfolio>) => {
            this.config = config;
            this.config.portfolios.push(snp);
            ReactDOM.render(<Main
                snpPortfolios={snpPortfolios}
                config={this.config}/>, $("#react_renderer")[0])
        });
    }

    getSnpPortfolios() {
        let dfd = $.Deferred();
        $.ajax({
            url: "/portfolios/get/snpPortfolios",
            dataType: "json",
            method: "post",
            success: (res) => {
                dfd.resolve(res);
            }
        });
        return dfd;
    }

    getConfig () {
        let dfd = $.Deferred();

        $.getJSON("config.json", (data) => {
            dfd.resolve(data);
        });
        return dfd;
    }

    getSnP500() {
        let dfd = $.Deferred();
        $.ajax({
            url: "/portfolios/symbols/snp500",
            dataType: "json",
            method: "post",
            success: (res) => {
                dfd.resolve(res);
            }
        });
        return dfd;
    }
};

