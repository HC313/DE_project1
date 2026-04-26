import plotly.express as px
import pandas as pd
from collections import Counter

def get_severity_kr(text):
    text = str(text)
    # 심각도 키워드 (실제 데이터 특성 반영)
    severe_keys = ['응급실', '병원', '입원', '죽을', '뒤질', '너무아픔', '참을수없음', '미치', '미칠', '수액', '응급', '탈수']
    mod_keys = ['심함', '힘듦', '힘들', '아픔', '불편', '계속', '자주', '괴로움', '못참겠음', '밤새', '고통']
    mild_keys = ['살짝', '조금', '그럭저럭', '참을만함', '괜찮음', '약간', '잠시', '잠깐']
    
    if any(k in text for k in severe_keys): return 'Severe'
    if any(k in text for k in mod_keys): return 'Moderate'
    if any(k in text for k in mild_keys): return 'Mild'
    return 'Unspecified'

def get_dashboard_graphs_dc(df, drug_type, color_scale):
    drug_df = df[df['drug_type'] == drug_type].copy()
    
    # 1. 상위 10개 부작용 빈도
    all_effects = [e.strip() for row in drug_df['side_effects'].dropna().astype(str) for e in row.split(',') if e.strip()]
    top_10 = Counter(all_effects).most_common(10)
    top_10_names = [item[0] for item in top_10]
    fig_bar = px.bar(pd.DataFrame(top_10, columns=['부작용', '언급량']), x='부작용', y='언급량', color='언급량', color_continuous_scale=color_scale, title="상위 10개 부작용 빈도")

    # 2. 상위 5개 부작용 시계열 추이
    top_5 = top_10_names[:5]
    drug_df['split'] = drug_df['side_effects'].str.split(',')
    exploded = drug_df.explode('split')
    exploded['split'] = exploded['split'].str.strip()
    all_months = pd.date_range(start='2024-09', end='2025-12', freq='MS').strftime('%Y-%m').tolist()
    
    trend = exploded[exploded['split'].isin(top_5)].groupby(['year_month', 'split']).size().reset_index(name='count')
    pivot = trend.pivot(index='year_month', columns='split', values='count').fillna(0).reindex(index=all_months, columns=top_5, fill_value=0)
    trend_filled = pivot.reset_index().melt(id_vars='year_month', var_name='split', value_name='count')
    fig_line = px.line(trend_filled, x='year_month', y='count', color='split', markers=True, title="상위 5개 부작용 추이")
    fig_line.update_xaxes(range=[all_months[0], all_months[-1]], type='category')

    # 3. 상위 10개 부작용 심각도 (original_full_text 사용!)
    sev_data = []
    for _, row in drug_df.iterrows():
        sev = get_severity_kr(str(row.get('original_full_text', ''))) # 원문 분석
        effects = [e.strip() for e in str(row['side_effects']).split(',') if e.strip()]
        for eff in effects:
            if eff in top_10_names: # 상위 10개만 포함
                sev_data.append({'부작용': eff, '심각도': sev})
    
    df_sev = pd.DataFrame(sev_data)
    pivot_sev = pd.crosstab(df_sev['부작용'], df_sev['심각도']).reindex(index=top_10_names, columns=['Mild', 'Moderate', 'Severe', 'Unspecified'], fill_value=0)
    fig_sev = px.bar(pivot_sev, barmode='stack', orientation='h', title="상위 10개 부작용 심각도 분포")
    
    return fig_bar, fig_line, fig_sev