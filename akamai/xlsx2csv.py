#!/usr/bin/env python3
"""
xlsx 파일을 CSV로 변환하는 스크립트
사용법: python xlsx2csv.py input.xlsx [output.csv]
"""

import sys
import pandas as pd
import os
from pathlib import Path
import warnings

# pandas 2.x에서 발생할 수 있는 경고 무시
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


def xlsx_to_csv(input_file, output_file=None, sheet_name=0):
    """
    xlsx 파일을 CSV로 변환하는 함수 (pandas 2.x 최적화)
    
    Args:
        input_file (str): 입력 xlsx 파일 경로
        output_file (str, optional): 출력 csv 파일 경로. None이면 자동 생성
        sheet_name: 시트 이름 또는 인덱스 (기본값: 0, 첫 번째 시트)
    """
    try:
        # xlsx 파일 읽기 (pandas 2.x 최적화)
        print(f"xlsx 파일을 읽는 중: {input_file}")
        
        # 엔진을 명시적으로 지정하여 pandas 2.x에서 더 안정적으로 작동
        if input_file.lower().endswith('.xlsx'):
            df = pd.read_excel(input_file, sheet_name=sheet_name, engine='openpyxl')
        else:
            df = pd.read_excel(input_file, sheet_name=sheet_name, engine='xlrd')
        
        # 출력 파일명이 지정되지 않은 경우 자동 생성
        if output_file is None:
            input_path = Path(input_file)
            output_file = input_path.with_suffix('.csv')
        
        # CSV로 저장 (pandas 2.x 최적화)
        print(f"CSV 파일로 저장 중: {output_file}")
        
        # pandas 2.x에서 권장되는 방식으로 저장
        df.to_csv(
            output_file, 
            index=False, 
            encoding='utf-8-sig',
            lineterminator='\n'  # 명시적으로 줄바꿈 문자 지정
        )
        
        print(f"변환 완료! {len(df)} 행, {len(df.columns)} 열의 데이터가 저장되었습니다.")
        print(f"컬럼: {', '.join(df.columns.tolist())}")
        return True
        
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - {input_file}")
        return False
    except ImportError as e:
        print(f"오류: 필요한 라이브러리가 설치되지 않았습니다 - {e}")
        print("다음 명령으로 설치하세요: pip install openpyxl xlrd")
        return False
    except Exception as e:
        print(f"오류: {e}")
        return False


def main():
    """메인 함수"""
    # 명령행 인자 확인
    if len(sys.argv) < 2:
        print("사용법: python xlsx2csv.py input.xlsx [output.csv]")
        print("예시: python xlsx2csv.py data.xlsx")
        print("예시: python xlsx2csv.py data.xlsx output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 입력 파일 존재 확인
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일이 존재하지 않습니다 - {input_file}")
        sys.exit(1)
    
    # 파일 확장자 확인
    if not input_file.lower().endswith(('.xlsx', '.xls')):
        print("오류: xlsx 또는 xls 파일만 지원됩니다.")
        sys.exit(1)
    
    # pandas 버전 확인
    print(f"pandas 버전: {pd.__version__}")
    
    # 변환 실행
    success = xlsx_to_csv(input_file, output_file)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
