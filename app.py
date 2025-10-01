from flask import Flask, render_template
import pandas as pd
import os
import json

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
            df = pd.read_csv(file_path, header=3)
            df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]
            df.dropna(axis=1, how='all', inplace=True)
            data[key] = df
    return data

@app.route('/')
def index():
    all_data = load_data()
    tables = {}
    
    # Create HTML tables with data attributes for interactivity
    for key in ['organizations', 'contacts', 'opportunities']:
        if key in all_data:
            df = all_data[key].fillna('')
            # The column to use for matching (e.g., 'Name' for organizations)
            # This is a simplification; a robust solution would use unique IDs.
            interactive_col = 'Name' if key in ['organizations', 'opportunities'] else 'Full Name (First, Last)'
            if interactive_col not in df.columns:
                 interactive_col = df.columns[0]

            tables[key] = df.to_html(
                classes='table table-hover',
                index=False,
                border=0,
                table_id=f'{key}-table',
                render_links=True,
                escape=False
            )

    # Prepare interactions data as a JSON object for JavaScript
    interactions_json = "[]"
    if 'interactions' in all_data:
        interactions_df = all_data['interactions'].fillna('')
        interactions_json = interactions_df.to_json(orient='records')

    return render_template('index.html', tables=tables, interactions_json=interactions_json)

if __name__ == '__main__':
    app.run(debug=True)
