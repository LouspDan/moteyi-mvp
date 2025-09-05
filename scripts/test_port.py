from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bienvenue sur ton serveur local exposé avec Ngrok !"

if __name__ == '__main__':
    app.run(port=5000)
