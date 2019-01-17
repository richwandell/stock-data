import Main from "./components/Main"
import React from "react"
import ReactDOM from 'react-dom';

new class Vis {

    constructor() {
        $.getJSON("config.json", (data) => {
            this.config = data;
            ReactDOM.render(<Main config={this.config}/>, $("#react_renderer")[0])
        });
    }
};

