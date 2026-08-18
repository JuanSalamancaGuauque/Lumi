class ConversationMemory:

    def __init__(self):
        self.last_place = None
        self.last_category = None

    def remember_place(self, place):

        self.last_place = place

    def remember_category(self, category):

        self.last_category = category

    def get_last_place(self):

        return self.last_place

    def get_last_category(self):

        return self.last_category