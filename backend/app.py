from flask import Flask, request, send_file
from flask_cors import CORS
import pandas as pd
import json
import io
import os

app = Flask(__name__)
CORS(app)  # This allows React to talk to Python

@app.route('/', methods=['GET'])
def home():
    return "<h1>Backend is running successfully!</h1>"

@app.route('/convert', methods=['POST'])
def convert_json():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    try:
        # Read JSON file directly from memory
        data = json.load(file)
        
        b2b_rows = []
        cdnr_rows = []
        
        # Access the main document data block
        docdata = data.get('data', {}).get('docdata', {})

        # --- PROCESS B2B ---
        if 'b2b' in docdata:
            for supplier in docdata['b2b']:
                supplier_gstin = supplier.get('ctin')
                trade_name = supplier.get('trdnm')
                supplier_filing_date = supplier.get('supfildt')
                
                for inv in supplier.get('inv', []):
                    b2b_rows.append({
                        'GSTIN': supplier_gstin,
                        'Trade Name': trade_name,
                        'Invoice No': inv.get('inum'),
                        'Date': inv.get('dt'),
                        'Value': inv.get('val'),
                        'Taxable Val': inv.get('txval'),
                        'IGST': inv.get('igst', 0),
                        'CGST': inv.get('cgst', 0),
                        'SGST': inv.get('sgst', 0),
                        'POS': inv.get('pos'),
                        'Filing Date': supplier_filing_date
                    })

        # --- PROCESS CDNR ---
        if 'cdnr' in docdata:
            for supplier in docdata['cdnr']:
                supplier_gstin = supplier.get('ctin')
                trade_name = supplier.get('trdnm')
                supplier_filing_date = supplier.get('supfildt')
                
                for note in supplier.get('nt', []):
                    cdnr_rows.append({
                        'GSTIN': supplier_gstin,
                        'Trade Name': trade_name,
                        'Note No': note.get('ntnum'),
                        'Note Date': note.get('dt'),
                        'Note Type': note.get('nttyp'),
                        'Value': note.get('val'),
                        'Taxable Val': note.get('txval'),
                        'IGST': note.get('igst', 0),
                        'CGST': note.get('cgst', 0),
                        'SGST': note.get('sgst', 0),
                        'Filing Date': supplier_filing_date
                    })

        # Create Excel in Memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if b2b_rows:
                pd.DataFrame(b2b_rows).to_excel(writer, sheet_name='B2B', index=False)
            if cdnr_rows:
                pd.DataFrame(cdnr_rows).to_excel(writer, sheet_name='CDNR', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='GSTR_Converted.xlsx'
        )

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
