import re
import os.path
from datetime import datetime, date
from telethon import TelegramClient


class Job:
    def __init__(self, target_group_id, post_at_time, job_text):
        self._target_group_id = target_group_id
        self._post_at_time = post_at_time
        self._job_text = job_text
        time = post_at_time.split(":")
        self._hour = int(time[0]) - 3
        self._minute = int(time[1])

    @property
    def target_group_id(self):
        return self._target_group_id

    @property
    def job_text(self):
        return self._job_text

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute


file_name = "vacancy_list.txt"
if not os.path.isfile(file_name):
    print("CAN'T FIND CONFIG FILE " + file_name)
    quit()

with open(file_name, encoding='utf-8', mode='r') as file:
    text = file.read()

client_info_pattern = re.compile(
    r"app_id=(?P<app_id>.+)\napi_hash=(?P<api_hash>.+)\nstart_send=(?P<start_send>(true|false))")
all_data_arr = text.split("####\n")
data = all_data_arr[0]
match = client_info_pattern.match(data)
app_id = int(match.group("app_id"))
api_hash = match.group("api_hash")
is_start_send = match.group("start_send")
client = TelegramClient('anon', app_id, api_hash)


async def main():
    me = await client.get_me()
    print("INFO ABOUT ME:")
    print(me.stringify())
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)
    if len(all_data_arr) < 2:
        print("Can't find vacancies in file", file_name)
        quit()
    vacancies = all_data_arr[1]

    print(vacancies)
    raw = vacancies.split("----\n")
    print(raw)
    jobs = []
    for job in raw:
        result = job.split("-\n")
        jobs.append(Job(result[0], "".join(result[1].split()).replace('\n', ' '), result[2]))
    print(jobs)

    if is_start_send.lower() == 'true':
        today = date.today()
        for job in jobs:
            await client.send_message(int(job.target_group_id),
                                      job.job_text,
                                      schedule=datetime(today.year, today.month, today.day, job.hour, job.minute))


with client:
    client.loop.run_until_complete(main())
