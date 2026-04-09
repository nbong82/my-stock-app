import streamlit as st
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta

st.title("🔥 코치님 퀀트 투자 시스템")

start = "20220101"
end = datetime.today().strftime("%Y%m%d")

st.header("📊 백테스트 실행")

if st.button("백테스트 시작"):

    tickers = stock.get_market_ticker_list(market="KOSPI")

    result = []

    for t in tickers:
        try:
            df = stock.get_market_fundamental(end, end, t)
            if df.empty:
                continue

            per = df['PER'].values[0]
            roe = df['ROE'].values[0]
            div = df['DIV'].values[0]

            if per < 15 and roe > 10 and div > 3:

                price_df = stock.get_market_ohlcv(start, end, t)
                if len(price_df) < 2:
                    continue

                start_price = price_df.iloc[0]['종가']
                end_price = price_df.iloc[-1]['종가']

                rtn = (end_price / start_price - 1) * 100

                result.append([t, rtn])

        except:
            continue

    df_result = pd.DataFrame(result, columns=["티커", "수익률"])

    df_top = df_result.sort_values(by="수익률", ascending=False).head(10)

    st.subheader("🏆 백테스트 TOP 10")
    st.dataframe(df_top)

    avg_return = df_result['수익률'].mean()

    st.subheader("📈 평균 수익률")
    st.success(f"{avg_return:.2f}%")
