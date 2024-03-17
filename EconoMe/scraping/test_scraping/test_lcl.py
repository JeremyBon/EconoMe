
from json import load
from scraping.lcl import convert_LCLpdf_to_df
from dotenv import load_dotenv
import numpy as np
import os
load_dotenv()

def test_lcl():
    folder="LCL"
    LCL_balance=os.getenv("END_LCL")
    assert LCL_balance is not None
    df=convert_LCLpdf_to_df(folder)
    debit_total=np.round(df['DEBIT'].sum(),2)
    credit_total=np.round(df['CREDIT'].sum(),2)
    balance=np.round(0-debit_total+credit_total-LCL_balance,2)
    assert balance==0
   
    