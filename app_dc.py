import streamlit as st
from data_loader_dc import load_dc_data # 위에서 만든 로컬 csv 읽기 함수
from visualizer_dc import get_dashboard_graphs_dc
from collections import Counter
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("DC Visualization Dashboard")

df = load_dc_data()

col1, col2 = st.columns(2)
drugs = {'🔴Wegovy': ('wegovy', 'Reds'), '🔵Mounjaro': ('mounjaro', 'Blues')}

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
        st.subheader(f"{name} DC Data Visualization")
        fig_bar, fig_line, fig_sev = get_dashboard_graphs_dc(df, key, color)
        
        st.plotly_chart(fig_bar, use_container_width=True)
        st.plotly_chart(fig_line, use_container_width=True)
        st.plotly_chart(fig_sev, use_container_width=True)

