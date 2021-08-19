import requests
import asyncio
import discord
import os
from bs4 import BeautifulSoup
from command import Command
from tools import is_positive_integer

class CodeforcesRecentSubmissionsCrawler(Command):
    is_toggled = False
    def __init__(self,channel,arguments):
        self.channel = channel
        self.arguments = arguments

    # Get status page from contest ID.
    def get_status_URL(self):
        contest_id = self.arguments[1]
        if not is_positive_integer(contest_id):
            return None
        contest_id = int(contest_id)

        if contest_id == 0: # Whole problemset
            return 'https://codeforces.com/problemset/status'
        elif contest_id >= 1 and contest_id <= 5000: # Normal Codeorces Rounds
            return 'https://codeforces.com/contest/' + str(contest_id) + '/status'
        elif contest_id >= 100001 and contest_id <= 500000: # Gyms & Mashups
            return 'https://codeforces.com/gym/' + str(contest_id) + '/status'
        else:
            return None

    # Remove redundant suffix (Because of virtual contest or Out of Competition contestants) by crawling
    def parse_handle(self,handle):
        if handle.endswith('#'): # Virtual contest ended mark
            handle = handle[:-1]
        if len(handle) >= 3 and handle[-3]==':': # During virtual contest mark
            handle = handle[:-5]
        return handle

    async def get_recent_submissions(self):
        status_url = self.get_status_URL()
        if status_url == None:
            return None

        try:
            request_headers = {
                'Cookie': os.getenv('COOKIE'),
                'Host': 'codeforces.com',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
            }
            response = requests.get(status_url, headers=request_headers, allow_redirects=False)
        except requests.ConnectionError:
            return None

        if response.status_code != requests.codes.ok:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        submissions = soup.select('.datatable')[0].select('tr')[1:]

        submission_list = []
        for submission in submissions:
            attributes = submission.select('td')

            #submission_id = attributes[0].get_text().strip()
            handle = attributes[2].get_text().strip()
            handle = self.parse_handle(handle)
            problem = attributes[3].get_text().strip()
            verdict = attributes[5].get_text().strip()

            # submission_list.append((submission_id,handle,problem,verdict))
            submission_list.append((handle,problem,verdict))
        return submission_list

    async def track_contest(self,track_time=180,interval=60):
        tracked_submissions = await self.get_recent_submissions()
        if tracked_submissions == None:
            await self.channel.send("track: Contest ID not valid or Connection Error")
            return
        tracked_submissions = set(tracked_submissions)

        await self.channel.send("Ok, start tracking Codeforces contest " + self.arguments[1] + "...")

        track_times = track_time * 60 // interval + 1
        for _ in range(track_times):
            await asyncio.sleep(interval)
            if not self.__class__.is_toggled:
                return
            recent_submissions = await self.get_recent_submissions()
            if tracked_submissions == None:
                await self.channel.send("track: Contest ID not valid or Connection Error")
                return

            for submission in recent_submissions:
                if submission in tracked_submissions or submission[2] != 'Accepted':
                    continue
                tracked_submissions.add(submission)
                embed = discord.Embed(title="Congrats :tada:", description="Congrats to contestant `" + submission[0] + "` on solving problem `" + submission[1] + "` !!", color=0x00aa00)
                await self.channel.send(embed=embed)

        await self.channel.send("track: Track finished after " + track_time + "minutes")



    async def run(self):
        if self.arguments[0] == 'track':
            if self.__class__.is_toggled:
                await self.channel.send("track: Already tracking")
                return
            self.__class__.is_toggled = True
            await self.track_contest()
        elif self.arguments[0] == 'untrack':
            self.__class__.is_toggled = False
            await self.channel.send("untrack: Tracking disabled")
        else:
            await self.channel.send("nho2: Command not found: " + self.arguments[0])
