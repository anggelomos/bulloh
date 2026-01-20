from datetime import datetime
import logging
import os

from nothion import NotionClient, PersonalStats
from tickthon import TicktickClient, TicktickListIds
from dotenv import load_dotenv

from bulloh import Bulloh
from bulloh import RescuetimeClient
from bulloh.health_connect_client import HealthConnectClient, HealthConnectSource
from bulloh.s3_client import S3Client


load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
ENVIRONMENT = os.getenv("ENVIRONMENT")


def main():
    current_date = datetime.now()
    current_date_str = current_date.strftime("%Y-%m-%d")
    connection_filename = os.getenv("CONNECTION_DATA_FILENAME")

    if ENVIRONMENT != "local":
        s3_client = S3Client("bulloh-plotter")
        file_data = s3_client.download_file(current_date_str)
        connection_data = s3_client.download_connection_file(connection_filename)

    rescuetime = RescuetimeClient(os.getenv("RT_API_KEY"))
    ticktick = TicktickClient(os.getenv("TT_USER"),
                              os.getenv("TT_PASS"),
                              TicktickListIds(
                                    INBOX="inbox114478622",
                                    TODAY_BACKLOG="6616e1af8f08b66b69c7a5c5",
                                    WEEK_BACKLOG="61c62f198f08c92d0584f678",
                                    MONTH_BACKLOG="61c634f58f08c92d058540ba",
                                    WEIGHT_MEASUREMENTS="640c03cd8f08d5a6c4bb32e7"),
                              api_token=connection_data.ticktick_data.token,
                              cookies=connection_data.ticktick_data.cookies
                            )
    notion = NotionClient(os.getenv("NT_AUTH"), stats_db_id="baa09f8600924192b1e9ceef4cfa70ce")
    
    # Re-enable health connect client once it's working again
    
    # health_connect = HealthConnectClient(os.getenv("HC_USERNAME"), 
    #                                      os.getenv("HC_PASSWORD"), 
    #                                      connection_data.health_connect_data.token, 
    #                                      connection_data.health_connect_data.refresh_token)
    
    # connection_data.health_connect_data.token = health_connect.token
    # connection_data.health_connect_data.refresh_token = health_connect.refresh_token
    connection_data.ticktick_data.token = ticktick.ticktick_api.auth_token
    connection_data.ticktick_data.cookies = ticktick.ticktick_api.cookies
    personal_focus_time_tags = ["stask", "dtask", "personal-project"]
    work_focus_time_tags = ["swtask", "dwtask", "work-project", "wørk-focus-meeting"]
    bulloh = Bulloh()

    for date in notion.stats.get_incomplete_dates(current_date):
        logging.info(f"Processing date: {date}")

        # fall_asleep_time, sleep_stages = health_connect.get_sleep(date, HealthConnectSource.GOOGLE_FITNESS.value, [4, 5, 6])
        # total_sleep_time = round(sum(sleep_stages.values()), 2)
        # deep_sleep_time = round(sum([st for ss, st in sleep_stages.items() if ss == 5 ]), 2)
        # rem_sleep_time = round(sum([st for ss, st in sleep_stages.items() if ss == 6 ]), 2)
        # steps = max(health_connect.get_steps(date, HealthConnectSource.XIAOMI_WEARABLE.value), 
        #             health_connect.get_steps(date, HealthConnectSource.GOOGLE_FITNESS.value))

        personal_stats = PersonalStats(date=date,
                                       focus_total_time=ticktick.get_overall_focus_time(date),
                                       focus_personal_time=ticktick.get_active_focus_time(date, personal_focus_time_tags),
                                       focus_work_time=ticktick.get_active_focus_time(date, work_focus_time_tags),
                                       work_time=rescuetime.get_productive_time(date),
                                       leisure_time=rescuetime.get_leisure_time(date),
                                       # sleep_time_amount=total_sleep_time or 0,
                                       # sleep_deep_amount=deep_sleep_time or 0,
                                       # sleep_rem_amount=rem_sleep_time or 0,
                                       # fall_asleep_time=fall_asleep_time,
                                       sleep_score=None,
                                       weight=bulloh.process_weight(date, ticktick.weight_measurements),
                                       # steps=steps or None,
                                       water_cups = None)

        logging.info(f"Updating stats for date: {date}, stats: {personal_stats}")
        notion.stats.update(personal_stats, overwrite_stats=True)

        if date == current_date_str:
            personal_stats.date = current_date.isoformat()
            file_data.stats_data.append(personal_stats)

            if ENVIRONMENT != "local":
                s3_client.upload_file(file_data, current_date_str)
                s3_client.upload_connection_file(connection_data, connection_filename)

if __name__ == "__main__":
    main()
