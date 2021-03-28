import React, {Suspense} from "react";
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import {BrowserRouter as Router, Redirect, Route, Switch} from "react-router-dom";
import {Placeholder} from "./shared/Placeholder";
import {Login} from "./pages/login/Login";
import AuthContextProvider from "./shared/AuthContextProvider";
import Dashboard from "./pages/dashboard/Dashboard";

ReactDOM.render(
    <Router>
        <Suspense fallback={<Placeholder/>}>
            <Switch>
                <Route exact path="/">
                    <Redirect to={"/login"}/>
                </Route>
                <Route exact path="/login">
                    <Login />
                </Route>
                <Route exact path="/dashboard" >
                    <AuthContextProvider>
                        <Dashboard />
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