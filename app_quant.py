import streamlit as st
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta

st.title("🔥 코치님 퀀트 투자 시스템")

# 🟢 [추가] 안전한 날짜 가져오기
def get_safe_date():
    today = datetime.today()
    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y%m%d")
        try:
            df = stock.get_market_ohlcv(date, date, "005930")
            if not df.empty:
                return date
        except:
            continue
    return None

today = get_safe_date()

# 🟢 [추가] 데이터 없으면 중단
if today is None:
    st.error("데이터 날짜 조회 실패")
    st.stop()

# 🟢 [추가] 캐싱 (서버 부하 방지)
@st.cache_data(ttl=3600)
def get_fundamental(ticker):
    return stock.get_market_fundamental(today, today, ticker)

st.header("📊 백테스트 실행")

# 🔴 [수정] 버튼 눌렀을 때만 실행
if st.button("백테스트 시작"):

    # 🔴 [수정] 종목 수 제한 (중요!!)
    tickers = stock.get_market_ticker_list(today, market="KOSPI")[:100]

    result = []

    for t in tickers:
        try:
            df = get_fundamental(t)

            if df.empty:
                continue

            per = df['PER'].values[0]
            roe = df['ROE'].values[0]
            div = df['DIV'].values[0]

            # 🔴 [수정] 조건 완화 + 점수 방식
            score = 0
            if per < 20: score += 1
            if roe > 5: score += 1
            if div > 2: score += 1

            if score >= 2:

                price_df = stock.get_market_ohlcv("20220101", today, t)

                if len(price_df) < 2:
                    continue

                start_price = price_df.iloc[0]['종가']
                end_price = price_df.iloc[-1]['종가']

                rtn = (end_price / start_price - 1) * 100

                result.append([t, rtn])

        except:
            continue

    # 🟢 [추가] 결과 없을 때 처리
    if len(result) == 0:
        st.warning("조건에 맞는 종목 없음 (조건 완화 필요)")
    else:
        df_result = pd.DataFrame(result, columns=["티커", "수익률"])

        df_top = df_result.sort_values(by="수익률", ascending=False).head(10)

        st.subheader("🏆 백테스트 TOP 10")
        st.dataframe(df_top)

        avg_return = df_result['수익률'].mean()

        st.subheader("📈 평균 수익률")
        st.success(f"{avg_return:.2f}%")
