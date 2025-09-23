# Import the Flask app from the api module
from api.app import app

if __name__ == "__main__":
    app.run(debug=True)
