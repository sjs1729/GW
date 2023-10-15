import pandas as pd
import streamlit as st
import plotly.io as pio
from PIL import Image
from fpdf import FPDF
import tempfile
import io
import base64
import uuid
import os
from io import BytesIO






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
        ret_text = ret_text + ' Although your doing fine, you need to improve your Score to a Perfect 100. Please consult your Financial Advisor'

        if fund_needed > 0:
            ret_advise.append('1. You have a fund shortfall of Rs. {}. Review your Expenses, Goals and Other Income sources'.format(fund_needed))

        if sip_needed > 0 and years_to_retire > 0:
            ret_advise.append('2. You have {} years to retire, you need to save an additional Rs. {} monthly'.format(years_to_retire,sip_needed))

        if cagr < opt_xirr:
            ret_advise.append('3. Your corpus is growing at an annual rate of {}%. You can meet your Retirement Targets if you can grow your assets at {}%'.format(cagr,opt_xirr))


    elif ret_score >= 75 and ret_score < 95:
        ret_text = 'Dear {}, your Retirement Score is {}. You are in Amber Zone. Please consult your Financial Advisor to improve your Retirement Planning'.format(name, ret_score)

        if fund_needed > 0:
            ret_advise.append('1. You have a fund shortfall of Rs. {}. Review your Expenses, Goals and Other Income sources'.format(fund_needed))

        if sip_needed > 0 and years_to_retire > 0:
            ret_advise.append('2. You have {} years to retire, you need to save an additional Rs. {} monthly'.format(years_to_retire,sip_needed))

        if cagr < opt_xirr:
            ret_advise.append('3. Your corpus is growing at an annual rate of {}%. You can meet your Retirement Targets if you can grow your assets at {}%'.format(cagr,opt_xirr))


    else:
        ret_text = 'Dear {}, your Retirement Score is {}. You are in Red Zone and need immediate help. Please consult your Financial Advisor to improve your Retirement Planning'.format(name, ret_score)

        if fund_needed > 0:
            ret_advise.append('1. You have a fund shortfall of Rs. {}. Review your Expenses, Goals and Other Income sources'.format(fund_needed))

        if sip_needed > 0 and years_to_retire > 0:
            ret_advise.append('2. You have {} years to retire, you need to save an additional Rs. {} monthly'.format(years_to_retire,sip_needed))

        if cagr < opt_xirr:
            ret_advise.append('3. Your corpus is growing at an annual rate of {}%. You can meet your Retirement Targets if you can grow your assets at {}%'.format(cagr,opt_xirr))



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

    image_bytes = pio.to_image(fig_1, format="png", engine="orca")
    pil_image = Image.open(io.BytesIO(image_bytes))

    temp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    pil_image.save(temp_image.name, format="PNG")

    #fig_1.write_image(temp_filename)
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
        #pdf.image(temp_filename, x=0, y=39, w=110)
        pdf.image(temp_image.name, x=0, y=39, w=110)
        #if os.path.exists(temp_filename):
        #    os.remove(temp_filename)


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
        pdf.cell(25, 10, "Plan Till:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{PlanAge}" , align='L')
        #pil_image.save(temp_image.name, format="PNG")

        start_pos_y = start_pos_y + line_gap
        start_pos_x = 140
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Annual Income:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"Rs. {AnnInc}" , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Annual Expense:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"Rs. {AnnExp}" , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Annual Hike:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{AnnHikPct} %" , align='L')
        #pil_image.save(temp_image.name, format="PNG")


        start_pos_y = start_pos_y + line_gap
        start_pos_x = 140
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Current Networth:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"Rs. {Corpus}" , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, "Networth CAGR:", align='L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(10, 10, f"{Cagr} %" , align='L')

        start_pos_x = start_pos_x + 50
        pdf.set_xy(start_pos_x,start_pos_y)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(25, 10, f"Networth at {PlanAge}:", align='L')
        pdf.set_font('Arial', '', 8)
        if TermCorp > 0:
            pdf.cell(10, 10, f"Rs. {TermCorp}" , align='L')
        else:
            pdf.cell(10, 10, " -- " , align='L')

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

            pdf.cell(30, 10, "Retirement Goals:" , align='L')
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
                pdf.cell(20,line_height,f"Rs. {str(df_goals.loc[j,'Amount'])}",border=1, align='C')
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
                    pdf.cell(15,line_height,"--",border=1, align='C')

                pdf.cell(55,line_height,f"{df_ret_income.loc[j,'Desc']}",border=1, align='C')
                pdf.cell(20,line_height,f"Rs. {str(df_ret_income.loc[j,'Amount'])}",border=1, align='C')
                pdf.cell(20,line_height,f"{freq_text}",border=1, align='C')
                pdf.cell(15,line_height,f"{str(incr_pct)}",border=1, align='C')



        #pdf.add_page()
        #pdf.image("gw_header.png",5,3,WIDTH-10,24)
        #pdf.image("gw_footer.png",5,HEIGHT-15,WIDTH-10,12)

        #fig_2.write_image(report_filenm)
        #pdf.image(report_filenm, x=12, y=25,w=280,h=165)

        #if os.path.exists(report_filenm):
            #os.remove(report_filenm)



    except Exception as e:
        st.write(e)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        if os.path.exists(report_filenm):
            os.remove(report_filenm)







    # Save the PDF to a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)

    pdf_bytes = open(temp_pdf.name, 'rb').read()


    return pdf_bytes
