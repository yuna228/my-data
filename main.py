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
    "원본 데이터의 요약통계와 이상 데이터를 확인합니다."
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    # 한글이 깨지는 경우를 대비하여 인코딩 자동 처리
    try:
        df = pd.read_csv(DATA_URL, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_URL, encoding="cp949")

    # 열 이름에 혹시 공백이 있으면 제거
    df.columns = df.columns.str.strip()

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 기온 열 숫자형 변환
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
        st.metric(
            "데이터 시작일",
            df["날짜"].min().strftime("%Y-%m-%d")
        )

    with col3:
        st.metric(
            "데이터 종료일",
            df["날짜"].max().strftime("%Y-%m-%d")
        )

    # --------------------------------------------------
    # 2. 원본 데이터 요약통계
    # --------------------------------------------------
    st.subheader("📊 원본 데이터 요약통계")

    # 기온별 통계 계산
    summary = df[
        ["평균기온", "최저기온", "최고기온"]
    ].describe().T

    # 통계 항목을 한글로 변경
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

    # 행과 열 바꾸기
    # 기존: 평균기온 / 최저기온 / 최고기온 → 행
    # 변경: 개수 / 평균 / 최소값 ... → 행
    summary = summary.T

    summary = summary.round(2)

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

    missing = df[
        ["날짜", "지점", "평균기온", "최저기온", "최고기온"]
    ].isnull().sum().reset_index()

    missing.columns = ["열 이름", "결측값 개수"]

    st.dataframe(
        missing,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 4. 연도별 연평균 기온 계산
    # --------------------------------------------------
    yearly_temp = (
        df.dropna(subset=["평균기온"])
        .groupby("연도")["평균기온"]
        .mean()
    )

    # 분석할 100년
    start_year = 1908
    end_year = start_year + 99

    # 모든 연도를 먼저 만든 뒤 데이터 연결
    # → 값이 없는 연도도 그래프에 표시 가능
    all_years = pd.Index(
        range(start_year, end_year + 1),
        name="연도"
    )

    yearly_temp = yearly_temp.reindex(all_years)

    # --------------------------------------------------
    # 5. 유난히 낮은 연도 판별
    # --------------------------------------------------
    valid_temps = yearly_temp.dropna()

    mean_temp = valid_temps.mean()
    std_temp = valid_temps.std()

    # 평균보다 2표준편차 이상 낮은 연도
    low_threshold = mean_temp - (2 * std_temp)

    low_years = yearly_temp[
        yearly_temp < low_threshold
    ].dropna()

    # 값이 없는 연도
    missing_years = yearly_temp[
        yearly_temp.isna()
    ].index.tolist()

    # --------------------------------------------------
    # 6. 100년간 연평균 기온 그래프
    # --------------------------------------------------
    st.subheader(
        f"📈 {start_year}년~{end_year}년 서울 연평균 기온 변화"
    )

    fig, ax = plt.subplots(figsize=(13, 6))

    # 기본 연평균 기온
    ax.plot(
        yearly_temp.index,
        yearly_temp.values,
        linewidth=2,
        marker="o",
        markersize=3,
        label="연평균 기온"
    )

    # 유난히 낮은 연도 강조
    if len(low_years) > 0:
        ax.scatter(
            low_years.index,
            low_years.values,
            s=100,
            color="red",
            zorder=5,
            label="유난히 낮은 연도"
        )

        for year, temp in low_years.items():
            ax.annotate(
                f"{year}\n{temp:.1f}℃",
                xy=(year, temp),
                xytext=(0, -35),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color="red",
                fontweight="bold"
            )

    # 값이 없는 연도 강조
    if missing_years:
        ax.scatter(
            missing_years,
            [mean_temp] * len(missing_years),
            marker="X",
            s=120,
            color="red",
            zorder=6,
            label="값이 없는 연도"
        )

        for year in missing_years:
            ax.annotate(
                f"{year}\n값 없음",
                xy=(year, mean_temp),
                xytext=(0, 30),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color="red",
                fontweight="bold"
            )

    # 낮은 기온 기준선
    ax.axhline(
        low_threshold,
        linestyle="--",
        linewidth=1.5,
        label=f"낮은 기온 기준 ({low_threshold:.1f}℃)"
    )

    ax.set_title(
        "서울 연평균 기온 변화",
        fontsize=18
    )

    ax.set_xlabel("연도")
    ax.set_ylabel("연평균 기온 (℃)")

    ax.set_xticks(
        range(start_year, end_year + 1, 10)
    )

    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    st.pyplot(fig)

    # --------------------------------------------------
    # 7. 이상 데이터 요약
    # --------------------------------------------------
    st.subheader("⚠️ 이상 데이터 확인")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔴 값이 없는 연도")

        if missing_years:
            st.write(
                f"총 **{len(missing_years)}개 연도**에서 "
                "연평균 기온을 계산할 수 없습니다."
            )

            st.write(
                ", ".join(map(str, missing_years))
            )
        else:
            st.success("값이 없는 연도가 없습니다.")

    with col2:
        st.markdown("### 🔻 유난히 낮은 연도")

        if len(low_years) > 0:
            st.write(
                f"판정 기준: **{low_threshold:.1f}℃ 미만**"
            )

            low_table = low_years.reset_index()
            low_table.columns = ["연도", "연평균 기온"]

            low_table["연평균 기온"] = (
                low_table["연평균 기온"].round(2)
            )

            st.dataframe(
                low_table,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success(
                "통계적으로 유난히 낮은 연도가 없습니다."
            )

    # --------------------------------------------------
    # 8. 100년간 변화 요약
    # --------------------------------------------------
    st.subheader("🌡️ 100년간 기온 변화 요약")

    valid_yearly_temp = yearly_temp.dropna()

    if len(valid_yearly_temp) >= 2:
        first_year = valid_yearly_temp.index[0]
        last_year = valid_yearly_temp.index[-1]

        first_temp = valid_yearly_temp.iloc[0]
        last_temp = valid_yearly_temp.iloc[-1]
        change = last_temp - first_temp

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                f"{first_year}년 연평균 기온",
                f"{first_temp:.1f} ℃"
            )

        with col2:
            st.metric(
                f"{last_year}년 연평균 기온",
                f"{last_temp:.1f} ℃"
            )

        with col3:
            st.metric(
                "첫해 대비 변화",
                f"{change:+.1f} ℃"
            )

    st.caption(
        "※ 유난히 낮은 연도는 100년간 연평균 기온의 평균에서 "
        "2표준편차 이상 낮은 연도로 판단했습니다."
    )


except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
