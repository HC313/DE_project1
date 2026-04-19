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
        df.columns = df.columns.str.strip().str.lower()
       
        # 1. timestamp를 datetime 객체로 변환
        df['date'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
        
        # 2. 모든 데이터의 year_month를 'YYYY-MM'으로 통일
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        
        # 3. 변환 실패한 데이터 처리
        df['year_month'] = df['year_month'].fillna("Unknown")
        
        return df
