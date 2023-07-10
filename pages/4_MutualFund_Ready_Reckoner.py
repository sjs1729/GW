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
    layout="wide",
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
c_2.image('growealth-logo_long.png', width=300)

@st.cache_data()
def get_mf_perf():
    df = pd.read_csv('mf_data.csv')
    df['Date'] = df['Date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d').date())

    df.set_index('Date',inplace=True)

    df_perf = pd.read_csv('revised_mf_perf.csv')
    df_perf.set_index('Scheme_Code', inplace=True)

    df_port_dtl = pd.read_csv('mf_port_detail.csv')

    return df, df_perf, df_port_dtl







st.title('Fund Details')

df, df_mf_perf, df_port_dtl = get_mf_perf()

params=st.experimental_get_query_params()

def_value = 0
if len(params) > 0:
    try:
        def_schm_id = int(params['id'][0])
        def_value = df_mf_perf.index.get_loc(def_schm_id)
    except:
        def_value = 0


schm_list = [ "{}-{}".format(j, df_mf_perf.loc[j]['Scheme_Name']) for j in df_mf_perf.index ]

s_layout = st.columns((13,8))

schm_select = s_layout[0].selectbox("Select Scheme",schm_list,def_value)
amfi_code = int(schm_select.split("-")[0])
schm_select = schm_select.split("-")[1]

comp_date   = s_layout[1].date_input("Select Date", dt.date(2022, 1, 1))
comp_date = dt.date(comp_date.year, comp_date.month, comp_date.day)



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

num_stocks = df_mf_perf.loc[amfi_code]['NumStocks']

if num_stocks == num_stocks:
    num_stocks = int(df_mf_perf.loc[amfi_code]['NumStocks'])

dict_port_info_1 = {'No of Stocks': num_stocks,
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

if len(rec) > 0:
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

notice_txt = '<p><BR><BR><span style="font-family: Verdana, Geneva, sans-serif; font-size: 10px;">'
notice_txt = notice_txt + '<span style="color: rgb(255,0,20);">Note:Market Data as on 5th July 2023</span>'
st.markdown(notice_txt,unsafe_allow_html=True)
