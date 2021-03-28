import {Navbar} from "react-bootstrap";
import {useContext} from "react";
import {AuthContext} from "./AuthContextProvider";


export function TopNavBar() {
    const userContext = useContext(AuthContext)

    return <Navbar bg="dark" variant="dark">
        <Navbar.Brand href="#home">
            <img
                alt=""
                src="/static/frontend/logo192.png"
                width="30"
                height="30"
                className="d-inline-block align-top"
            />{' '}
            React Bootstrap
        </Navbar.Brand>
    </Navbar>
}