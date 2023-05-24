import datetime

class EpochConverter:
    @staticmethod
    def convert(epoch_time):
        if epoch_time is None:
            return None
        
        try:
            epoch_int = int(epoch_time)
            if epoch_int < 0:
                return None  # if value is none
            
            timestamp = datetime.datetime.fromtimestamp(epoch_int)
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError, OSError):
            return None
