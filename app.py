from flask import Flask, render_template, request, jsonify
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

    # Prepare dropdowns data from dropdowns.csv
    dropdown_data = {}
    if 'dropdowns' in all_data:
        df = all_data['dropdowns']
        for column in df.columns:
            dropdown_data[column] = df[column].dropna().tolist()

    # Add lists of existing items for dynamic dropdowns
    if 'organizations' in all_data:
        dropdown_data['Organization'] = all_data['organizations']['Name'].dropna().tolist()
    if 'contacts' in all_data:
        dropdown_data['Contact'] = all_data['contacts']['Full Name (First, Last)'].dropna().tolist()
    if 'opportunities' in all_data:
        dropdown_data['Opportunity'] = all_data['opportunities']['Name'].dropna().tolist()

    return render_template('index.html', tables=tables, interactions_json=interactions_json, dropdown_data=json.dumps(dropdown_data))

@app.route('/add', methods=['POST'])
def add_entry():
    data = request.get_json()
    entry_type = data.get('type')
    payload = data.get('payload')

    if not entry_type or not payload:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    files = {
        'organization': 'BnL.SampleCRM - Organizations.csv',
        'contact': 'BnL.SampleCRM - Contacts.csv',
        'opportunity': 'BnL.SampleCRM - Opportunities.csv'
    }

    filename = files.get(entry_type.lower())
    if not filename:
        return jsonify({'success': False, 'message': 'Invalid entry type'}), 400

    try:
        file_path = os.path.join(DATA_DIR, filename)
        
        # Load existing data to get columns in the correct order
        # We use header=3 and skip the first column like in load_data
        df_existing = pd.read_csv(file_path, header=3).iloc[:, 1:]
        
        # Create a new DataFrame from the payload
        new_df = pd.DataFrame([payload])
        
        # Ensure the new DataFrame has the same columns in the same order
        new_df = new_df.reindex(columns=df_existing.columns)

        # Append to the CSV file without writing the header
        new_df.to_csv(file_path, mode='a', header=False, index=False)

        return jsonify({'success': True})
    except Exception as e:
        # In a real app, you'd log the error `e`
        return jsonify({'success': False, 'message': 'Failed to save data.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
