import css from "./main.module.css";
import {State as DashboardState} from "./Dashboard";
import {Portfolio, PortfolioSymbol} from "../../react-app-env";
import {gql, useQuery} from "@apollo/client";

interface Props {
    loading: boolean,
    state: DashboardState,
    portfolio: Portfolio
}

const GET_PORTFOLIO_STATS = gql`
    query Portfolio($portfolioId: String!) {
      portfolioStats(portfolioId: $portfolioId) {
        portfolioId,
        portfolioStats
      },
      optimizedPortfolios(portfolioId: $portfolioId) {
        portfolioId,
        efficientPortfolio
      }
    }
`

export function Main({state, portfolio}: Props) {

    const {loading, error, data} = useQuery(GET_PORTFOLIO_STATS, {
        variables: {
            portfolioId: portfolio.portfolioId
        }
    })

    console.log(data)


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