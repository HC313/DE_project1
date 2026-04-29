import pandas as pd
import streamlit as st
import pymongo

# 몽고DB 연결 정보
MONGO_URI = "mongodb+srv://DEproject1:sksmsskawo123!@nje-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

@st.cache_data(ttl=600) # 10분마다 캐시 갱신
def load_and_clean_data():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client["DEproject"] # DB 이름 확인 필요
        
        # 1. Reddit 컬렉션 로드
        reddit_data = list(db["Reddit_Cleaned_v3"].find())
        df_reddit = pd.DataFrame(reddit_data)
        
        # 2. X(트위터) 컬렉션 로드 
        x_data = list(db["X_Cleaned_v3"].find())
        df_x = pd.DataFrame(x_data)
        
        # 데이터 합치기
        df = pd.concat([df_reddit, df_x], ignore_index=True)
        
        # 몽고DB의 _id 컬럼 제거
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
            
        # 데이터 정제
        df.columns = df.columns.str.strip().str.lower()
        df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        
        # 날짜 변환
        try:
            df['date'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
            df['year_month'] = df['date'].dt.strftime('%Y-%m')
        except:
            df['year_month'] = "Unknown"
            
        df['year_month'] = df['year_month'].fillna("Unknown")
        
        return df
        
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {e}")
        return pd.DataFrame() # 빈 데이터프레임 반환
