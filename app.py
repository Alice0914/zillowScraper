from flask import Flask, request, jsonify
from zillowScraper import main

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def handle_form():
    # Get form data
    zip = request.form.get('zip')
    type = request.form.get('type')
    
    # Call the imported function to process the data
    response = main(zip, type)
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)