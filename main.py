from bot import *

if __name__ == '__main__':
    scheduler.add_job(scheduled_forecast_job, 'cron', hour=7, minute=0, replace_existing=True)
    bot.infinity_polling()
