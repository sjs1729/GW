import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import time
import plotly.express as px
from urllib.request import urlopen
import json

@st.cache_data()
def get_mf_perf():
    df = pd.read_csv('mf_data.csv')
    df['Date'] = df['Date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))

    df.set_index('Date',inplace=True)

    df_perf = pd.read_csv('revised_mf_perf.csv')
    df_perf.set_index('Scheme_Code', inplace=True)

    df_port_dtl = pd.read_csv('mf_port_detail.csv')

    return df, df_perf, df_port_dtl

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


st.title('Fund Details')

df, df_mf_perf, df_port_dtl = get_mf_perf()

schm_list = [ "{}-{}".format(j, df_mf_perf.loc[j]['Scheme_Name']) for j in df_mf_perf.index ]

s_layout = st.columns((13,8))

schm_select = s_layout[0].selectbox("Select Scheme",schm_list,0)
amfi_code = int(schm_select.split("-")[0])
schm_select = schm_select.split("-")[1]

comp_date   = s_layout[1].date_input("Select Date", dt.date(2022, 1, 1))
comp_date = dt.datetime(comp_date.year, comp_date.month, comp_date.day)



cols = ['Nifty',schm_select]
df_mf=df[df.index >= comp_date][cols].dropna()


df_mf_norm = df_mf * 100 / df_mf.iloc[0]


fig = px.line(df_mf_norm)


fig.update_layout(title_text="{} vs Nifty".format(schm_select),
                          title_x=0.2,
                          title_font_size=17,
                          xaxis_title="",
                          yaxis_title="Value of Rs.100")
fig.update_layout(showlegend=True)
fig.update_layout(legend_title='')
fig.update_layout(legend=dict(
                    x=0.3,
                    y=-0.25,
                    traceorder='normal',
                    font=dict(size=12,)
                 ))

fig.update_layout(height=500)
fig.update_layout(width=550)

s_layout[0].markdown('<BR>',unsafe_allow_html=True)
s_layout[0].plotly_chart(fig)

#st.write(df_mf_perf.columns)
dict_basic_info = {'Fund House': df_mf_perf.loc[amfi_code]['Fund_House'],
         'Fund Category': df_mf_perf.loc[amfi_code]['Scheme_Category'],
         'Inception Date': df_mf_perf.loc[amfi_code]['Inception_Date'],
         'Fund Age': "{} Yrs".format(df_mf_perf.loc[amfi_code]['Age']),
         'AUM': "{} Cr".format(df_mf_perf.loc[amfi_code]['AUM']),
         'Expense Ratio': df_mf_perf.loc[amfi_code]['Expense'],
         'Crisil Rating': df_mf_perf.loc[amfi_code]['CrisilRank'],
         'Fund Manager': df_mf_perf.loc[amfi_code]['FundManagers']
        }

html_text = get_markdown_dict(dict_basic_info,12)
#html_text = '<b>Basic Info</b>' + html_text
s_layout[1].markdown('<b>Basic Info</b>',unsafe_allow_html=True)

s_layout[1].markdown(html_text,unsafe_allow_html=True)

dict_perf_info = {'3M Returns': df_mf_perf.loc[amfi_code]['3M Ret'],
         '1Y Returns': df_mf_perf.loc[amfi_code]['1Y Ret'],
         '3Y Returns': df_mf_perf.loc[amfi_code]['3Y Ret'],
         '5Y Returns': df_mf_perf.loc[amfi_code]['5Y Ret'],
         '1Y Rolling Returns': df_mf_perf.loc[amfi_code]['Roll_Ret_1Y'],
         '3Y Rolling Returns': df_mf_perf.loc[amfi_code]['Roll_Ret_3Y'],
         'Sharpe Ratio': df_mf_perf.loc[amfi_code]['Sharpe Ratio'],
         'Sortino Ratio': df_mf_perf.loc[amfi_code]['Sortino Ratio'],
         'Info Ratio': df_mf_perf.loc[amfi_code]['Info Ratio']

        }

html_text = get_markdown_dict(dict_perf_info,12)

s_layout[1].markdown('<b>Key Performance</b>',unsafe_allow_html=True)

s_layout[1].markdown(html_text,unsafe_allow_html=True)

s_layout = st.columns((4,4,4))

df_schm_port = df_port_dtl[df_port_dtl['Scheme_Code']==amfi_code]


dict_port_info_1 = {'No of Stocks': int(df_mf_perf.loc[amfi_code]['NumStocks']),
             'Equity %': df_mf_perf.loc[amfi_code]['Equity_Holding'],
             'Large Cap %': round(df_schm_port[df_schm_port['M-Cap']=='Large Cap']['Pct_Holding'].sum(),2),
             'Mid Cap %': round(df_schm_port[df_schm_port['M-Cap']=='Mid Cap']['Pct_Holding'].sum(),2),
             'Small Cap %': round(df_schm_port[df_schm_port['M-Cap']=='Small Cap']['Pct_Holding'].sum(),2),
             'F&O %': df_mf_perf.loc[amfi_code]['F&O_Holding'],
             'Foreign %': df_mf_perf.loc[amfi_code]['Foreign_Holding'],
             'Top 5 %': df_mf_perf.loc[amfi_code]['Top5_Pct'],
             'Debt Modified Duration': df_mf_perf.loc[amfi_code]['Modified_Duration'],
             'Debt YTM': df_mf_perf.loc[amfi_code]['YTM']
            }
html_text = get_markdown_dict(dict_port_info_1,12)

s_layout[0].markdown('<br>',unsafe_allow_html=True)
s_layout[0].markdown('<b>Fund Portfolio Summary</b>',unsafe_allow_html=True)
s_layout[0].markdown(html_text,unsafe_allow_html=True)

dict_port_info_2 = {'Volatility': round(df_mf_perf.loc[amfi_code]['Volatility'],2),
             'Beta': df_mf_perf.loc[amfi_code]['Beta'],
             'Alpha': df_mf_perf.loc[amfi_code]['Alpha'],
             'R-Squared': df_mf_perf.loc[amfi_code]['R-Squared'],
             '% Positive Year': df_mf_perf.loc[amfi_code]['Pos_Year%'],
             'Rel Max Drawdown Nifty':  round(df_mf_perf.loc[amfi_code]['Rel_MaxDD'],2),
             'Probability >10% Return': round(df_mf_perf.loc[amfi_code]['Prob_10Pct'],2),
             'Corr Coeff with Nifty': round(df_mf_perf.loc[amfi_code]['NIFTY_CORR'],2),
             '****':'NA',
             '**** ':'NA'
            }
html_text = get_markdown_dict(dict_port_info_2,12)

s_layout[1].markdown('<br>',unsafe_allow_html=True)
s_layout[1].markdown('<b>Fund Volatility Details</b>',unsafe_allow_html=True)
s_layout[1].markdown(html_text,unsafe_allow_html=True)

dict_port_info_3 = {'Daily Returns > 1%': round(df_mf_perf.loc[amfi_code]['GT_1PCT'],2),
             'Daily Returns > 3%': df_mf_perf.loc[amfi_code]['GT_3PCT'],
             'Daily Returns > 5%': df_mf_perf.loc[amfi_code]['GT_5PCT'],
             'Daily Returns < -1%': df_mf_perf.loc[amfi_code]['LT_NEG_1PCT'],
             'Daily Returns < -3%': df_mf_perf.loc[amfi_code]['LT_NEG_3PCT'],
             'Daily Returns < -5%':  round(df_mf_perf.loc[amfi_code]['LT_NEG_5PCT'],2),
             'Positive Daily Returns': round(df_mf_perf.loc[amfi_code]['POS_PCT'],2),
             'Returns > Nifty': round(df_mf_perf.loc[amfi_code]['PCT_GT_NIFTY'],2),
             'Returns > Nifty+':round(df_mf_perf.loc[amfi_code]['GT_NIFTY_UP'],2),
             'Returns > Nifty-':round(df_mf_perf.loc[amfi_code]['GT_NIFTY_DOWN'],2)
            }
html_text = get_markdown_dict(dict_port_info_3,12)

s_layout[2].markdown('<br>',unsafe_allow_html=True)
s_layout[2].markdown('<b>Daily Returns - Statistics</b>',unsafe_allow_html=True)
s_layout[2].markdown(html_text,unsafe_allow_html=True)


df_top10_stks = df_schm_port[df_schm_port['Equity_Debt']=='Equity'][['Asset_Name','Pct_Holding']].head(10)
#df_top10_stks.loc[len(df_top10_stks)]=['Total',df_top10_stks['Pct_Holding'].sum()]

df_top10_sector = df_schm_port.groupby(by=['Sector']).sum()['Pct_Holding'].sort_values(ascending=False).head(10)
#df_top10_sector.loc[len(df_top10_sector)] = df_top10_sector.sum()

df_stk_new_add = df_schm_port[df_schm_port['Status']=='New Addition']['Asset_Name'].head(10)
df_stk_net_inc = df_schm_port[df_schm_port['Status']=='Increased']['Asset_Name'].head(10)
df_stk_net_dec = df_schm_port[df_schm_port['Status']=='Decreased']['Asset_Name'].head(10)
df_stk_removed = df_schm_port[df_schm_port['Status']=='Removed']['Asset_Name'].head(10)



rec = []
for i in range(len(df_top10_stks)):
    serial_no = i + 1
    top10_asset = df_top10_stks.iloc[i]['Asset_Name']
    top10_asset_holding = round(df_top10_stks.iloc[i]['Pct_Holding'],2)

    if i < len(df_top10_sector):
        top10_sector = df_top10_sector.index[i]
        top10_sector_holding = round(df_top10_sector.values[i],2)
    else:
        top10_sector = ''
        top10_sector_holding = ''

    if i < len(df_stk_new_add):
        stk_added = df_stk_new_add.values[i]
    else:
        stk_added = ''

    if i < len(df_stk_net_inc):
        stk_increased = df_stk_net_inc.values[i]
    else:
        stk_increased = ''

    if i < len(df_stk_net_dec):
        stk_decreased = df_stk_net_dec.values[i]
    else:
        stk_decreased = ''

    if i < len(df_stk_removed):
        stk_removed = df_stk_removed.values[i]
    else:
        stk_removed = ''



    values = i+1, top10_asset, top10_asset_holding, top10_sector, top10_sector_holding,  \
                  stk_added, stk_increased, stk_decreased, stk_removed
    rec.append(values)

values = 'Total','',round(df_top10_stks['Pct_Holding'].sum(),2),'',round(df_top10_sector.sum(),2),'','','',''
rec.append(values)

df_top10_port = pd.DataFrame(rec,columns=['Serial','Top10 Stocks','Top10 Stock %', 'Top10 Sectors','Top10 Sector %',    \
                                          'Stocks Added', 'Stocks Increased','Stocks Decreased','Stocks Removed'
                                         ])
html_script = get_markdown_table(df_top10_port)

st.markdown('<BR><BR>Fund Portfolio Details',unsafe_allow_html=True)
st.markdown(html_script,unsafe_allow_html=True)
#s_layout[2].write(df_top10_sector.index)
#except:
#st.markdown('<BR><BR>*** Data Not Available for {}'.format(schm_select),unsafe_allow_html=True)
