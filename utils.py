class NoAssignmentsError(Exception):
    def __init__(self, message="No assignments to show"):
        self.message = message
        super().__init__(self.message)
