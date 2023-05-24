import datetime
# function to convert epoch time to human-readable time
class EpochConverter:
    @staticmethod
    def convert(epoch_time):
        if epoch_time is not None:
            epoch_time = float(epoch_time)  
            readable_time = datetime.datetime.fromtimestamp(epoch_time / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            return readable_time
        return None
