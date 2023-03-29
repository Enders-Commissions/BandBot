import datetime


# hour=24, minute=0 would result in 12:00:00 AM
# hour=10, minute=10 would result in 10:10:00 AM
# hour=12, minute=30, second=50 would result in 12:30:50 PM

DAY = "Monday" # Set this to whatever day you want it to run, Monday, Tuesday, etc...
NOTIFY_CHANNEL = 0000 # The ID of the channel you want the message to be sent to
TASK_DATE = datetime.time(hour=0, minute=0, second=0) # Timezone is UTC
DATABASE = "postgresql://user:password@host/database" # PostgreSQL database connection URL
BOT_TOKEN = "" # Your bot's token