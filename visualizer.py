import plotly.express as px
import pandas as pd
from collections import Counter
import streamlit as st

def get_severity(text):
    text = str(text).lower()
    keywords = {
        'Severe': ['severe', 'hospital', 'emergency', 'unbearable', 'agony', 'debilitating', 'excruciating', 'brutal', 'violent', 'crying'],
        'Moderate': [ 'terrible', 'worst', 'extreme', 'horrible', 'awful', 'intense', 'painful', 'uncomfortable', 'rough', 'struggling', 'hard', 'tough', 'exhausting', 'sucks', 'frustrating', 'sick', 'constant', 'frequent'],
        'Mild': ['mild', 'little', 'bearable', 'slight', 'manageable', 'annoying', 'fine', 'okay', 'minor', 'fleeting', 'temporary', 'occasional', 'barely', 'subtle', 'tolerable', 'light']
    }
    scores = {sev: sum(1 for word in words if word in text) for sev, words in keywords.items()}
    if all(v == 0 for v in scores.values()): return 'Unspecified'
    return max(scores, key=scores.get)

def get_dashboard_graphs(df, drug_name, color_scale):
    if 'drug_type' not in df.columns:
        st.error(f"데이터에 'drug_type' 컬럼이 없습니다. 현재 컬럼: {df.columns.tolist()}")
        return None, None, None

    drug_df = df[df['drug_type'].str.contains(drug_name, case=False, na=False)].copy()
    
    if drug_df.empty:
        return None, None, None
    
    # 'drug_type'으로 매핑된 필드에서 약물 검색
    drug_df = df[df['drug_type'].str.contains(drug_name, case=False, na=False)].copy()
    
    if drug_df.empty:
        return None, None, None

    # 1. 빈도수 (Top 10)
    all_effects = [e.strip() for row in drug_df['side_effects'].dropna().astype(str) for e in row.split(',') if e.strip()]
    if not all_effects:
        return None, None, None
        
    counts = Counter(all_effects)
    top_10 = [item[0] for item in counts.most_common(10)]
    df_counts = pd.DataFrame(counts.most_common(10), columns=['Side_Effect', 'Frequency'])
    fig_bar = px.bar(df_counts, x='Side_Effect', y='Frequency', color='Frequency', color_continuous_scale=color_scale)

    # 2. 월별 추이 (Top 5)
    top_5 = top_10[:5]
    drug_df['split'] = drug_df['side_effects'].str.split(',')
    exploded = drug_df.explode('split')
    exploded['split'] = exploded['split'].str.strip()
    
    trend = exploded[exploded['split'].isin(top_5)].groupby(['year_month', 'split']).size().reset_index(name='count')
    # 이미지에 'ts' 기반으로 생성된 year_month 활용
    trend = trend[trend['year_month'] != "Unknown"]
    
    fig_line = px.line(trend, x='year_month', y='count', color='split', markers=True)
    fig_line.update_traces(line=dict(width=2), marker=dict(size=4))

    # 3. 심각도 (content 필드 기반)
    results = []
    for _, row in drug_df.iterrows():
        # data_loader에서 text_segment를 content로 매핑함
        sev = get_severity(str(row.get('content', '')))
        effects = [e.strip() for e in str(row['side_effects']).split(',') if e.strip()]
        for eff in effects:
            if eff in top_10: 
                results.append({'Side_Effect': eff, 'Severity': sev})
    
    if results:
        pivot = pd.crosstab(pd.DataFrame(results)['Side_Effect'], pd.DataFrame(results)['Severity'])
        for col in ['Mild', 'Moderate', 'Severe', 'Unspecified']:
            if col not in pivot.columns: pivot[col] = 0
        fig_sev = px.bar(pivot[['Mild', 'Moderate', 'Severe', 'Unspecified']], barmode='stack', orientation='h',
                         color_discrete_map={'Mild': '#74c476', 'Moderate': '#fd8d3c', 'Severe': '#e31a1c', 'Unspecified': '#cccccc'})
    else:
        fig_sev = None
    
    return fig_bar, fig_line, fig_sev
