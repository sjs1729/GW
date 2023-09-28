import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import time
import plotly.express as px
from urllib.request import urlopen
import json
from shared_functions import *


st.set_page_config(
    page_title="GroWealth Investments       ",
    page_icon="nirvana.ico",
    layout="wide"
    )


np.set_printoptions(precision=3)

tday = dt.datetime.today()

st.markdown(
    """
    <style>
    .css-k1vhr4 {
        margin-top: -60px;
    }



    </style>
    """,
    unsafe_allow_html=True
)
c_1, c_2 = st.columns((8,4))
c_2.image('growealth-logo_long.png')

@st.cache_data()
def get_mf_portfolio():

    df_perf = pd.read_csv('revised_mf_perf.csv')
    df_perf.set_index('Scheme_Name', inplace=True)

    df_port_dtl = pd.read_csv('mf_port_detail.csv')
    stock_list = [ j for j in df_port_dtl[df_port_dtl['Equity_Debt'] == 'Equity']['Asset_Name'].unique()]
    return df_perf, df_port_dtl, stock_list




st.title('Stocks in Mutual Funds')

df_perf,df_port_dtl, stock_list = get_mf_portfolio()


#col1,col2 = st.columns((2,4))
Reverse_Search, Top_20 = st.tabs(["Stock Reverse Search", "Top 20 Most Traded Stocks in MF"])
with Reverse_Search:
    st.markdown("<BR>",unsafe_allow_html=True)

    s_layout = st.columns((3,9,8))

    s_layout[0].markdown('<p style="font-size:18px;font-weight: bold;text-align:right   ;vertical-align:middle;color:brown;margin:0px;padding:0px">Search a Stock</p>', unsafe_allow_html=True)

    stk_select = s_layout[1].selectbox("Search a Stock",stock_list,0,label_visibility="collapsed")

    df_search = df_port_dtl[df_port_dtl['Asset_Name']==stk_select][['Scheme_Name','Pct_Holding','Status']]

    df_search['AUM'] = 0.0


    for i in df_search.index:
        sch_name = df_search.loc[i,'Scheme_Name']
        df_search.at[i,'AUM'] = df_perf.loc[sch_name,'AUM']

    tot_increase = df_search[df_search['Status'] == 'Increased']['Scheme_Name'].count()
    tot_decrease = df_search[df_search['Status'] == 'Decreased']['Scheme_Name'].count()
    tot_new_add  = df_search[df_search['Status'] == 'New Addition']['Scheme_Name'].count()
    tot_removed  = df_search[df_search['Status'] == 'Removed']['Scheme_Name'].count()
    tot_nochange = df_search[df_search['Status'] == 'No Change']['Scheme_Name'].count()
    total = df_search['Scheme_Name'].count()

    st.markdown(" ")
    st.markdown(" ")

    s_layout = st.columns((1,1,1,1,1,1))
    html_text = '<p style="text-align:center;"><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:blue;">New Addition: </span></strong>'
    html_text = html_text + '<span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:brown;">{}</span>'.format(tot_new_add)
    s_layout[0].markdown(html_text,unsafe_allow_html=True)
    html_text = '<p style="text-align:center;"><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:blue;">Increased: </span></strong>'
    html_text = html_text + '<span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:brown;">{}  </span>'.format(tot_increase)
    s_layout[1].markdown(html_text,unsafe_allow_html=True)
    html_text = '<p style="text-align:center;"><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:blue;">Decreased: </span></strong>'
    html_text = html_text + '<span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:brown;">{}  </span>'.format(tot_decrease)
    s_layout[2].markdown(html_text,unsafe_allow_html=True)
    html_text = '<p style="text-align:center;"><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:blue;">Removed: </span></strong>'
    html_text = html_text + '<span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:brown;">{} </span>'.format(tot_removed)
    s_layout[3].markdown(html_text,unsafe_allow_html=True)
    html_text = '<p style="text-align:center;"><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:blue;">No Change: </span></strong>'
    html_text = html_text + '<span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:brown;">{}  </span>'.format(tot_nochange)
    s_layout[4].markdown(html_text,unsafe_allow_html=True)

    html_text = '<p style="text-align:center;"><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:red;">Total: </span></strong>'
    html_text = html_text + '<span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:brown;">{}  </span>'.format(total)
    s_layout[5].markdown(html_text,unsafe_allow_html=True)

    html_text = get_markdown_table(df_search)
    st.markdown(html_text,unsafe_allow_html=True)

    notice_txt = '<p><BR><BR><span style="font-family: Verdana, Geneva, sans-serif; font-size: 10px;">'
    notice_txt = notice_txt + '<span style="color: rgb(255,0,20);">Note:Market Data as on {}</span>'.format(get_data_refresh_date())
    st.markdown(notice_txt,unsafe_allow_html=True)


with Top_20:
    st.markdown('<p style="font-size:18px;font-weight:bold;text-align:left;vertical-align:middle;color:brown;margin:0px;padding:0px">Top 20 Stocks Traded in MF</p>', unsafe_allow_html=True)
    st.markdown("<BR>",unsafe_allow_html=True)




    for status in ['New Addition','Increased','Decreased','Removed']:


        df_1 = df_port_dtl[df_port_dtl['Status']== status]
        result = df_1.groupby('Asset_Name').size().reset_index(name='Count')
        result = result.sort_values(by='Count',ascending=False).head(20)
        result.columns = ["Top 20 Stocks - {}".format(status),"{} - Count".format(status)]
        result.index = [i for i in range(20)]

        if status == 'New Addition':
            df_x = result
        else:
            df_x = pd.concat([df_x,result],join="outer", axis=1)

    html_text = get_markdown_table(df_x)
    st.markdown(html_text,unsafe_allow_html=True)

    notice_txt = '<p><BR><BR><span style="font-family: Verdana, Geneva, sans-serif; font-size: 10px;">'
    notice_txt = notice_txt + '<span style="color: rgb(255,0,20);">Note:Market Data as on {}</span>'.format(get_data_refresh_date())
    st.markdown(notice_txt,unsafe_allow_html=True)
