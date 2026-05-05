from pandas_market_calendars import get_calendar
from datetime import datetime
import pytz

class MarketCalendar:
    def __init__(self):
        self.us = get_calendar('NYSE')

    def get_session(self):
        now = datetime.now(pytz.utc).date()
        status = {}
        
        us_sched = self.us.schedule(start_date=now, end_date=now)
        status['US'] = 'open' if not us_sched.empty else 'closed'
        
        return status

