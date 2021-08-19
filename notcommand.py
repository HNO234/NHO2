from command import Command

class NotCommand(Command):
    def __init__(self,channel,arguments):
        self.channel = channel
        self.arguments = arguments
    async def run(self):
        await self.channel.send("nho2: command not found: " + self.arguments[0])
