type Config = {
    portfolios: Array<Portfolio>
};

type MainProps = {
    config: {
        portfolios: Array<Portfolio>
    }
};

type MainState = {
    page: string,
    selected_portfolio: Portfolio
};

type Actions = {
    setPortfolio: Function,
    pageClicked: Function,
    portfolioSelected: Function
};

type Portfolio = {
    name: string,
    symbols: Array<string>,
    allocations: Array<number>,
    risk_return_sharpe: Array<number>
};

type NavProps = {
    page: string,
    actions: Actions,
    config: Config
};

type PMProps = {
    selected_portfolio: Portfolio,
    actions: Actions
};

type PMState = {
    error: boolean,
    error_message: string,
    portfolio_perc: number
};

export {MainProps, Portfolio, MainState, Actions, Config, NavProps,
PMProps, PMState};