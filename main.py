from recommender import create_app
import datetime

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)