import pandas as pd
from prophet import Prophet
from influxdb_client import InfluxDBClient

# Replace with your InfluxDB details
token = "06zDP68xjXb7Cb_JlfgKzJZ3cGiq-j7H2RgOSnBwKgIpWSqhsmqGw5qCtYSE_vsKy85RP3VlNCJpdH6wnivXVQ=="
org = "fjcollector"
bucket = "fjcollector"
url = "https://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org,verify_ssl=False)
query = f'''
from(bucket: "{bucket}")
  |> range(start: -360d)
  |> filter(fn: (r) => r._measurement == "cpu" and r._field == "use")
  |> aggregateWindow(every: 1d, fn: mean)
  |> yield(name: "mean")
'''
tables = client.query_api().query(query, org=org)
print(tables)
# Convert the query result to a DataFrame
data = []
for table in tables:
    for record in table.records:
        data.append((record.get_time(), record.get_value()))
print(data[0:5])
df = pd.DataFrame(data, columns=['ds', 'y'], index=None)
df['ds'] = df['ds'].values.astype('<M8[D]')
df.head()

# Initialize and fit the Prophet model
model = Prophet()
model.fit(df)

# Make future predictions
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Save the forecast to a CSV file
forecast.to_csv('forecast.csv', index=False)
