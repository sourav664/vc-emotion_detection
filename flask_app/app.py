# updated app.py
import os
from flask import Flask, render_template,request
import pickle
import numpy as np
import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def lemmatization(text):
    """Lemmatize the text."""
    lemmatizer = WordNetLemmatizer()
    text = text.split()
    text = [lemmatizer.lemmatize(word) for word in text]
    return " ".join(text)

def remove_stop_words(text):
    """Remove stop words from the text."""
    stop_words = set(stopwords.words("english"))
    text = [word for word in str(text).split() if word not in stop_words]
    return " ".join(text)

def removing_numbers(text):
    """Remove numbers from the text."""
    text = ''.join([char for char in text if not char.isdigit()])
    return text

def lower_case(text):
    """Convert text to lower case."""
    text = text.split()
    text = [word.lower() for word in text]
    return " ".join(text)

def removing_punctuations(text):
    """Remove punctuations from the text."""
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
    text = text.replace('؛', "")
    text = re.sub('\s+', ' ', text).strip()
    return text

def removing_urls(text):
    """Remove URLs from the text."""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def remove_small_sentences(df):
    """Remove sentences with less than 3 words."""
    for i in range(len(df)):
        if len(df.text.iloc[i].split()) < 3:
            df.text.iloc[i] = np.nan

def normalize_text(text):
    text = lower_case(text)
    text = remove_stop_words(text)
    text = removing_numbers(text)
    text = removing_punctuations(text)
    text = removing_urls(text)
    text = lemmatization(text)

    return text

# load the port info from env vars
port = os.environ["PORT"]

# make the flask app
app = Flask(__name__)

# Load the model
model = pickle.load(open('models/model.pkl', 'rb'))
# Load the vectorizer
vectorizer = pickle.load(open('models/vectorizer.pkl','rb'))

    
@app.route('/')
def home():
    return render_template('index.html',result=None)

@app.route('/predict', methods=['POST'])
def predict():
    input_text = request.form['text']
    # clean
    text = normalize_text(input_text)
    
    # bow
    features = vectorizer.transform([text])

    # prediction
    result = model.predict(features)[0]
    
    # open a file in test folder
    with open("audit/predictions.txt", "a") as file:
        file.write(f"{input_text}, {'Happpy' if result == 1 else 'Sad' if result == 0 else 'Neutral'} \n")
    
    # show
    return render_template('index.html', result=result)

if __name__ == "__main__":
    # start the server
    app.run(host="0.0.0.0", port=port, debug=True)