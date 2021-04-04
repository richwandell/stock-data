import {Container, Row} from "react-bootstrap";
import {Sidebar} from "./Sidebar";
import {Main} from "./Main";
import { gql, useQuery } from "@apollo/client";
import {useState} from "react";
import {Portfolio} from "../../react-app-env";
import css from "./dashboard.module.css";


const PORTFOLIOS = gql`
    query{
        allPortfolios {
          id,
          name
        }
      }
    `

export default function Dashboard() {    
    const {loading, data} = useQuery<{allPortfolios: Portfolio[]}>(PORTFOLIOS)
    const [state, setState] = useState()

    return <Container fluid>
        <Row className={css.containerRow}>
            <Sidebar loading={loading} portfolios={data?.allPortfolios || []} />
            <Main />
        </Row>
    </Container>
}