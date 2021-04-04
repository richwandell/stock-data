import {Container, Row} from "react-bootstrap";
import {Sidebar} from "./Sidebar";
import {Main} from "./Main";
import {gql, useQuery} from "@apollo/client";
import {useEffect, useState} from "react";
import {Portfolio} from "../../react-app-env";
import css from "./dashboard.module.css";
import {useParams} from "react-router-dom";


const PORTFOLIOS = gql`
    query{
      allPortfolios {
        id
        name,
        symbols {
          id,
          symbol
        }
      }
    }
    `

export interface State {
    selected_portfolio: number
}

export default function Dashboard() {
    const {loading, data} = useQuery<{ allPortfolios: Portfolio[] }>(PORTFOLIOS)
    const [state, setState] = useState<State>({selected_portfolio: 0})
    const {portfolio_id} = useParams<{ portfolio_id: string | undefined }>()

    useEffect(() => {
        if (!(data && data.allPortfolios)) return
        if (!portfolio_id) return
        const selected = data.allPortfolios.findIndex(((value, index) => value.id === portfolio_id))
        if (selected > -1) {
            setState({...state, selected_portfolio: selected})
        }
    }, [data, portfolio_id])

    const selectedPortfolio = data?.allPortfolios?.length ?
        data.allPortfolios[state.selected_portfolio] : {id: "", name: "", symbols: []}

    return <Container fluid>
        <Row className={css.containerRow}>
            <Sidebar
                state={state}
                loading={loading}
                portfolios={data?.allPortfolios || []}/>
            <Main
                loading={loading}
                state={state}
                portfolio={selectedPortfolio}/>
        </Row>
    </Container>
}