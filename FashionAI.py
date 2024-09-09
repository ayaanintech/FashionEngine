pip install streamlit flask firebase-admin requests beautifulsoup4 openai lxml
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import json

app = Flask(__name__)

# Setup Firebase
cred = credentials.Certificate("path/to/your-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# OpenAI API key for GPT
openai.api_key = "your_openai_api_key"

# Web Scraping for fashion items
def scrape_fashion_items(query):
    search_results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # List of e-commerce sites to scrape (mock URLs for example)
    urls = [
        f"https://www.example1.com/search?q={query}",
        f"https://www.example2.com/search?q={query}"
    ]
    
    for url in urls:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')

        # Assume products are inside a div with class 'product-item'
        products = soup.find_all('div', class_='product-item')

        for product in products:
            image = product.find('img')['src']
            description = product.find('h2').text
            price = product.find('span', class_='price').text
            link = product.find('a')['href']
            
            search_results.append({
                'image': image,
                'description': description,
                'price': price,
                'link': link
            })
    
    return search_results

# Caching logic to avoid re-scraping
def cache_query(query, results):
    hashed_query = hashlib.md5(query.encode()).hexdigest()
    db.collection('cache').document(hashed_query).set({'results': results})

def get_cached_results(query):
    hashed_query = hashlib.md5(query.encode()).hexdigest()
    doc = db.collection('cache').document(hashed_query).get()
    if doc.exists:
        return doc.to_dict().get('results')
    return None

# AI-powered search function using OpenAI GPT
def ai_search(query):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Recommend fashion items for the following search query: {query}",
        max_tokens=100
    )
    return response.choices[0].text.strip()

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data['query']

    # Check cache first
    cached_results = get_cached_results(query)
    if cached_results:
        return jsonify({'results': cached_results})

    # AI-powered search
    ai_recommendation = ai_search(query)

    # Scrape fashion items from multiple websites
    results = scrape_fashion_items(query)

    # Cache the results
    cache_query(query, results)

    return jsonify({
        'recommendation': ai_recommendation,
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True)
import streamlit as st
import requests

# Streamlit UI
st.title("AI Fashion Search Engine")

query = st.text_input("Search for Clothes or Occasion", placeholder="e.g., Evening Dress, Casual Wear")

if st.button("Search"):
    if query:
        # Call the Flask API
        response = requests.post("http://localhost:5000/search", json={"query": query})
        data = response.json()

        # Display AI-powered recommendations
        st.subheader("AI Recommendation")
        st.write(data.get("recommendation"))

        # Display Search Results
        st.subheader("Search Results")
        for result in data.get("results"):
            st.image(result["image"], width=150)
            st.write(f"**Description:** {result['description']}")
            st.write(f"**Price:** {result['price']}")
            st.write(f"[Buy Now]({result['link']})")

    else:
        st.write("Please enter a query.")
def scrape_fashion_items(query):
    search_results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    urls = [
        f"https://www.example1.com/search?q={query}",
    ]

    for url in urls:
        while url:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'lxml')

            products = soup.find_all('div', class_='product-item')
            for product in products:
                image = product.find('img')['src']
                description = product.find('h2').text
                price = product.find('span', class_='price').text
                link = product.find('a')['href']
                
                search_results.append({
                    'image': image,
                    'description': description,
                    'price': price,
                    'link': link
                })

            # Find the next page link
            next_page = soup.find('a', class_='next-page')
            if next_page:
                url = next_page['href']
            else:
                url = None

    return search_results
