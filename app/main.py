from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Mini Social App is running"}

if __name__ == "__main__":
    app.run(debug=True)
