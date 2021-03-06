## General info
This project is designed to take a machine learning model from development to live production. The code will query trading platform API for
model input data, process that data and feed it into the model (example used in this project is an xgBoost model) for live predictions. It will then
append predictions to a running file containing prior interval predictions. 

Finally, each time that file is amended with a new prediction, the project has a Dash application, which will automatically pick up the latest
entry data and update the interactive dashboard. Dashboard has the ability to track historical actual vs predictions
on both long term and single day time intervals as well as calculate
differences between periods to better assist with understanding real-time model drivers.

## Screenshots

<b>Main Tab View:</b>

![MainTab](examples/dash_app_main_window_screenshot.PNG)  


<b>Differences Tab View:</b>

![DiffTab](examples/dash_app_differences_window_screenshot.PNG)
	
