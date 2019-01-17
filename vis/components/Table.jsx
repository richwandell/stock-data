import React from "react";
/** @type {Math.MathJsStatic} **/
import math from "mathjs"
import same from "deep-equal"

export default class Table extends React.Component {

    shouldComponentUpdate(nextProps, nextState){
        if(!same(this.props, nextProps)){
            return true;
        }
        return false;
    }

    tableValueChanged(changes) {
        if (!changes) return;
        let data = this.hot.getDataAtCol(1);
        data = math.round(math.multiply(100, data));
        this.props.actions.portfolioPercChanged(math.sum(data));
    }

    getHotSettings() {
        return {
            afterChange: (changes) => this.tableValueChanged(changes),
            data: this.props.data,
            columns: [
                {
                    data: 'asset',
                    type: 'text',

                    readOnly: true
                },
                {
                    data: 'allocation',
                    type: 'numeric',
                    numericFormat: {
                        pattern: '0.00'
                    }
                }
            ],
            autoWrapRow: true,
            rowHeaders: true,
            colHeaders: [
                'Asset',
                'Allocation'
            ],
            contextMenu: true,
            columnSorting: {
                sortEmptyCells: true,
                initialConfig: {
                    column: 1,
                    sortOrder: 'desc'
                }
            },
            width: 233
        };
    }

    createHotTable() {
        this.hotElement = $("#hot-table-1")[0];
        /** @type {Handsontable} **/
        this.hot = new Handsontable(this.hotElement, this.getHotSettings());
    }

    componentDidUpdate() {
        this.hot.loadData(this.props.data);
        this.hot
            .getPlugin('columnSorting')
            .sort({
                column: 1,
                sortOrder: 'desc'
            })
    }

    componentDidMount() {
        this.createHotTable();
    }

    render() {
        return (
            <div id="hot-table-1"/>
        );
    }
}