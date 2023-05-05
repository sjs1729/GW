import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import time
import plotly.express as px
from urllib.request import urlopen
import json

@st.cache_data()
def get_mf_portfolio():

    df_perf = pd.read_csv('revised_mf_perf.csv')
    df_perf.set_index('Scheme_Name', inplace=True)

    df_port_dtl = pd.read_csv('mf_port_detail.csv')
    stock_list = [ j for j in df_port_dtl[df_port_dtl['Equity_Debt'] == 'Equity']['Asset_Name'].unique()]
    return df_perf, df_port_dtl, stock_list

def get_markdown_table(data, header='Y', footer='Y'):


    if header == 'Y':

        cols = data.columns
        ncols = len(cols)
        if ncols < 5:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>"
        elif ncols < 7:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:13px'>"
        else:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:11px'>"


        for i in cols:
            if 'Fund' in i or 'Name' in i:
                html_script = html_script + "<th style='text-align:left'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        if ncols < 5:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:13px;padding:1px;';>"
        elif ncols < 7:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:10px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:
            if 'Fund' in k or 'Name' in k:
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'>{}</td>".format(a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script

def get_markdown_dict(dict, font_size = 10, format_amt = 'N'):


    html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>"

    #html_script = html_script +  "<table><style> th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>"

    for j in dict.keys():

        if dict[j] == dict[j]:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:{}px;padding:1px;';>".format(font_size)
            html_script = html_script + "<td style='border:none;padding:2px;font-family:Courier; color:Blue; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size,j)
            if format_amt == 'N':
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:Black; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size -1,dict[j])
            else:
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:Black; font-size:{}px;text-align:right' rowspan='1'>{}</td>".format(font_size -1,display_amount(dict[j]))



    html_script = html_script + '</tbody></table>'

    return html_script


def display_amount(amount):

    if amount != amount:
        amount = 0

    if amount < 0:
        amt_str = '₹ -'
        amount = abs(amount)
    else:
        amt_str = '₹ '

    decimal_part_str = str(round(amount,2)).split(".")

    if len(decimal_part_str) > 1:
        decimal_part = decimal_part_str[1][:2]
        if len(decimal_part) == 1:
            decimal_part = decimal_part.ljust(2,'0')
        else:
            decimal_part = decimal_part.rjust(2,'0')
    else:
        decimal_part = '00'


    amount = round(amount,2)
    cr_amt = int(amount/10000000)
    cr_bal = int(amount - cr_amt * 10000000)

    lkh_amt = int (cr_bal/100000)
    lkh_bal = int(cr_bal - lkh_amt * 100000)

    th_amt  = int(lkh_bal/1000)
    th_bal  = int(lkh_bal - th_amt * 1000)


    if cr_amt > 0:
        if cr_bal > 0:
            amt_str = amt_str + str(cr_amt) + "," + str(lkh_amt).rjust(2,'0') + "," + str(th_amt).rjust(2,'0') + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
        else:
            amt_str = amt_str + str(cr_amt) + ",00,00,000.00"
    elif lkh_amt > 0:
        if lkh_bal > 0:
            amt_str = amt_str + str(lkh_amt) + "," + str(th_amt).rjust(2,'0') + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
        else:
            amt_str = amt_str + str(lkh_amt) + ",00,000.00"
    elif th_amt > 0:
        amt_str = amt_str + str(th_amt) + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
    else:
        amt_str = amt_str + str(th_bal) + "." + decimal_part


    return amt_str


st.title('Stocks in Mutual Funds')

df_perf,df_port_dtl, stock_list = get_mf_portfolio()

s_layout = st.columns((3,9,8))
s_layout[0].markdown(" ")
s_layout[0].markdown(" ")
s_layout[0].markdown('<p style="font-size:20px;font-weight: bold;text-align:right   ;vertical-align:middle;color:brown;margin:0px;padding:0px">Search a Stock</p>', unsafe_allow_html=True)

stk_select = s_layout[1].selectbox("Search a Stock",stock_list,0,label_visibility="hidden")

df_search = df_port_dtl[df_port_dtl['Asset_Name']==stk_select][['Scheme_Name','Pct_Holding','Status']]

df_search['AUM'] = 0.0

for i in df_search.index:
    sch_name = df_search.loc[i]['Scheme_Name']
    df_search.at[i,'AUM'] = df_perf.loc[sch_name]['AUM']

tot_increase = df_search[df_search['Status'] == 'Increased']['Scheme_Name'].count()
tot_decrease = df_search[df_search['Status'] == 'Decreased']['Scheme_Name'].count()
tot_new_add  = df_search[df_search['Status'] == 'New Addition']['Scheme_Name'].count()
tot_removed  = df_search[df_search['Status'] == 'Removed']['Scheme_Name'].count()
tot_nochange = df_search[df_search['Status'] == 'No Change']['Scheme_Name'].count()
total = df_search['Scheme_Name'].count()

st.markdown(" ")
st.markdown(" ")

s_layout = st.columns((1,1,1,1,1,1))
html_text = '<p><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:blue;">New Addition: </span></strong>'
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

html_text = '<p style="text-align:right;"><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:red;">Total: </span></strong>'
html_text = html_text + '<span style="font-family: Verdana, Geneva, sans-serif; font-size: 13px;color:brown;">{}  </span>'.format(total)
s_layout[5].markdown(html_text,unsafe_allow_html=True)

html_text = get_markdown_table(df_search)
st.markdown(html_text,unsafe_allow_html=True)
