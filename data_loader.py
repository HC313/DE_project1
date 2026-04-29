import pandas as pd
import streamlit as st
import json

# 파일 경로 설정 (동일한 디렉토리에 있다고 가정)
DATA_FILE = "Reddit_v7_v2_FINAL_FULL.jsonl"

@st.cache_data(ttl=600)
def load_and_clean_data():
    try:
        # 1. JSONL 파일 로드
        # lines=True 옵션은 각 줄이 개별 JSON 객체인 파일을 읽을 때 사용합니다.
        # 데이터가 크므로 필요한 컬럼만 추리거나 chunk 단위 처리가 가능하지만, 
        # 우선 가장 기본적인 전체 읽기 방식을 적용합니다.
        df = pd.read_json(DATA_FILE, lines=True)
        
        # 2. 기존 데이터 정제 로직 유지
        # 데이터베이스의 _id 필드가 있다면 제거
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
            
        df.columns = df.columns.str.strip().str.lower()
        
        # timestamp가 숫자형인지 확인하고 변환
        df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        
        # 날짜 변환
        try:
            df['date'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
            df['year_month'] = df['date'].dt.strftime('%Y-%m')
        except:
            df['year_month'] = "Unknown"
            
        df['year_month'] = df['year_month'].fillna("Unknown")
        
        return df
        
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다: {DATA_FILE}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()
