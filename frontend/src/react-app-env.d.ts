/// <reference types="react-scripts" />
export type UserInfo = {
    email: string,
    first_name: string,
    last_name: string,
    username: string
    date_joined: string
    is_active: boolean,
    is_staff: boolean,
    logged_in: boolean
}

export type AuthContextState = {
    user: UserInfo,
    csrfHeader: {
        'X-CsrfToken': string
    },
    setUser: Function
}