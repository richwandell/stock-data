import css from "./sidebar.module.css";
import {Link} from "react-router-dom";
import {Nav} from "react-bootstrap";

export function Sidebar() {
    return <Nav className={"col-md-3 col-lg-2 bg-light " + css.sidebar}>
        <div className={"position-sticky pt-3"}>
            <ul className={"nav flex-column"}>
                <li className={"nav-item"}>
                    <Link className={"nav-link"} to={"/dashboard/1"}>Item 1</Link>
                </li>
                <li className={"nav-item"}>Item 2</li>
                <li className={"nav-item"}>Item 3</li>
            </ul>
        </div>
    </Nav>
}