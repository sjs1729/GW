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

# Hide Streamlit menu and footer
hide_streamlit_style = """
        <style>
        .stToolbarActions {display: none !important;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

c_1, c_2 = st.columns((8,4))
c_2.image('growealth-logo_long.png')

def get_emi(emi, rate, nperiods,target_amt,present_corpus):
    tot_val = present_corpus * pow((1+ rate/100),nperiods/12)
    for per in range(nperiods):
        tot_val = tot_val + emi * pow((1+ rate/1200),nperiods - per)

    return tot_val - target_amt



@st.cache_data()
def get_risk_matrix_data():
    df_risk_mat = pd.read_csv('Risk_Profile_Matrix.csv')
    return df_risk_mat

def get_risk_profile(years_remaining, exp_roi):

    if years_remaining < 1:
        years_remaining = 1
    elif years_remaining > 7:
        years_remaining = 7

    if exp_roi < 5:
        exp_roi = 5

    df_risk_mat = get_risk_matrix_data()

    risk_mat = df_risk_mat[(df_risk_mat['Years_Left'] == years_remaining) & (df_risk_mat['Expected_Return'] == round(exp_roi))].iloc[0]

    return risk_mat



left,centre,right = st.columns((8,1,7))

left.markdown('<BR>',  unsafe_allow_html=True)
left.markdown("**:blue[Select Life Goal]**")
goal_type = left.selectbox("Select Goal", ('Marriage', 'Higher Education','Vacation','Buying a Dream Car','Buying Dream Home','Miscellaneous Goal'),1, label_visibility='collapsed')
if goal_type == 'Marriage':
    image_path = 'marriage.jpeg'
elif goal_type == 'Higher Education':
    image_path = 'highereducation.jpeg'
elif goal_type == 'Vacation':
    image_path = 'vacation.jpeg'
elif goal_type == 'Buying a Dream Car':
    image_path = 'dreamcar.jpeg'
elif goal_type == 'Buying Dream Home':
    image_path = 'dreamhome.jpeg'
else:
    image_path = 'goal.jpeg'

left.image(image_path)
right.markdown('<BR><BR>',  unsafe_allow_html=True)

placeholder_summary = right.empty()
placeholder_advise = right.empty()
placeholder_image = right.empty()

gp_flds = st.columns((4,1,4))

st.markdown('<BR>',  unsafe_allow_html=True)

left,centre,right = st.columns((7,1,6))

variable_color = "blue"
markdown_txt = f"**:{variable_color}[{goal_type} ]** :{variable_color}[ (Cost in Today's Price)]"
left.markdown(markdown_txt)
goal_amount = left.number_input(f"Cost of {goal_type} (in Today's Price)", value=100000,step=10000, label_visibility='collapsed')
left.markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:green;margin:0px;padding:0px">({})</p>'.format(display_amount(goal_amount)), unsafe_allow_html=True)
left.markdown("  ")

right.markdown("**:blue[In How Many Years?]**")
years_to_goal = right.slider("Years to Goal?", min_value=1, max_value=30, step=1, value=3, label_visibility='collapsed')

left,buffer,centre,right = st.columns((14,2,6,6))

left.markdown("**:blue[Corpus I Already Have]**")
present_corpus = left.number_input("Corpus I Already Have", value=0,step=10000, max_value=goal_amount,label_visibility='collapsed')
left.markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:green;margin:0px;padding:0px">({})</p>'.format(display_amount(present_corpus)), unsafe_allow_html=True)

max_rate_of_return = 15.0

if years_to_goal < 3:
    max_rate_of_return = 8.0
elif years_to_goal < 5:
    max_rate_of_return = 10.0
elif years_to_goal < 7:
    max_rate_of_return = 12.0
else:
    max_rate_of_return = 15.0

centre.markdown("**:blue[Return on Assets]**")
rate = round(centre.number_input("Return on Assets", step=0.10, value=7.0, max_value=max_rate_of_return, min_value=0.0,label_visibility='collapsed'),2)

right.markdown("**:blue[Inflation]**")
infl = right.number_input("Inflation", step =0.1, value=4.0,label_visibility='collapsed')

adj_amount = goal_amount*pow((1+infl/100),years_to_goal)

present_value = adj_amount/pow((1+rate/100),years_to_goal)

tot_mths = 12*years_to_goal

mthly_amt=round(optimize.newton(get_emi, 0, tol=0.0000001, args=(rate, tot_mths,adj_amount,present_corpus)),2)

risk_matrix = get_risk_profile(years_to_goal, rate)


#html_text = '<p><strong><u><span style="color: rgb(148, 33, 147);">Goal Planning Summary:</span></u></strong></p>'
html_text =''
html_text = html_text + '<BR><p><span style="color: rgb(4, 51, 255);">You can achieve the Goal by either of the following: &nbsp;&nbsp; </span><p>'
html_text = html_text + '<ol><li><span style="color: rgb(4, 51, 255);">Invest One Time Amount of <strong>&nbsp;</span>'
html_text = html_text + '<span style="color: rgb(148, 33, 147);">{}</span></strong></li>'.format(display_amount(present_value - present_corpus))
html_text = html_text + '<li><span style="color: rgb(4, 51, 255);"> Invest Montly SIP of </span>'
html_text = html_text + '<strong><span style="color: rgb(148, 33, 147);">{}</span></strong></li></ol>'.format(display_amount(mthly_amt))

placeholder_summary.markdown(html_text, unsafe_allow_html=True)



html_text = '<p><span style="color: rgb(4, 51, 255);">Based on your Expected Rate of Return & Years to Goal, the suggested Asset Allocation: &nbsp;&nbsp; </span>'
html_text = html_text +  '<strong><span style="color: rgb(148, 33, 147);"> {}</span></strong></p><BR><BR><BR>'.format(risk_matrix['Asset_Allocation'])
html_text = html_text + '<p><span style="color: rgb(255, 50, 50); font-size: 13px;">Consult your Financial Advisor for specific guidance.'
html_text = html_text + 'For MF Investment, you can also email Growealth Investments </span>'
html_text = html_text + '<span style="color: rgb(4, 51, 255); font-size: 13px;"><u>(helpdesk@gro-wealth.in)</u></span></p>'
placeholder_advise.markdown(html_text, unsafe_allow_html=True)
