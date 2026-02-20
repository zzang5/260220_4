import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(
    page_title="포켓몬스터 데이터 대시보드",
    page_icon="🐉",
    layout="wide"
)

# --- 1. 데이터 로드 및 전처리 ---
@st.cache_data
def generate_mock_pokemon_data():
    """파일이 없을 경우 사용할 샘플 포켓몬 데이터를 생성합니다."""
    data = {
        'Name': ['이상해씨', '파이리', '꼬부기', '피카츄', '뮤츠', '망나뇽', '루기아', '칠색조'],
        'Type 1': ['Grass', 'Fire', 'Water', 'Electric', 'Psychic', 'Dragon', 'Psychic', 'Fire'],
        'Total': [318, 309, 314, 320, 680, 600, 680, 680],
        'HP': [45, 39, 44, 35, 106, 91, 106, 106],
        'Attack': [49, 52, 48, 55, 110, 134, 90, 130],
        'Defense': [49, 43, 65, 40, 90, 95, 130, 90],
        'Speed': [45, 65, 43, 90, 130, 80, 110, 90], # 오류 해결: Speed 컬럼 추가
        'Generation': [1, 1, 1, 1, 1, 1, 2, 2],
        'Legendary': [False, False, False, False, True, False, True, True]
    }
    return pd.DataFrame(data)

def load_data(file):
    if file is not None:
        try:
            df = pd.read_csv(file)
            return df
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            return generate_mock_pokemon_data()
    else:
        return generate_mock_pokemon_data()

# 포켓몬 타입별 공식 테마 색상 지정
type_colors = {
    'Normal': '#A8A77A', 'Fire': '#EE8130', 'Water': '#6390F0', 'Electric': '#F7D02C',
    'Grass': '#7AC74C', 'Ice': '#96D9D6', 'Fighting': '#C22E28', 'Poison': '#A33EA1',
    'Ground': '#E2BF65', 'Flying': '#A98FF3', 'Psychic': '#F95587', 'Bug': '#A6B91A',
    'Rock': '#B6A136', 'Ghost': '#735797', 'Dragon': '#6F35FC', 'Dark': '#705746',
    'Steel': '#B7B7CE', 'Fairy': '#D685AD'
}

# --- 2. 사이드바 컨트롤 ---
st.sidebar.header("⚙️ 설정 및 필터")
uploaded_file = st.sidebar.file_uploader("Pokemon.csv 파일 업로드", type=['csv'])

# 데이터 로드
df = load_data(uploaded_file)

# 필터링 옵션 추출
available_gens = sorted(df['Generation'].unique())
available_types = sorted(df['Type 1'].unique())

st.sidebar.divider()
st.sidebar.subheader("🔍 데이터 필터링")
selected_gens = st.sidebar.multiselect("세대(Generation) 선택", available_gens, default=available_gens)
selected_types = st.sidebar.multiselect("주 속성(Type 1) 선택", available_types, default=available_types)
show_legendary_only = st.sidebar.checkbox("전설의 포켓몬만 보기 (Legendary Only)")

# 조건에 맞게 데이터 필터링
df_filtered = df.copy()
if selected_gens:
    df_filtered = df_filtered[df_filtered['Generation'].isin(selected_gens)]
if selected_types:
    df_filtered = df_filtered[df_filtered['Type 1'].isin(selected_types)]
if show_legendary_only:
    df_filtered = df_filtered[df_filtered['Legendary'] == True]

# --- 3. 메인 대시보드 UI ---
st.title("🐉 포켓몬스터 종합 스탯 분석 대시보드")
st.markdown("포켓몬의 속성, 세대별 능력치와 전설의 포켓몬 분포를 분석합니다.")

# 데이터가 없을 경우 처리
if df_filtered.empty:
    st.warning("선택한 조건에 맞는 포켓몬이 없습니다. 필터를 조정해 주세요.")
else:
    # 3-1. 핵심 지표 (KPI)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 포켓몬 수", f"{len(df_filtered)} 마리")
    col2.metric("평균 종합 능력치 (Total)", f"{df_filtered['Total'].mean():.1f}")
    col3.metric("최고 공격력 (Attack)", f"{df_filtered['Attack'].max()}")
    col4.metric("전설의 포켓몬 비율", f"{(df_filtered['Legendary'].sum() / len(df_filtered) * 100):.1f} %")
    
    st.divider()

    # 3-2. 차트 레이아웃 1행 (산점도 & 바 차트)
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.subheader("⚔️ 공격력(Attack) vs 방어력(Defense)")
        
        # hover_data에 사용할 컬럼이 실제 데이터프레임에 존재하는지 확인
        hover_columns = ["Generation", "HP", "Speed"]
        valid_hover_cols = [col for col in hover_columns if col in df_filtered.columns]

        fig_scatter = px.scatter(
            df_filtered, 
            x="Attack", 
            y="Defense", 
            color="Type 1",
            color_discrete_map=type_colors,
            size="Total",
            hover_name="Name",
            hover_data=valid_hover_cols,
            opacity=0.8
        )
        fig_scatter.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)

    with row1_col2:
        st.subheader("📊 주 속성(Type 1) 분포")
        type_counts = df_filtered['Type 1'].value_counts().reset_index()
        type_counts.columns = ['Type 1', 'Count']
        
        fig_bar = px.bar(
            type_counts, 
            x="Type 1", 
            y="Count", 
            color="Type 1",
            color_discrete_map=type_colors,
            text_auto=True
        )
        fig_bar.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'}, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # 3-3. 차트 레이아웃 2행 (박스플롯 & Top 10)
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.subheader("📈 세대별 종합 능력치(Total) 분포")
        fig_box = px.box(
            df_filtered, 
            x="Generation", 
            y="Total", 
            color="Legendary",
            color_discrete_sequence=['#3b82f6', '#fbbf24'],
            hover_name="Name"
        )
        fig_box.update_layout(xaxis=dict(tickmode='linear', dtick=1), margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_box, use_container_width=True)

    with row2_col2:
        st.subheader("🏆 현재 조건 내 종합 능력치 Top 10")
        top10_df = df_filtered.nlargest(10, 'Total').sort_values('Total', ascending=True)
        fig_top10 = px.bar(
            top10_df, 
            x="Total", 
            y="Name", 
            orientation='h',
            color="Type 1",
            color_discrete_map=type_colors,
            text_auto=True
        )
        fig_top10.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_top10, use_container_width=True)

    # 3-4. 원본 데이터 테이블 표시
    st.subheader("📋 상세 데이터 표")
    st.dataframe(df_filtered.drop(columns=['#'], errors='ignore'), use_container_width=True, hide_index=True)
