import os
import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from fairlearn.metrics import MetricFrame
from fairlearn.reductions import ExponentiatedGradient, DemographicParity
import matplotlib.pyplot as plt

# Setup logger
logging.basicConfig(filename='bias_detection.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a folder for saving images
output_folder = 'bias_detection_images'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def check_bias(df, y_pred, y_test, column):
    """
    Check model performance (accuracy) across different subgroups.
    """
    # Make sure we apply the mask only on the rows corresponding to X_test
    subgroups = df[column].unique()
    results = {}
    
    # Ensure that we are only working with the test set (y_test and y_pred)
    test_indices = y_test.index  
    df_test = df.iloc[test_indices]  # Filter df based on the test set indices
    
    for subgroup in subgroups:
        mask = df_test[column] == subgroup  # Apply mask on the test set only
        acc = accuracy_score(y_test[mask], y_pred[mask])
        results[subgroup] = acc
        logging.info(f'Accuracy for {column} = {subgroup}: {acc}')
    
    return results


def plot_bias(results, title):
    """
    Plot the model's performance across different subgroups and save as an image.
    """
    plt.bar(results.keys(), results.values())
    plt.xlabel('Subgroups')
    plt.ylabel('Accuracy')
    plt.title(title)
    
    # Save the plot to the bias_detection_images folder
    plot_filename = os.path.join(output_folder, f'{title.replace(" ", "_")}.png')
    plt.savefig(plot_filename)
    plt.close()  # Close the plot to avoid display

    logging.info(f'Bias plot saved as {plot_filename}.')

def handle_bias(df):
    """
    This function will handle the bias detection and mitigation process.
    It accepts the DataFrame and performs all necessary steps inside.
    """
    
    # Step 1: Prepare the target variable and features
    df = df.dropna(subset=['sentiment_label', 'rating', 'verified_purchase', 'Category'])  # Drop rows with missing values
    y = df['sentiment_label'].apply(lambda x: 1 if x == 'positive' else 0)  # Convert sentiment label to binary
    X = df[['rating', 'helpful_vote', 'verified_purchase']]  # Select features (you can adjust this as needed)

    # Step 2: Split the dataset into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Step 3: Train a classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Step 4: Get predictions
    y_pred = clf.predict(X_test)

    # Step 5: Detecting Bias in Your Data: Evaluate performance for different subgroups
    verified_purchase_results = check_bias(df, y_pred, y_test, 'verified_purchase')
    sentiment_results = check_bias(df, y_pred, y_test, 'sentiment_label')
    category_results = check_bias(df, y_pred, y_test, 'Category')

    # Print and log performance metrics
    logging.info(f"Accuracy by Verified Purchase: {verified_purchase_results}")
    logging.info(f"Accuracy by Sentiment Label: {sentiment_results}")
    logging.info(f"Accuracy by Category: {category_results}")

    # Visualizing the performance disparity across subgroups
    plot_bias(verified_purchase_results, "Accuracy by Verified Purchase")
    plot_bias(sentiment_results, "Accuracy by Sentiment Label")
    plot_bias(category_results, "Accuracy by Category")

    # Step 6: Bias Mitigation - Applying fairness constraints (e.g., Demographic Parity)
    mitigator = ExponentiatedGradient(clf, DemographicParity())
    mitigator.fit(X_train, y_train, sensitive_features=X_train['verified_purchase'])
    y_pred_fair = mitigator.predict(X_test)

    # Step 7: Check fairness performance after mitigation
    fair_results = check_bias(df, y_pred_fair, y_test, 'verified_purchase')

    logging.info(f"Fair Results after Mitigation: {fair_results}")

    # Return the results for further use
    return {
        'verified_purchase_results': verified_purchase_results,
        'sentiment_results': sentiment_results,
        'category_results': category_results,
        'fair_results': fair_results
    }
