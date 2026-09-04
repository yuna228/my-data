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
st.write(
    "서울의 일별 기온 데이터를 이용하여 연평균 기온의 변화를 살펴보고, "
    "원본 데이터의 요약통계를 확인합니다."
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"])

    # 기온 열을 숫자형으로 변환
    for column in ["평균기온", "최저기온", "최고기온"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    return df


try:
    df = load_data()

    # --------------------------------------------------
    # 1. 원본 데이터 개요
    # --------------------------------------------------
    st.subheader("📋 원본 데이터 개요")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("전체 데이터 개수", f"{len(df):,}개")

    with col2:
        st.metric("데이터 시작일", df["날짜"].min().strftime("%Y-%m-%d"))

    with col3:
        st.metric("데이터 종료일", df["날짜"].max().strftime("%Y-%m-%d"))

    # --------------------------------------------------
    # 2. 요약통계
    # --------------------------------------------------
    st.subheader("📊 원본 데이터 요약통계")

    # 기온 데이터의 요약통계
    summary = df[["평균기온", "최저기온", "최고기온"]].describe().T

    # 보기 좋은 한글 열 이름으로 변경
    summary = summary.rename(
        columns={
            "count": "개수",
            "mean": "평균",
            "std": "표준편차",
            "min": "최소값",
            "25%": "25%",
            "50%": "중앙값",
            "75%": "75%",
            "max": "최대값"
        }
    )

    # 소수점 표시
    summary = summary.round(2)

    # 행 이름 한글화
    summary.index = ["평균기온", "최저기온", "최고기온"]

    st.dataframe(
        summary,
        use_container_width=True
    )

    st.caption(
        "※ 기온의 단위는 ℃이며, 결측값은 통계 계산에서 제외됩니다."
    )

    # --------------------------------------------------
    # 3. 결측값 확인
    # --------------------------------------------------
    st.subheader("🔎 열별 결측값")

    missing = df.isnull().sum().reset_index()
    missing.columns = ["열 이름", "결측값 개수"]

    st.dataframe(
        missing,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 4. 연평균 기온 계산
    # --------------------------------------------------
    yearly_temp = (
        df.dropna(subset=["평균기온"])
        .groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    # 100년간 데이터 선택
    start_year = 1908
    end_year = start_year + 99

    yearly_temp = yearly_temp[
        (yearly_temp["연도"] >= start_year) &
        (yearly_temp["연도"] <= end_year)
    ]

    # --------------------------------------------------
    # 5. 100년간 연평균 기온 그래프
    # --------------------------------------------------
    st.subheader(
        f"📈 {start_year}년~{end_year}년 서울 연평균 기온 변화"
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        yearly_temp["연도"],
        yearly_temp["평균기온"],
        linewidth=2
    )

    ax.set_title(
        "서울 연평균 기온 변화",
        fontsize=18
    )
    ax.set_xlabel("연도")
    ax.set_ylabel("연평균 기온 (℃)")

    ax.grid(True, alpha=0.3)

    # 10년 단위로 x축 표시
    ax.set_xticks(
        range(start_year, end_year + 1, 10)
    )

    plt.tight_layout()

    st.pyplot(fig)

    # --------------------------------------------------
    # 6. 100년간 변화 요약
    # --------------------------------------------------
    st.subheader("🌡️ 100년간 기온 변화 요약")

    first_temp = yearly_temp.iloc[0]["평균기온"]
    last_temp = yearly_temp.iloc[-1]["평균기온"]
    change = last_temp - first_temp

    col1, col2, col3 = st.columns(3)

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
            "첫해 대비 변화",
            f"{change:+.1f} ℃"
        )

    st.caption(
        "※ 연평균 기온은 해당 연도의 일별 평균기온을 산술평균하여 계산했습니다."
    )


except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
