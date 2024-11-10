#import statments needed for databases and linear regression model
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np
import joblib

#creates the model dir if not avaiable(couldn't work without this for some reason)
model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
os.makedirs(model_dir, exist_ok=True)


#load the three generated datasets 
df1 = pd.read_csv("model\ptsd_survey1.csv")
df2 = pd.read_csv("model\ptsd_survey2.csv")
df3 = pd.read_csv("model\ptsd_survey3.csv")

#combine all three datasets into one single datasets
ptsd_survey = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

#clean the dataframe by transfering into a new one, removing duplicates and dropping any rows with nan values
cleaned_survey = pd.DataFrame(ptsd_survey)
cleaned_survey.drop_duplicates(inplace=True)
cleaned_survey.dropna(inplace=True)

#convert the 'Sex' category into 0 fort Female and 1 for Male, making it easier for the model later
cleaned_survey['Sex'] = cleaned_survey['Sex'].replace({'F': 0, 'M': 1})

#X {age, sex, score} is defined as values that would determine the Y {PTSD percentage} value
X = cleaned_survey[['Age', 'Sex', 'PCL-Score']]
Y = cleaned_survey['PTSD']

#this is the line that is used to train imported from sklearn
#we also used this in our Lab3 for data management, so similar strcuture to follow
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=327)

#here we intilize the scale and use it to condese our data
#this is more relevant to the PTSD score because it allows the data to be more condesed for the categories and grouping 
#of different severity levels {mild, moderate, serious} this shows in the graph
#X train and X test are scaled for the training data to be more accurate to the sevrity level
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

#initial call to the import Linear Regression
linear_regression = LinearRegression()

#.fit(x,y) allows the model to train based off the scaled x and y train (input v. expected)
linear_regression.fit(X_train_scaled, y_train)

#y predicts values from the x test values that are scaled
# this is a test to make sure that the linear regression works and continues to train itself
y_pred = linear_regression.predict(X_test_scaled)

#multiplies the prediction values by 100 to convert to percentage and cuts off at second decimal place
ptsd_probability_percent = np.round(y_pred * 100, 2)

#copied from LAB3, MSE, R-squared values displayed that show accuracy 
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(cleaned_survey['Sex'].value_counts())  # See how many males and females are in the dataset
print(cleaned_survey['PTSD'].groupby(cleaned_survey['Sex']).mean())

print(f"Mean Squared Error: {mse:.2f}")
print(f"R-squared: {r2:.2f}")

#set size of figure
plt.figure(figsize=(8,6))

#define colors specific to sex and prediction
sex_colors = ['blue' if sex == 1 else 'red' for sex in X_test['Sex']]

#scatter plots based off of criteria of expected test values and predicted test values, also color coordination
plt.scatter(y_test, y_pred, c = sex_colors, alpha=0.3)
plt.xlabel("PTSD Data")
plt.ylabel("Predicted PTSD (0-1)")
plt.title("Actual vs Predicted PTSD (Percentile)")

#handles in order to take care of color matching
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Male'),
           plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Female')]
plt.legend(handles=handles, title="Sex")
#plt.savefig('static/predictive-plot.png') 
plt.show()

#test print to see predictions based off the ptsd probability
print(f"Predicted PTSD for first 10 values: {ptsd_probability_percent[:10]}%")


#different manually entered test data's in order to test out how the data would react to new user inputs
test_data1 = pd.DataFrame({
    'Age': [24],
    'Sex': ['M'],
    'PCL-Score': [62]
})

test_data2 = pd.DataFrame({
    'Age': [22],
    'Sex': ['F'],
    'PCL-Score': [52]
})

test_data3 = pd.DataFrame({
    'Age': [43],
    'Sex': ['F'],
    'PCL-Score': [78]
})

test_data4 = pd.DataFrame({
    'Age': [18],
    'Sex': ['M'],
    'PCL-Score': [14]
})

#transfer sex into binary values
test_data4['Sex'] = test_data4['Sex'].replace('F', 0)
test_data4['Sex'] = test_data4['Sex'].replace('M', 1)

#scales new data
test_data_scaled = scaler.transform(test_data4)

#new predictionn value
ptsd_prediction = linear_regression.predict(test_data_scaled)

#convert into percentage
ptsd_percentage = np.round(ptsd_prediction * 100, 2)

#final test print
print(f"Predicted PTSD for test case: {ptsd_percentage[0]}%")

#exports into joblib import so other classes can access and use
joblib.dump(linear_regression, os.path.join(model_dir, "linear_regression_model.pkl"))
joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))