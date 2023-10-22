import pandas as pd
import streamlit as st
from fpdf import FPDF
import tempfile
import io
import uuid
import os
from io import BytesIO
import math






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


def get_retirement_summary_text(name,ret_score,fund_needed,sip_needed,opt_xirr, years_to_retire, cagr):

    ret_text = ''
    ret_advise = []
    if ret_score == 100:
        ret_text = 'Congratulations {}!!! You have a Perfect Retirement Score.'.format(name)

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


def generate_pdf_report(fig_1, fig_2, retirement_dict, df_goals, df_ret_income, retirement_assets):

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


    #st.write(retirement_assets)


    ret_text, ret_advise = get_retirement_summary_text(Name,RetScore,FundShort,SIPNeed,OptXIRR, RetAge, Cagr)


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


        pdf.image(qr_code_img, x=70, y=163, w=60)


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
            pdf.cell(0, 10, f" Annual Inflation considered is {Inflation} % and the effect of Inflation stops when Age = {ExpCapAge}" , align='L')
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

                display_amount(df_goals.loc[j,'Amount']).replace('₹','Rs.')

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
