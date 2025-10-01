from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_data():
    """Loads all CSV files into a dictionary of pandas DataFrames."""
    data = {}
    files = {
        'contacts': 'BnL.SampleCRM - Contacts.csv',
        'organizations': 'BnL.SampleCRM - Organizations.csv',
        'opportunities': 'BnL.SampleCRM - Opportunities.csv',
        'interactions': 'BnL.SampleCRM - Interactions.csv',
        'dropdowns': 'BnL.SampleCRM - Dropdowns.csv'
    }
    for key, filename in files.items():
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            # The header is on the 4th row (index 3)
            df = pd.read_csv(file_path, header=3)
            # Drop the first column if it's unnamed, which happens with a leading comma
            if df.columns[0].startswith('Unnamed:'):
                df = df.iloc[:, 1:]
            data[key] = df
    return data

@app.route('/')
def index():
    data = load_data()
    # Converting dataframes to HTML tables to display them easily
    tables = {key: df.to_html(classes='table table-striped', index=False) for key, df in data.items()}
    return render_template('index.html', tables=tables)

if __name__ == '__main__':
    app.run(debug=True)
