import React, {useEffect, useState} from "react";
import {AuthContextState} from "../react-app-env";

export const AuthContext = React.createContext<AuthContextState>({
    user: {}
});

export default function AuthContextProvider(props: any) {
    const [user, setUser] = useState({});


    const context: AuthContextState = {
        user
    }

    useEffect(() => {
        (async () => {
            try {
                const response = await fetch('/userauth/get-user')
                const userData = await response.json()
                setUser(userData)
            } catch {
                window.location.href = "/login"
            }
        })()
    }, []);

    return (
        <AuthContext.Provider value={{...context}}>
            {props.children}
        </AuthContext.Provider>
    )
}