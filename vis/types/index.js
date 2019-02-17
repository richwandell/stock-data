type Config = {
    portfolios: Array<Portfolio>
};

type MainProps = {
    snpPortfolios: Array<Portfolio>,
    config: {
        portfolios: Array<Portfolio>
    }
};

type MainState = {
    page: string,
    selected_portfolio: Portfolio
};

type Actions = {
    setPortfolio: (Portfolio),
    pageClicked: (string),
    portfolioSelected: (string),
    portfolioTypeSelected: (string)
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
    portfolios: Array<Portfolio>
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