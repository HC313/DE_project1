import streamlit as st
import pandas as pd
import plotly.express as px
from visualizer import get_dashboard_graphs
from data_loader import load_and_clean_data
from collections import Counter

st.set_page_config(layout="wide", page_title="Reddit Visualization Dashboard")
st.title("Reddit Visualization Dashboard")

# 데이터 로드
df = load_and_clean_data()

# 만약 데이터프레임에 source(출처) 컬럼이 있다면 Reddit만 필터링하는 로직 추가
if 'source' in df.columns:
    df = df[df['source'].str.lower() == 'reddit']

col1, col2 = st.columns(2)

drugs = {'🔴 Wegovy': 'wegovy', '🔵 Mounjaro': 'mounjaro'}
for i, (name, key) in enumerate(drugs.items()):
    with [col1, col2][i]:
        st.subheader(f"{name} Reddit Data Visualization")
        # visualizer.py의 함수를 호출하여 그래프 생성
        b, l, s = get_dashboard_graphs(df, key, 'Reds' if key=='wegovy' else 'Blues')
        
        if b is not None:
            st.plotly_chart(b, use_container_width=True)
            st.plotly_chart(l, use_container_width=True)
            st.plotly_chart(s, use_container_width=True)
        else:
            st.info(f"{name}에 대한 분석 데이터가 충분하지 않습니다.")
