import streamlit as st
import pandas as pd
import plotly.express as px
from visualizer import get_dashboard_graphs
from data_loader import load_and_clean_data
from collections import Counter

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

f_col1, f_col2 = st.columns(2)

def get_reddit_counts(df, drug_type):
    drug_df = df[df['drug_type'].str.contains(drug_type, case=False, na=False)]
    all_effects = []
    for effects in drug_df['side_effects'].dropna().astype(str):
        all_effects.extend([e.strip() for e in effects.split(',')])
    return Counter(all_effects), len(all_effects)

def plot_comparison(drug_name, drug_key, fda_data, color_map):
    counts, total = get_reddit_counts(df, drug_key)
    
    comp_data = []
    for effect, fda_pct in fda_data.items():
        # Reddit 내 빈도를 100점 만점 비율로 계산
        reddit_pct = (counts.get(effect, 0) / total) * 100 if total > 0 else 0
        comp_data.append({'Side Effect': effect.replace('_', ' ').title(), 'Source': 'Reddit+X', 'Percentage (%)': reddit_pct})
        comp_data.append({'Side Effect': effect.replace('_', ' ').title(), 'Source': 'FDA', 'Percentage (%)': fda_pct})
    
    fig = px.bar(pd.DataFrame(comp_data), x='Percentage (%)', y='Side Effect', color='Source', 
                 barmode='group', orientation='h', color_discrete_map=color_map,
                 title=f"{drug_name} Side Effects")
    fig.update_layout(yaxis={'categoryorder':'total ascending'}) # 빈도순 정렬
    return fig

with f_col1:
    wegovy_fda = {
        'nausea': 44.0, 'diarrhea': 30.0, 'vomiting': 24.0, 'constipation': 24.0, 'stomach_pain': 20.0,
        'headache': 14.0, 'fatigue': 11.0, 'acid_reflux': 9.0, 'dizziness': 8.0
    }
    # plot_comparison 함수 호출 (위고비)
    st.plotly_chart(plot_comparison("Wegovy", "wegovy", wegovy_fda, {'Reddit+X': '#d62728', 'FDA': '#ff9f9a'}), use_container_width=True)

with f_col2:
    mounjaro_fda = {
        'nausea': 18.0, 'diarrhea': 17.0, 'vomiting': 9.0, 'acid_reflux': 8.0,
        'constipation': 7.0, 'stomach_pain': 6.0
    }
    # plot_comparison 함수 호출 (마운자로)
    st.plotly_chart(plot_comparison("Mounjaro", "mounjaro", mounjaro_fda, {'Reddit+X': '#1f77b4', 'FDA': '#aec7e8'}), use_container_width=True)
