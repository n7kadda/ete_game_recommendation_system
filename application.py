from flask import Flask, render_template, request
from pipeline.prediction_pipeline import PredictionPipeline
import pandas as pd

app = Flask(__name__)

# Initialize the pipeline once when the app starts
try:
    pipeline = PredictionPipeline()
except Exception as e:
    print(f"Error initializing prediction pipeline: {e}")
    pipeline = None

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations_df = None

    if request.method == 'POST':
        if pipeline:
            try:
                user_id_str = request.form.get("userID")
                if user_id_str:
                    user_id = int(user_id_str)
                    # The pipeline returns a DataFrame
                    recommendations_df = pipeline.hybrid_recommendation(user_id)
                    # Ensure it's a DataFrame for the template
                    if not isinstance(recommendations_df, pd.DataFrame):
                        recommendations_df = pd.DataFrame()
                else:
                    recommendations_df = pd.DataFrame() # Handle empty input
            except Exception as e:
                print(f"Error in recommendation: {e}")
                recommendations_df = pd.DataFrame() # Ensure it's a df on error
        else:
            print("Pipeline not available.")
            
    # Pass the DataFrame directly to the template
    return render_template('home.html', recommendations=recommendations_df)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
