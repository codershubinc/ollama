from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/scrape')
def scrape():
    url = 'https://marketplace.visualstudio.com/items?itemName=codershubinc.music'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')


        # Extract title
        title_element = soup.find('span', class_='ux-item-name')
        title = title_element.get_text(strip=True) if title_element else 'Title not found'

        # Extract publisher
        publisher_element = soup.find('a', class_='ux-dev-name')
        publisher = publisher_element.get_text(strip=True) if publisher_element else 'Publisher not found'

        # Extract description
        description_element = soup.find('div', class_='body-M')
        description = description_element.get_text(strip=True) if description_element else 'Description not found'

        # Extract total installs
        installs_element = soup.find('span', class_='installs-text')
        installs = installs_element.get_text(strip=True) if installs_element else 'Installs not found'

        return jsonify({
            'title': title,
            'publisher': publisher,
            'description': description,
            'installs': installs
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def home():
    return 'Backend is running!'

if __name__ == '__main__':
    app.run(debug=True)
