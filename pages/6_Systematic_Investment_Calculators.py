import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import time
from scipy import optimize
import math
import plotly.express as px
from urllib.request import urlopen
import json
from shared_functions import *



st.set_page_config(
    page_title="GroWealth Investments       ",
    page_icon="nirvana.ico",
    layout="wide",
)

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

# Hide Streamlit menu and footer
hide_streamlit_style = """
        <style>
        .stToolbarActions {display: none !important;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


np.set_printoptions(precision=3)

tday = dt.datetime.today()

c_1, c_2 = st.columns((8,4))
c_2.image('growealth-logo_long.png')


#@st.cache_data()
#def get_mf_perf():
#    df = pd.read_csv('mf_data.csv')
#    df['Date'] = df['Date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))

#    df.set_index('Date',inplace=True)
#
#    df_perf.set_index('Scheme_Code', inplace=True)
#
#    df_stp_src.set_index('Scheme_Code', inplace=True)

#    df_port_dtl = pd.read_csv('mf_port_detail.csv')

#    return df, df_perf, df_port_dtl, df_stp_src



def xirr(rate,cash_flow,terminal_value=0):

    npv = 0
    for i in cash_flow.index:
        nYears = cash_flow.loc[i,'Num_Days']/365
        pv = cash_flow.loc[i,'Tran_Value']*(pow((1 + rate / 100), nYears))
        npv = npv + pv

    return  npv+terminal_value

def get_stp(df, ini_inv, stp_amount, stp_freq, dynamic_model):
    ndays = 0
    rec = []
    tday = dt.date.today()
    num_stp = 0
    stp_in_bal_units = 0
    for i in df.index:
        num_days = 0
        units_sold = 0.0
        units_pur = 0.0
        stp_out = 0
        curr_nav_stp_out = df.loc[i]['Source_NAV']
        curr_nav_stp_in  = df.loc[i]['Dest_NAV']
        cashflow =0
        cap_gains = 0.0
        holding_period = 0
        tax_year=""
        tax_amt = 0
        if ndays == 0:
            pur_units = ini_inv/curr_nav_stp_out
            bal_units = pur_units
            net_value = ini_inv
            cashflow  = -1*ini_inv
            num_days = (tday - i).days
            pur_date = i
            pur_nav = curr_nav_stp_out

        if i.month < 4:
            fin_year = i.year
        else:
            fin_year = i.year+1

        if ndays > 0 and ndays % stp_freq == 0:

            if stp_amount > stp_src_value :
                units_sold = bal_units
                stp_out = round(bal_units * curr_nav_stp_out,0)

                units_pur = stp_out/curr_nav_stp_in


            elif bal_units == 0.0:
                units_sold = 0.0
                stp_out = 0.0

            else:
                units_sold = stp_amount/curr_nav_stp_out
                stp_out = stp_amount
                units_pur = stp_out/curr_nav_stp_in


            bal_units = bal_units - units_sold
            cashflow  = stp_out
            num_days = (tday - i).days
            cap_gains = units_sold * (curr_nav_stp_out - pur_nav)
            holding_period = (i - pur_date).days

            stp_in_bal_units  += units_pur




            num_stp = num_stp + 1



        stp_src_value  = round(bal_units * curr_nav_stp_out, 0 )
        stp_dest_value = round(stp_in_bal_units * curr_nav_stp_in, 0 )
        net_value =  stp_src_value + stp_dest_value

        values = i,units_sold, bal_units, curr_nav_stp_out ,stp_out, units_pur, stp_in_bal_units, curr_nav_stp_in, stp_src_value, stp_dest_value, net_value,cashflow,num_days,cap_gains,holding_period,fin_year

        rec.append(values)

        ndays = ndays + 1



    stp  = pd.DataFrame(rec, columns=['Date','STP_OUT_Units','Bal_Units_STP_Out','STP_OUT_NAV','STP_AMOUNT', \
                                      'STP_IN_Units','Bal_Units_STP_In','STP_IN_NAV','STP_SOURCE_FUND_VAL','STP_DEST_FUND_VAL','Net_Value', \
                                      'Tran_Value','Num_Days','Cap Gains','Holding Period','FY'])

    stp.set_index('Date',inplace=True)

    return stp

def get_swp(df, ini_inv, swp_amt, swp_freq,inflation):
    #st.write(df)
    ndays = 0
    rec = []
    tday = dt.date.today()
    num_swp = 0
    for i in df.index:
        num_days = 0
        units_sold = 0
        swp_a = 0
        curr_nav = df.loc[i]['Nav']
        cashflow =0
        cap_gains = 0.0
        holding_period = 0
        tax_year=""
        tax_amt = 0
        if ndays == 0:
            pur_units = ini_inv/curr_nav
            bal_units = pur_units
            net_value = ini_inv
            cashflow  = -1*ini_inv
            num_days = (tday - i).days
            pur_date = i
            pur_nav = curr_nav
        ndays = ndays + 1

        if i.month < 4:
            fin_year = i.year
        else:
            fin_year = i.year+1

        if ndays % swp_freq == 0:

            if swp_amt > net_value:
                units_sold = bal_units
                swp_a = round(bal_units * curr_nav,0)
            elif bal_units == 0.0:
                units_sold = 0.0
                swp_a = 0.0
            else:
                units_sold = swp_amt/curr_nav
                swp_a = swp_amt

            bal_units = bal_units - units_sold
            cashflow  = swp_a
            num_days = (tday - i).days
            cap_gains = units_sold * (curr_nav - pur_nav)
            holding_period = (i - pur_date).days
            if holding_period < 365:
                tax_amt= cap_gains * 0.15
            else:
                tax_amt= cap_gains * 0.1



            num_swp = num_swp + 1
            if num_swp % 12 == 0:
                swp_amt = swp_amt * (1+inflation)


        if net_value > 0.0:
            net_value = round(bal_units * curr_nav,0)

            values = i,curr_nav, bal_units, units_sold,swp_a,net_value,cashflow,num_days,cap_gains,holding_period,fin_year,tax_amt

            rec.append(values)



    swp  = pd.DataFrame(rec, columns=['Date','Nav','Bal_Units','Units_Sold','SWP_AMOUNT','Net_Value','Tran_Value','Num_Days','Cap Gains','Holding Period','FY','TAX_AMOUNT'])

    swp.set_index('Date',inplace=True)

    return swp

config = {'displayModeBar': False}
html_text = '<p style="text-align:center"><BR>'
html_text = html_text + '<strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 24px;">'
html_text = html_text + '<span style="color: rgb(9, 0, 220);text-align:center;">Systematic Investment Calculators</span></strong>'

st.markdown(html_text,unsafe_allow_html=True)

#df, df_mf_perf, df_port_dtl, df_stp_src = get_mf_perf()

df_mf_perf = get_mf_perf()
#st.dataframe(df_mf_perf)

stp_hybrid_categories = ['Equity Savings','Balad Advantage','Arbitrage','Conservative']
df_stp_src = df_mf_perf[(df_mf_perf['SCHEME_TYPE'] == 'Debt') | ((df_mf_perf['SCHEME_CATEGORY'].isin(stp_hybrid_categories)))]

sip,stp, swp = st.tabs(["SIP - Calculator","STP Calculator", "SWP - Calculator"])



with sip:
    col1,col,col2 = st.columns((6,1,7))

   #st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    mthly_sip = col1.number_input("Monthly SIP", min_value=0, step=1000, value=1000)
    investment_period = col1.number_input("Investment period (in years)", min_value=1, max_value=50, value=10)
    step_up_pct = col1.number_input("Annual % Increment in Monthly SIP", min_value=0.0, max_value=50.0, value=0.0, step=0.5)

    expected_return = col1.number_input("Expected return (%)", min_value=0.0, max_value=20.0, step=0.5, value=8.0)

    # Calculations
    monthly_sip = mthly_sip
    investment_value = 0
    total_investment = 0
    rec = []
    for i in range(investment_period * 12):
        if i !=0 and i%12 == 0:
            monthly_sip  = monthly_sip * (1 + step_up_pct/100.0)
        investment_value += monthly_sip
        total_investment += monthly_sip
        investment_value *= (1 + expected_return / 100 / 12)


        values = i+1, monthly_sip,investment_value
        rec.append(values)


    sip_df = pd.DataFrame(rec,columns=['Month','SIP','Fund Value'])
    sip_df.set_index('Month', inplace=True)

    html_text = '<p style="text-align:center">'
    html_text = html_text + '<strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11px;">'
    html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">Investment Value:</span></strong>'
    html_text = html_text + '<span style="color: rgb(0,0, 200);"> {}</span>'.format(display_amount(investment_value))
    html_text = html_text + '<BR><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11px;">'
    html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">Amount Invested:</span></strong>'
    html_text = html_text + '<span style="color: rgb(0,0, 200);"> {}</span><span>  | </span>'.format(display_amount(total_investment))
    html_text = html_text + '<strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11px;">'
    html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">Interest Earned:</span></strong>'
    html_text = html_text + '<span style="color: rgb(0,0, 200);"> {}  </span>'.format(display_amount(investment_value - total_investment))
    html_text = html_text + '<BR></p>'
    col2.markdown(html_text,unsafe_allow_html=True)


    fig = px.line(sip_df[['Fund Value']])


    fig.update_layout(title_text="Fund Growth - Fixed Return",
                              title_x=0.35,
                              title_font_size=16,
                              xaxis_title="Months",
                              yaxis_title="Fund Value")

    fig.update_layout(margin=dict(l=1,r=1,b=1,t=30))

    fig.update_layout(showlegend=False)
    fig.update_layout(legend_title='')
    fig.update_layout(legend=dict(
                        x=0.3,
                        y=-0.25,
                        traceorder='normal',
                        font=dict(size=12,)
                     ))

    fig.update_layout(height=300)
    fig.update_layout(width=450)

    col2.plotly_chart(fig,config=config)
    #col2.markdown(html_text,unsafe_allow_html=True)

    col1.markdown('<BR>',unsafe_allow_html=True)


    st.markdown("-----------------------------------------")

    col1,col,col2 = st.columns((6,1,7))

    checked = col1.checkbox("Back Test with MF Market Data")

    if checked:
        st_date = col1.date_input("Start Date", dt.date(2018, 1, 1))
        st_date = dt.datetime(st_date.year, st_date.month, st_date.day)
        st_date = st_date - dt.timedelta(days=1)
        #start_date = start_date.date()

        end_date = col1.date_input("End Date", dt.date.today(), min_value=st_date)
        end_date = dt.datetime(end_date.year, end_date.month, end_date.day)
        end_date = end_date + dt.timedelta(days=1)

        #df_mf_perf['Inception_Date']= pd.to_datetime(df_mf_perf['Inception_Date'])

        df_mf_perf_sel = df_mf_perf[df_mf_perf['LAUNCH DATE'] < st_date]
        schm_list = [ "{}-{}".format(j, df_mf_perf_sel.loc[j]['SCHEMES']) for j in df_mf_perf_sel.index ]



        schm_select = col1.selectbox("Select Scheme",schm_list,0)
        amfi_code = int(float(schm_select.split("-")[0]))
        schm_select = schm_select.split("-")[1]

        df_mf = get_historical_nav(amfi_code,tday.day)
        #col1.write(df_mf.index[0])
        df_mf = df_mf[(df_mf.index > st_date.date()) & (df_mf.index < end_date.date())]
        df_mf['Units'] = 0.0
        df_mf['Tran_Value'] = 0.0
        df_mf['Num_Days'] = 0.0

        i = 0
        nTran = 0
        units = 0.0
        monthly_sip = mthly_sip
        for j in df_mf.index:


            if i%21 == 0:
                if nTran != 0 and nTran % 12 == 0:
                    monthly_sip  = monthly_sip * (1 + step_up_pct/100.0)
                    #col1.write("{} - {}".format(nTran,display_amount(monthly_sip)))

                nTran = nTran + 1
                #col1.write("{} - {}".format(nTran,i))

                nav = df_mf.loc[j]['Nav']
                units = units + monthly_sip/nav
                df_mf.at[j,'Tran_Value'] = monthly_sip
                df_mf.at[j,'Num_Days'] = (tday.date() - j).days

            i = i + 1
            df_mf.at[j,'Units'] = units

        df_mf['Fund Value'] = df_mf['Nav'] * df_mf['Units']

        #col1.write("Total Investment - {} | Value - {}".format(display_amount(df_mf['Tran_Value'].sum()),display_amount(df_mf['Fund Value'].iloc[-1])))
        #df_mf = df_mf[schm_select]
        #col1.write(df_mf)
        #df_mf.to_csv('SIP.csv')
        df_cash_flow = df_mf[df_mf['Tran_Value'] != 0][['Tran_Value','Num_Days']]
        mkt_amt_invested = df_mf['Tran_Value'].sum()
        mkt_value = df_mf['Fund Value'].iloc[-1]
        mkt_gains = mkt_value - mkt_amt_invested
        market_xirr = round(optimize.newton(xirr, 3, args=(df_cash_flow, mkt_value * -1.0,)),2)
        #col1.write(market_xirr)

        html_text = '<p style="text-align:center">'
        html_text = html_text + '<strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11px;">'
        html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">Investment Value:</span></strong>'
        html_text = html_text + '<span style="color: rgb(0,0, 200);"> {}</span>'.format(display_amount(mkt_value))
        html_text = html_text + '<BR><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11px;">'
        html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">Amt Invested:</span></strong>'
        html_text = html_text + '<span style="color: rgb(0,0, 200);"> {}</span><span>  | </span>'.format(display_amount(mkt_amt_invested))
        html_text = html_text + '<strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11px;">'
        html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">Total Gain:</span></strong>'
        html_text = html_text + '<span style="color: rgb(0,0, 200);"> {}  </span><span>  | </span>'.format(display_amount(mkt_gains))
        html_text = html_text + '<strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11px;">'
        html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">XIRR:</span></strong>'
        html_text = html_text + '<span style="color: rgb(0,0, 200);"> {}%  </span>'.format(market_xirr)
        html_text = html_text + '<BR></p>'
        col2.markdown(html_text,unsafe_allow_html=True)

        fig1 = px.line(df_mf[['Fund Value']])


        fig1.update_layout(title_text="Fund - Market Return",
                                  title_x=0.35,
                                  title_font_size=16,
                                  xaxis_title="",
                                  yaxis_title="Fund Value")

        fig1.update_layout(margin=dict(l=1,r=1,b=1,t=30))

        fig1.update_layout(showlegend=False)
        fig1.update_layout(legend_title='')
        fig1.update_layout(legend=dict(
                            x=0.3,
                            y=-0.25,
                            traceorder='normal',
                            font=dict(size=12,)
                         ))

        fig1.update_layout(height=300)
        fig1.update_layout(width=450)

        #col2.markdown('<BR>',unsafe_allow_html=True)
        col2.plotly_chart(fig1,config=config)
        #col2.markdown(html_text,unsafe_allow_html=True)


        #col1.write(df_cash_flow)



with swp:




    col1,col,col2 = st.columns((10,1,12))

   #st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    corpus = col1.number_input("Initial Corpus", min_value=0, step=100000, value=10000000)

    col2.markdown("   ")

    html_text = '<p style="text-align:left">'
    html_text = html_text + '<BR><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 15px;">'
    html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">{}</span></strong>'.format(display_amount(corpus))
    col2.markdown(html_text, unsafe_allow_html=True)
    swp_withdrawal_freq   = col1.selectbox("SWP Frequency",['Monthly','Fortnightly','Quarterly','Annually'],0)

    if swp_withdrawal_freq == 'Monthly':
        swp_def_value = 0.005 * corpus
        swp_freq = 21
    elif swp_withdrawal_freq == 'Fortnightly':
        swp_def_value = 0.0025 * corpus
        swp_freq = 10
    elif swp_withdrawal_freq == 'Quarterly':
        swp_def_value = 0.015 * corpus
        swp_freq = 126
    elif swp_withdrawal_freq == 'Annualy':
        swp_def_value = 0.06 * corpus
        swp_freq = 252

    swp_def_value = max(100 * int(swp_def_value/100),1000)
    swp_withdrawal_amount = col2.number_input("SWP ", min_value=1000, step=1000, value=swp_def_value, help="Monthly Withdraw amount is recommended to be roughly 0.5% (i.e 6% annually)")

    swp_st_date = col1.date_input("SWP Start Date", dt.date(2017, 1, 1))
    swp_st_date = dt.datetime(swp_st_date.year, swp_st_date.month, swp_st_date.day)
    swp_st_date = swp_st_date - dt.timedelta(days=1)
    #start_date = start_date.date()

    swp_end_date = col2.date_input("SWP End Date", dt.date.today(), min_value=swp_st_date)
    swp_end_date = dt.datetime(swp_end_date.year, swp_end_date.month, swp_end_date.day)
    swp_end_date = swp_end_date + dt.timedelta(days=1)

    swp_inflation = col1.number_input("Annual % Increase in Withdrawal", min_value=0.0, max_value=50.0, value=0.0, step=0.5,help="Annual % Increase in Withdrawal Amount due to Inflation")
    #df_mf_perf['Inception_Date']= pd.to_datetime(df_mf_perf['Inception_Date'])

    df_mf_perf_sel = df_mf_perf[df_mf_perf['LAUNCH DATE'] < swp_st_date]
    schm_list = [ "{}-{}".format(j, df_mf_perf_sel.loc[j]['SCHEMES']) for j in df_mf_perf_sel.index ]



    schm_select = col2.selectbox("Select SWP Scheme",schm_list,0)
    amfi_code = int(float(schm_select.split("-")[0]))
    schm_select = schm_select.split("-")[1]
    #col1.write(swp_st_date)
    #col1.write(swp_end_date)

    df_mf = get_historical_nav(amfi_code,tday)
    #st.write(df_mf.index[0],type(df_mf.index[0]))
    df_mf = df_mf[(df_mf.index > swp_st_date.date()) & (df_mf.index < swp_end_date.date())]

    df_swp = get_swp(df_mf,corpus, swp_withdrawal_amount, swp_freq,swp_inflation/100.0)

    fy_rec = []
    for fy in df_swp['FY'].unique():
        swp_amt_fy   = df_swp[df_swp['FY']==fy]['SWP_AMOUNT'].sum()
        cap_gains_fy = df_swp[df_swp['FY']==fy]['Cap Gains'].sum()
        net_value_fy_close_bal = df_swp[df_swp['FY']==fy]['Net_Value'].iloc[-1]
        net_value_fy_open_bal = df_swp[df_swp['FY']==fy]['Net_Value'].iloc[0]


        values = fy, display_amount(net_value_fy_open_bal),display_amount(swp_amt_fy),display_amount(net_value_fy_close_bal),  \
                    display_amount(cap_gains_fy)
        fy_rec.append(values)

    values = "","",display_amount(df_swp['SWP_AMOUNT'].sum()),  \
                display_amount(df_swp['Net_Value'].iloc[-1]), display_amount(df_swp['Cap Gains'].sum())
    fy_rec.append(values)

    df_fy_data = pd.DataFrame(fy_rec,columns=['FY','Open Bal','SWP Withdrawal','Close Bal','Capital Gains'])
    st.markdown("-----------------------------------------")
    col1,col2 = st.columns((12,9))

    df_cash_flow = df_swp[df_swp['Tran_Value'] != 0][['Tran_Value','Num_Days']]
    mkt_value = df_swp['Net_Value'].iloc[-1]
    #col1.write(df_cash_flow)
    #col1.write(mkt_value)
    swp_xirr = round(optimize.newton(xirr, 3, args=(df_cash_flow, mkt_value,)),2)
    html_table = get_markdown_table(df_fy_data)
    col1.markdown('<BR><BR>',unsafe_allow_html=True)
    col1.markdown(html_table,unsafe_allow_html=True)
    #col1.write(df_fy_data)
    #col2.write(df_swp['Net_Value'])
    fig = px.line(df_swp['Net_Value'])


    #fig.update_layout(title_text="SWP Balance ( XIRR - {}% )".format(str(swp_xirr)),
    fig.update_layout(title_text="",
                              title_x=0.35,
                              title_font_size=16,
                              xaxis_title="",
                              yaxis_title="Net Fund")

    fig.update_layout(margin=dict(l=1,r=1,b=1,t=30))

    fig.update_layout(showlegend=False)
    fig.update_layout(legend_title='')
    fig.update_layout(legend=dict(
                        x=0.3,
                        y=-0.25,
                        traceorder='normal',
                        font=dict(size=12,)
                     ))

    fig.update_layout(height=300)
    fig.update_layout(width=400)

    #col2.markdown('<BR>',unsafe_allow_html=True)
    col2.markdown('<p style="text-align:center"><BR><strong><span style="font-size:18px;color:rgb(0,50,255)">&nbsp; \
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;SWP Balance</span><span   \
                        style="font-size:16px;color:rgb(0,200,255)"> (XIRR - {}%)</span>'.format(str(swp_xirr)),    \
                        unsafe_allow_html=True)

    col2.plotly_chart(fig,config=config)

    col1.markdown('<p style="text-align:left"><span style="font-size:11px;color:rgb(255,0,20)">**FY2024: Apr 2023 - Mar 2024</span>',unsafe_allow_html=True)
    #st.markdown(html_text,unsafe_allow_html=True)


with stp:


    col1,col,col2 = st.columns((10,1,12))

   #st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    corpus = col1.number_input("STP Investment", min_value=0, step=100000, value=1000000)
    col2.markdown("   ")
    html_text = '<p style="text-align:left">'
    html_text = html_text + '<BR><strong><span style="font-family: Verdana, Geneva, sans-serif; font-size: 15px;">'
    html_text = html_text + '<span style="color: rgb(65, 168, 95);text-align:center;">{}</span></strong><BR>'.format(display_amount(corpus))
    col2.markdown(html_text, unsafe_allow_html=True)
    stp_freq   = col1.selectbox("STP Frequency",['Monthly','Fortnightly','Weekly','Daily'],0)

    if stp_freq == 'Monthly':
        stp_freq = 21
    elif stp_freq == 'Fortnightly':
        stp_freq = 10
    elif stp_freq == 'Weekly':
        stp_freq = 5
    elif stp_freq == 'Daily':
        stp_freq = 1

    stp_opt_amt = (corpus/12.0)/int(21/stp_freq )
    stp_opt_amt = int(stp_opt_amt/1000) * 1000

    stp_amount = col2.number_input("STP Investment ", min_value=1000, step=1000, value=stp_opt_amt, help="Amount to be Transferred from Debt to Equity_Holding")

    stp_st_date = col1.date_input("STP Start Date", dt.date(2017, 1, 1))
    stp_st_date = dt.datetime(stp_st_date.year, stp_st_date.month, stp_st_date.day)
    stp_st_date = stp_st_date - dt.timedelta(days=1)
    #start_date = start_date.date()

    stp_end_date = col2.date_input("STP End Date", dt.date.today(), min_value=stp_st_date)
    stp_end_date = dt.datetime(stp_end_date.year, stp_end_date.month, stp_end_date.day)
    stp_end_date = stp_end_date + dt.timedelta(days=1)

    #swp_inflation = col1.number_input("Annual % Increase in Withdrawal", min_value=0.0, max_value=50.0, value=0.0, step=0.5,help="Annual % Increase in Withdrawal Amount due to Inflation")
    #df_mf_perf['Inception_Date']= pd.to_datetime(df_mf_perf['Inception_Date'])
    #df_stp_src['Inception_Date']= pd.to_datetime(df_stp_src['Inception_Date'])

    df_stp_src_sel = df_stp_src[df_stp_src['LAUNCH DATE'] < stp_st_date]

    schm_list_source = [ "{}-{}".format(j, df_stp_src_sel.loc[j]['SCHEMES']) for j in df_stp_src_sel.index ]



    schm_select_source = col1.selectbox("Select STP Source Scheme",schm_list_source,0)
    amfi_code_source = int(float(schm_select_source.split("-")[0]))
    schm_select_source = schm_select_source.split("-")[1]
    fund_house_source = df_stp_src_sel[df_stp_src_sel.index == amfi_code_source]['FUND_HOUSE'].iloc[0]
    #col1.write(swp_st_date)
    #col1.write(swp_end_date)

    df_mf_perf_sel = df_mf_perf[(df_mf_perf['LAUNCH DATE'] < stp_st_date) & (df_mf_perf['FUND_HOUSE'] == fund_house_source)]
    schm_list_dest = [ "{}-{}".format(j, df_mf_perf_sel.loc[j]['SCHEMES']) for j in df_mf_perf_sel.index if j != amfi_code_source ]


    schm_select_dest = col2.selectbox("Select STP Target Scheme",schm_list_dest,0)
    amfi_code_dest = int(float(schm_select_dest.split("-")[0]))
    schm_select_dest = schm_select_dest.split("-")[1]

    df_mf_source = get_historical_nav(amfi_code_source,tday.day)
    df_mf_source.columns = ['Source_NAV']
    df_mf_source = df_mf_source[(df_mf_source.index > stp_st_date.date()) & (df_mf_source.index < stp_end_date.date())]
    df_mf_dest = get_historical_nav(amfi_code_dest,tday.day)
    df_mf_dest.columns = ['Dest_NAV']

    df_mf_dest = df_mf_dest[(df_mf_dest.index > stp_st_date.date()) & (df_mf_dest.index < stp_end_date.date())]

    df_mf = pd.concat([df_mf_source,df_mf_dest],join="inner", axis=1)

    #st.write(df_mf)

    df_stp = get_stp(df_mf,corpus, stp_amount, stp_freq,dynamic_model='N')

    #st.write(df_stp)

    df_cashflow_stp_out = df_stp[df_stp['Tran_Value'] != 0][['Tran_Value','Num_Days','STP_OUT_NAV','STP_OUT_Units','Bal_Units_STP_Out']]
    mkt_val_stp_out = df_stp['STP_SOURCE_FUND_VAL'].iloc[-1]
    #st.write(df_cashflow_stp_out)
    #st.write(mkt_val_stp_out)
    stp_out_xirr = round(optimize.newton(xirr, 3, args=(df_cashflow_stp_out, mkt_val_stp_out,)),2)
    #st.write("STP OUT XIRR - {}".format(stp_out_xirr))

    df_cashflow_stp_in = df_stp[df_stp['Tran_Value'] > 0][['Tran_Value','Num_Days']]
    mkt_val_stp_in = df_stp['STP_DEST_FUND_VAL'].iloc[-1] * -1
    #st.write(df_cashflow_stp_in)
    #st.write(mkt_val_stp_in)
    stp_in_xirr = round(optimize.newton(xirr, 3, args=(df_cashflow_stp_in, mkt_val_stp_in,)),2)
    #st.write("STP OUT XIRR - {}".format(stp_in_xirr))

    stp_ini_val = df_stp['Net_Value'].iloc[0]
    stp_fin_val = df_stp['Net_Value'].iloc[-1]
    tot_years = df_stp['Num_Days'].iloc[0]/365.0

    #st.write("{} - {} - {}".format(stp_ini_val,stp_fin_val,tot_years))

    stp_xirr = round(100*(np.power(stp_fin_val/stp_ini_val, 1.0/tot_years) - 1),2)

    #st.write("STP  XIRR - {}".format(stp_xirr))
    # sqrt(252) = 15.87, factor for Daily Volatility to Annualised Volatility
    ann_volatility = round(df_stp['Net_Value'].pct_change().dropna().std() * 15.87 * 100,2)

    df_stp.rename(columns = {'STP_SOURCE_FUND_VAL':"STP OUT - {} ({} %)".format(schm_select_source,stp_out_xirr), \
                             'STP_DEST_FUND_VAL':"STP IN - {} - ({} %)".format(schm_select_dest,stp_in_xirr), \
                             'Net_Value':"STP Overall - ({} %)".format(stp_xirr)}, inplace=True)
    fig = px.line(df_stp[["STP OUT - {} ({} %)".format(schm_select_source,stp_out_xirr), \
                          "STP IN - {} - ({} %)".format(schm_select_dest,stp_in_xirr),    \
                          "STP Overall - ({} %)".format(stp_xirr)]])

    #st.markdown(html_text,unsafe_allow_html=True)
    #fig.update_layout(title_text="SWP Balance ( XIRR - {}% )".format(str(swp_xirr)),
    fig.update_layout(title_text="Fund Growth - STP ",
                              title_x=0.40,
                              title_font_size=22,
                              xaxis_title="",
                              yaxis_title="Net Fund Value")

    fig.update_layout(margin=dict(l=1,r=1,b=1,t=30))

    fig.update_layout(showlegend=True)
    fig.update_layout(legend_title='')
    fig.update_layout(legend=dict(
                        x=0.20,
                        y=-0.35,
                        traceorder='normal',
                        font=dict(size=14,)
                     ))

    fig.update_layout(height=550)
    fig.update_layout(width=600)

    st.markdown("-----------------------------------------")

    col1, col2, col3 = st.columns((8,1,4))


    col1.markdown('<BR>', unsafe_allow_html = True)

    col1.plotly_chart(fig, config = config)

    realized_cap_gains = df_stp['Cap Gains'].sum(0)
    dict_basic_info = {'Amount Invested': display_amount(stp_ini_val + realized_cap_gains),
             'Current Market Value': display_amount(stp_fin_val),
             'Realized Cap Gains': display_amount(realized_cap_gains),
             'Unrealized Cap Gains':display_amount(stp_fin_val - stp_ini_val - realized_cap_gains),
             'XIRR': "{}%".format(stp_xirr),
             'Annualised Volatility': "{}%".format(ann_volatility)
            }

    html_text = get_markdown_dict(dict_basic_info,12)
    #html_text = '<b>Basic Info</b>' + html_text
    col3.markdown('<BR><BR><BR><BR><BR><P style="text-align:center;color:Magenta"><u><b>STP Summary</b></u></P>',unsafe_allow_html=True)

    col3.markdown(html_text,unsafe_allow_html=True)
