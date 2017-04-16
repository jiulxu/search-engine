from flask import Flask, render_template
import main

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

app.register_blueprint(main.main)

# Listen on external IPs
# For us, listen to port 3000 so you can just run 'python app.py' to start the server
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='0.0.0.0', port= 2999, debug=True)
