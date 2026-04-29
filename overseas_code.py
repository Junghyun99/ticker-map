'''해외주식종목코드 정제 파이썬 파일
미국 : nasmst.cod, nysmst.cod, amsmst.cod, 
중국 : shsmst.cod, shimst.cod, szsmst.cod, szimst.cod, 
일본 : tsemst.cod, 
홍콩 : hksmst.cod, 
베트남 : hnxmst.cod, hsxmst.cod'''

'''
※ 유의사항 ※
실행 환경 혹은 원본 파일의 칼럼 수의 변경으로 간혹 정제코드 파일(overseas_stock_code.py)이 실행되지 않을 수 있습니다.
해당 경우, URL에 아래 링크를 복사+붙여넣기 하여 원본 파일을 다운로드하시기 바랍니다.
. https://new.real.download.dws.co.kr/common/master/{val}mst.cod.zip
. {val} 자리에 원하시는 시장코드를 넣어주세요.
. 'nas','nys','ams','shs','shi','szs','szi','tse','hks','hnx','hsx'
. 순서대로 나스닥, 뉴욕, 아멕스, 상해, 상해지수, 심천, 심천지수, 도쿄, 홍콩, 하노이, 호치민
'''

import pandas as pd
import urllib.request
import ssl
import zipfile
import os

base_dir = os.getcwd()

def get_overseas_master_dataframe(base_dir,val):

    ssl._create_default_https_context = ssl._create_unverified_context
    # urllib.request.urlretrieve(f"https://new.real.download.dws.co.kr/common/master/{val}mst.cod.zip", base_dir + f"\\{val}mst.cod.zip")
    urllib.request.urlretrieve(f"https://new.real.download.dws.co.kr/common/master/{val}mst.cod.zip", os.path.join(base_dir, f"{val}mst.cod.zip"))
    os.chdir(base_dir)

    overseas_zip = zipfile.ZipFile(f'{val}mst.cod.zip')
    overseas_zip.extractall()
    overseas_zip.close()

    # file_name = base_dir + f"\\{val}mst.cod"
    file_name = os.path.join(base_dir, f"{val}mst.cod")
    columns = ['National code', 'Exchange id', 'Exchange code', 'Exchange name', 'Symbol', 'realtime symbol', 'Korea name', 'English name', 'Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)', 'currency', 'float position', 'data type', 'base price', 'Bid order size', 'Ask order size', 'market start time(HHMM)', 'market end time(HHMM)', 'DR 여부(Y/N)', 'DR 국가코드', '업종분류코드', '지수구성종목 존재 여부(0:구성종목없음,1:구성종목있음)', 'Tick size Type', '구분코드(001:ETF,002:ETN,003:ETC,004:Others,005:VIX Underlying ETF,006:VIX Underlying ETN)','Tick size type 상세']
    
    print(f"Downloading...{val}mst.cod")
    # df = pd.read_table(base_dir+f"\\{val}mst.cod",sep='\t',encoding='cp949')
    df = pd.read_table(os.path.join(base_dir, f"{val}mst.cod"), sep='\t',encoding='cp949')
    print(f"Actual columns: {len(df.columns)}")
    if len(df.columns) != len(columns):
        raise ValueError(f"Column count mismatch: expected {len(columns)}, got {len(df.columns)}")
    df.columns = columns
    df.to_excel(f'{val}_code.xlsx',index=False)  # 현재 위치에 엑셀파일로 저장
    print("Excel saved")

    
    return df

try:
    df = get_overseas_master_dataframe(base_dir,'nas')
    print("Done nas")
    df = get_overseas_master_dataframe(base_dir,'nys')
    print("Done nys")
    df = get_overseas_master_dataframe(base_dir,'ams')
    print("Done ams")
except Exception as e:
    print(f"An error occurred: {e}")
