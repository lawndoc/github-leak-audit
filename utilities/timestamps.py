from datetime import datetime, timedelta


def timestampToDatetime(ts):
    timestamp = float(ts[:ts.index("Z")])
    return datetime.fromtimestamp(timestamp)


def utcNowTimestamp(deltaDays=0, deltaHours=0, deltaMinutes=0, deltaSeconds=0):
    delta = timedelta(days=deltaDays,
                      hours=deltaHours,
                      minutes=deltaMinutes,
                      seconds=deltaSeconds)
    return str(datetime.timestamp(datetime.utcnow()+delta))+"Z"
