import {useContext} from "react";
import {AuthContext} from "../../shared/AuthContextProvider";
import {Container, Row} from "react-bootstrap";
import {Sidebar} from "./Sidebar";
import {Main} from "./Main";



export default function Dashboard() {
    const userContext = useContext(AuthContext)

    return <Container fluid>
        <Row>
            <Sidebar />
            <Main />
        </Row>
    </Container>
}