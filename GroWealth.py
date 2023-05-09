import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
from scipy import optimize
import math
import time
import plotly.express as px
from urllib.request import urlopen
import json

st.set_page_config(
    page_title="GroWealth Investments       ",
    page_icon="nirvana.ico",
    layout="wide",
)


np.set_printoptions(precision=3)

tday = dt.datetime.today()

col1, col2 = st.sidebar.columns(2)
col1.image('gw_logo.png', width=300)

st.write("# Welcome to Growealth Investments! ")

html_text = '<p><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 20px;">'
html_text = html_text + '<em><span style="color: rgb(65, 168, 95);">GroWealth Investments</span></em>'
html_text = html_text + '</span></strong> is a <span style="color: rgb(255, 47, 146);">SEBI</span> registered '
html_text = html_text + '<span style="color: rgb(255, 47, 146);">Mutual Fund Distributor</span><span style="color: rgb(243, 121, 52);">'
html_text = html_text + '.&nbsp;</span><span style="color: rgb(0, 0, 0);">With our years of expertise in</span>'
html_text = html_text + '<span style="color: rgb(243, 121, 52);">&nbsp;</span><span style="color: rgb(255, 47, 146);">'
html_text = html_text + 'Financial Products</span><span style="color: rgb(243, 121, 52);">&nbsp;</span>'
html_text = html_text + '<span style="color: rgb(0, 0, 0);">and understanding in</span><span style="color: rgb(243, 121, 52);'
html_text = html_text + '">&nbsp;</span><span style="color: rgb(255, 47, 146);">Data Science</span><span style="color: rgb(243, 121, 52);">'
html_text = html_text + '&nbsp;</span><span style="color: rgb(0, 0, 0);">driven</span><span style="color: rgb(243, 121, 52);">'
html_text = html_text + '&nbsp;</span><span style="color: rgb(255, 47, 146);">Quantitative Models,</span><span style="color: rgb(0, 0, 0);">'
html_text = html_text + ' we help our customers define</span><span style="color: rgb(243, 121, 52);">&nbsp;</span><span style="color: rgb(255, 47, 146);">'
html_text = html_text + 'Financial Goals</span><span style="color: rgb(0, 0, 0);"> and develop </span><span style="color: rgb(255, 47, 146);">'
html_text = html_text + 'Investment Plans</span><span style="color: rgb(0, 0, 0);"> to create </span><span style="color: rgb(255, 47, 146);">'
html_text = html_text + 'Long Term Wealth,</span><span style="color: rgb(0, 0, 0);"> pursuing our mantra - </span>'
html_text = html_text + '<span style="color: rgb(44, 130, 201); font-size: 18px;"></span><span style="color: rgb(4, 51, 255); font-size: 17px;">'
html_text = html_text + '<em>Achieving Financial Nirvana.</em></span></p>'

st.markdown(html_text,unsafe_allow_html=True)


st.markdown('')
st.markdown('')

st.markdown(":red[Have you planned your child's **Higher Education**?]")
st.markdown(":red[Are you worried you won't be able to maintain your standard of living **post-retirement**?]")
st.markdown(":red[Is your insurance policy not adequate to cover any **unforeseen life events** or **medical emergency**?]")
st.markdown(":red[Are you spending too much on your **Taxes**?]")

st.markdown('')
st.markdown(":blue[***Let's GroWealth!!!***]")
st.markdown(":email: [helpdesk@gro-wealth.in](emailto:helpdesk@gro-wealth.in)")




@st.cache_data()
def get_mf_perf():
    df = pd.read_csv('mf_data.csv')
    df['Date'] = df['Date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))

    df.set_index('Date',inplace=True)

    df_perf = pd.read_csv('revised_mf_perf.csv')
    df_perf.set_index('Scheme_Code', inplace=True)

    df_port_dtl = pd.read_csv('mf_port_detail.csv')

    return df, df_perf, df_port_dtl

@st.cache_data()
def get_schm_mapping_data():
    df_schm_map = pd.read_csv('Scheme_Code_Mapping.csv')
    df_schm_map.set_index('Mint_Scheme',inplace=True)
    return df_schm_map


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
            amt_str = amt_str + str(cr_amt) + ",00,000.00"
    elif lkh_amt > 0:
        if lkh_bal > 0:
            amt_str = amt_str + str(lkh_amt) + "," + str(th_amt).rjust(2,'0') + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
        else:
            amt_str = amt_str + str(lkh_amt) + ",000.00"
    elif th_amt > 0:
        amt_str = amt_str + str(th_amt) + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
    else:
        amt_str = amt_str + str(th_bal) + "." + decimal_part


    return amt_str
