import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울의 100년간 연평균 기온 변화")
st.write("1907년 이후 서울의 일별 기온 데이터를 이용해 연평균 기온의 변화를 살펴봅니다.")

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# CSV 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"])

    # 평균기온을 숫자형으로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    return df


try:
    df = load_data()

    # 연도별 평균기온 계산
    yearly_temp = (
        df.dropna(subset=["평균기온"])
        .groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    # 분석할 100년 선택
    start_year = 1908
    end_year = start_year + 99

    yearly_temp = yearly_temp[
        (yearly_temp["연도"] >= start_year) &
        (yearly_temp["연도"] <= end_year)
    ]

    # 제목
    st.subheader(f"📈 {start_year}년~{end_year}년 서울 연평균 기온")

    # 그래프
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        yearly_temp["연도"],
        yearly_temp["평균기온"],
        linewidth=2
    )

    ax.set_title("서울 연평균 기온 변화", fontsize=18)
    ax.set_xlabel("연도")
    ax.set_ylabel("연평균 기온 (℃)")

    ax.grid(True, alpha=0.3)

    # x축 눈금 간격
    ax.set_xticks(range(start_year, end_year + 1, 10))

    plt.tight_layout()

    st.pyplot(fig)

    # 요약 정보
    col1, col2, col3 = st.columns(3)

    first_temp = yearly_temp.iloc[0]["평균기온"]
    last_temp = yearly_temp.iloc[-1]["평균기온"]
    change = last_temp - first_temp

    with col1:
        st.metric(
            "첫해 연평균 기온",
            f"{first_temp:.1f} ℃"
        )

    with col2:
        st.metric(
            "마지막해 연평균 기온",
            f"{last_temp:.1f} ℃"
        )

    with col3:
        st.metric(
            "기온 변화",
            f"{change:+.1f} ℃"
        )

    st.caption(
        "※ 연평균 기온은 해당 연도의 일별 평균기온을 산술평균하여 계산했습니다."
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
