import Main from "./components/Main"
import React from "react"
import ReactDOM from 'react-dom';

new class Vis {

    constructor() {
        $.when(
            this.getConfig(),
            this.getSnP500()
        ).then((config, snp) => {
            this.config = config;
            this.config.portfolios.push(snp);
            ReactDOM.render(<Main
                config={this.config}/>, $("#react_renderer")[0])
        });
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

