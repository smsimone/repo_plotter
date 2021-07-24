
class AggregatedData(object):
    """
        Class that contains the aggregated data calculated by `cloc`
    """

    def __init__(self, data: map):
        self.blank = data['blank']
        self.comment = data['comment']
        self.code = data['code']
        self.nFiles = data['nFiles']

    def to_string(self):
        return f"Total lines of code: {self.code}"

    def as_map(self) -> map:
        return {
            'blank': self.blank,
            'comment': self.comment,
            'code': self.code,
            'nFiles': self.nFiles,
        }
