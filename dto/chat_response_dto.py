class ChatResponseDto:
    def __init__(self, bot_reply:str, reply_content:list ):
        self.status_code = None
        self.bot_reply = bot_reply
        self.reply_content = reply_content

    # setter : status_code
    def set_status_code(self, status_code):
        self.status_code = status_code

    # getter : status_code
    def get_status_code(self):
        return self.status_code
    