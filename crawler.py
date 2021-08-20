import requests
import asyncio
import os
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from tools import is_positive_integer

class CodeforcesRecentSubmissionsCrawler(commands.Cog):
    is_toggled = False
    def __init__(self,bot):
        self.bot=bot

    # Get status page from contest ID.
    def get_status_URL(self, contest_id):
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
    def parse_handle(self, handle):
        if handle.endswith('#'): # Virtual contest ended mark
            handle = handle[:-1]
        if len(handle) >= 3 and handle[-3]==':': # During virtual contest mark
            handle = handle[:-5]
        return handle

    async def get_recent_accepted_submissions(self, contest_id):
        status_url = self.get_status_URL(contest_id)
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

            if verdict == 'Accepted'
                submission_list.append((handle,problem))
        return submission_list

    async def track_contest(self, ctx, contest_id, track_time=180, interval=60):
        tracked_submissions = await self.get_recent_accepted_submissions(contest_id)
        if tracked_submissions == None:
            await ctx.send("track: Contest ID not valid or Connection Error")
            return
        tracked_submissions = set(tracked_submissions)

        await ctx.send("Ok, start tracking Codeforces contest " + contest_id + "...")

        track_times = track_time * 60 // interval + 1
        for _ in range(track_times):
            await asyncio.sleep(interval)
            if not self.__class__.is_toggled:
                return
            recent_submissions = await self.get_recent_accepted_submissions(contest_id)
            if tracked_submissions == None:
                await ctx.send("track: Contest ID not valid or Connection Error")
                return

            for submission in recent_submissions:
                if submission in tracked_submissions:
                    continue
                tracked_submissions.add(submission)
                embed = discord.Embed(title="Congrats :tada:", description="Contestant `" + submission[0] + "` solved problem `" + submission[1] + "` !!", color=0x00aa00)
                await ctx.send(embed=embed)

        await ctx.send("track: Track finished after " + track_time + "minutes")

    @commands.command()
    async def track(self, ctx, contest_id):
        if self.__class__.is_toggled:
            await ctx.send("track: Already tracking")
            return
        self.__class__.is_toggled = True
        await self.track_contest(ctx, contest_id)

    @commands.command()
    async def untrack(self,ctx):
        self.__class__.is_toggled = False
        await ctx.send("untrack: Tracking disabled")

def setup(bot):
    bot.add_cog(CodeforcesRecentSubmissionsCrawler(bot))
