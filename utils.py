POSITIVE_RESPONSES = ['y', 'Y', 'yes' 'YES']
NEGATIVE_RESPONSES = ['n', 'N', 'no', 'NO']

class NoAssignmentsError(Exception):
    def __init__(self, message="No assignments to show"):
        self.message = message
        super().__init__(self.message)


class SelectionOutOfBoundsError(Exception):
    def __init__(self, message="Selected range does not match the assignments"):
        self.message = message
        super().__init__(self.message)
