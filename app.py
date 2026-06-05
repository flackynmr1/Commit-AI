from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    print("🔥 JARVIS WEB RUNNING")
    app.run(debug=True)