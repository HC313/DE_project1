import pandas as pd
import streamlit as st
from pymongo import MongoClient

# MongoDB 연결 정보
MONGO_URI = "mongodb+srv://DEproject1:sksmsskawo123!@nje-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

@st.cache_data(ttl=3600) # 파일을 캐시하여 속도 극대화
def load_dc_data():
    try:
        client = MongoClient(MONGO_URI)
        db = client['DEproject']
        
        # 컬렉션에서 데이터 가져오기
        df_mounjaro = pd.DataFrame(list(db['dc_test_cleaned'].find()))
        df_wegovy = pd.DataFrame(list(db['dc_wegovy_cleaned'].find()))
        
        df_wegovy['drug_type'] = 'wegovy'
        df_mounjaro['drug_type'] = 'mounjaro'
        
        df = pd.concat([df_wegovy, df_mounjaro], ignore_index=True)
        
        # _id 컬럼은 스트림릿 출력 시 오류를 유발할 수 있으므로 제거
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
            
        # 날짜 전처리
        df['date'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['year_month'] = df['date'].dt.strftime('%Y-%m').fillna("Unknown")
        
        # 기존 필터링 로직 (부작용 명시되지 않음 제거)
        exclude_keywords = ['명시되지 않음', '기타', '알 수 없음']
        
        def clean_effects(effects_str):
            if pd.isnull(effects_str): return ""
            effects = [e.strip() for e in str(effects_str).split(',') if e.strip()]
            filtered = [e for e in effects if not any(ex in e for ex in exclude_keywords)]
            return ','.join(filtered)

        df['side_effects'] = df['side_effects'].apply(clean_effects)
        
        return df
    
    except Exception as e:
        st.error(f"MongoDB 로드 실패: {e}")
        return pd.DataFrame()