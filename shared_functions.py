import pandas as pd
import streamlit as st
from fpdf import FPDF
from scipy import optimize
import tempfile
import io
import uuid
import os
from io import BytesIO
import math
import datetime as dt
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen
import json

tday = dt.datetime.today()

cols=['SCHEMES', 'FUND_HOUSE', 'AUM', 'LAUNCH DATE', '1_DAY_RETURN', '7_DAY_RETURN',
       '15_DAY_RETURN', '30_DAY_RETURN', '3_MONTH_RETURN', '6_MONTH_RETURN', '1_YEAR_RETURN',
       '2_YEAR_RETURN', '3_YEAR_RETURN','5_YEAR_RETURN', '7_YEAR_RETURN', '10_YEAR_RETURN',
       '15_YEAR_RETURN', '20_YEAR_RETURN', '25_YEAR_RETURN','SINCE_INCEPTION_RETURN',
       'FUND_RATING', 'CATEGORY', 'CURRENT NAV', 'ALPHA', 'BETA', 'MEAN', 'VOLATILITY',
       'SHARPE', 'SORTINO','FUND MANAGER', 'AVG_MATURITY', 'MODIFIED_DURATION', 'YTM',
       'PURCHASE MIN AMOUNT', 'SIP MIN AMOUNT', 'LARGE_CAP', 'MID_CAP',
       'SMALL_CAP', 'PRICE_TO_BOOK', 'PRICE_TO_EARNINGS', 'EXIT_LOAD', 'EQUITY_PCT',
       'DEBT_PCT', 'GOLD_PCT', 'GLOBAL_EQUITY_PCT', 'OTHER_PCT', 'RSQUARED',
       'EXPENSE', 'SOV_RATED_DEBT', 'A_RATED_DEBT', 'AA_RATED_DEBT', 'AAA_RATED_DEBT',
       'BIG', 'CASH','DOWNSIDE_DEVIATION', 'DOWNSIDE_PROBABILITY']



@st.cache_data()
def get_mf_perf():
    df = pd.read_csv('MINT_Scheme_Data.csv')
    df.columns = cols
    df.set_index("SCHEMES", inplace=True)

    df_mapping = pd.read_csv("MINT_AMFI_MAPPING.csv")
    df_mapping = df_mapping[df_mapping['AMFI_CODE'].notna()]
    df_mapping.set_index("MINT_SCHEME", inplace=True)

    df_mapping=df_mapping[['AMFI_CODE','AMFI_SCHEME']]
    df_mapping['AMFI_CODE']=df_mapping['AMFI_CODE'].apply(lambda x: int(x))
    df_mapping = df_mapping[df_mapping['AMFI_CODE'].notna()]


    for j in df_mapping.index:
        amfi_code = df_mapping.loc[j,'AMFI_CODE']
        df.at[j,'AMFI_CODE'] = amfi_code

    df.reset_index(inplace=True)
    df = df[(df['AMFI_CODE'].notna())]
    df = df[ (df['FUND_HOUSE'].notna())]
    df.set_index("AMFI_CODE", inplace=True)

    df['SCHEME_TYPE'] = df['CATEGORY'].apply(lambda x: x.split(":")[0].strip())
    df['SCHEME_CATEGORY'] = df['CATEGORY'].apply(lambda x: x.split(":")[1].strip())

    df['LAUNCH DATE'] = pd.to_datetime(df['LAUNCH DATE'],dayfirst=False)
    df['AGE'] = df['LAUNCH DATE'].apply(lambda x: (tday - x).days)

    #st.write(df_mapping.dtypes)

    return df

@st.cache_data()
def get_historical_nav(amfi_code,tdate):
    try:
        success = 'N'
        url = 'https://api.mfapi.in/mf/{}'.format(amfi_code)
        response = urlopen(url)
        result = json.loads(response.read())
        data = result['data']
        nav_list = []
        for rec in reversed(data):
            dt_rec = dt.datetime.strptime(rec['date'], '%d-%m-%Y').date()
            nav = float(rec['nav'])
            values = dt_rec, nav
            nav_list.append(values)

        df_mf = pd.DataFrame(nav_list,columns=['Date','Nav'])

        df_mf.set_index('Date',inplace=True)

    except:
        result='{}'.format(success)
        st.warning("AMFI NAV Data not accessible, try after sometime")
        st.stop()
        return result

    return df_mf


def display_amount(amount, paisa='N'):

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
            amt_str = amt_str + str(cr_amt) + ",00,00,000.00"
    elif lkh_amt > 0:
        if lkh_bal > 0:
            amt_str = amt_str + str(lkh_amt) + "," + str(th_amt).rjust(2,'0') + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
        else:
            amt_str = amt_str + str(lkh_amt) + ",00,000.00"
    elif th_amt > 0:
        amt_str = amt_str + str(th_amt) + "," + str(th_bal).rjust(3,'0') + "." + decimal_part
    else:
        amt_str = amt_str + str(th_bal) + "." + decimal_part

    if paisa == 'N':
        amt_str = amt_str.split(".")[0]

    return amt_str

def get_markdown_table_highlighted_row(data, highlight_index, header='Y', footer='Y'):


    if header == 'Y':

        cols = data.columns
        ncols = len(cols)
        if ncols < 5:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        elif ncols < 7:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:12px'>"
        else:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:10px'>"


        for i in cols:
            if 'Fund' in i or 'Name' in i:
                html_script = html_script + "<th style='text-align:left'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:

        if j == highlight_index:
            if ncols < 5:
                html_script = html_script + "<tr style='border:none;font-family:Courier; color:Red; font-size:12px;padding:1px;';>"
            elif ncols < 7:
                html_script = html_script + "<tr style='border:none;font-family:Courier; color:Red; font-size:11px;padding:1px;';>"
            else:
                html_script = html_script + "<tr style='border:none;font-family:Courier; color:Red; font-size:9px;font-weight:bold;padding:1px;';>"
        else:
            if ncols < 5:
                html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"
            elif ncols < 7:
                html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:11px;padding:1px;';>"
            else:
                html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:9px;padding:1px;';>"


        a = data.loc[j]
        for k in cols:
            if 'Fund' in k or 'Name' in k:
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'>{}</td>".format(a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script


def get_markdown_table(data, header='Y', footer='Y'):


    if header == 'Y':

        cols = data.columns
        ncols = len(cols)
        if ncols < 5:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:14px'>"
        elif ncols < 7:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:12px'>"
        else:
            html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:10px'>"


        for i in cols:
            if 'Fund' in i or 'Name' in i:
                html_script = html_script + "<th style='text-align:left'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center''>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        if ncols < 5:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:12px;padding:1px;';>"
        elif ncols < 7:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:11px;padding:1px;';>"
        else:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:9px;padding:1px;';>"

        a = data.loc[j]
        for k in cols:
            if 'Fund' in k or 'Name' in k:
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'>{}</td>".format(a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])

    html_script = html_script + '</tbody></table>'

    return html_script


def get_markdown_col_fields(field_label, field_value, format_amt = 'N'):
    markdown_txt = '<p><span style="font-family: Verdana, Geneva, sans-serif; font-size: 12px;">'
    markdown_txt = markdown_txt + '<span style="color: rgb(20,20,255);"><strong>{}: </strong></span>'.format(field_label)
    if format_amt == 'Y':
        markdown_txt = markdown_txt + '<span style="color: rgb(0,0,0);">{}</span>'.format(display_amount(field_value))
    else:
        markdown_txt = markdown_txt + '<span style="color: rgb(0,0,0);">{}</span>'.format(field_value)

    return markdown_txt


def get_markdown_dict(dict, font_size = 10, format_amt = 'N'):


    html_script = "<table><style> table {border-collapse: collapse;width: 100%; border: 1px solid #ddd;}th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>"

    #html_script = html_script +  "<table><style> th {background-color: #ffebcc;padding:0px;} td {font-size='5px;text-align:center;padding:0px;'}tr:nth-child(even) {background-color: #f2f2f2;}</style><thead><tr style='width:100%;border:none;font-family:Courier; color:Red; font-size:15px'>"

    for j in dict.keys():

        if dict[j] == dict[j]:
            html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:{}px;padding:1px;';>".format(font_size)
            html_script = html_script + "<td style='border:none;padding:2px;font-family:Courier; color:Blue; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size,j)
            if format_amt == 'N':
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:Black; font-size:{}px;text-align:left' rowspan='1'>{}</td>".format(font_size -1,dict[j])
            else:
                html_script = html_script + "<td style='border:none;padding:4px;font-family:Courier; color:Black; font-size:{}px;text-align:right' rowspan='1'>{}</td>".format(font_size -1,display_amount(dict[j]))



    html_script = html_script + '</tbody></table>'

    return html_script


@st.cache_data()
def get_data_refresh_date():
    data = pd.read_csv('mf_data.csv')

    return data['Date'].iloc[-1]


def get_retirement_summary_text(name,ret_score,fund_needed,sip_needed,opt_xirr, years_to_retire, cagr, final_networth):

    ret_text = ''
    ret_advise = []
    if ret_score == 100:
        ret_text = 'Congratulations {}!!! You have a Perfect Retirement Score, and at the end, you will still be left with a surplus of {}.'.format(name, display_amount(final_networth).replace('₹','Rs.'))
        if opt_xirr/cagr <= 0.85:
            ret_text = ret_text + " Enjoy Life, you have earned the freedom to be bit more extravagant"

    elif ret_score >= 95 and ret_score < 100:
        ret_text = 'Congratulations {}, you have planned your Retirement well.'.format(name)
        ret_text = ret_text + 'Your Retirement Score is {}, and you are in Green Zone.'.format(ret_score)
        ret_text = ret_text + ' Although your doing fine, you need to improve your Score to a Perfect 100. Please consult your Financial Advisor.'

        if fund_needed > 0:
            ret_advise.append('1. You have a fund shortfall of {}. Review your Expenses, Goals and Other Income sources.'.format(display_amount(fund_needed).replace('₹','Rs.')))

        if sip_needed > 0 and years_to_retire > 0:
            ret_advise.append('2. You have {} years to retire, you need to save an additional {} monthly.'.format(years_to_retire,display_amount(sip_needed).replace('₹','Rs.')))

        if cagr < opt_xirr:
            ret_advise.append('3. Your corpus is growing at an annual rate of {}%. You can meet your Retirement Targets if you can grow your assets at {}%.'.format(cagr,opt_xirr))


    elif ret_score >= 75 and ret_score < 95:
        ret_text = 'Dear {}, your Retirement Score is {}. You are in Amber Zone. Please consult your Financial Advisor to improve your Retirement Planning.'.format(name, ret_score)

        if fund_needed > 0:
            ret_advise.append('1. You have a fund shortfall of {}. Review your Expenses, Goals and Other Income sources.'.format(display_amount(fund_needed).replace('₹','Rs.')))

        if sip_needed > 0 and years_to_retire > 0:
            ret_advise.append('2. You have {} years to retire, you need to save an additional {} monthly.'.format(years_to_retire,display_amount(sip_needed).replace('₹','Rs.')))

        if cagr < opt_xirr:
            ret_advise.append('3. Your corpus is growing at an annual rate of {}%. You can meet your Retirement Targets if you can grow your assets at {}%.'.format(cagr,opt_xirr))


    else:
        ret_text = 'Dear {}, your Retirement Score is {}. You are in Red Zone and need immediate help. Please consult your Financial Advisor to improve your Retirement Planning.'.format(name, ret_score)

        if fund_needed > 0:
            ret_advise.append('1. You have a fund shortfall of {}. Review your Expenses, Goals and Other Income sources.'.format(display_amount(fund_needed).replace('₹','Rs.')))

        if sip_needed > 0 and years_to_retire > 0:
            ret_advise.append('2. You have {} years to retire, you need to save an additional {} monthly.'.format(years_to_retire,display_amount(sip_needed).replace('₹','Rs.')))

        if cagr < opt_xirr:
            ret_advise.append('3. Your corpus is growing at an annual rate of {}%. You can meet your Retirement Targets if you can grow your assets at {}%.'.format(cagr,opt_xirr))



    return ret_text, ret_advise


#def generate_pdf_report(fig_1, fig_2, retirement_dict, df_goals, df_ret_income, retirement_assets):
def generate_pdf_report( retirement_dict, df_goals, df_ret_income, retirement_assets):


    WIDTH = 297
    HEIGHT = 210
    session_id = str(uuid.uuid4())
    temp_filename = f"file_{session_id}.png"
    report_filenm = f"report_{session_id}.png"
    qr_code_img = 'gw_QR.png'
    Name = retirement_dict['Name']

    Age = retirement_dict['Age']
    RetAge = retirement_dict['RetAge']
    PlanAge = retirement_dict['PlanAge']

    AnnInc =  retirement_dict['AnnInc']
    AnnExp = retirement_dict['AnnExp']
    AnnHikPct = retirement_dict['AnnHikPct']
    ExpCapAge = retirement_dict['ExpCapAge']
    Corpus = retirement_dict['Corpus']
    TermCorp = retirement_dict['TermCorp']
    Cagr = retirement_dict['Cagr']
    Inflation = retirement_dict['Inflation']

    RetScore = retirement_dict['RetScore']
    FundShort = int(retirement_dict['FundShort'])
    SIPNeed = int(retirement_dict['SIPNeed'])
    OptXIRR = retirement_dict['OptXIRR']

    final_networth = retirement_assets.iloc[-1]['Networth'] * 100000



    ret_text, ret_advise = get_retirement_summary_text(Name,RetScore,FundShort,SIPNeed,OptXIRR, RetAge, Cagr, final_networth)


    try:

        # Create a PDF document
        pdf = FPDF('L')
        pdf.add_page()

        pdf.image("gw_header.png",5,3,WIDTH-10,24)
        pdf.image("gw_footer.png",5,HEIGHT-15,WIDTH-10,12)

        pdf.set_font('Arial', 'BU', 12)
        pdf.set_xy(48,30)
        pdf.set_text_color(255,0,0)

        pdf.cell(75,5,'Retirement Score', align='L')
        pdf.image("dial_guage.png", x=10, y=39, w=110)


        line_gap = 5
        start_pos_x = 5
        start_pos_y = 92
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(4,51,255)
        pdf.multi_cell(120,5,ret_text)

        start_pos_y = 120
        pdf.set_xy(start_pos_x,start_pos_y)
        if len(ret_advise) > 0:
            pdf.set_font('Arial', 'BU', 10)
            pdf.cell(75,5,'Few Suggestions to Improve your Retirement Score', align='L')

            pdf.set_font('Arial', '', 7)

            for i in range(len(ret_advise)):
                start_pos_y = start_pos_y + 8
                pdf.set_xy(start_pos_x,start_pos_y)
                advise_text = ret_advise[i]
                pdf.multi_cell(120,5,advise_text)


        pdf.image(qr_code_img, x=80, y=163, w=50)


        pdf.line(135,28,135,195)

        # Basic Heading
        line_gap = 5
        start_pos_x = 140
        start_pos_y = 30
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'BU', 10)
        pdf.set_text_color(255,0,0)
        pdf.cell(35,5,'Basic Retirement Inputs Considered')


        # Age, Retirement Age, Years to Live, Annual Income/Expense, Corpus, Terminal Corpus
        pdf.set_text_color(4,51,255)
        start_pos_y = start_pos_y + line_gap
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Age:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{Age}" , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Years to Retire:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{RetAge}" , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(28, 10, "Plan Till:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{PlanAge}" , align='L')
        #pil_image.save(temp_image.name, format="PNG")

        start_pos_y = start_pos_y + line_gap
        start_pos_x = 140
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Annual Income:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, display_amount(AnnInc).replace('₹','Rs.') , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Annual Expense:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, display_amount(AnnExp).replace('₹','Rs.') , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(28, 10, "Annual Hike:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{round(AnnHikPct,2)} %" , align='L')
        #pil_image.save(temp_image.name, format="PNG")


        start_pos_y = start_pos_y + line_gap
        start_pos_x = 140
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Current Networth:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, display_amount(Corpus).replace('₹','Rs.') , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Networth CAGR:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{Cagr} %" , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(28, 10, f"Residual Networth:", align='L')
        pdf.set_font('Arial', '', 8)
        if TermCorp > 0:
            pdf.cell(10, 10, display_amount(TermCorp).replace('₹','Rs.') , align='L')
        else:
            pdf.cell(10, 10, "  N/A " , align='L')

        #pil_image.save(temp_image.name, format="PNG")

        # Embed the image in the PDF
        start_pos_y = start_pos_y + 2*line_gap
        start_pos_x = 140
        pdf.set_xy(start_pos_x,start_pos_y)

        pdf.set_font('Arial', 'BU', 7)
        pdf.set_text_color(255,0,0)

        pdf.cell(8, 10, "Note:" , align='R')
        pdf.set_font('Arial', '', 7)
        pdf.set_text_color(4,51,255)

        if ExpCapAge < PlanAge:
            pdf.cell(0, 10, f" Annual Inflation considered is {round(Inflation,2)} % and the effect of Inflation stops when Age > {ExpCapAge}" , align='L')
        else:
            pdf.cell(0, 10, f" Annual Inflation considered is {Inflation} %" , align='L')

        start_pos_y = start_pos_y + 3*line_gap
        start_pos_x = 140
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_fill_color(170,190,230)

        if len(df_goals) > 0:
            pdf.set_font('Arial', 'BU', 7)
            pdf.set_text_color(255,0,0)

            pdf.cell(30, 10, "Other Expenses (Life Goals):" , align='L')
            pdf.set_font('Arial', '', 5)
            pdf.set_text_color(4,51,255)

            start_pos_y = start_pos_y + 1.5 * line_gap
            start_pos_x = 140
            pdf.set_xy(start_pos_x,start_pos_y)

            line_height = 5
            pdf.cell(8,line_height,"Goal#",border=1,fill=True, align='C')
            pdf.cell(15,line_height,"Start Age",border=1,fill=True, align='C')
            pdf.cell(15,line_height,"End Age",border=1,fill=True, align='C')
            pdf.cell(55,line_height,"Description",border=1,fill=True, align='C')
            pdf.cell(20,line_height,"Amount",border=1,fill=True, align='C')
            pdf.cell(20,line_height,"Frequency",border=1,fill=True, align='C')
            pdf.cell(15,line_height,"Inflation %",border=1,fill=True, align='C')

            pdf.set_font('Arial', '', 5)

            for j in df_goals.index:

                start_pos_y = start_pos_y + line_gap
                start_pos_x = 140
                pdf.set_xy(start_pos_x,start_pos_y)

                freq = df_goals.loc[j,'Frequency']
                freq_text = "One Time"
                infl = round(df_goals.loc[j,'Inflation_Pct'],2)
                pdf.cell(8,line_height,f"{j+1}",border=1, align='C')

                if freq > 0:
                    freq_text = "Once in {} years".format(freq)
                pdf.cell(15,line_height,f"{df_goals.loc[j,'Start_Age']}",border=1, align='C')
                if freq > 0:
                    pdf.cell(15,line_height,f"{df_goals.loc[j,'End_Age']}",border=1, align='C')
                else:
                    pdf.cell(15,line_height,"--",border=1, align='C')

                pdf.cell(55,line_height,f"{df_goals.loc[j,'Desc']}",border=1, align='C')
                pdf.cell(20,line_height,display_amount(df_goals.loc[j,'Amount']).replace('₹','Rs.'),border=1, align='C')
                pdf.cell(20,line_height,f"{freq_text}",border=1, align='C')
                pdf.cell(15,line_height,f"{str(infl)}",border=1, align='C')


        start_pos_y = start_pos_y + 3*line_gap
        start_pos_x = 140
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_fill_color(170,190,230)

        if len(df_ret_income) > 0:
            pdf.set_font('Arial', 'BU', 7)
            pdf.set_text_color(255,0,0)

            pdf.cell(30, 10, "Other Income Streams:" , align='L')
            pdf.set_font('Arial', '', 5)
            pdf.set_text_color(4,51,255)

            start_pos_y = start_pos_y + 1.5 * line_gap
            start_pos_x = 140
            pdf.set_xy(start_pos_x,start_pos_y)

            line_height = 5
            pdf.cell(8,line_height,"Income#",border=1,fill=True, align='C')
            pdf.cell(15,line_height,"Start Age",border=1,fill=True, align='C')
            pdf.cell(15,line_height,"End Age",border=1,fill=True, align='C')
            pdf.cell(55,line_height,"Description",border=1,fill=True, align='C')
            pdf.cell(20,line_height,"Amount",border=1,fill=True, align='C')
            pdf.cell(20,line_height,"Frequency",border=1,fill=True, align='C')
            pdf.cell(15,line_height,"Increment %",border=1,fill=True, align='C')

            pdf.set_font('Arial', '', 5)

            for j in df_ret_income.index:

                start_pos_y = start_pos_y + line_gap
                start_pos_x = 140
                pdf.set_xy(start_pos_x,start_pos_y)

                freq = df_ret_income.loc[j,'Frequency']
                freq_text = "One Time"
                incr_pct = round(df_ret_income.loc[j,'Increment_Pct'],2)
                pdf.cell(8,line_height,f"{j+1}",border=1, align='C')

                if freq > 0:
                    freq_text = "Once in {} years".format(freq)
                pdf.cell(15,line_height,f"{df_ret_income.loc[j,'Start_Age']}",border=1, align='C')
                if freq > 0:
                    pdf.cell(15,line_height,f"{df_ret_income.loc[j,'End_Age']}",border=1, align='C')
                else:
                    pdf.cell(15,line_height," --",border=1, align='C')

                pdf.cell(55,line_height,f"{df_ret_income.loc[j,'Desc']}",border=1, align='C')
                pdf.cell(20,line_height,display_amount(df_ret_income.loc[j,'Amount']).replace('₹','Rs.'),border=1, align='C')


                pdf.cell(20,line_height,f"{freq_text}",border=1, align='C')
                pdf.cell(15,line_height,f"{str(incr_pct)}",border=1, align='C')


        pdf.set_line_width(1)
        #pdf.line(65,83,65,45)

        theta = 180 - (180.0 * RetScore/100.0)
        if theta < 1:
            theta = 1
        elif theta > 179:
            theta = 179

        arrow_height = 38.5
        arrow_x0 = 66
        arrow_y0 = 82.5
        cos_theta = math.cos(math.radians(theta))
        sin_theta = math.sin(math.radians(theta))
        x2 = arrow_x0 + arrow_height * cos_theta
        y2 = arrow_y0 - arrow_height * sin_theta
        #st.write(theta,cos_theta, sin_theta,x2,y2)
        pdf.line(arrow_x0,arrow_y0,x2,y2)

        theta_1 = theta - 1
        theta_2 = theta + 1

        r_1 = 0.95 * arrow_height
        ax_1 = arrow_x0 + r_1 * math.cos(math.radians(theta_1))
        ax_2 = arrow_x0 + r_1 * math.cos(math.radians(theta_2))
        ay_1 = arrow_y0 - r_1 * math.sin(math.radians(theta_1))
        ay_2 = arrow_y0 - r_1 * math.sin(math.radians(theta_2))

        pdf.line(ax_1,ay_1,x2,y2)
        pdf.line(ax_2,ay_2,x2,y2)

        pdf.set_line_width(0.2)
        pdf.ellipse(arrow_x0 - 1,arrow_y0 - 1,2,2)

        if RetScore > 95:
            pdf.set_text_color(0, 255, 25)
        elif RetScore > 75:
            pdf.set_text_color(255, 150, 0)
        else:
            pdf.set_text_color(255, 0, 25)

        pdf.set_font('Arial', 'B', 55)



        if theta < 75 or theta > 105:
            if RetScore == 100:
                pdf.text(50 ,74,str(int(RetScore)) )
            else:
                pdf.text(56,74,str(int(RetScore)) )

        elif theta > 75 and theta < 90:
            pdf.text(56,74,str(int(RetScore)) )
        elif theta > 90 and theta < 105:
            pdf.text(56,74,str(int(RetScore)) )



        pdf.add_page()
        pdf.image("gw_header.png",5,3,WIDTH-10,24)
        pdf.image("gw_footer.png",5,HEIGHT-15,WIDTH-10,12)

        nBars = len(retirement_assets)
        chart_x0 = 25
        chart_y0 = 180
        chart_width = 262
        chart_height = 125
        bar_gap = 1
        bar_width = (chart_width - bar_gap * nBars )/nBars

        pdf.set_text_color(4,51,255)


        #pdf.rect(chart_x0, chart_y0 - chart_height , chart_width, chart_height )
        if RetScore > 0:
            pos_max = retirement_assets[retirement_assets['Networth'] > 0]['Networth'].max()
        else:
            pos_max = 0

        if RetScore < 100:
            neg_max = abs(retirement_assets[retirement_assets['Networth'] < 0]['Networth'].min())
        else:
            neg_max = 0

        if neg_max == 0:
            x_axis_pos = 180
        elif pos_max == 0:
            x_axis_pos = 50
        else:
            x_axis_pos = chart_y0 - chart_height * neg_max / (pos_max + neg_max)


        #st.write(nBars,bar_width,pos_max,neg_max,(pos_max + neg_max)/6,y_interval)
        #pdf.line(chart_x0, x_axis_pos, chart_x0 + chart_width, x_axis_pos)

        pdf.line(chart_x0, chart_y0,chart_x0,chart_y0 - chart_height)


        for i in retirement_assets.index:
            age_x = retirement_assets.loc[i,'Age']
            networth_y = retirement_assets.loc[i,'Networth']

            bar_i_x = chart_x0 + i * (bar_gap + bar_width) - bar_width/2.0

            bar_height_x = chart_height * (networth_y/ (pos_max + neg_max))
            if networth_y > 0:
                pdf.set_fill_color(0,150,80)
                pdf.rect(bar_i_x,x_axis_pos - bar_height_x,bar_width,bar_height_x, style='FD')
            else:
                pdf.set_fill_color(255,0,0)
                pdf.rect(bar_i_x,x_axis_pos,bar_width,abs(bar_height_x), style='FD')

            if age_x % 10 == 0:
                pdf.dashed_line(bar_i_x + bar_width/2.0,chart_y0,bar_i_x + bar_width/2.0,chart_y0 - chart_height)
                pdf.set_font('Arial', '', 7)
                #pdf.set_text_color(0, 0, 255)
                pdf.text(bar_i_x,chart_y0 +5,str(age_x) )



        #st.write(retirement_assets)

        pdf.set_font('Arial', 'B', 10)
        #pdf.set_text_color(0, 0, 255)
        pdf.text(chart_x0 + 0.43 * chart_width,chart_y0 +10,"Age ( in Year )" )

        y_interval = int(int(((pos_max + neg_max)/6.0)/25.0) * 25)

        pdf.set_font('Arial', '', 7)

        tick = 0
        while tick < pos_max:
            tick_interval = chart_height * (tick / (pos_max + neg_max))
            pdf.dashed_line(chart_x0,x_axis_pos - tick_interval,bar_i_x + 2*bar_width,x_axis_pos - tick_interval)
            pdf.text(chart_x0 - 6,x_axis_pos - tick_interval,str(tick) )
            tick = tick + y_interval

        tick = 0
        while tick > -1 * neg_max:
            tick_interval = chart_height * (tick / (pos_max + neg_max))
            pdf.dashed_line(chart_x0,x_axis_pos - tick_interval,bar_i_x + 2*bar_width,x_axis_pos - tick_interval)
            pdf.text(chart_x0 - 6,x_axis_pos - tick_interval,str(tick) )
            tick = tick - y_interval

        pdf.line(chart_x0, x_axis_pos, bar_i_x + 2*bar_width, x_axis_pos)

        #fig_2.write_image(report_filenm)
        #pdf.image(report_filenm, x=12, y=25,w=280,h=165)

        #if os.path.exists(report_filenm):
        #    os.remove(report_filenm)

        pdf.set_text_color(255,25,25)
        pdf.set_font('Arial', 'BU', 20)
        pdf.text(chart_x0 + 0.38 * chart_width, chart_y0 - chart_height - 12, "Retirement Corpus by Age" )


        pdf.image("y_axis_label.png",chart_x0 - 20,chart_y0 - 0.75 * chart_height,8,53 )


    except Exception as e:
        st.write(e)

        #if os.path.exists(report_filenm):
        #    os.remove(report_filenm)




    # Save the PDF to a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)

    pdf_bytes = open(temp_pdf.name, 'rb').read()


    return pdf_bytes

def get_color_code(value):
    """
    Returns a hex color code based on the input value.

    Parameters:
    value (float): Input value.

    Returns:
    str: Hex color code.
    """
    if 0 <= value <= 0.25:
        return "#ADE5A4"  # Amber
    elif 0.25 < value <= 1:
        return "#85D476"  # Light Green
    elif value > 1:
        return "#66C84D"  # Dark Green
    elif 0 > value >= -0.25:
        return "#EE8A87"  # Light Red
    elif -0.25 > value >= -1:
        return "#EB6660"  # Dark Red
    elif value < -1:
        return "#E93425"

def get_recent_ret_calendar_display(df):


    day0_value = "#FFFFFF"
    day1_value = "#FFFFFF"
    day2_value = "#FFFFFF"
    day3_value = "#FFFFFF"
    day4_value = "#FFFFFF"
    week_no = 0

    last_indx = df.index[-1]

    rec = []
    flag = ""
    for i in df.index:
        week_day = df.loc[i,'Day']
        day_change = round(df.loc[i,'DailyChg'],2)



        if week_day == 0:
            day0_value = get_color_code(day_change)
            flag = f"{flag}{week_day}"

        elif week_day == 1:
            day1_value = get_color_code(day_change)
            flag = f"{flag}{week_day}"

        elif week_day == 2:
            day2_value = get_color_code(day_change)
            flag = f"{flag}{week_day}"

        elif week_day == 3:
            day3_value = get_color_code(day_change)
            flag = f"{flag}{week_day}"

        elif week_day == 4 :
            day4_value = get_color_code(day_change)
            flag = f"{flag}{week_day}"

            if week_no == 0:
                if flag[0] == '1':
                    if day2_value == "#FFFFFF":
                        day2_value = "#D6D6D6"
                    elif day3_value == "#FFFFFF":
                        day3_value = "#D6D6D6"
                    elif day4_value == "#FFFFFF":
                        day4_value = "#D6D6D6"
                elif flag[0] == '2':
                    if day3_value == "#FFFFFF":
                        day3_value = "#D6D6D6"
                    elif day4_value == "#FFFFFF":
                        day4_value = "#D6D6D6"
                elif flag[0] == '3':
                    if day4_value == "#FFFFFF":
                        day4_value = "#D6D6D6"


            values = week_no, day0_value, day1_value, day2_value, day3_value, day4_value
            rec.append(values)
            week_no += 1
            flag=""

            day0_value = "#D6D6D6"
            day1_value = "#D6D6D6"
            day2_value = "#D6D6D6"
            day3_value = "#D6D6D6"
            day4_value = "#D6D6D6"

        if i == last_indx and week_day != 4:

            if flag[-1] == '0':
                values = week_no, day0_value, "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"
            elif flag[-1] == '1':
                values = week_no, day0_value, day1_value , "#FFFFFF", "#FFFFFF", "#FFFFFF"
            elif flag[-1] == '2':
                values = week_no, day0_value, day1_value , day2_value, "#FFFFFF", "#FFFFFF"
            elif flag[-1] == '3':
                values = week_no, day0_value, day1_value , day2_value, day3_value, "#FFFFFF"

            rec.append(values)








    df_mf_cal = pd.DataFrame(rec, columns=['Week','Mon','Tue','Wed','Thu','Fri'])
    df_mf_cal.set_index('Week',inplace=True)

    html_script = "<table style='border-collapse: collapse; width:80%;margin:0'><tbody>"

    for j in df_mf_cal.index:

        html_script = html_script + "<tr style='border:1px;font-family:Courier; font-size:9px;padding:0px;margin:0';>"

        a = df_mf_cal.loc[j]
        for k in df_mf_cal.columns:

            html_script = html_script + "<td style='border:2px solid #fff;border-radius:10%;width:3px;height:3px;line-height:3;margin:5px;color:{};text-align:center;background-color:{}' rowspan='1'> A </td>".format(a[k],a[k])

    html_script = html_script + '</tbody></table>'

    return html_script


def calculate_cagr(initial_investment, current_value, nyears):

    abs_ret = round(100 * (current_value - initial_investment)/initial_investment,2)
    cagr = round((((current_value/initial_investment) ** (1/nyears)) - 1) * 100, 2)

    return abs_ret, cagr

def get_lumpsum_inv_ret(df, investment_amount):

    current_date = dt.date.today()
    incep_date = df.index[0]
    fund_age = (current_date - incep_date).days/365.0

    one_year_ago = current_date - relativedelta(months=12)
    three_years_ago = current_date - relativedelta(months=36)
    five_years_ago = current_date - relativedelta(months=60)
    ten_years_ago = current_date - relativedelta(months=120)

    rec = []

    if one_year_ago > incep_date:
        period = 1
        df_1 = df[df.index >= one_year_ago]
        current_val = investment_amount * df_1['Nav'].iloc[-1]/df_1['Nav'].iloc[0]
        abs_ret, cagr = calculate_cagr(investment_amount, current_val, period)

        values = "1 Year", one_year_ago, display_amount(current_val), abs_ret, cagr
        rec.append(values)

    if three_years_ago > incep_date:
        period = 3
        df_3 = df[df.index >= three_years_ago]

        current_val = investment_amount * df_3['Nav'].iloc[-1]/df_3['Nav'].iloc[0]
        abs_ret, cagr = calculate_cagr(investment_amount, current_val, period)

        values = "3 Year", three_years_ago, display_amount(current_val), abs_ret, cagr
        rec.append(values)

    if five_years_ago > incep_date:
        period = 5
        df_5 = df[df.index >= five_years_ago]

        current_val = investment_amount * df_5['Nav'].iloc[-1]/df_5['Nav'].iloc[0]
        abs_ret, cagr = calculate_cagr(investment_amount, current_val, period)

        values = "5 Year", five_years_ago, display_amount(current_val), abs_ret, cagr
        rec.append(values)

    if ten_years_ago > incep_date:
        period = 10
        df_10 = df[df.index >= ten_years_ago]

        current_val = investment_amount * df_10['Nav'].iloc[-1]/df_10['Nav'].iloc[0]
        abs_ret, cagr = calculate_cagr(investment_amount, current_val, period)

        values = "10 Year", ten_years_ago, display_amount(current_val), abs_ret, cagr
        rec.append(values)



    current_val = investment_amount * df['Nav'].iloc[-1]/df['Nav'].iloc[0]
    abs_ret, cagr = calculate_cagr(investment_amount, current_val, fund_age)

    values = "Since Inception", incep_date, display_amount(current_val), abs_ret, cagr
    rec.append(values)

    df_cagr = pd.DataFrame(rec, columns=['Period Invested for',f"{display_amount(investment_amount)} Invested on","Latest Value","Absolute Returns %","Annualised Returns %"])

    return df_cagr

def xirr(rate,cash_flow,terminal_value=0):

    npv = 0
    for i in cash_flow.index:
        nYears = cash_flow.loc[i,'Num_Days']/365
        pv = cash_flow.loc[i,'SIP_Value']*(pow((1 + rate / 100), nYears))
        npv = npv + pv

    return  npv+terminal_value

def get_sip_cashflow(df,sip_investment):

    current_date = dt.date.today()
    curr_nav = df['Nav'].iloc[-1]
    total_units = 0.0
    n_sip = 0

    total_investment = 0
    df['SIP_Value'] = 0
    for i in df.index:
        if n_sip % 21 == 0:
            sip_date = i
            nav = df.loc[i,'Nav']
            sip_units = sip_investment / nav
            total_units  += sip_units
            df.at[i,'SIP_Value'] = -1 * sip_investment
            df.at[i,'Num_Days'] = (current_date - i).days
            total_investment += sip_investment

        n_sip += 1

    df_cash_flow = df[df['SIP_Value'] != 0]


    current_value = curr_nav * total_units

    abs_return = 100 * ( current_value - total_investment) / total_investment

    root = round(optimize.newton(xirr, 0, args=(df_cash_flow,current_value,)),2)

    return total_investment, current_value, round(abs_return,2), round(root,2)


def get_sip_inv_ret(df,sip_investment):

    current_date = dt.date.today()
    incep_date = df.index[0]
    fund_age = (current_date - incep_date).days/365.0

    one_year_ago = current_date - relativedelta(months=12)
    three_years_ago = current_date - relativedelta(months=36)
    five_years_ago = current_date - relativedelta(months=60)
    ten_years_ago = current_date - relativedelta(months=120)

    rec = []

    if one_year_ago > incep_date:
        period = 1
        df_1 = df[df.index >= one_year_ago]


        total_investment, current_val, abs_ret, root = get_sip_cashflow(df_1,sip_investment)
        values = "1 Year", one_year_ago, display_amount(total_investment), display_amount(current_val), abs_ret, root
        rec.append(values)

    if three_years_ago > incep_date:
        period = 3
        df_3 = df[df.index >= three_years_ago]

        total_investment, current_val, abs_ret, root = get_sip_cashflow(df_3,sip_investment)
        values = "3 Year", three_years_ago, display_amount(total_investment), display_amount(current_val), abs_ret, root
        rec.append(values)

    if five_years_ago > incep_date:
        period = 5
        df_5 = df[df.index >= five_years_ago]

        total_investment, current_val, abs_ret, root = get_sip_cashflow(df_5,sip_investment)
        values = "5 Year", five_years_ago, display_amount(total_investment), display_amount(current_val), abs_ret, root
        rec.append(values)

    if ten_years_ago > incep_date:
        period = 10
        df_10 = df[df.index >= ten_years_ago]

        total_investment, current_val, abs_ret, root = get_sip_cashflow(df_10,sip_investment)
        values = "10 Year", ten_years_ago, display_amount(total_investment), display_amount(current_val), abs_ret, root
        rec.append(values)



    total_investment, current_val, abs_ret, root = get_sip_cashflow(df,sip_investment)
    values = "Since Inception", incep_date, display_amount(total_investment), display_amount(current_val), abs_ret, root
    rec.append(values)

    df_sip = pd.DataFrame(rec, columns=['Period Invested for',f"{display_amount(sip_investment)} SIP Started on","Total Investments","Latest Value","Absolute Returns %","Annualised Returns %"])

    return df_sip
