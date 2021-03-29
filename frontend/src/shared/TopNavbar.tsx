import {Button, Nav, Navbar} from "react-bootstrap";
import {useContext} from "react";
import {AuthContext} from "./AuthContextProvider";
import {PersonCircle} from "./svg/PersonCircle";
import {GraphUp} from "./svg/GraphUp";
import css from "./topbarnav.module.css"

export function TopNavBar() {
    const {user} = useContext(AuthContext)

    return <Navbar className={css.outerNavbar + " sticky-top"} >
        <Navbar.Brand className={css.navbarBrand} href="/dashboard">
            <span className={css.graphUpIcon}>
                <GraphUp />
            </span> {' '}
            Portfolio Manager
        </Navbar.Brand>
        <Nav className={"ml-auto"}>
            <Button >
                <PersonCircle />{' '}
                <span>{user.username}</span>
            </Button>
        </Nav>
    </Navbar>
}