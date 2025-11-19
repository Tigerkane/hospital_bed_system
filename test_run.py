from flask import Flask
print("starting test")
app = Flask(__name__)
@app.route('/')
def i(): return 'ok'
app.run(debug=True)
