import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import plotly.express as px
from scipy.optimize import minimize
from scipy import optimize
import random
import math

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

# Hide Streamlit menu and footer
hide_streamlit_style = """
        <style>
        .stToolbarActions {display: none !important;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

c_1, c_2 = st.columns((8,4))
c_2.image('growealth-logo_long.png')


@st.cache_data()
def get_help_texts():
    help_text_df = pd.read_csv("Retirement_Help.csv")
    return help_text_df


def get_goals(st_age,end_age,desc,amt,freq,infl):
    goals = []
    #st.write(st_age,end_age,desc,amt,freq,infl)
    if amt >  0 and st_age <= end_age:
        n_years_to_goal = st_age - curr_age
        goal_fut_value = np.power((1 + infl/100),n_years_to_goal) * amt

        values = st_age, desc, round(goal_fut_value,0)
        goals.append(values)

        if freq > 0:
            for m in range(st_age + freq, end_age, freq):
                n_years_to_goal = m - curr_age
                goal_fut_value = np.power((1 + infl/100),n_years_to_goal) * amt
                values = m, desc, round(goal_fut_value,0)
                goals.append(values)

    return goals

def get_fut_income(st_age,end_age,amt,freq,incr):
    fut_income = []
    #st.write(st_age,end_age,amt,freq,incr)
    if amt >  0 and st_age <= end_age:

        values = st_age, round(amt,0)
        fut_income.append(values)

        if freq > 0:
            for m in range(st_age + freq, end_age, freq):
                n_years_to_income = m - curr_age
                f_income = np.power((1 + incr/100),n_years_to_income) * amt
                values = m,  round(f_income,0)
                fut_income.append(values)

    return fut_income

def get_corpus(rate, curr_age, ann_income, retirement_age, corpus, expenses, fut_income,col_name):
    rec = []
    income = 0
    yr_corpus = corpus
    n= len(fut_income)
    for j in expenses.index:
        if j > curr_age:
            if j < retirement_age:
                income = ann_income
            else:
                income = 0

            for k in range(n):
                if j==fut_income[k][0]:
                    income=income + fut_income[k][1]

            yr_corpus = yr_corpus * (1 + rate/100) + income - expenses.loc[j]['Expenses']
        values = j, round(yr_corpus,0)
        rec.append(values)

    df = pd.DataFrame(rec,columns=['Years',col_name])
    df.set_index('Years', inplace=True)
    return df



def get_optimised_rate(rate, curr_age, ann_income, retirement_age, corpus, expenses, terminal_corpus, fut_income):
    rec = []
    income = 0
    yr_corpus = corpus
    n= len(fut_income)
    for j in expenses.index:
        if j > curr_age:
            if j < retirement_age:
                income = ann_income
            else:
                income = 0

            for k in range(n):
                if j==fut_income[k][0]:
                    income=income + fut_income[k][1]

            yr_corpus = yr_corpus * (1 + rate/100) + income - expenses.loc[j]['Expenses']

    yr_corpus = yr_corpus - terminal_corpus

    return yr_corpus

def get_optimised_corpus(corpus,rate, curr_age, ann_income, retirement_age, expenses, terminal_corpus, fut_income):
    rec = []
    income = 0
    yr_corpus = corpus
    n= len(fut_income)
    for j in expenses.index:
        if j > curr_age:
            if j < retirement_age:
                income = ann_income
            else:
                income = 0

            for k in range(n):
                if j==fut_income[k][0]:
                    income=income + fut_income[k][1]

            yr_corpus = yr_corpus * (1 + rate/100) + income - expenses.loc[j]['Expenses']

    yr_corpus = yr_corpus - terminal_corpus

    return yr_corpus

def xirr(rate,cash_flow,terminal_value=0):

    npv = 0
    for i in cash_flow.index:
        nYears = cash_flow.loc[i,'Num_Days']/365
        pv = cash_flow.loc[i,'Tran_Value']*(pow((1 + rate / 100), nYears))
        npv = npv + pv

    return  npv+terminal_value





st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Retirement Readiness Score</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)


st.markdown('<p><BR></p>', unsafe_allow_html=True)

left, buf, right = st.columns((10,1,14))
placeholder_header_1 = left.empty()
placeholder_score = left.empty()
placeholder_score_txt = left.empty()
placeholder_header_2 = right.empty()
placeholder_chart = right.empty()
placeholder_fund = right.empty()


dummy1, place_here, dummy2 = st.columns((5,2,5))

placeholder_button = place_here.empty()

st.markdown('<p><BR></p>', unsafe_allow_html=True)

basic_info,oth_incomes,oth_expenses, help = st.tabs(["Basic Information","Other Incomes", "Other Expenses","Help"])


with basic_info:

    user_inputs = st.columns((3,6,1,4,6))

    #user_inputs[0].markdown('<p><BR></p>', unsafe_allow_html=True)
    #user_inputs[1].markdown('<p><BR></p>', unsafe_allow_html=True)

    user_inputs[0].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Name:</p><p>', unsafe_allow_html=True)
    name = user_inputs[1].text_input(":blue[Name]",label_visibility="collapsed", value="John Doe")
    user_inputs[3].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Current Age:</p><p>', unsafe_allow_html=True)
    curr_age = user_inputs[4].number_input(":blue[Your Current Age?]",label_visibility="collapsed",  min_value=18, max_value=100, step=1, value=40)

    user_inputs[0].markdown(' ')
    user_inputs[3].markdown(' ')

    user_inputs[0].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Years to Retire:</p><p>', unsafe_allow_html=True)
    user_inputs[3].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Expected Life Span:</p><p>', unsafe_allow_html=True)
    yrs_to_retire = user_inputs[1].number_input(":blue[Years to Retire:]", label_visibility="collapsed", min_value=0, max_value=30, step=1, value=10,help="How many years till Retirement")
    plan_till = user_inputs[4].number_input("Plan Till", label_visibility="collapsed", min_value=curr_age + yrs_to_retire, max_value=100, step=1, value=90,help="Till what age you want to plan for?")



    user_inputs[0].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Annual Income:</p><BR><BR>', unsafe_allow_html=True)
    user_inputs[3].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Annual Hike %:</p><BR><BR>', unsafe_allow_html=True)
    c_annual_income = user_inputs[1].number_input(":blue[Annual Income]", label_visibility="collapsed", value=1200000,step=100000)
    user_inputs[1].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:green;margin:0px;padding:0px">({})</p>'.format(display_amount(c_annual_income)), unsafe_allow_html=True)
    ann_hike = user_inputs[4].number_input(":blue[Annual Hike %]", label_visibility="collapsed", min_value=0.0, max_value=20.0, step=0.1, value=4.0, help="Expected % increase in Annual Income")

    #user_inputs[0].markdown(' ')

    user_inputs[1].markdown(' ')
    user_inputs[4].markdown(' ')
    user_inputs[4].markdown(' ')

    user_inputs[0].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Annual Expense:</p><BR><BR>', unsafe_allow_html=True)
    user_inputs[3].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Inflation %:</p><BR><BR>', unsafe_allow_html=True)

    c_annual_expense = user_inputs[1].number_input(":blue[Annual Expense]",label_visibility="collapsed",  value=800000,step=100000)
    user_inputs[1].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:green;margin:0px;padding:0px">({})</p>'.format(display_amount(c_annual_expense)), unsafe_allow_html=True)
    inflation = user_inputs[4].number_input(":blue[Inflation]", value=4.0,step =0.1,help="Expected Inflation Rate",label_visibility="collapsed")


    user_inputs[0].markdown(' ')
    user_inputs[1].markdown(' ')
    user_inputs[3].markdown(' ')

    user_inputs[4].markdown(' ')
    user_inputs[4].markdown(' ')

    user_inputs[0].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Current Corpus:</p><BR><BR>', unsafe_allow_html=True)
    user_inputs[3].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Return % on Assets:</p><BR><BR>', unsafe_allow_html=True)


    c_corpus = user_inputs[1].number_input(":blue[Current Corpus]",label_visibility="collapsed", value=7500000,step=100000,help="Your Total Current Savings")
    user_inputs[1].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:green;margin:0px;padding:0px">({})</p>'.format(display_amount(c_corpus)), unsafe_allow_html=True)
    cagr = round(user_inputs[4].number_input(":blue[Return on Assets]", label_visibility="collapsed", value=8.0,step=0.10,help="Expected Rate of Return on your Assets"),2)


    user_inputs[1].markdown(' ')
    user_inputs[4].markdown(' ')
    user_inputs[4].markdown(' ')


    #user_inputs[2].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">****</p>', unsafe_allow_html=True)
    #user_inputs[0].markdown(' ')
    #user_inputs[1].markdown(' ')
    user_inputs[0].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Expense Cap:</p><BR><BR>', unsafe_allow_html=True)
    user_inputs[3].markdown('<p style="font-size:16px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:4px">Terminal Corpus:</p><BR><BR>', unsafe_allow_html=True)

    exp_cap_at = user_inputs[1].number_input(":blue[Expense Cap]", label_visibility="collapsed",  min_value=curr_age + yrs_to_retire, max_value=plan_till, step=1, value=plan_till, help="Age after which expense will not increase due to Inflation")

    terminal_corpus = user_inputs[4].number_input(":blue[Terminal Corpus]", label_visibility="collapsed", value=0,step=100000, help="Money you want to leave behind")
    user_inputs[4].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:green;margin:0px;padding:0px">({})</p>'.format(display_amount(terminal_corpus)), unsafe_allow_html=True)

#placeholder_header_1.markdown('<p style="font-size:20px;font-weight:bold;text-align:center;vertical-align:middle;color:brown;margin:0px;padding:0px"><u>Retirement Score</u></p>', unsafe_allow_html=True)



freq_options = ['0-One Time','1-Once Every Year','2-Once in 2 Years','3-Once in 3 Years','4-Once in 4 Years','5-Once in 5 Years', \
                '6-Once in 6 Years', '7-Once in 7 Years','8-Once in 8 Years','9-Once in 9 Years','10-Once in 10 Years']

#st_age = curr_age + yrs_to_retire
st_age = curr_age
end_age = plan_till


with oth_incomes:

    left, mid, mid_right, right = st.columns((2,4,1.5,2))
    left.markdown("****:red[OTHER INCOME SOURCES (If Applicable)]****")
    mid_right.markdown(":red[No of Income Rows]")
    n_pr_incomes = right.slider("", min_value=1, max_value=6, step=1, value=4, label_visibility="collapsed")

    p_inputs = st.columns((4,4,6,6,6,5))

    p_inputs[0].markdown("**:blue[Start Age]**")
    p_inputs[1].markdown("**:blue[End Age]**")
    p_inputs[2].markdown("**:blue[Description]**")
    p_inputs[3].markdown("**:blue[Amount]**")
    p_inputs[4].markdown("**:blue[Frequency]**")
    p_inputs[5].markdown("**:blue[Yearly Increment %]**")

    help_txt_1 = "Age at which this Income Starts"
    i_start_age = [p_inputs[0].number_input("i_Start_Age", key=f"Start_Age_{col}",min_value=st_age + 1, max_value=end_age, step=1, value=st_age + 1 ,label_visibility="collapsed") for col in range(n_pr_incomes)]
    i_end_age = [p_inputs[1].number_input("i_End_Age", key=f"End_Age_{col}",min_value=i_start_age[col], max_value=end_age, step=1, value=end_age, label_visibility="collapsed") for col in range(n_pr_incomes)]
    i_income_desc = [p_inputs[2].text_input("i_Income",value="",key=f"Desc_{col}", label_visibility="collapsed")  for col in range(n_pr_incomes)]
    i_income_amt = [p_inputs[3].number_input("i_Amount", key=f"Income_amt_{col}", min_value=0, step=10000, value=0, help="Income Annual Value", label_visibility="collapsed")  for col in range(n_pr_incomes)]
    i_income_freq = [p_inputs[4].selectbox("i_Frequency",freq_options,0,key=f"Income_Frequency_{col}", label_visibility="collapsed")  for col in range(n_pr_incomes)]
    i_income_incr_pct = [p_inputs[5].number_input("i_income_incr_pct",key=f"Income_incr_{col}",min_value=0.00, step=0.05, value=0.00, help="Income Increment %",label_visibility="collapsed")  for col in range(n_pr_incomes)]



    income_rec = []
    for p_i in range(n_pr_incomes):

        if i_income_amt[p_i] > 0:
            values = i_start_age[p_i],i_end_age[p_i],i_income_desc[p_i],i_income_amt[p_i],int(i_income_freq[p_i].split("-")[0]),i_income_incr_pct[p_i]
            income_rec.append(values)

    df_ret_income = pd.DataFrame(income_rec,columns=['Start_Age','End_Age','Desc','Amount','Frequency','Increment_Pct'])




with oth_expenses:
    left, mid, mid_right, right = st.columns((2,4,1.5,2))
    left.markdown("****:red[OTHER EXPENSES - LIFE GOALS (If Applicable)]****")
    mid_right.markdown(":red[No of Goal Rows]")
    n_goals = right.slider("", min_value=1, max_value=10, step=1, value=4, label_visibility="collapsed")

    g_inputs = st.columns((4,4,6,6,6,5))

    g_inputs[0].markdown("**:blue[Start Age]**")
    g_inputs[1].markdown("**:blue[End Age]**")
    g_inputs[2].markdown("**:blue[Description]**")
    g_inputs[3].markdown("**:blue[Amount]**")
    g_inputs[4].markdown("**:blue[Frequency]**")
    g_inputs[5].markdown("**:blue[Annual Inflation %]**")


    g_start_age = [g_inputs[0].number_input("Start Age", key=f"gStart_Age_{col}",min_value=st_age + 1, max_value=end_age, step=1, value=st_age + 1,label_visibility="collapsed") for col in range(n_goals)]
    g_end_age = [g_inputs[1].number_input("End Age", key=f"gEnd_Age_{col}",min_value=g_start_age[col], max_value=end_age, step=1, value=end_age, label_visibility="collapsed") for col in range(n_goals)]
    g_desc = [g_inputs[2].text_input("Desc",value="",key=f"gDesc_{col}", label_visibility="collapsed")  for col in range(n_goals)]
    g_amt = [g_inputs[3].number_input("Amount", key=f"gAmt_{col}", min_value=0, step=10000, value=0, help="Income Annual Value", label_visibility="collapsed")  for col in range(n_goals)]
    g_freq = [g_inputs[4].selectbox("Frequency",freq_options,0,key=f"gFrequency_{col}", label_visibility="collapsed")  for col in range(n_goals)]
    g_infl_pct = [g_inputs[5].number_input("Inflation_pct",key=f"gInflation_pct_{col}",min_value=0.00, step=0.05, value=0.00,label_visibility="collapsed")  for col in range(n_goals)]



    goal_rec = []
    for g_i in range(n_goals):
        if g_amt[g_i] > 0:
            values = g_start_age[g_i],g_end_age[g_i],g_desc[g_i],g_amt[g_i],int(g_freq[g_i].split("-")[0]),g_infl_pct[g_i]
            goal_rec.append(values)

    df_goals = pd.DataFrame(goal_rec,columns=['Start_Age','End_Age','Desc','Amount','Frequency','Inflation_Pct'])


    with help:
        help_text_df = get_help_texts()

        left, buf, right = st.columns((4,1,10))

        tab_list = [i for i in help_text_df['Tab_Name'].unique()]

        select_tab = left.selectbox("",tab_list,0)

        help_text_tab_df = help_text_df[help_text_df['Tab_Name'] == select_tab][['Field_Name','Help_Text']]

        st.markdown(get_markdown_table(help_text_tab_df, header='Y', footer='N'), unsafe_allow_html=True)


st.write("-----")
n_Retire = st.button('Calculate Score', key="Button 2")


if n_Retire:


    #validation_flag = 'Y'
    #df_ret_income = edited_df_post_ret_income[edited_df_post_ret_income['Amount'] > 0]
    #df_goals = edited_df_goals[edited_df_goals['Amount'] > 0 ]
    #st.write(df_goals)
    #st.write(df_ret_income)

    exp_data = []
    tot_assets = c_corpus
    start_year = curr_age
    age_at_retirement = curr_age + yrs_to_retire
    end_year = plan_till + 1
    expense = c_annual_expense
    nyear = 0

    goals = []
    if len(df_goals) > 0:

        for i in df_goals.index:
            gc_st_age = df_goals.loc[i][0]
            gc_end_age = df_goals.loc[i][1]
            gc_amt = df_goals.loc[i]['Amount']
            gc_freq =df_goals.loc[i][4]
            gc_infl = df_goals.loc[i][5]
            g_desc = df_goals.loc[i][2]

            if gc_amt !=0:
                goals = goals + get_goals(gc_st_age, gc_end_age, g_desc, gc_amt, gc_freq, gc_infl)
                #st.write(goals)
        goals_df=pd.DataFrame(goals,columns=['Years','Desc','Amount'])
    #st.write(goals_df.groupby(['Years']).sum())
    #st.write(goals_df)


    for n in range(start_year, end_year):

        if n==start_year:
            expense_rec = n, 0
        elif n == (start_year + 1):
            expense_rec = n, expense
        elif n > exp_cap_at:
            expense_rec = n, round(expense,0)
        else:
            expense = expense * (1 + inflation/100)
            expense_rec = n, round(expense,0)

        exp_data.append(expense_rec)

    #st.write(pd.DataFrame(expense_rec))

    df_expense = pd.DataFrame(exp_data,columns=['Years','Expenses'])
    df_expense = df_expense.set_index('Years')

    #st.write(df_expense)

    if len(goals) > 0:
        for key in range(len(goals)):
            #st.write(key,goals[key])
            df_expense.loc[goals[key][0]]['Expenses'] = df_expense.loc[goals[key][0]]['Expenses'] + goals[key][2]

    #st.write(cagr,curr_age, c_annual_income, age_at_retirement, c_corpus)
    #st.write(df_expense)

    fut_income = []
    if len(df_ret_income) > 0:
        for i in df_ret_income.index:
            fi_st_age = df_ret_income.loc[i][0]
            fi_end_age = df_ret_income.loc[i][1]
            fi_amt = df_ret_income.loc[i]['Amount']
            fi_freq =df_ret_income.loc[i][4]
            fi_incr = df_ret_income.loc[i][5]

            if fi_amt > 0:
                fut_income = fut_income + get_fut_income(fi_st_age,fi_end_age,fi_amt,fi_freq,fi_incr)

    #st.write(fut_income)

    df_corpus = get_corpus(cagr,curr_age, c_annual_income, age_at_retirement, c_corpus, df_expense, fut_income,"Corpus@{} %".format(cagr))

    retirement_assets = df_expense.merge(df_corpus, on='Years')
    retirement_assets_pdf = retirement_assets
    be_year = plan_till
    for i in retirement_assets.index:
        expense_y = retirement_assets.loc[i][0]
        corpus_y  = retirement_assets.loc[i][1]

        if corpus_y < expense_y:
            be_year = i
            break

    retirement_score = round(100 * (be_year - curr_age)/(plan_till - curr_age),2)

    try:
        root=round(optimize.newton(get_optimised_rate, 25, tol=0.0000001, args=(curr_age, c_annual_income, age_at_retirement, c_corpus, df_expense,terminal_corpus, fut_income)),2)
        #st.write(root)
        opt_corpus = round(optimize.newton(get_optimised_corpus, c_corpus,tol=0.0001,args=(cagr,curr_age, c_annual_income, age_at_retirement, df_expense,terminal_corpus, fut_income)),0)
        opt_corpus = opt_corpus - c_corpus
        mth_sip = -1
        if opt_corpus > 0:
            if yrs_to_retire > 0:
                mthly_r = cagr / 1200.0
                tot_mths = 12 * yrs_to_retire
                mth_sip = opt_corpus * mthly_r * np.power(1+mthly_r,tot_mths) / (np.power(1+mthly_r,tot_mths) -1)

        #st.write(opt_corpus)

    #st.write(opt_corpus)
    #st.write(root)
        if -10 < root < 50:
            optimised_rate = get_corpus(root,curr_age, c_annual_income, age_at_retirement, c_corpus, df_expense, fut_income,"Optimised Corpus@{}%".format(root))
            retirement_assets = retirement_assets.merge(optimised_rate, on='Years')
        else:
            placeholder_fund.markdown(":red[ Warning: Optimised IRR is out of bounds. Input data seems too high/low]")
            optimised_rate = ""

    except:
        placeholder_fund.markdown(":red[ Error: Solution for Optimized IRR not possible. Input data seems too high/low]")
    #optimised_corpus = get_corpus(cagr,curr_age, c_annual_income, age_at_retirement, opt_corpus, df_expense, fut_income,"Optimised Corpus-{}".format(cagr))
    #retirement_assets = retirement_assets.merge(optimised_corpus, on='Years')


    retirement_assets = retirement_assets / 10000000


    c_corpus = c_corpus /10000000
    config = {'displayModeBar': False}

    #st.write(retirement_assets)
    fig = px.line(retirement_assets)
    fig.update_layout(title_text="",
                      title_x=0.2,
                      title_font_size=20,
                      xaxis_title="Age (in Years) ",
                      yaxis_title="Retirement Fund (Crores)")

    fig.update_layout(margin=dict(l=1,r=11,b=1,t=1))
    yrange = [-1*c_corpus, 5*c_corpus]
    fig.update_yaxes(range=yrange, dtick=1,showgrid=True)
    fig.update_xaxes(showgrid=True)
    fig.update_layout(legend_title='')
    #fig.update_yaxes(automargin=True)
    #fig.update_xaxes(automargin=True)
    #fig.update_layout(autosize=True)
    fig.update_layout(height=350)
    fig.update_layout(width=550)


    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=-0.25,
        xanchor="left",
        x=0.7
    ))

    #user_inputs[2].write("   ")
    #user_inputs[2].write("   ")

    #user_inputs[2].write("   ")

    placeholder_header_2.markdown('<p style="font-size:18px;font-weight: bold;text-align:center;vertical-align:middle;color:brown;margin:0px;padding:0px"><u>Lifetime - Expense vs Savings Chart</u></p>', unsafe_allow_html=True)
    #user_inputs[3].markdown('<BR>',unsafe_allow_html=True)
    #user_inputs[3].markdown('<BR>',unsafe_allow_html=True)


    placeholder_chart.plotly_chart(fig,config=config,use_container_width=True)


    fig_1 = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = retirement_score,
            mode = "gauge+number",
            title = {'text': ""},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},

            'steps' : [
                {'range': [0, 75], 'color': "red"},
                {'range': [75, 95], 'color': "orange"},
                {'range': [95, 100], 'color': "green"}]
            }))
    fig_1.update_layout(margin=dict(l=30,r=10,b=10,t=10))
    fig_1.update_layout(height=200)
    fig_1.update_layout(width=475)

    if opt_corpus > 0:
        if mth_sip > 0:
            html_t_text = '<p style="text-align:center"><strong><span style="font-size:16px;color:rgb(10, 100, 40);">&nbsp;&nbsp;Fund Shortfall:</span></em></strong>'
            html_t_text = html_t_text + '<span style="font-size:14px;color: rgb(0, 0, 255);"> One Time: {}  | Monthly SIP till Retirement: {}</span><BR><BR></em>'.format(display_amount(opt_corpus),display_amount(mth_sip))
        else:
            html_t_text = '<p style="text-align:center"><strong><span style="font-size:16px;color:rgb(10, 100, 40);">Fund Shortfall:</span></em></strong>'
            html_t_text = html_t_text + '<span style="font-size:14px;color: rgb(0, 0, 255);"> {}</span><BR><BR></em>'.format(display_amount(opt_corpus))
    else:
        html_t_text = ""


    placeholder_score_txt.markdown(html_t_text, unsafe_allow_html=True)

    #fig_1.update_layout(paper_bgcolor = "lavender", font = {'color': "darkblue", 'family': "Arial"})
    fig_1.update_layout(title_text= "",
              title_x=0.32,
              title_y=0.1,
              titlefont=dict(size=1, color='blue', family='Arial, sans-serif'),
              xaxis_title="Optimised Corpus Required is {}".format(display_amount(opt_corpus)),
              yaxis_title="")

    with right.container():
        #placeholder_header_1.markdown('<p style="font-size:20px;font-weight:bold;text-align:center;vertical-align:middle;color:brown;margin:0px;padding:0px"><u>Retirement Score</u></p><BR>', unsafe_allow_html=True)
        placeholder_score.plotly_chart(fig_1,config=config,use_container_width=True)
    #placeholder_score.markdown(":blue[ Retirement Score : {} %]".format(retirement_score))
    #placeholder_fund.markdown('<p style="font-size:16px;font-weight: normal;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Optimised Fund : {}</p>'.format(display_amount(opt_corpus)), unsafe_allow_html=True)

    retirement_dict = {'Name': name,
             'Age': curr_age,
             'RetAge': yrs_to_retire,
             'PlanAge': plan_till,
             'AnnInc': c_annual_income,
             'AnnExp': c_annual_expense,
             'AnnHikPct': ann_hike,
             'ExpCapAge': exp_cap_at,
             'Corpus': int(c_corpus * 10000000),
             'TermCorp': terminal_corpus,
             'Cagr': cagr,
             'Inflation': inflation,
             'RetScore': retirement_score,
             'FundShort': opt_corpus,
             'SIPNeed': mth_sip,
             'OptXIRR': root
            }






    retirement_assets_pdf.reset_index(inplace=True)
    retirement_assets_pdf.columns = ['Age','Expenses','Networth']
    retirement_assets_pdf['Networth'] = retirement_assets_pdf['Networth'] /100000.0



    # Show the chart in Streamlit
    #st.plotly_chart(fig_2)

    #pdf_bytes = generate_pdf_report(fig_1, fig_2, retirement_dict, df_goals, df_ret_income, retirement_assets_pdf)
    pdf_bytes = generate_pdf_report( retirement_dict, df_goals, df_ret_income, retirement_assets_pdf)

    # Create a download button for the PDF
    placeholder_button.download_button(
        label="Download Report",
        data=pdf_bytes,
        key='download_button_1',
        file_name="Retirement_Score_{}.pdf".format(name)
    )
