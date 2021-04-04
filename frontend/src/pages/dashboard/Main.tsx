import css from "./main.module.css";
import {State as DashboardState} from "./Dashboard";
import {Portfolio, PortfolioSymbol} from "../../react-app-env";

interface Props {
    loading: boolean,
    state: DashboardState,
    portfolio: Portfolio
}

export function Main({state, portfolio, loading}: Props) {
    return <main className={css.main + " col-md-9 ms-sm-auto col-lg-10 px-md-4" + (loading ? " skeleton" : "")}>
        <table className={css.symbolTable}>
            <caption>{portfolio.name}</caption>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Open</th>
                    <th>High</th>
                    <th>Low</th>
                    <th>Close</th>
                    <th>Volume</th>
                </tr>
            </thead>
            <tbody>
                {portfolio.symbols.map((item: PortfolioSymbol, index: number) => {
                    return <tr>
                        <td>{item.symbol}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                })}
            </tbody>
        </table>
    </main>
}