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

    .expander > .header > span {
        font-size: 20px;
    }

    .css-z5fcl4 {
    padding-top: 2rem;
    }

    .css-k1ih3n {
    padding-top: 6rem;
    }
}

    </style>

    """,
    unsafe_allow_html=True
)


def loss_set_off(src,dest):
    set_off = src + dest

    if set_off < 0:
        dest = 0.0
        src = set_off
    else:
        src = 0.0
        dest = set_off

    return src, dest


def get_tax_old_regime(income, deductions=0, age=50):

    tax = 0.0
    income = max(income - deductions,0)
    if age < 60:
        income = max(income - 250000,0)
        if income <= 250000:
            return 0.0
        else:
            income = income - 250000
            tax = tax + 12500.0
    elif age >= 60 and age < 80:
        income = max(income - 300000,0)
        if income <= 200000:
            return 0.0
        else:
            income = income - 200000
            tax = tax + 10000.0
    else:
        income = max(income - 500000,0)

    if income < 500000:
        tax = tax + 0.2 * income
    else:
        tax = tax + 100000 + 0.3 * (income - 500000)


    return tax * 1.04


def get_tax_new_regime(income, version='N'):

    tax = 0.0

    if version != 'N':
        if income <= 500000:
            tax = 0.0
        elif income <= 750000:
            tax = tax + 12500 + 0.1 * (income - 500000)
        elif income <= 1000000:
            tax = tax + 37500 + 0.15 * (income - 750000)
        elif income <= 1250000:
            tax = tax + 75000 + 0.2 * (income - 1000000)
        elif income <= 1500000:
            tax = tax + 125000 + 0.25 * (income  - 1250000)
        else:
            tax = tax + 187500 + 0.3 * (income - 1500000)

    else:

        if income <= 700000:
            tax = 0
        elif income <= 900000:
            tax = tax + 15000 + 0.1 * (income - 600000)
        elif income <= 1200000:
            tax = tax + 45000 + 0.15 * (income - 900000)
        elif income <= 1500000:
            tax = tax + 90000 + 0.20 * (income - 1200000)
        else:
            tax = tax + 150000 + 0.30 * (income - 1500000)


    return tax * 1.04


c_1, c_2 = st.columns((8,4))
c_2.image('growealth-logo_long.png')





st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">Tax Calculator</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)

st.markdown('<BR>',unsafe_allow_html=True)
st.markdown(' ',unsafe_allow_html=True)


left, centre, right = st.columns((4,4,4))



name = left.text_input(":blue[Name]",value="John Doe")
curr_age = centre.number_input(":blue[Your Current Age?]", min_value=18, max_value=100, step=1, value=40)

gross_salary = right.number_input(":blue[Gross Salary]", value=1200000,step=100000)

st.markdown('<BR>', unsafe_allow_html=True)

total_tax = 0.0
total_deductions = 0.0

left, centre, right = st.columns((4,4,4))

placeholder_header_1 = left.empty()
placeholder_header_2 = right.empty()

st.markdown('<BR>', unsafe_allow_html=True)
st.markdown('<BR>', unsafe_allow_html=True)

Income_Other_Sources, IT_Deduction = st.tabs(["Income from Other Sources", "Income Tax Deductions"])

#with st.expander("Income from Other Sources"):
with Income_Other_Sources:

    st.markdown('<BR>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    long_equity = col1.number_input("Long Term Equity", value=0)
    short_equity = col2.number_input("Short Term Equity", value=0)

    long_debt = col1.number_input("Long Term Debt", value=0)
    short_debt = col2.number_input("Short Term Debt", value=0)

    if short_debt < 0:
        if long_debt > 0:
            short_debt, long_debt = loss_set_off(short_debt, long_debt)

    if short_debt < 0:
        if short_equity > 0:
            short_debt, short_equity = loss_set_off(short_debt, short_equity)

    if short_debt < 0:
        if long_equity > 0:
            short_debt, long_equity = loss_set_off(short_debt, long_equity)



    saving_bank_interest = col1.number_input("Savings Bank Interest", value=0)
    net_sav_bnk_int = max((saving_bank_interest-10000.0),0.0)

    rental_income = col2.number_input("Rental Income", value=0)

    net_rental_income = 0.7 * rental_income

    business_income = col1.number_input("Business Income (Loss)", value=0)
    col2.markdown('<BR>', unsafe_allow_html=True)
    col2.markdown(' ', unsafe_allow_html=True)

    net_businiess_income = business_income
    presumptive = col2.checkbox("Presumptive Taxation on Business Income?")

    if presumptive:
        total_turnover = col1.number_input("Business Turnover", value=0)
        col2.markdown('<BR>', unsafe_allow_html=True)
        col2.markdown(' ', unsafe_allow_html=True)
        is_online = col2.checkbox("Online Transactions?", value=True)

        if is_online:
            net_businiess_income = 0.06 * total_turnover
        else:
            net_businiess_income = 0.08 * total_turnover

#with st.expander("Deductions"):
with IT_Deduction:
    st.markdown('<BR>', unsafe_allow_html=True)

    col1, col2= st.columns((4,6))

    ded_80C = col1.number_input("Sec 80C - Deductions", value=0)

    col2.markdown('<BR>', unsafe_allow_html=True)
    col2.markdown(' ', unsafe_allow_html=True)

    col2.markdown(":blue[(Includes PF, PPF, NSC, ELSS, Principal Repayment on Home Loan, etc)]")

    max_80C_deductions = min(ded_80C, 150000.00)
    col1, col2, col3= st.columns((4,4,2))

    ded_80G_Self = col1.number_input("Sec 80D - Medical Insurance for Self", value=0)
    ded_80G_parent = col2.number_input("Sec 80D - Medical Insurance for Parents", value=0)
    col3.markdown('<BR>', unsafe_allow_html=True)
    col3.markdown(' ', unsafe_allow_html=True)

    age_chk = col3.checkbox("Parent Age over 60?", value=True)

    if curr_age < 60:
        max_80G_self = min(ded_80G_Self, 25000.00)
    else:
        max_80G_self = min(ded_80G_Self, 50000.00)

    if age_chk:
        max_80G_parent = min(ded_80G_parent, 50000.00)
    else:
        max_80G_parent = min(ded_80G_parent, 25000.00)

    max_80G = max_80G_self + max_80G_parent



    int_home_loan = col1.number_input("Sec 24(b) - Interest on Home Loan", value=0)
    ded_nps = col2.number_input("Sec 80CCD - National Pension Scheme (NPS) Contributions", value=0)

    max_nps_ded = min(ded_nps,50000.00)
    max_home_int = min(200000.00,int_home_loan)

    st.markdown('<BR>', unsafe_allow_html=True)

    hra_claim = st.checkbox("Claim HRA Deduction?")

    hra_deduction = 0.0

    if hra_claim:
        col1, col2 = st.columns((4,4))

        hra_received = col1.number_input("HRA Received", value=0)
        rent_paid = col2.number_input("Actual Rent Paid", value=0)

        basic_da_sal = col1.number_input("Total - Basic Salary & DA", value=0)

        col2.markdown('<BR>', unsafe_allow_html=True)
        col2.markdown(' ', unsafe_allow_html=True)

        is_metro = col2.checkbox("Metro?", value=True)

        if is_metro:
            hra_deduction = min(hra_received,rent_paid,0.5 * basic_da_sal )
        else:
            hra_deduction = min(hra_received,rent_paid,0.4 * basic_da_sal )

total_deductions = max_80C_deductions + max_80G + max_nps_ded + max_home_int + hra_deduction

#st.write("Total Deductions {} - {} - {} - {} ".format(total_deductions,hra_deduction,max_80G_self,max_80G_parent))

tot_other_income = net_businiess_income + net_rental_income + net_sav_bnk_int
#st.write("Total Income {} - {}-{}".format(net_businiess_income,net_rental_income,saving_bank_interest))

#st.write("Total Income {} - {} - {} - {} - {} - {}".format(tot_other_income,net_rental_income,short_debt,long_debt,short_equity, long_equity))

if tot_other_income < 0:
    if short_debt > 0:
        tot_other_income, short_debt = loss_set_off(tot_other_income, short_debt)

#st.write("Total Income {} - {}".format(tot_other_income,short_debt))

if tot_other_income < 0:
    if long_debt > 0:
        tot_other_income, long_debt = loss_set_off(tot_other_income, long_debt)

#st.write("Total Income {} - {}".format(tot_other_income,long_debt))


if tot_other_income < 0:
    if short_equity > 0:
        tot_other_income, short_equity = loss_set_off(tot_other_income, short_equity)
#st.write("Total Income {} - {}".format(tot_other_income,short_equity))


if tot_other_income < 0:
    if long_equity > 0:
        tot_other_income, long_equity = loss_set_off(tot_other_income, long_equity)

#st.write("Total Income: {} Short Debt: {} - Long Debt: {} STCG: {} LTCG: {}".format(tot_other_income,short_debt,long_debt,short_equity, long_equity))

std_deduction = 50000.0
total_income = tot_other_income + gross_salary + long_debt + short_debt
total_income = max(total_income - std_deduction,0)
slab_0_new = 700000.0 + max_nps_ded
slab_0_old = 500000.0 + total_deductions

ltcg_taxrate = 0.1
stcg_taxrate = 0.15

tick_emoji = "\u2705"

new_regime_tax = get_tax_new_regime(total_income - max_nps_ded)
old_regime_tax = get_tax_old_regime(total_income, total_deductions, curr_age )


if total_income  > slab_0_new:
    spl_rate_tax = max(long_equity - 100000.0,0) * ltcg_taxrate + short_equity * stcg_taxrate
else:

    if total_income + long_equity - slab_0_new < 0:
        if total_income + long_equity + short_equity - slab_0_new < 0:
            spl_rate_tax = 0.0
        else:
            spl_rate_tax = stcg_taxrate * (total_income + long_equity + short_equity - slab_0_new)
    else:
        long_equity = total_income + long_equity - slab_0_new
        spl_rate_tax = max(total_income + long_equity - slab_0_new - 100000.0,0) * ltcg_taxrate + short_equity * stcg_taxrate



tot_new_regime_tax = new_regime_tax + spl_rate_tax

if total_income  > slab_0_old:
    spl_rate_tax = max(long_equity - 100000.0,0) * ltcg_taxrate + short_equity * stcg_taxrate
else:

    if total_income + long_equity - slab_0_old < 0:
        if total_income + long_equity + short_equity - slab_0_old < 0:
            spl_rate_tax = 0.0
        else:
            spl_rate_tax = stcg_taxrate * (total_income + long_equity + short_equity - slab_0_old)
    else:
        long_equity = total_income + long_equity - slab_0_old
        spl_rate_tax = max(total_income + long_equity - slab_0_new - 100000.0,0) * ltcg_taxrate + short_equity * stcg_taxrate


tot_old_regime_tax = old_regime_tax + spl_rate_tax


if tot_old_regime_tax < tot_new_regime_tax:
    placeholder_header_1.markdown("**:blue[Old Regime Tax Outstanding:]**  :blue[{}] :green[{}]".format(display_amount(tot_old_regime_tax),tick_emoji))
    placeholder_header_2.markdown("**:blue[New Regime Tax Outstanding:]**  :blue[{}]".format(display_amount(tot_new_regime_tax)))
else:
    placeholder_header_1.markdown("**:blue[Old Regime Tax Outstanding:]**  :blue[{}] ".format(display_amount(tot_old_regime_tax)))
    placeholder_header_2.markdown("**:blue[New Regime Tax Outstanding:]**  :blue[{}] :green[{}]".format(display_amount(tot_new_regime_tax),tick_emoji))


disclaimer_text_1 = "This tax calculator provides an estimate based on the information provided and current tax laws. It is not a substitute for professional financial advice."
disclaimer_text_2 = " Please consult with a qualified tax advisor for accurate and personalized tax guidance. This Tax Calculator is still work-in-progress, we do not guarantee the accuracy or completeness of the results."

notice_txt = '<p><BR><BR><BR><BR><span style="font-family: Verdana, Geneva, sans-serif; font-size: 10px;">'
notice_txt = notice_txt + '<span style="color: rgb(255,0,20);"><strong>Disclaimer: </strong></span><span style="color: rgb(20,20,255);">{}</span>'.format(disclaimer_text_1)
notice_txt = notice_txt + '<span style="color: rgb(20,20,255);">{}</span>'.format(disclaimer_text_2)
st.markdown(notice_txt,unsafe_allow_html=True)
