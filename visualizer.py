import plotly.express as px
import pandas as pd
from collections import Counter

def get_severity(text):
    text = str(text).lower()
    # 부작용 이름에 의한 오인 방지
    text = text.replace('severe_gastrointestinal', 'gi_issue')
    
    # 심각도 가중치 점수제
    keywords = {
        'Severe': ['hospital', 'er', 'emergency', 'unbearable', 'agony', 'debilitating', 'excruciating', 'brutal', 'violent', 'crying'],
        'Moderate': ['severe', 'terrible', 'worst', 'extreme', 'horrible', 'awful', 'intense', 'painful', 'uncomfortable', 'rough', 'struggling', 'hard', 'tough', 'exhausting', 'sucks', 'frustrating', 'sick', 'constant', 'frequent'],
        'Mild': ['mild', 'little', 'bearable', 'slight', 'manageable', 'annoying', 'fine', 'okay', 'minor', 'fleeting', 'temporary', 'occasional', 'barely', 'subtle', 'tolerable', 'light']
    }
    scores = {sev: sum(1 for word in words if word in text) for sev, words in keywords.items()}
    if all(v == 0 for v in scores.values()): return 'Unspecified'
    return max(scores, key=scores.get)

def get_dashboard_graphs(df, drug_name, color_scale):
    drug_df = df[df['drug_type'].str.contains(drug_name, case=False, na=False)].copy()

    # 1. 빈도수 (Top 10)
    all_effects = [e.strip() for row in drug_df['side_effects'].dropna().astype(str) for e in row.split(',') if e.strip()]
    top_10 = [item[0] for item in Counter(all_effects).most_common(10)]
    df_counts = pd.DataFrame(Counter(all_effects).most_common(10), columns=['Side_Effect', 'Frequency'])
    fig_bar = px.bar(df_counts, x='Side_Effect', y='Frequency', color='Frequency', color_continuous_scale=color_scale)
    fig_bar.update_layout(coloraxis_cmin=5, coloraxis_cmax=max(df_counts['Frequency']))
    
    # 2. 월별 추이 (Top 5)
    top_5 = top_10[:5]
    drug_df['split'] = drug_df['side_effects'].str.split(',')
    exploded = drug_df.explode('split')
    exploded['split'] = exploded['split'].str.strip()
    trend = exploded[exploded['split'].isin(top_5)].groupby(['year_month', 'split']).size().reset_index(name='count')
    fig_line = px.line(trend, x='year_month', y='count', color='split', markers=True)
    fig_line.update_traces(line=dict(width=2), marker=dict(size=2))

    # 3. 심각도 (Top 10 부작용, content 기준)
    results = []
    for _, row in drug_df.iterrows():
        sev = get_severity(str(row.get('content', '')))
        effects = [e.strip() for e in str(row['side_effects']).split(',') if e.strip()]
        for eff in effects:
            if eff in top_10: results.append({'Side_Effect': eff, 'Severity': sev})
    
    pivot = pd.crosstab(pd.DataFrame(results)['Side_Effect'], pd.DataFrame(results)['Severity'])
    for col in ['Mild', 'Moderate', 'Severe', 'Unspecified']:
        if col not in pivot.columns: pivot[col] = 0
    fig_sev = px.bar(pivot[['Mild', 'Moderate', 'Severe', 'Unspecified']], barmode='stack', orientation='h',
                     color_discrete_map={'Mild': '#74c476', 'Moderate': '#fd8d3c', 'Severe': '#e31a1c', 'Unspecified': '#cccccc'})
    
    return fig_bar, fig_line, fig_sev

