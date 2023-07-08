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

def get_emi(emi, rate, nperiods,target_amt,present_corpus):
    tot_val = present_corpus * pow((1+ rate/100),nperiods/12)
    for per in range(nperiods):
        tot_val = tot_val + emi * pow((1+ rate/1200),nperiods - per)

    return tot_val - target_amt





left,centre,right = st.columns((8,1,6))
goal_type = left.selectbox("Select Goal", ('Marriage', 'Higher Education','Vacation','Buying a Dream Car','Buying Dream Home','Miscellaneous'),1)
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

gp_flds = st.columns((4,1,4))

goal_amount = right.number_input(f"Cost of {goal_type} (in Today's Price)", value=0,step=10000)
right.markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">({})</p>'.format(display_amount(goal_amount)), unsafe_allow_html=True)

years_to_goal = right.slider("Years to Goal?", min_value=1, max_value=30, step=1, value=3)

present_corpus = right.number_input("Corpus I Already Have", value=0,step=10000)
right.markdown('<p style="font-size:12px;font-weight: bold;text-align:center;vertical-align:middle;color:red;margin:0px;padding:0px">({})</p>'.format(display_amount(present_corpus)), unsafe_allow_html=True)

rate = round(right.number_input("Return on Assets", step=0.10),2)
infl = right.number_input("Inflation", step =0.1)

adj_amount = goal_amount*pow((1+infl/100),years_to_goal)

present_value = adj_amount/pow((1+rate/100),years_to_goal)

tot_mths = 12*years_to_goal

mthly_amt=round(optimize.newton(get_emi, 0, tol=0.0000001, args=(rate, tot_mths,adj_amount,present_corpus)),2)


html_text = '<p style="font-family:Courier; color:Blue; font-size: 18px;">Onetime Investment Required: ' + " {}</p>".format(display_amount(present_value - present_corpus))

left.markdown(html_text, unsafe_allow_html=True)
html_text = '<p style="font-family:Courier; color:Blue; font-size: 18px;">Monthly SIP Required: ' + " {}</p>".format(display_amount(mthly_amt))
left.markdown(html_text, unsafe_allow_html=True)
