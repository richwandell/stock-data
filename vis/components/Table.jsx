// @flow
import React from "react";
import {perc} from "../Utils";
import type {PortfolioAllocation, TableProps} from "../types";

export default class Table extends React.Component<TableProps> {
    render() {
        let data = this.props.data.filter((i) => {
                return perc(i.allocation) > 0;
            });
        data.sort((a, b) => b.allocation - a.allocation);

        return (
            <div id="allocation_table" >
                <table>
                    <thead>
                        <tr>
                            <td/>
                            <td>Symbol</td>
                            <td>Allocation</td>
                        </tr>
                    </thead>
                    <tbody>
                    {data.map((item: PortfolioAllocation, index: number) =>
                        <tr key={"allocation-" + index}>
                            <td>{index}</td>
                            <td>
                                <a href="javascript:void(0);"
                                   onClick={() => this.props.actions.symbolClicked(item)}>{item.asset}</a>
                            </td>
                            <td>{perc(item.allocation)}</td>
                        </tr>)}
                    </tbody>
                </table>
            </div>
        );
    }
}