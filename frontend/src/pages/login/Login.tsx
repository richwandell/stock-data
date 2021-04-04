import {TopNavBar} from "../../shared/TopNavbar";
import {Button, Form, Image} from "react-bootstrap";
import css from "./login.module.css"
import {useContext, useState} from "react";
import {AuthContext} from "../../shared/AuthContextProvider";
import {UserInfo} from "../../react-app-env";
import { useHistory } from "react-router-dom";

interface State {
    user: string,
    pass: string
}

export function Login() {
    const {user, csrfHeader, setUser} = useContext(AuthContext)
    const [state, setState] = useState<State>({user: '', pass: ''})
    const history = useHistory()

    async function submitForm() {
        try {
            const response = await fetch("/userauth/login/", {
                method: 'post',
                body: JSON.stringify(state),
                headers: {
                    'Content-Type': 'application/json',
                    ...csrfHeader
                }
            })
            const data: {user: UserInfo} = await response.json()
            if (data.user.is_active && data.user.logged_in) {
                history.push("/dashboard")
            }
        } catch (error) {
            console.log(error)
        }
    }


    return <>
        <TopNavBar  />
        <Form className={css.form}>
            <Image width={70} src={"/static/frontend/graph-up.svg"} className={"mb-4"}/>
            <h3 className={"font-weight-normal mb-3"}>Please sign In</h3>
            <Form.Label className={"sr-only"}>Email address</Form.Label>
            <Form.Control type="text" placeholder="Email address"
                onChange={(event) => setState({...state, user: event.target.value})} />
            <Form.Label className={"sr-only"}>Password</Form.Label>
            <Form.Control type="password" placeholder="Password"
                onChange={(event) => setState({...state, pass: event.target.value})} />
            <div className={css.formCheckbox + " mb-3"}>
                <Form.Check type="checkbox" label="Remember me"/>
            </div>
            <Button variant={"primary"} className={"btn-block"} onClick={() => submitForm()}>
                Sign in
            </Button>
        </Form>
    </>
}