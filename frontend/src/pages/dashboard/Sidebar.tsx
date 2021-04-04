import css from "./sidebar.module.css";
import {Link} from "react-router-dom";
import {Nav} from "react-bootstrap";
import { gql, useQuery } from "@apollo/client";

const API_CREDENTIALS = gql`
    query{
        allCredentials(name:"ALPHAVANTAGE") {
          id,
          apiKey,
          datasource {
            id,
            dstype
          }
        }
      }
    `

export function Sidebar() {
    const {loading, error, data} = useQuery(API_CREDENTIALS)

    console.log(loading, error, data)

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