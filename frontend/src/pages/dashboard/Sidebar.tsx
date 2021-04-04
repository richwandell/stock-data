import css from "./sidebar.module.css";
import {Link} from "react-router-dom";
import {Nav} from "react-bootstrap";
import {Portfolio} from "../../react-app-env";

interface Props {
    portfolios: Portfolio[],
    loading: boolean
}

export function Sidebar({loading, portfolios}: Props) {


    return <Nav className={(loading ? "skeleton " : "bg-light ") + "col-md-3 col-lg-2 " + css.sidebar}>
        <div className={"position-sticky pt-3 " + css.innerDiv}>
            <label>Portfolios</label>
            <ul className={"nav flex-column"}>
                {portfolios.map((p) => {
                    return <li key={p.id} className={"nav-item"}>
                        <Link className={"nav-link"} to={`/dashboard/${p.id}`}>{p.name}</Link>
                    </li>
                })}
            </ul>
            <div>Create Portfolio +</div>
            <hr />
        </div>
    </Nav>
}