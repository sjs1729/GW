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
import matplotlib.pyplot as plt



def get_emi(emi, rate, nperiods,target_amt,present_corpus):
    tot_val = present_corpus * pow((1+ rate/100),nperiods/12)
    for per in range(nperiods):
        tot_val = tot_val + emi * pow((1+ rate/1200),nperiods - per)

    return tot_val - target_amt

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
years_to_goal = right.slider("Years to Goal?", min_value=1, max_value=30, step=1, value=3)

present_corpus = right.number_input("Corpus I Already Have", value=0,step=10000)

rate = round(right.number_input("Return on Assets", step=0.10),2)
infl = right.number_input("Inflation", step =0.1)

adj_amount = goal_amount*pow((1+infl/100),years_to_goal)

present_value = adj_amount/pow((1+rate/100),years_to_goal)

tot_mths = 12*years_to_goal

mthly_amt=round(optimize.newton(get_emi, 0, tol=0.0000001, args=(rate, tot_mths,adj_amount,present_corpus)),2)


html_text = '<p style="font-family:Courier; color:Blue; font-size: 18px;">Onetime Investment Required: ' + "Rs. {:,.2f}</p>".format(present_value - present_corpus)

left.markdown(html_text, unsafe_allow_html=True)
html_text = '<p style="font-family:Courier; color:Blue; font-size: 18px;">Monthly SIP Required: ' + "Rs. {:,.2f}</p>".format(mthly_amt)
left.markdown(html_text, unsafe_allow_html=True)
