import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
c_1, c_2 = st.columns((8,4))
c_2.image('growealth-logo_long.png', width=300)





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




st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Retirement Planning</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)

user_inputs = st.columns((4,4,1,12))


name = user_inputs[0].text_input(":blue[Name]",value="John Doe")
curr_age = user_inputs[1].number_input(":blue[Your Current Age?]", min_value=18, max_value=100, step=1, value=40)
yrs_to_retire = user_inputs[0].number_input(":blue[Years to Retire:]", min_value=0, max_value=30, step=1, value=10,help="How many years till Retirement")

plan_till = user_inputs[1].number_input("Plan Till", min_value=curr_age + yrs_to_retire, max_value=100, step=1, value=90,help="Till what age you want to plan for?")




c_annual_income = user_inputs[0].number_input(":blue[Annual Income]", value=1200000,step=100000)
user_inputs[0].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">({})</p>'.format(display_amount(c_annual_income)), unsafe_allow_html=True)
c_annual_expense = user_inputs[1].number_input(":blue[Annual Expense]", value=800000,step=100000)
user_inputs[1].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">({})</p>'.format(display_amount(c_annual_expense)), unsafe_allow_html=True)

ann_hike = user_inputs[0].number_input(":blue[Annual Hike %]", min_value=0.0, max_value=20.0, step=0.1, value=4.0, help="Expected % increase in Annual Income")
exp_cap_at = user_inputs[1].number_input(":blue[Expense Cap]", min_value=curr_age + yrs_to_retire, max_value=plan_till, step=1, value=plan_till, help="Age after which expense will not increase due to Inflation")

c_corpus = user_inputs[0].number_input(":blue[Current Corpus]", value=7500000,step=100000,help="Your Total Current Savings")
user_inputs[0].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">({})</p>'.format(display_amount(c_corpus)), unsafe_allow_html=True)

terminal_corpus = user_inputs[1].number_input(":blue[Terminal Corpus]", value=0,step=100000, help="Money you want to leave behind")
user_inputs[1].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">({})</p>'.format(display_amount(terminal_corpus)), unsafe_allow_html=True)

cagr = round(user_inputs[0].number_input(":blue[Return on Assets]", value=8.0,step=0.10,help="Expected Rate of Return on your Assets"),2)
inflation = user_inputs[1].number_input(":blue[Inflation]", value=4.0,step =0.1,help="Expected Inflation Rate")
#user_inputs[2].markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">****</p>', unsafe_allow_html=True)
placeholder_header_1 = user_inputs[3].empty()
placeholder_score = user_inputs[3].empty()
placeholder_header_2 = user_inputs[3].empty()
placeholder_chart = user_inputs[3].empty()
placeholder_fund = user_inputs[3].empty()

placeholder_header_1.markdown('<p style="font-size:20px;font-weight:bold;text-align:center;vertical-align:middle;color:brown;margin:0px;padding:0px"><u>Retirement Score</u></p>', unsafe_allow_html=True)

n_Retire_1 = st.button('Retirement  Score')


st_age = curr_age + yrs_to_retire
end_age = plan_till
df_post_ret_income = pd.DataFrame(
    [
        { "Income Start Age": st_age, "Income End Age": end_age, "Income Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, =0 if OneTime)":0,"Annual Increment Rate":0.0},
        { "Income Start Age": st_age, "Income End Age": end_age, "Income Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, =0 if OneTime)":0,"Annual Increment Rate":0.0},
        { "Income Start Age": st_age, "Income End Age": end_age, "Income Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, =0 if OneTime)":0,"Annual Increment Rate":0.0},
        { "Income Start Age": st_age, "Income End Age": end_age, "Income Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, =0 if OneTime)":0,"Annual Increment Rate":0.0},
        { "Income Start Age": st_age, "Income End Age": end_age, "Income Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, =0 if OneTime)":0,"Annual Increment Rate":0.0},
    ]
)

#df_post_ret_income = load_data()
st.markdown('<p style="font-size:20px;font-weight: bold;text-align:left;vertical-align:middle;color:blue;margin:0px;padding:0px">Edit Post Retirement Income (if any)</p>', unsafe_allow_html=True)
edited_df_post_ret_income = st.experimental_data_editor(df_post_ret_income)
placeholder_income = st.empty()
placeholder_income.markdown(":blue[Validations - Start Age => {}, End Age < {}, Frequency 0,1,2,...10 ]".format(curr_age + yrs_to_retire,plan_till))

df_goals = pd.DataFrame(
    [
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
        { "Goal Start Age": curr_age, "Goal End Age": end_age, "Goal Description":"","Amount":0,"Frequency (Frequency = 3 if Once in 3 years, Frequency=0 if OneTime)":0,"Inflation Rate":inflation},
    ]
)
st.markdown('<p style="font-size:20px;font-weight: bold;text-align:left;vertical-align:middle;color:blue;margin:0px;padding:0px">Edit Future Financial Goals(if any)</p>', unsafe_allow_html=True)
edited_df_goals = st.experimental_data_editor(df_goals)
placeholder_goals = st.empty()
placeholder_goals.markdown(":blue[Validations - Start Age => {}, End Age < {}, Frequency 0,1,2,...10 ]".format(curr_age + yrs_to_retire,plan_till))

n_Retire_2 = st.button('Retirement Score')


if n_Retire_1 or n_Retire_2:

    validation_flag = 'Y'
    df_ret_income = edited_df_post_ret_income[edited_df_post_ret_income['Amount'] > 0]
    df_goals = edited_df_goals[edited_df_goals['Amount'] > 0 ]
    for i in df_ret_income.index:
        gc_st_age = df_ret_income.loc[i][0]
        gc_end_age = df_ret_income.loc[i][1]
        gc_amt = df_ret_income.loc[i]['Amount']
        gc_freq =df_ret_income.loc[i][4]
        gc_incr = df_ret_income.loc[i][5]
        if gc_st_age > (curr_age + yrs_to_retire - 1) and gc_end_age < (plan_till + 1) and gc_freq in [0,1,2,3,4,5,6,7,8,9,10]:
            try:
                gc_amt  = int(gc_amt)
                gc_incr = int(gc_incr)
            except:
                validation_flag = 'N'
        else:
            validation_flag = 'N'
    #st.write(df_goals)
    for i in df_goals.index:
        gc_st_age = df_goals.loc[i][0]
        gc_end_age = df_goals.loc[i][1]
        gc_amt = df_goals.loc[i]['Amount']
        gc_freq =df_goals.loc[i][4]
        gc_infl = df_goals.loc[i][5]
        if gc_st_age > (curr_age - 1) and gc_end_age < (plan_till + 1) and gc_freq in [0,1,2,3,4,5,6,7,8,9,10]:
            try:
                gc_amt  = int(gc_amt)
                gc_infl = int(gc_infl)
            except:
                validation_flag = 'N'
        else:
            validation_flag = 'N'

    if validation_flag == 'N':
        placeholder_income.markdown(":red[Validations Failed - Start Age => {}, End Age < {}, Frequency 0,1,2,...10 ]".format(curr_age + yrs_to_retire,plan_till))
        placeholder_goals.markdown(":red[Validations Failed - Start Age => {}, End Age < {}, Frequency 0,1,2,...10 ]".format(curr_age + yrs_to_retire,plan_till))
    else:

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
                gc_incr = df_goals.loc[i][5]
                g_desc = df_goals.loc[i][2]

                if gc_amt !=0:
                    goals = goals + get_goals(gc_st_age, gc_end_age, g_desc, gc_amt, gc_freq, gc_incr)
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

        fut_income = []
        if len(df_ret_income) > 0:
            for i in df_ret_income.index:
                gc_st_age = df_ret_income.loc[i][0]
                gc_end_age = df_ret_income.loc[i][1]
                gc_amt = df_ret_income.loc[i]['Amount']
                gc_freq =df_ret_income.loc[i][4]
                gc_incr = df_ret_income.loc[i][5]

                if gc_amt > 0:
                    fut_income = fut_income + get_fut_income(st_age,end_age,gc_amt,gc_freq,gc_incr)

        #st.write(fut_income)

        df_corpus = get_corpus(cagr,curr_age, c_annual_income, age_at_retirement, c_corpus, df_expense, fut_income,"Corpus@{} %".format(cagr))

        retirement_assets = df_expense.merge(df_corpus, on='Years')
        #st.write(retirement_assets)

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
            #st.write(opt_corpus)

        #st.write(opt_corpus)
        #st.write(root)
            if 0 < root < 25:
                optimised_rate = get_corpus(root,curr_age, c_annual_income, age_at_retirement, c_corpus, df_expense, fut_income,"Optimised Corpus@{}%".format(root))
                retirement_assets = retirement_assets.merge(optimised_rate, on='Years')
            else:
                placeholder_fund.markdown(":red[ Error: Optimized Rate out of Range. Check input data!]")

        except:
            placeholder_fund.markdown(":red[ Error: Solution for Optimized Rate not possible. Check input data!]")
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

        fig.update_layout(height=350)
        fig.update_layout(width=550)
        fig.update_layout(legend=dict(
            yanchor="bottom",
            y=-0.25,
            xanchor="left",
            x=0.7
        ))

        user_inputs[2].write("   ")
        user_inputs[2].write("   ")

        #user_inputs[2].write("   ")

        placeholder_header_2.markdown('<p style="font-size:18px;font-weight: bold;text-align:center;vertical-align:middle;color:brown;margin:0px;padding:0px"><u>Lifetime - Expense vs Savings Chart</u></p>', unsafe_allow_html=True)
        user_inputs[3].markdown('<BR>',unsafe_allow_html=True)
        user_inputs[3].markdown('<BR>',unsafe_allow_html=True)


        placeholder_chart.plotly_chart(fig,config=config)


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
        fig_1.update_layout(margin=dict(l=130,r=10,b=30,t=1))
        fig_1.update_layout(height=200)
        fig_1.update_layout(width=400)
        #fig_1.update_layout(paper_bgcolor = "lavender", font = {'color': "darkblue", 'family': "Arial"})
        fig_1.update_layout(title_text="Min Fund Needed - {}".format(display_amount(opt_corpus)),
                  title_x=0.32,
                  title_y=0.1,
                  titlefont=dict(size=15, color='blue', family='Arial, sans-serif'),
                  xaxis_title="Optimised Corpus Required is {}".format(display_amount(opt_corpus)),
                  yaxis_title="")

        with user_inputs[3].container():
            placeholder_header_1.markdown('<p style="font-size:20px;font-weight:bold;text-align:center;vertical-align:middle;color:brown;margin:0px;padding:0px"><u>Retirement Score</u></p>', unsafe_allow_html=True)
            placeholder_score.plotly_chart(fig_1,config=config)
        #placeholder_score.markdown(":blue[ Retirement Score : {} %]".format(retirement_score))
        #placeholder_fund.markdown('<p style="font-size:16px;font-weight: normal;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Optimised Fund : {}</p>'.format(display_amount(opt_corpus)), unsafe_allow_html=True)
