import {useContext} from "react";
import {AuthContext} from "../../shared/AuthContextProvider";

export default function Dashboard() {
    const userContext = useContext(AuthContext)

    return <div>dashboard</div>
}