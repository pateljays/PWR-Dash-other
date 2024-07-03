from flask import Flask, render_template, request, render_template_string
import pandas as pd
import plotly.graph_objs as go

app = Flask(__name__)

df = pd.read_csv('Processed_DData.csv')
df['Treatment Completion Date'] = pd.to_datetime(df['Treatment Completion Date'])

#df.rename(columns={'Oral_Hygiene': 'Oral Hygiene',
#                   'Caries_Risk': 'Caries Risk', 'Diabetes/HbA1C': 'Diabetes',
#                   'Alcohol_Use': 'Alcohol Use', 'Health_Literacy': 'Health Litracy',
#                   'Self_Image': 'Self Image', 'Blood_Pressure': 'Blood Pressure',
#                   'Caries_Lesions': 'Caries Lesions', 'Perio_Inflammation': 'Perio Inflammation',
#                   'Perio_Pockets': 'Perio Pockets', 'Health_Literacy':'Health Literacy'}, inplace=True)
# 'Treatment Completion Date':'Date'

variables = ['Overall Performance', 'Anxiety - New',
             'Diabetes A1c','Social_Q1','Chewing - New','Speaking - New','Comfort - New',
             'Health Literacy - New', 'BP Prog. Favored','BP Improv. Favored','Smoking - New',
             'Smoking Medical',	'Smoking Perio', 'Alcohol Use',	'Caries Lesions', 'Perio Inflammation',
             'Perio Pockets','Caries Risk','Oral Hygiene']

# Define colors for the bars
colors = {'No-Change': '#f2e824', 'Improvement': '#15db0b',
          'Progression': '#e60000', 'Unknown': '#3d3a3a'}

min_date = df['Treatment Completion Date'].min()
min_date = min_date.strftime('%Y-%m-%d')

max_date = df['Treatment Completion Date'].max()
max_date = max_date.strftime('%Y-%m-%d')

@app.template_filter('intcomma')
def intcomma_filter(value):
    return f"{value:,}"


@app.route('/', methods=['GET', 'POST'])
def index():
    # Set default dates if none are provided
    start_date = request.form.get('start_date', min_date)
    end_date = request.form.get('end_date', max_date)

    html_strings = []

    filtered_df = df[(df['Treatment Completion Date'] >= start_date) & (df['Treatment Completion Date'] <= end_date)]

    total_count = len(filtered_df)

    for var in variables:
        counts = filtered_df[var].value_counts(dropna=False).reset_index()
        counts.columns = [var, 'Count']
        counts[var] = counts[var].fillna('Unknown')

        total_count_var = counts['Count'].sum()
        counts['Percentage'] = (counts['Count'] / total_count_var) * 100

        fig = go.Figure()

        for status in ['No-Change', 'Improvement', 'Progression', 'Unknown']:
            count_value = counts.loc[counts[var] == status, 'Count'].values
            percentage_value = counts.loc[counts[var] == status, 'Percentage'].values

            if len(count_value) > 0:
                fig.add_trace(go.Bar(name=status, y=[var], x=count_value,
                                     orientation='h', marker={'color': colors[status],
                                                              'line': {'color': 'black', 'width': 1}},
                                     showlegend=True, text=[f'{percentage_value[0]:.0f}%'],
                                     textposition='inside'))

        fig.update_layout(
            barmode='stack',
            title={'text': f'{var}', 'font': {'size': 28},'x': 0.5, 'xanchor': 'center'},
            showlegend=True,
            height=220,
            margin=dict(l=50, r=50, b=50, t=50, pad=4),
            legend=dict(orientation="h", yanchor="top", y=-0.8, xanchor="center", x=0.5, 
                        font=dict(size=12), itemwidth=70),
            plot_bgcolor='#ebedec', paper_bgcolor='#ebedec')

        fig.update_xaxes(tickcolor='darkgray', gridcolor='darkgray')
        
        html_string = fig.to_html(full_html=False, include_plotlyjs='cdn')
        html_strings.append(html_string)

    return render_template_string('''
 <!DOCTYPE html>
<html lang="en">
<head>
    <style>
        body {
            font-family: Arial;
            background-color: #ebedec;
            margin: 0;
            padding: 0;
        }
        h1 {
            text-align: center;
            color: #ffffff;
            margin: 0;
            font-size: 40px;
        }
        h2 {
            text-align: center;
            color: #B20838;
            margin: 0;
            font-size: 24px;
            margin-top: 10px;
            margin-bottom: 30px;
        }
        .plot-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            padding: 20px;
        }
        .plot-container > div {
            margin-bottom: 10px;
        }
        .full-width {
            width: 100%;
        }
        .third-width {
            width: 30%;
        }
        @media (max-width: 768px) {
            .third-width {
                width: 100%;
            }
        }
        @media (max-width: 1400px) {
            .third-width {
                width: 48%;
            }
        }
        /* Styles for the date selection form */
        form {
            margin: 20px auto;
            width: 60%;
            padding: 10px;
            background-color: #d1d1d1;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 18px;
        }
        form label {
            margin-right: 5px;
        }
        form input[type="date"] {
            padding: 6px;
            border-radius: 4px;
            border: 1px solid #ccc;
            font-size: 18px;
        }
        form input[type="submit"] {
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
            background-color: #B20838;
            color: white;
            cursor: pointer;
            font-size: 18px;
        }
        form input[type="submit"]:hover {
            background-color: #7d0628;
        }
        .date-group {
            display: flex;
            align-items: center;
            margin-right: 10px;
        }
        .date-group label {
            margin-right: 5px;
        }
        .navbar {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #B20838;
            justify-content: space-between;
        }
        .navbar-brand {
            margin-right: 20px;
        }
        .navbar-content {
            display: flex;
            align-items: center;
        }
        .navbar-content h1 {
            margin-left: 10px;
            margin-right: 10px;
            font-size: 24px;
        }
        /* Custom scrollbar styles */
        ::-webkit-scrollbar {
            width: 12px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background:  #8a8a8a;
            border-radius: 6px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-brand">
            <img src="static/Image_2.jpg" alt="PWR Logo" style="height:80px;">
        </div>
        <div class="navbar-content">
            <img src="static/Image_1.png" alt="PWR Logo" style="height:80px;">
            <h1>Patient Wellness Report Dashboard</h1>
            <img src="static/Image_1.png" alt="PWR Logo" style="height:80px;">
        </div>
        <div class="navbar-brand">
            <img src="static/Image_2.jpg" alt="PWR Logo" style="height:80px;">
        </div>
    </nav>

    <form action="" method="post">
        <div class="date-group">
            <label for="start_date">Start Date:</label>
            <input type="date" id="start_date" name="start_date" value="{{start_date}}">
        </div>
        <div class="date-group">
            <label for="end_date">End Date:</label>
            <input type="date" id="end_date" name="end_date" value="{{end_date}}">
        </div>
        <input type="submit" value="Filter Data">
    </form>
    <div class="plot-container">
        <h2>Total Patient Records: {{total_count | intcomma}}</h2>
        {% for i, html_string in enumerate(html_strings) %}
            <div class="{{ 'full-width' if i == 0 else 'third-width' }}">{{ html_string | safe }}</div>
        {% endfor %}
    </div>
</body>
</html>

''', request=request, start_date=start_date, end_date=end_date, html_strings=html_strings, total_count=total_count, enumerate=enumerate)

if __name__ == '__main__':
    app.run(debug=False, port=0)
