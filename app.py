import streamlit as st
import pandas as pd
import plotly.express as px
from visualizer import get_dashboard_graphs
from data_loader import load_and_clean_data
from collections import Counter
# 비교 함수를 여기서 직접 정의하거나 visualizer에서 가져오세요
# 여기서는 코드 통합을 위해 직관적으로 작성했습니다.

st.set_page_config(layout="wide", page_title="비만치료제 통합 분석 대시보드")
st.title("💊 비만치료제 부작용 통합 대시보드")

df = load_and_clean_data()

# 1. 기존 6개 그래프 영역
col1, col2 = st.columns(2)

drugs = {'🔴 위고비': 'wegovy', '🔵 마운자로': 'mounjaro'}
for i, (name, key) in enumerate(drugs.items()):
    with [col1, col2][i]:
        st.subheader(f"{name} 분석")
        b, l, s = get_dashboard_graphs(df, key, 'Reds' if key=='wegovy' else 'Blues')
        if b is not None:
            st.plotly_chart(b, use_container_width=True)
            st.plotly_chart(l, use_container_width=True)
            st.plotly_chart(s, use_container_width=True)

# 2. 하단에 신규 FDA 비교 그래프 2개 추가 (총 8개 완성)
f_col1, f_col2 = st.columns(2)

def get_reddit_counts(df, drug_type):
    drug_df = df[df['drug_type'].str.contains(drug_type, case=False, na=False)]
    all_effects = []
    for effects in drug_df['side_effects'].dropna().astype(str):
        all_effects.extend([e.strip() for e in effects.split(',')])
    return Counter(all_effects), len(all_effects)

def plot_fixed_ratio_comparison(drug_name, drug_key, fda_data):
    counts, total = get_reddit_counts(df, drug_key)
    
    # 1. FDA 데이터를 비율(%) 기준으로 합계가 100이 되도록 보정
    total_fda = sum(fda_data.values())
    fda_fixed = {k: (v / total_fda) * 100 for k, v in fda_data.items()}
    
    comp_data = []
    for effect, fda_pct in fda_fixed.items():
        # Reddit 데이터도 동일하게 비율 계산
        reddit_pct = (counts.get(effect, 0) / total) * 100 if total > 0 else 0
        
        comp_data.append({'Side Effect': effect.replace('_', ' ').title(), 'Source': 'Reddit+X', 'Percentage (%)': reddit_pct})
        comp_data.append({'Side Effect': effect.replace('_', ' ').title(), 'Source': 'FDA', 'Percentage (%)': fda_pct})
    
    fig = px.bar(pd.DataFrame(comp_data), x='Percentage (%)', y='Side Effect', color='Source', 
                 barmode='group', orientation='h',
                 title=f"{drug_name} 부작용 비중 비교")
    return fig

with f_col1:
    wegovy_fda = {
        'nausea': 44.0, 'diarrhea': 30.0, 'vomiting': 24.0, 'constipation': 24.0, 'stomach_pain': 20.0,
        'headache': 14.0
    }
    # 붉은색 계열로 색상 팔레트 변경
    red_colors = {'Reddit+X': '#d62728', 'FDA (보정)': '#ff9f9a'}
    st.plotly_chart(plot_fixed_ratio_comparison("Wegovy", "wegovy", wegovy_fda), use_container_width=True)

# 마운자로 호출부 수정
with f_col2:
    mounjaro_fda = {
        'nausea': 18.0, 'diarrhea': 17.0, 'vomiting': 9.0, 'acid_reflux': 8.0,
        'constipation': 7.0, 'stomach_pain': 6.0
    }
    # 4번째 인자 제거
    st.plotly_chart(plot_fixed_ratio_comparison("Mounjaro", "mounjaro", mounjaro_fda), use_container_width=True)
