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








def get_html_table_scroll(data, header='Y'):
    if header == 'Y':

        cols = data.columns
        ncols = len(cols)



        html_script = "<style> .tableFixHead {overflow-y: auto; height: 500px;}"
        html_script = html_script + ".tableFixHead thead th {position: sticky; top: 0px;}"
        html_script = html_script + "table {border-collapse: collapse; width: 100%;}"
        html_script = html_script + "th, td {padding: 8px 16px; border: 1px solid #cc} th {background: #eee;}"
        html_script = html_script + "tr:nth-child(even) {background-color: #f2f2f2;}</style>"
        html_script = html_script + '<div class="tableFixHead"><table><thead>'
        html_script = html_script + "<tr style='border:none;font-family:Courier; color:Red; font-size:12px;'>"

        for i in cols:
            if i in ['SCHEMES','SCHEME_CATEGORY','FUND_HOUSE']:
                html_script = html_script + "<th style='text-align:left;background-color: #ffebcc;'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center;background-color: #ffebcc;'>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        #url_link = "http://localhost:8501/Fact_Sheet?id={}".format(j)
        url_link = "https://growealth.streamlit.app/Fact_Sheet?id={}".format(j)


        html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:10px;'>"
        a = data.loc[j]
        for k in cols:
            if k in ['Rel_MaxDD','Prob_10Pct','NIFTY_CORR']:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(round(a[k],2))
            elif k in ['SCHEME_CATEGORY','FUND_HOUSE']:
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'>{}</td>".format(a[k])
            elif k == 'SCHEMES':
                #html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'><a href={}>{}</a></td>".format(url_link,a[k])
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'><a href={}>{}</a></td>".format(url_link,a[k])
                #st.write(url_link,a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])




    html_script = html_script + '</tbody></table>'

    return html_script

def plot_chart(df_chart,chart_x_axis,chart_y_axis,chart_color,chart_size):
    if len(df_chart) > 0:

        df_chart = df_chart[(df_chart[chart_x_axis] > 0) & (df_chart[chart_x_axis] < 90)]

        y_spread = df_chart[chart_y_axis].max() - df_chart[chart_y_axis].min()
        yrange = [df_chart[chart_y_axis].min() - 0.1 * y_spread, df_chart[chart_y_axis].max() + 0.1 * y_spread]
        x_spread = df_chart[chart_x_axis].max() - df_chart[chart_x_axis].min()
        xrange = [df_chart[chart_x_axis].min() - 0.1 * x_spread, df_chart[chart_x_axis].max() + 0.1 * x_spread]
        x_mid = (df_chart[chart_x_axis].max() + df_chart[chart_x_axis].min())/2
        y_mid = (df_chart[chart_y_axis].max() + df_chart[chart_y_axis].min())/2

        #st.write(chart_x_axis,x_spread)

        cols = [chart_x_axis,chart_y_axis,chart_color,chart_size]


        fig = px.scatter(df_chart, x=df_chart[chart_x_axis], y=df_chart[chart_y_axis], color=df_chart[chart_color],
                         size=df_chart[chart_size], size_max=25, hover_name=df_chart['SCHEMES'], color_continuous_scale='plasma')


        # fig.update_xaxes(type=[])
        fig.update_yaxes(range=yrange)
        fig.update_layout(title_text="Fund Performance Snapshot",
                      title_x=0.3,
                      title_font_size=30,
                      titlefont=dict(size=20, color='blue', family='Arial, sans-serif'),
                      xaxis_title=dict(text=chart_x_axis, font=dict(size=16, color='#C7004E')),
                      yaxis_title=dict(text=chart_y_axis, font=dict(size=16, color='#C7004E'))
                      )

        fig.update_layout(margin=dict(l=1,r=1,b=1,t=45))
        fig.update_layout(height=500)
        fig.update_layout(width=650)
        fig.update_layout(legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01)
                        )


        fig.add_vline(x = x_mid, line_width=1.5, line_dash="dash", line_color="blue")
        fig.add_hline(y = y_mid, line_width=1.5, line_dash="dash", line_color="blue")
        #fig.add_hline(y = yrange[0], line_width=4, line_color="blue")
        #fig.add_vline(x = xrange[0], line_width=1.5, line_color="blue")
        #fig.add_hline(y = yrange[1], line_width=4, line_color="blue")
        #fig.add_vline(x = xrange[1], line_width=1.5, line_color="blue")


        #fig.add_annotation(x=xrange[0]+ 0.3 * x_spread,y=yrange[0]+ 0.1 *y_spread,text="Q1 - Low Risk, Low Return",
        #  showarrow=False,  font=dict(family="Arial", size=10,color="red"),
        #  bgcolor="LightSkyBlue"
        #  )

        #fig.add_annotation(x=xrange[1] - 0.3 * x_spread,y=yrange[0]+ 0.1 *y_spread,text="Q2 - High Risk, Low Return",
        #  showarrow=False,  font=dict(family="Arial", size=10,color="red"),
        #  bgcolor="palegoldenrod"
        #  )

        #fig.add_annotation(x=xrange[0] + 0.3 * x_spread,y=yrange[1] - 0.1 *y_spread,text="Q3 - Low Risk, High Return",
        #  showarrow=False,  font=dict(family="Arial", size=10,color="red"),
        #  bgcolor="lightgreen"
        #  )

        #fig.add_annotation(x=xrange[1] - 0.3 * x_spread,y=yrange[1] - 0.1 *y_spread,text="Q4 - High Risk, High Return",
        #   showarrow=False,  font=dict(family="Arial", size=10,color="red"),
        #   bgcolor="Yellow"
        #   )





        return fig
    else:
        return False



def get_filtered_df(df_chart, df_filter, filter_attr, filter_condition, filter_value):

    if filter_condition == 'Less Than':
        df_filtered = df_chart[df_chart[filter_attr] < filter_value]
    elif filter_condition == 'Less or Equals':
        df_filtered = df_chart[df_chart[filter_attr] <= filter_value]
    elif filter_condition == 'Equals':
        df_filtered = df_chart[df_chart[filter_attr] == filter_value]
    elif filter_condition == 'Not Equals':
        df_filtered = df_chart[df_chart[filter_attr] != filter_value]
    elif filter_condition == 'Greater or Equals':
        df_filtered = df_chart[df_chart[filter_attr] >= filter_value]
    elif filter_condition == 'Greater Than':
        df_filtered = df_chart[df_chart[filter_attr] > filter_value]

    return df_filtered


df_0=get_mf_perf()

#st.dataframe(df_0)

#data_refresh_date = df.index[-1]
#st.write(df.columns)

st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">MF Screener</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)

st.markdown('<BR>',unsafe_allow_html=True)
st.markdown('<BR>',unsafe_allow_html=True)

st.markdown("**:blue[Fund Type]**")
selected_option = st.radio("Select an option:", ["Debt MF", "Equity/Other MF"], 1, horizontal=True, label_visibility="collapsed")

if selected_option == 'Debt MF':
    df = df_0[df_0['SCHEME_TYPE'] == 'Debt']
else:
    df = df_0[df_0['SCHEME_TYPE'] != 'Debt']



left,right = st.columns((13,16))

fh_list = [x for x in df['FUND_HOUSE'].unique()]

left.markdown("**:blue[Fund House]**")
fh_option = left.multiselect("Select Fund House", fh_list, label_visibility="collapsed")

if len(fh_option) == 0:
    df_1 = df
else:
    df_1 = df[df['FUND_HOUSE'].isin(fh_option)]




sch_cat_list = [x for x in df_1['SCHEME_CATEGORY'].unique()]
right.markdown("**:blue[Scheme Category]**")
sch_cat_option = right.multiselect("Select Fund Category", sch_cat_list, label_visibility="collapsed")
if len(sch_cat_option) > 0:
    df_2 = df_1[df_1['SCHEME_CATEGORY'].isin(sch_cat_option)]
else:
    df_2 = df_1


left.markdown("**:blue[Fund Manager]**")
fm_list = [ x for x in df_2['FUND MANAGER'].unique()]
fm_option = left.multiselect("Select Fund Manager", fm_list, label_visibility="collapsed")

if len(fm_option) == 0:
    df_3 = df_2
else:
    df_3 = df_2[df['FUND MANAGER'].isin(fm_option)]



right.markdown("**:blue[Fund Rating]**")
rating_list = ['0 Star','1 Star','2 Stars', '3 Stars', '4 Stars', '5 Stars']
rating_option = right.segmented_control("Select Fund Rating", rating_list, default=rating_list,selection_mode='multi', label_visibility="collapsed")

rating_values = []
if len(rating_option) > 0:
    for ratings in rating_option:
        if ratings == '0 Star':
            rating_values.insert(0,0)
        elif ratings == '1 Star':
            rating_values.insert(0,1)
        elif ratings == '2 Stars':
            rating_values.insert(0,2)
        elif ratings == '3 Stars':
            rating_values.insert(0,3)
        elif ratings == '4 Stars':
            rating_values.insert(0,4)
        elif ratings == '5 Stars':
            rating_values.insert(0,5)

    df_4 = df_3[df_3['FUND_RATING'].isin(rating_values)]
else:
    df_4 = df_3




filter_cols = ['30_DAY_RETURN', '3_MONTH_RETURN', '6_MONTH_RETURN', '1_YEAR_RETURN',
               '2_YEAR_RETURN', '3_YEAR_RETURN','5_YEAR_RETURN', '7_YEAR_RETURN', '10_YEAR_RETURN',
               '15_YEAR_RETURN', '20_YEAR_RETURN', '25_YEAR_RETURN','SINCE_INCEPTION_RETURN',
               'ALPHA', 'BETA', 'VOLATILITY', 'SHARPE','SORTINO', 'AVG_MATURITY', 'MODIFIED_DURATION','AGE',
               'YTM','LARGE_CAP','MID_CAP','SMALL_CAP','PRICE_TO_BOOK', 'PRICE_TO_EARNINGS',
               'EQUITY_PCT','DEBT_PCT', 'GOLD_PCT', 'GLOBAL_EQUITY_PCT', 'OTHER_PCT', 'RSQUARED',
               'EXPENSE', 'SOV_RATED_DEBT', 'A_RATED_DEBT', 'AA_RATED_DEBT', 'AAA_RATED_DEBT', 'BIG', 'CASH']

filter_df = df_4.describe()[filter_cols]

#st.write(filter_df)

chart_cols = ['SCHEMES','AUM','AGE','SHARPE','STDEV','1_YEAR_RETURN', '3_YEAR_RETURN','EXPENSE']
display_columns = ['SCHEMES','SCHEME_CATEGORY','FUND_HOUSE','EXPENSE', 'AUM', 'FUND_RATING', 'AGE', '3_MONTH_RETURN', \
                  '6_MONTH_RETURN', '1_YEAR_RETURN','2_YEAR_RETURN', '3_YEAR_RETURN','5_YEAR_RETURN', '7_YEAR_RETURN', \
                   '10_YEAR_RETURN', '15_YEAR_RETURN', '20_YEAR_RETURN', '25_YEAR_RETURN','SINCE_INCEPTION_RETURN', \
                   'SHARPE', 'SORTINO', 'RSQUARED', 'VOLATILITY',  'BETA','ALPHA','PRICE_TO_BOOK', 'PRICE_TO_EARNINGS', \
                   'EQUITY_PCT', 'DEBT_PCT', 'GOLD_PCT','GLOBAL_EQUITY_PCT', 'OTHER_PCT', \
                   'LARGE_CAP','MID_CAP','SMALL_CAP','CASH','SOV_RATED_DEBT', 'A_RATED_DEBT', 'AA_RATED_DEBT', 'AAA_RATED_DEBT']

basic_columns = ['SCHEMES','SCHEME_CATEGORY','FUND_HOUSE','FUND MANAGER']
config_columns = ['EXPENSE', 'AUM', 'FUND_RATING', 'AGE', '3_MONTH_RETURN', \
                  '6_MONTH_RETURN', '1_YEAR_RETURN','2_YEAR_RETURN', '3_YEAR_RETURN','5_YEAR_RETURN', '7_YEAR_RETURN', \
                   '10_YEAR_RETURN', '15_YEAR_RETURN', '20_YEAR_RETURN', '25_YEAR_RETURN','SINCE_INCEPTION_RETURN', \
                   'SHARPE', 'SORTINO', 'RSQUARED', 'VOLATILITY',  'BETA','ALPHA','PRICE_TO_BOOK', 'PRICE_TO_EARNINGS', \
                   'EQUITY_PCT', 'DEBT_PCT', 'GOLD_PCT','GLOBAL_EQUITY_PCT', 'OTHER_PCT', \
                   'LARGE_CAP','MID_CAP','SMALL_CAP','CASH','SOV_RATED_DEBT', 'A_RATED_DEBT', 'AA_RATED_DEBT', 'AAA_RATED_DEBT']

#df_chart = df_2[chart_cols]

df_chart = df_4





crisil_option = ['1 Star', '3 Stars', '2 Stars', '4 Stars', '5 Stars', 'Not Rated']
operator_list = ['Less Than','Less or Equals','Equals','Not Equals','Greater or Equals','Greater Than']

left,centre, right = st.columns((8,5,16))
left.markdown("**:blue[Filter Criteria]**")
centre.markdown("**:blue[Condition]**")
right.markdown("**:blue[Value]**")

filter_list1 = [x for x in filter_df.columns]

filter_1 = left.selectbox("Filter 1", filter_list1, 0, label_visibility="collapsed")


filter_min_value_1 = filter_df.loc['min',filter_1]
filter_max_value_1 = filter_df.loc['max',filter_1]
#filter_step_value_1 = df_filter[df_filter.index == filter_1]['Steps'].iloc[0]

operator_1 = centre.selectbox('Operator_1',operator_list,0,label_visibility="collapsed")
filter_1_value = right.number_input("Value_1",min_value=filter_min_value_1, max_value=filter_max_value_1, value=filter_max_value_1, label_visibility="collapsed")



df_filter_1 = get_filtered_df(df_4,filter_df,filter_1,operator_1,filter_1_value)

filter_list2 = [x for x in filter_df.columns if x != filter_1]

#st.dataframe(df_filter_1)

filter_2 = left.selectbox("Filter 2", filter_list2, 1, label_visibility="collapsed")

filter_min_value_2 = filter_df.loc['min',filter_2]
filter_max_value_2 = filter_df.loc['max',filter_2]

operator_2 = centre.selectbox('Operator_2',operator_list,0,label_visibility="collapsed")
filter_2_value = right.number_input("Value_2",min_value=filter_min_value_2, max_value=filter_max_value_2, value=filter_max_value_2, label_visibility="collapsed")




#st.write(df_filter_1)
if len(df_filter_1) > 0:
    df_filter_2 = get_filtered_df(df_filter_1,filter_df,filter_2,operator_2,filter_2_value)
else:
    df_filter_2 = df_filter_1

#st.write(df_filter_2)



st.markdown('<BR>',unsafe_allow_html=True)
st.markdown('<BR>',unsafe_allow_html=True)




ch_1, ch_2 = st.columns((4,16))

ch_1.markdown('<BR><BR>',unsafe_allow_html=True)
ch_1.markdown("**:blue[Configure X-Axis]**")
chart_x_axis = ch_1.selectbox('chart_x_axis',['VOLATILITY','PRICE_TO_BOOK','PRICE_TO_EARNINGS'],0,label_visibility="collapsed")
ch_1.markdown('<BR>',unsafe_allow_html=True)

ch_1.markdown("**:blue[Configure Y-Axis]**")
chart_y_axis = ch_1.selectbox('chart_y_axis',['3_MONTH_RETURN', '6_MONTH_RETURN', '1_YEAR_RETURN','2_YEAR_RETURN',
                                              '3_YEAR_RETURN','5_YEAR_RETURN', '7_YEAR_RETURN', '10_YEAR_RETURN',
                                              '15_YEAR_RETURN', '20_YEAR_RETURN', '25_YEAR_RETURN','SINCE_INCEPTION_RETURN'],0,
                                              label_visibility="collapsed")
ch_1.markdown('<BR>',unsafe_allow_html=True)

ch_1.markdown("**:blue[Configure Colour]**")
chart_color = ch_1.selectbox('chart_color',['SHARPE', 'SORTINO','EXPENSE'],0,label_visibility="collapsed")
ch_1.markdown('<BR>',unsafe_allow_html=True)

ch_1.markdown("**:blue[Configure Size]**")
chart_size = ch_1.selectbox('chart_size',['AUM', 'AGE'],0,label_visibility="collapsed")


ch_2.markdown('<BR>',unsafe_allow_html=True)
#show_quadrants = ch_1.checkbox("Show Quadrant Results?", value=False)

fig = plot_chart(df_filter_2,chart_x_axis,chart_y_axis,chart_color,chart_size)
placeholder_chart = ch_2.empty()

if fig:
    placeholder_chart.plotly_chart(fig, use_container_width=True)
else:
    placeholder_chart.empty()



df_filter_2 = df_filter_2.sort_values([filter_1,filter_2])

basic_columns = [ 'SCHEMES','SCHEME_CATEGORY','FUND_HOUSE','AGE', filter_1, filter_2,chart_x_axis,chart_y_axis,chart_color, chart_size]
#if len(report_columns) == 0:
#    report_columns = config_columns

config_columns = [x for x in config_columns if x not in basic_columns]


st.markdown("""---""")
st.markdown('<BR>',unsafe_allow_html=True)

st.markdown("**:blue[Configure Report Columns]**")
report_columns = st.multiselect("Report_Columns",config_columns, label_visibility="collapsed")




final_report_columns = basic_columns + report_columns

final_report_columns = list(dict.fromkeys(final_report_columns))

#final_report_columns = np.unique(final_report_columns)

html_text = get_html_table_scroll(df_filter_2[final_report_columns])

st.markdown(html_text, unsafe_allow_html=True)

#st.write(df_filter_1[display_columns])


#notice_txt = '<p><BR><BR><span style="font-family: Verdana, Geneva, sans-serif; font-size: 10px;">'
#notice_txt = notice_txt + '<span style="color: rgb(255,0,20);">Note:Market Data as on {}</span>'.format(get_data_refresh_date())
#st.markdown(notice_txt,unsafe_allow_html=True)
