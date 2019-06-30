create schema stock_data collate utf8_general_ci;

create table api_requests
(
	request_date int(10) not null,
	symbol varchar(50) not null,
	primary key (request_date, symbol)
);

create table monthly_portfolio_stats
(
	portfolio_key varchar(200) not null,
	portfolio_data json not null,
	constraint portfolio_key_UNIQUE
		unique (portfolio_key)
);

alter table monthly_portfolio_stats
	add primary key (portfolio_key);

create table newsapi_sentiment
(
	symbol varchar(50) not null,
	date_time int(10) not null,
	article_id varchar(64) not null,
	polarity double not null,
	subjectivity double not null,
	primary key (symbol, date_time, article_id)
);

create table symbol_prices
(
	symbol varchar(50) not null,
	date_time int(10) not null,
	low decimal(13,4) not null,
	divident_amount decimal(13,4) not null,
	adjusted_close decimal(13,4) not null,
	open decimal(13,4) not null,
	split_coefficient decimal(13,4) not null,
	close decimal(13,4) not null,
	high decimal(13,4) not null,
	volume bigint not null,
	primary key (symbol, date_time, adjusted_close),
	constraint symbol_prices_symbol_date_time_uindex
		unique (symbol, date_time)
);

create table twitter_sentiment
(
	symbol varchar(50) not null,
	date_time int(10) not null,
	tweet_id bigint not null,
	polarity double not null,
	subjectivity double not null,
	primary key (symbol, date_time, tweet_id)
);

