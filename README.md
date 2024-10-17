**Rules Engine with AST**
created a sql table named "rules" with columns rule_name,rule_string,ast.
installed required modules in python:
import mysql.connector
import json

created 3 functions :
1."create_rule" which takes input rule and make it clear to understand by python interpreter.
2."combine_rules" this function combines multiple rules.
3."evaluate_rule" This is the actual function that evaluates rules and form abstract syntax tree.

After completion of this process ast,rule_string,rule_name will be inserted into table.

**Real-Time Data Processing System for Weather Monitoring with Rollups and Aggregates**
installed required python modules
import requests
import mysql.connector
import time
import datetime
import matplotlib.pyplot as plt

created a sql table named weather with columns "id","city","main","temp","feels_like","timestamp"
signed up in https://openweathermap.org/ and got a api key
With that API key and city ids tempearature details is gathered.
created funtions:
1.store_weather_data(city, data) method to store the weather data.
2.calculate_daily_summary to calculate daily weather data that is average,maximum,minimum.
3.check_alerts if temperatures goes higher than threshold temperature then alert raised.
4.visualize_daily_summary This function represents weather in graphical way.

For every 5 minutes weather data will be gathered in inserted into table.
