import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. 페이지 기본 설정 및 제목
st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("---")


# 2. 데이터 불러오기 및 전처리 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 열 전처리: 세로막대(|)로 구분된 복수 장르 중 첫 번째 장르만 추출
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .apply(lambda x: x.split("|")[0].strip())
    )

    return df


# 데이터 로드
data = load_data()


# 3. 사이드바 (필터/정보 구역)
st.sidebar.header("ℹ️ 데이터 정보")
st.sidebar.write(f"총 분석 영화 수: **{len(data)}편**")


# 4. 그래프 구역 1: 장르별 영화 편수 분포 (도넛 그래프)
st.header("📌 Section 1. 장르별 영화 편수 분포")

# 장르별 영화 편수 집계
genre_counts = data["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화수"]

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화수",
    hole=0.4,
    title="개봉 영화 장르별 비중",
)

# 마우스 오버(호버) 시 편수와 비율이 보이도록 설정
fig1.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>장르:</b> %{label}<br><b>영화 수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>",
)

fig1.update_layout(
    legend_title="장르 목록",
)

# Streamlit에 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 해석 문구
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉한 영화들의 장르별 편수 분포를 통해 어떤 장르가 가장 높은 비중을 차지하고 있는지 시장의 장르 쏠림 현상을 파악할 수 있습니다."
)

st.markdown("---")


# 5. 그래프 구역 2: 장르 및 영화별 총 관객수 분포 (트리맵)
st.header("📌 Section 2. 장르 및 영화별 총 관객수 트리맵")

# Plotly 트리맵 생성 (계층 구조: 장르 -> 영화명, 크기: 총 관객수)
fig2 = px.treemap(
    data,
    path=[px.Constant("전체 장르"), "genre", "movieNm"],
    values="total_audi",
    color="genre",
    title="장르별 영화 구성 및 총 관객수 비중",
    labels={"total_audi": "총 관객수 (명)", "genre": "장르", "movieNm": "영화명"},
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br><b>총 관객수:</b> %{value:,.0f}명<extra></extra>"
)

fig2.update_layout(
    margin=dict(t=50, l=10, r=10, b=10),
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 각 장르가 전체 관객수에서 차지하는 비중과 더불어, 해당 장르 내에서 어떤 영화가 흥행을 주도했는지 계층적으로 비교할 수 있습니다."
)

st.markdown("---")


# 6. 그래프 구역 3: 총 관객수 분포 (히스토그램)
st.header("📌 Section 3. 총 관객수 분포 히스토그램")

# Plotly 히스토그램 생성
fig3 = px.histogram(
    data,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객수(total_audi) 분포",
    labels={"total_audi": "총 관객수 (명)", "count": "영화 수 (편)"},
    color_discrete_sequence=["#1f77b4"],
)

fig3.update_traces(
    hovertemplate="<b>총 관객수 구간:</b> %{x}명<br><b>영화 수:</b> %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객수 (명)",
    yaxis_title="영화 수 (편)",
    bargap=0.1,
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 관객수가 많은 영화 탐색
top_movie = data.loc[data["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

# 가장 많은 영화가 집중된 구간(Bin) 도출
counts, bins = np.histogram(data["total_audi"], bins=20)
max_bin_idx = counts.argmax()
bin_start = int(bins[max_bin_idx])
bin_end = int(bins[max_bin_idx + 1])
max_bin_count = counts[max_bin_idx]

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화는 **{bin_start:,.0f}명 ~ {bin_end:,.0f}명** 구간({max_bin_count}편)에 집중되어 있어 하위 구간 쏠림이 심하며, 가장 관객수가 많은 영화는 **'{top_movie_name}'**({top_movie_audi:,.0f}명)입니다."
)

st.markdown("---")


# 7. 그래프 구역 4: 개봉일 스크린수 vs 총 관객수 (산점도)
st.header("📌 Section 4. 개봉일 스크린수와 총 관객수의 관계")

# Plotly 산점도(Scatter Plot) 생성
fig4 = px.scatter(
    data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수(first_scrn) vs 총 관객수(total_audi)",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "genre": "장르",
        "movieNm": "영화명",
    },
)

# 마우스 오버 툴팁 설정
fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,.0f}개<br>총 관객수: %{y:,.0f}명<extra></extra>"
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수 (개)",
    yaxis_title="총 관객수 (명)",
    legend_title="장르",
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린수가 많을수록 대체로 총 관객수도 높아지는 양의 상관관계를 확인할 수 있으며, 장르별 스크린 확보 수준 및 관객 동원력 차이를 비교할 수 있습니다."
)

st.markdown("---")


# 8. 추후 그래프 추가를 위한 구역 예시
st.header("📌 Section 5. (추가 예정 구역)")
st.caption("새로운 분포 및 관계 분석 그래프가 추가될 위치입니다.")
st.info("💡 **이 그래프로 알 수 있는 것:** (추가 예정 설명 문구)")

st.markdown("---")
