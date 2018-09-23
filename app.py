from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return "Figaro web app created by Kate Lyons."

if __name__ == '__main__':
    app.run()
