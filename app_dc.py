import streamlit as st
from data_loader_dc import load_dc_data # 위에서 만든 로컬 csv 읽기 함수
from visualizer_dc import get_dashboard_graphs_dc
from collections import Counter
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("💊 DC 비만치료제 부작용 분석")

df = load_dc_data()

col1, col2 = st.columns(2)
drugs = {'위고비': ('wegovy', 'Reds'), '마운자로': ('mounjaro', 'Blues')}

def get_counts(df, drug_type):
    # 해당 약물로 필터링
    drug_df = df[df['drug_type'] == drug_type]
    
    # 부작용 리스트 추출 및 평탄화 (Flatten)
    all_effects = []
    for effects in drug_df['side_effects'].dropna().astype(str):
        # 쉼표로 구분된 부작용 문자열을 리스트로 변환
        all_effects.extend([e.strip() for e in effects.split(',') if e.strip()])
    
    # 등장 빈도 계산 및 전체 건수 반환
    return Counter(all_effects), len(all_effects)

for i, (name, (key, color)) in enumerate(drugs.items()):
    target = col1 if i == 0 else col2
    with target:
        st.subheader(f"{name} 상세 분석")
        fig_bar, fig_line, fig_sev = get_dashboard_graphs_dc(df, key, color)
        
        st.plotly_chart(fig_bar, use_container_width=True)
        st.plotly_chart(fig_line, use_container_width=True)
        st.plotly_chart(fig_sev, use_container_width=True)

def plot_dc_fda_comparison(drug_name, fda_data, counts, total):
    # 1. '명시되지 않음' 등 불필요한 항목 제거 (데이터 사전 필터링)
    clean_fda = {k: v for k, v in fda_data.items() if '명시' not in k and '기타' not in k}
    
    # 2. FDA 데이터 총합 100% 보정
    total_fda = sum(clean_fda.values())
    fda_fixed = {k: (v / total_fda) * 100 for k, v in clean_fda.items()}
    
    comp_data = []
    for effect, fda_pct in fda_fixed.items():
        # DC 언급 비율 계산
        dc_pct = (counts.get(effect, 0) / total) * 100 if total > 0 else 0
        
        comp_data.append({'부작용': effect, '출처': 'DC인사이드', '비율 (%)': dc_pct})
        comp_data.append({'부작용': effect, '출처': 'FDA (보정)', '비율 (%)': fda_pct})
    
    fig = px.bar(pd.DataFrame(comp_data), x='비율 (%)', y='부작용', color='출처', 
                 barmode='group', orientation='h',
                 title=f"{drug_name} 부작용 비중 비교 (DC vs FDA)")
    return fig

# 위에서 정의하신 딕셔너리 사용
wegovy_fda_kr = {'오심(메스꺼움)': 44.0, '설사': 30.0, '구토': 24.0, '변비': 24.0, '복통': 20.0, '두통': 14.0}
mounjaro_fda_kr = {'오심(메스꺼움)': 42.0, '구토': 36.0, '설사': 22.0, '두통': 17.0, '복통': 15.0, '어지러움': 8.0}

c1, c2 = st.columns(2)
with c1:
    counts_w, total_w = get_counts(df, 'wegovy')
    st.plotly_chart(plot_dc_fda_comparison("위고비", wegovy_fda_kr, counts_w, total_w), use_container_width=True)

with c2:
    counts_m, total_m = get_counts(df, 'mounjaro')
    st.plotly_chart(plot_dc_fda_comparison("마운자로", mounjaro_fda_kr, counts_m, total_m), use_container_width=True)