import css from "./main.module.css";
import {State as DashboardState} from "./Dashboard";
import {Portfolio, PortfolioSymbol} from "../../react-app-env";
import {gql, useQuery} from "@apollo/client";

interface Props {
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
      },
      randomPortfolios(portfolioId: $portfolioId) {
        portfolioId,
        portfolioStats
      }
    }
`

type QueryResponse = {
    optimizedPortfolios:  {
        portfolioId: string,
        efficientPortfolio: {
            symbols: string[],
            portfolios: number[][]
        }
    },
    portfolioStats: {
        portfolioId: string,
        portfolioStats: {
            asset_reward: number[],
            asset_risk: number[],
            assets: string[]
        }
    },
    randomPortfolios: {
        portfolioId: string,
        portfolioStats: {

        }
    }
}

export function Main({state, portfolio}: Props) {

    const {loading, data} = useQuery<QueryResponse>(GET_PORTFOLIO_STATS, {
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
                    <th>Risk</th>
                    <th>Reward</th>
                    <th>High</th>
                    <th>Low</th>
                    <th>Close</th>
                    <th>Volume</th>
                </tr>
            </thead>
            <tbody>
                {!loading && data && portfolio.symbols.map((item: PortfolioSymbol, index: number) => {
                    const iindex = data.portfolioStats.portfolioStats.assets.indexOf(item.symbol)
                    let risk = undefined
                    let reward = undefined
                    if (iindex > -1) {
                        risk = data.portfolioStats.portfolioStats.asset_risk[iindex]
                        reward = data.portfolioStats.portfolioStats.asset_reward[iindex]
                    }
                    return <tr key={index}>
                        <td>{item.symbol}</td>
                        <td>{risk && risk}</td>
                        <td>{reward && reward}</td>
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