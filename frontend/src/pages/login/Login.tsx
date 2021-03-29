import {TopNavBar} from "../../shared/TopNavbar";
import {Button, Form, Image} from "react-bootstrap";
import css from "./login.module.css"
import {useState} from "react";

interface State {
    user: string,
    pass: string
}

export function Login() {
    const [state, setState] = useState<State>({user: '', pass: ''})

    async function submitForm() {
        try {
            const token = document.querySelectorAll('input[name=csrfmiddlewaretoken]')[0]
                .getAttribute('value') || ''

            const response = await fetch("/userauth/login/", {
                method: 'post',
                body: JSON.stringify(state),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token
                }
            })
            const data = await response.json()
            console.log(data)
        } catch (error) {
            console.log(error)
        }
    }


    return <>
        <TopNavBar/>
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