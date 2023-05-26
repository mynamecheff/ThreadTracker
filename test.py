from datetime import datetime
import time

datetime_str = '2023-05-26 14:35:00'

# Convert datetime string to datetime object
datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

# Convert datetime object to epoch time
epoch_time = int(datetime_obj.timestamp())

print(epoch_time)