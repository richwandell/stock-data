import css from "./sidebar.module.css";
import {Link} from "react-router-dom";
import {Nav} from "react-bootstrap";
import {Portfolio} from "../../react-app-env";
import {State as DashboardState} from "./Dashboard";

interface Props {
    state: DashboardState,
    portfolios: Portfolio[],
    loading: boolean
}

export function Sidebar({state, loading, portfolios}: Props) {


    return <Nav className={(loading ? "skeleton " : "bg-light ") + "col-md-3 col-lg-2 " + css.sidebar}>
        <div className={"position-sticky pt-3 " + css.innerDiv}>
            <label>Portfolios</label>
            <ul className={"nav flex-column"}>
                {portfolios.map((p, index) => {
                    return <li key={p.id} className={"nav-item" + (index === state.selected_portfolio ? " active" : "")}>
                        <Link className={"nav-link"} to={`/dashboard/${p.id}`}>{p.name}</Link>
                    </li>
                })}
            </ul>
            <div>Create Portfolio +</div>
            <hr />
        </div>
    </Nav>
}