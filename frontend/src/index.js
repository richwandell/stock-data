import React, { Suspense } from "react";
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter as Router, Redirect, Route, Switch } from "react-router-dom";
import { Placeholder } from "./shared/Placeholder";
import { Login } from "./pages/login/Login";
import AuthContextProvider from "./shared/AuthContextProvider";
import Dashboard from "./pages/dashboard/Dashboard";
import { ApolloClient, InMemoryCache } from '@apollo/client';
import { gql } from '@apollo/client';
import { ApolloProvider } from '@apollo/client';



const client = new ApolloClient({
    uri: process.env.REACT_APP_GRAPHQL_ENDPOINT,
    cache: new InMemoryCache()
});


ReactDOM.render(
    <Router>
        <Suspense fallback={<Placeholder />}>
            <Switch>
                <Route exact path="/">
                    <Redirect to={"/login"} />
                </Route>
                <Route exact path="/login">
                    <Login />
                </Route>
                <Route exact path="/dashboard" >
                    <AuthContextProvider>
                        <ApolloProvider client={client} >
                            <Dashboard />
                        </ApolloProvider>
                    </AuthContextProvider>
                </Route>
            </Switch>
        </Suspense>
    </Router>,
    document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
