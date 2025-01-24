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
c_2.image('growealth-logo_long.png')

styles = {
    "Heading": "font-size:30px;font-weight: bold;text-align:center;vertical-align:bottom;color:blue;margin:0px;padding:0px;line-height:32px",
    "Subheading": "font-size:18px;font-weight: bold;text-decoration:underline;text-align:center;vertical-align:bottom;color:red;margin:10px;padding:0px;line-height:32px",
    "Field_Label_Top": "font-size:14px;font-weight:bold;text-align:center;vertical-align:bottom;color:blue;margin-right:3p5x;padding:0px;line-height:10px",
    "Display_Info": "font-size:15px;font-weight: bold;text-align:left;vertical-align:bottom;color:green;margin-top:8px;margin-bottom:4px;padding:0px;line-height:32px",
    "Scheme Level": "background-color: #ffffff; font-style: italic;",
    "Calligraphy_Font": "font-family:'Dancing Script', cursive; font-size: 18px; color: #6a1b9a;",
    "Error_Message": "background-color: #E1A2AA; font-style: italic;margin-top:14px;margin-bottom:0px",

}

#st.markdown('<p style="{}">Mobile Number:</p><BR>'.format(styles['Field_Label']), unsafe_allow_html=True)


def fund_rtg_stars(rating):
    stars = ""

    if rating == 1:
        stars = f"{rating} star"
    elif rating > 1:
        stars = f"{rating} star"
    else:
        stars = " -- "

    return stars

def fund_age(age_in_days):
    age_in_years = round(age_in_days/365,2)
    if age_in_years > 1:
        return f"{age_in_years} Years"
    else:
        return f"{age_in_years} Year"





col_basic_display = ['SCHEMES', 'SCHEME_CATEGORY','FUND_RATING','AUM', '1_YEAR_RETURN',
                     'VOLATILITY', 'SHARPE', 'PRICE_TO_EARNINGS', 'EXPENSE']




def display_fund_manager(fund_manager, amfi_code):

    df_fund_mgr = df[df['FUND MANAGER'] == fund_manager]
    tot_aum = df_fund_mgr['AUM'].sum()
    df_fund_mgr['FUND_RATING'] = df_fund_mgr['FUND_RATING'].replace(0,np.nan)
    #average_rating = df_fund_mgr[df_fund_mgr['FUND_RATING'] > 0]['FUND_RATING'].mean()
    average_rating = df_fund_mgr['FUND_RATING'].mean()
    schm_nm = df.loc[amfi_code,'SCHEMES']
    #st.write(schm_nm)

    if (len(df_fund_mgr) > 1):

        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown(get_markdown_col_fields('Total AUM Managed',f"{display_amount(tot_aum)} Cr"), unsafe_allow_html=True)
        st.markdown(get_markdown_col_fields('Average Fund rating',f"{average_rating} stars"), unsafe_allow_html=True)

        st.markdown('<BR><p style="{}">Other Funds Managed</p>'.format(styles['Display_Info']), unsafe_allow_html=True)
        html_text = get_markdown_table(df_fund_mgr[df_fund_mgr.index != amfi_code][col_basic_display])

        st.markdown(html_text,unsafe_allow_html=True)
    else:
        st.markdown('<BR><p style="{}">{} manages no Funds other than {} </p><BR>'.format(styles['Subheading'],fund_manager,schm_nm), unsafe_allow_html=True)

def display_debt_schemes():

    left,buf1,right1,buf2, right2 = st.columns((10,1,7,1,7))
    #fig = show_debt_fund_details(amfi_code, schm_select, comp_date)

    sov_debt = df.loc[amfi_code]['SOV_RATED_DEBT']
    aaa_debt = df.loc[amfi_code]['AAA_RATED_DEBT']
    aa_debt = df.loc[amfi_code]['AA_RATED_DEBT']
    a_debt  = df.loc[amfi_code]['A_RATED_DEBT']
    big_debt = df.loc[amfi_code]['BIG']
    cash_holdings = df.loc[amfi_code]['CASH']

    sov_aaa = sov_debt + aaa_debt
    aa_a = aa_debt + a_debt

    debt_md = df.loc[amfi_code]['MODIFIED_DURATION']
    debt_ytm = df.loc[amfi_code]['YTM']

    right1.markdown('<BR><BR>',unsafe_allow_html=True)
    right2.markdown('<BR><BR>',unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('AMC',df.loc[amfi_code]['FUND_HOUSE']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Fund Age',f"{fund_age(df.loc[amfi_code]['AGE'])}"), unsafe_allow_html=True)
    right1.markdown(get_markdown_col_fields('Fund Type',df.loc[amfi_code]['SCHEME_TYPE']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Fund Category',df.loc[amfi_code]['SCHEME_CATEGORY']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('Fund Rating',fund_rtg_stars(int(df.loc[amfi_code]['FUND_RATING']    ))), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Expense Ratio',df.loc[amfi_code]['EXPENSE']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('YTM',df.loc[amfi_code]['YTM']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Modified Duration',df.loc[amfi_code]['MODIFIED_DURATION']), unsafe_allow_html=True)
    right1.markdown(get_markdown_col_fields('AAA/SOV Bonds',sov_aaa), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('AA/A Bonds',aa_a), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('Fund Manager',df.loc[amfi_code]['FUND MANAGER']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Exit Load',df.loc[amfi_code]['EXIT_LOAD']), unsafe_allow_html=True)


    st.markdown('<BR>',unsafe_allow_html=True)

    pf_label = []
    pf_holdings = []

    if  sov_debt > 0:
        pf_label.append('SOV Rated')
        pf_holdings.append(sov_debt)

    if  aaa_debt > 0:
        pf_label.append('AAA Rated')
        pf_holdings.append(aaa_debt)

    if  aa_debt > 0:
        pf_label.append('AA Rated')
        pf_holdings.append(aa_debt)

    if  a_debt > 0:
        pf_label.append('A Rated')
        pf_holdings.append(a_debt)

    if  cash_holdings > 0 or big_debt > 0:
        pf_label.append('Cash/Others')
        pf_holdings.append(cash_holdings + big_debt )





    # Create a doughnut chart using Plotly Express
    fig_port = px.pie(
        names=pf_label,
        values=pf_holdings,
        hole=0.6,  # Set the size of the hole to create a doughnut chart
        title=' '
    )

    #fig.update_layout(width=200, height=100)

    fig_port.update_layout(
        title_font=dict(
            family="Arial",
            size=15,
            color="blue"
        ),
        width=300,
        height=300
    )

    #fig_port.update_layout(title_x=0.2, title_y=0.90)

    fig_port.update_layout(margin=dict(l=0, r=0, t=0, b=50))


    # Add text annotation inside the doughnut hole
    fig_port.update_layout(
        annotations=[
            dict(
                text='AUM: {}'.format(f"{display_amount(df.loc[amfi_code]['AUM'])} Cr"),
                x=0.5,
                y=0.55,
                font=dict(size=15),
                showarrow=False
            )
        ],
        legend=dict(
            x=-0.2,  # Adjust the x position for legend
            y=-0.1,  # Adjust the y position for legend
            #traceorder='normal',
            orientation="h",
            font=dict(size=12),
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(255, 255, 255, 0.5)'
        )
    )

    #s_layout[0].markdown('', unsafe_allow_html=True)
    left.markdown('<p style="{}">Portfolio Breakup</p><BR>'.format(styles['Subheading']), unsafe_allow_html=True)
    left.plotly_chart(fig_port)

    #st.plotly_chart(fig)

def display_equity_schemes():
    st.markdown('<BR>',unsafe_allow_html=True)
    left,buf1,right1,buf2, right2 = st.columns((10,1,7,1,7))

    #st.write(df.loc[amfi_code]['SINCE_INCEPTION_RETURN'])
    #fig = show_fund_details(amfi_code, comp_date )
    #right1.markdown('<BR>',unsafe_allow_html=True)
    #right2.markdown('<BR>',unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('AMC',df.loc[amfi_code]['FUND_HOUSE']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Fund Age',f"{fund_age(df.loc[amfi_code]['AGE'])}"), unsafe_allow_html=True)
    right1.markdown(get_markdown_col_fields('Fund Type',df.loc[amfi_code]['SCHEME_TYPE']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Fund Category',df.loc[amfi_code]['SCHEME_CATEGORY']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('Crisil Rating',fund_rtg_stars(int(df.loc[amfi_code]['FUND_RATING']    ))), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Expense Ratio',df.loc[amfi_code]['EXPENSE']), unsafe_allow_html=True)


    right1.markdown(get_markdown_col_fields('30 Day Return',df.loc[amfi_code]['30_DAY_RETURN']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('3 Month Return',df.loc[amfi_code]['3_MONTH_RETURN']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('6 Month Return',df.loc[amfi_code]['6_MONTH_RETURN']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('1 Year Return',df.loc[amfi_code]['1_YEAR_RETURN']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('3 Year Return',df.loc[amfi_code]['3_YEAR_RETURN']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('5 Year Return',df.loc[amfi_code]['5_YEAR_RETURN']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('Volatility',df.loc[amfi_code]['VOLATILITY']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('R-Square',df.loc[amfi_code]['RSQUARED']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('Sharpe Ratio',df.loc[amfi_code]['SHARPE']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Sortino Ratio',df.loc[amfi_code]['SORTINO']), unsafe_allow_html=True)



    right1.markdown(get_markdown_col_fields('Price to Earnings',df.loc[amfi_code]['PRICE_TO_EARNINGS']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Price to Book',df.loc[amfi_code]['PRICE_TO_BOOK']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('Alpha',df.loc[amfi_code]['ALPHA']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Beta',df.loc[amfi_code]['BETA']), unsafe_allow_html=True)

    right1.markdown(get_markdown_col_fields('Fund Manager',df.loc[amfi_code]['FUND MANAGER']), unsafe_allow_html=True)
    right2.markdown(get_markdown_col_fields('Exit Load',df.loc[amfi_code]['EXIT_LOAD']), unsafe_allow_html=True)


    #st.plotly_chart(fig)

    pf_label = []
    pf_holdings = []

    eqy_lcap = df.loc[amfi_code]['LARGE_CAP']
    eqy_mcap = df.loc[amfi_code]['MID_CAP']
    eqy_scap = df.loc[amfi_code]['SMALL_CAP']
    gold_pct  = df.loc[amfi_code]['GOLD_PCT']
    for_holdings = df.loc[amfi_code]['GLOBAL_EQUITY_PCT']
    debt_pct = df.loc[amfi_code]['DEBT_PCT']
    cash_holdings = df.loc[amfi_code]['CASH']






    if  eqy_lcap > 0:
        pf_label.append('Large Cap')
        pf_holdings.append(eqy_lcap)

    if  eqy_mcap > 0:
        pf_label.append('Mid Cap')
        pf_holdings.append(eqy_mcap)

    if  eqy_scap > 0:
        pf_label.append('Small Cap')
        pf_holdings.append(eqy_scap)

    if gold_pct > 0:
        pf_label.append('Gold Holdings')
        pf_holdings.append(gold_pct)

    if for_holdings > 0:
        pf_label.append('Foreign Holdings')
        pf_holdings.append(for_holdings)

    if debt_pct > 0 or cash_holdings > 0 :
        pf_label.append('Debt/Cash')
        pf_holdings.append(debt_pct + cash_holdings)


    debt_md = df.loc[amfi_code]['MODIFIED_DURATION']
    debt_ytm = df.loc[amfi_code]['YTM']


    # Create a doughnut chart using Plotly Express
    fig_port = px.pie(
        names=pf_label,
        values=pf_holdings,
        hole=0.6,  # Set the size of the hole to create a doughnut chart
        title=' '
    )

    #fig.update_layout(width=200, height=100)

    fig_port.update_layout(
        title_font=dict(
            family="Arial",
            size=15,
            color="blue"
        ),
        width=300,
        height=300
    )

    #fig_port.update_layout(title_x=0.2, title_y=0.90)

    fig_port.update_layout(margin=dict(l=0, r=0, t=0, b=50))


    # Add text annotation inside the doughnut hole
    fig_port.update_layout(
        annotations=[
            dict(
                text='{}'.format(f"{display_amount(df.loc[amfi_code]['AUM'])} Cr"),
                x=0.5,
                y=0.5,
                font=dict(size=16,         # Font size
                          color='blue',    # Font color
                          family='Arial Bold' # Font family
                ),
                showarrow=False
            )
        ],
        legend=dict(
            x=-0.2,  # Adjust the x position for legend
            y=-0.1,  # Adjust the y position for legend
            #traceorder='normal',
            orientation="h",
            font=dict(size=12),
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(255, 255, 255, 0.5)'
        )
    )

    #s_layout[0].markdown('', unsafe_allow_html=True)
    left.markdown('<p style="{}">Portfolio Breakup</p><BR>'.format(styles['Subheading']), unsafe_allow_html=True)
    left.plotly_chart(fig_port)




#st.title('Fund Details')

st.markdown('<BR><p style="{}">Fact Sheet</p><BR>'.format(styles['Heading']), unsafe_allow_html=True)


df = get_mf_perf()

#st.dataframe(df)

params=st.query_params
def_value = 0
if len(params) > 0:
    try:
        def_schm_id = int(float(params['id']))
        def_value = df.index.get_loc(def_schm_id)
    except:
        def_value = 0

#st.write(def_schm_id)

schm_list = [ "{}-{}".format(int(j), df.loc[j]['SCHEMES']) for j in df.index ]


main_layout = st.columns((13,8))

schm_select = main_layout[0].selectbox("Select Scheme",schm_list,def_value,label_visibility="collapsed")
amfi_code = int(float(schm_select.split("-")[0]))
schm_select = schm_select.split("-")[1]
fund_manager = df.loc[amfi_code,'FUND MANAGER']
fund_house = df.loc[amfi_code,'FUND_HOUSE']
fund_category = df.loc[amfi_code,'SCHEME_CATEGORY']
fund_type = df.loc[amfi_code,'SCHEME_TYPE']






#comp_date   = main_layout[1].date_input("Select Date", dt.date(2022, 1, 1), label_visibility="collapsed")
#comp_date = dt.date(comp_date.year, comp_date.month, comp_date.day)

schm_type = df.loc[amfi_code,'SCHEME_TYPE']


st.markdown('<BR>',unsafe_allow_html=True)




t_overview, t_fund_returns, t_fund_mgr, t_peer = st.tabs(["Fund Overview","Fund Returns",f"Fund Manager - {fund_manager}",f"Peers - {fund_type}:{fund_category}"])

with t_peer:

    col_cat_display = ['SCHEMES','AUM','FUND_RATING', '3_MONTH_RETURN', '6_MONTH_RETURN','1_YEAR_RETURN',
                     'VOLATILITY', 'SHARPE', 'PRICE_TO_EARNINGS', 'EXPENSE']

    df_cat = df[df['SCHEME_CATEGORY'] == fund_category].sort_values(by='1_YEAR_RETURN', ascending=False)
    df_cat['AUM'] = df_cat['AUM'].apply(lambda x: f"{display_amount(x)} Cr")

    df_cat['RANK'] = df_cat['1_YEAR_RETURN'].rank(ascending=False, method='dense')

    st.markdown(f" :blue[**{schm_select}**] is ranked within the :blue[**{fund_type}:{fund_category} Category**]")

    left, right = st.columns((1,20))

    df_cat['RANK'] = df_cat['1_YEAR_RETURN'].rank(ascending=False, method='dense')
    right.markdown(f" &mdash; :blue[**{int(df_cat.loc[amfi_code,'RANK'])}/{len(df_cat)}**] based on :blue-background[**1 Year Returns**] ")

    df_cat['RANK'] = df_cat['SHARPE'].rank(ascending=False, method='dense')
    right.markdown(f" &mdash; :blue[**{int(df_cat.loc[amfi_code,'RANK'])}/{len(df_cat)}**]based on :blue-background[**3-Year Sharpe Ratio**] ")

    df_cat['RANK'] = df_cat['FUND_RATING'].rank(ascending=False)
    right.markdown(f" &mdash; :blue[**{int(df_cat.loc[amfi_code,'RANK'])}/{len(df_cat)}**] based on :blue-background[**Fund Rating**] ")

    st.markdown('<BR><p style="{}">Complete List of {}:{} Schemes</p>'.format(styles['Display_Info'],fund_type,fund_category), unsafe_allow_html=True)
    df_cat['FUND_RATING'] = df_cat['FUND_RATING'].replace(0,np.nan)
    html_text = get_markdown_table_highlighted_row(df_cat[col_cat_display],amfi_code)
    st.markdown(html_text,unsafe_allow_html=True)

with t_fund_mgr:

    display_fund_manager(fund_manager, amfi_code)

with t_overview:

    if schm_type == 'Debt':
        display_debt_schemes()
    else:
        display_equity_schemes()

with t_fund_returns:


    left, buf, right = st.columns((6,2,10))

    df_mf = get_historical_nav(amfi_code, tday)

    df_mf['DailyChg']=df_mf['Nav'].pct_change()*100
    df_mf['1YRollingRet']=df_mf['Nav'].pct_change(252)*100

    df_mf['Day'] = df_mf.index.map(lambda x: x.weekday())


    first_of_month = dt.date(tday.year,tday.month,1)

    #df_mf_curr_mth = df_mf[df_mf.index >= dt.date(tday.year,tday.month,1)]
    df_mf_curr_mth = df_mf.tail(20)


    html_text = get_recent_ret_calendar_display(df_mf_curr_mth)

    left.markdown('<BR><p style="{}">Last 20 Day Heat Map</p>'.format(styles['Field_Label_Top']), unsafe_allow_html=True)
    left.markdown(html_text, unsafe_allow_html=True)

    fig = px.line(df_mf['1YRollingRet'].dropna())



    fig.update_layout(title_text=" ",
                              title_x=0.35,
                              title_font_size=17,
                              xaxis_title="Date",
                              yaxis_title="1 Year Roll Ret")
    fig.update_layout(showlegend=True)
    fig.update_layout(showlegend=False)
    fig.update_layout(margin=dict(
                l=20,  # Left margin
                r=20,  # Right margin
                t=0,  # Top margin
                b=50   # Bottom margin
            )
        )


    fig.update_layout(height=250)
    fig.update_layout(width=450)


    chart_title = f"Rolling 1-Year Return"
    right.markdown('<BR><p style="{}">{}</p>'.format(styles['Field_Label_Top'],chart_title), unsafe_allow_html=True)
    #right.plotly_chart(fig)

    right.plotly_chart(fig)

#notice_txt = '<p><BR><BR><span style="font-family: Verdana, Geneva, sans-serif; font-size: 10px;">'
#notice_txt = notice_txt + '<span style="color: rgb(255,0,20);">Note:Market Data as on {}</span>'.format(get_data_refresh_date())
#st.markdown(notice_txt,unsafe_allow_html=True)

    st.write("-----------")
    st.markdown('<p style="{}">Lumpsum Investment Returns</p><BR>'.format(styles['Subheading']), unsafe_allow_html=True)

    df_cagr = get_lumpsum_inv_ret(df_mf, 10000)

    st.markdown(get_markdown_table(df_cagr), unsafe_allow_html=True)


    st.markdown('<BR>', unsafe_allow_html=True)
    if len(df_mf) > 60:
        st.write("-----------")
        st.markdown('<p style="{}">SIP Investment Returns</p><BR>'.format(styles['Subheading']), unsafe_allow_html=True)

        df_sip = get_sip_inv_ret(df_mf, 1000)

        st.markdown(get_markdown_table(df_sip), unsafe_allow_html=True)
