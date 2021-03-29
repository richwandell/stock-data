import React, {useEffect, useState} from "react";
import {AuthContextState, UserInfo} from "../react-app-env";
import {TopNavBar} from "./TopNavbar";

const csrfHeader = {
    'X-CsrfToken': document.querySelectorAll('input[name=csrfmiddlewaretoken]')[0]
        .getAttribute('value') || ''
}

const defaultUser = {
    email: '',
    first_name: '',
    last_name: '',
    username: '',
    date_joined: '',
    is_active: false,
    is_staff: false,
    logged_in: false
}

export const AuthContext = React.createContext<AuthContextState>({
    user: defaultUser,
    csrfHeader: csrfHeader,
    setUser: () => {}
});

export default function AuthContextProvider(props: any) {
    const [user, setUser] = useState<UserInfo>(defaultUser);


    const context: AuthContextState = {
        user,
        csrfHeader,
        setUser
    }

    useEffect(() => {
        (async () => {
            try {
                const response = await fetch('/userauth/get-user/')
                const userData: UserInfo = await response.json()
                if (!userData.logged_in || !userData.is_active) {
                    throw ''
                }
                setUser(userData)
            } catch {
                window.location.href = "/login"
            }
        })()
    }, []);

    return (
        <AuthContext.Provider value={{...context}}>
            <TopNavBar  />
            {props.children}
        </AuthContext.Provider>
    )
}