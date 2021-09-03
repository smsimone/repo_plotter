class AggregatedData(object):
    """
    Class that contains the aggregated data calculated by `cloc`
    """

    def __init__(self, data: map):
        self.blank = data["blank"]
        self.comment = data["comment"]
        self.code = data["code"]
        self.nFiles = data["nFiles"]

    def to_string(self):
        return f"Total lines of code: {self.code}"

    def add(self, other, inPlace=True):
        """
        Sums the values from self with the values of `other`

        `other` must be an `AggregatedData` object

        if `inPlace` is set to `False` this function will return a new `AggregatedData` object
        """
        if not isinstance(other, AggregatedData):
            raise Exception("You can only sum another `AggregatedData` object")
        if inPlace:
            self.blank += other.blank
            self.comment += other.comment
            self.code += other.code
            self.nFiles += other.nFiles
        else:
            return AggregatedData({
                "blank": self.blank + other.blank,
                "comment": self.comment + other.comment,
                "code": self.code + other.code,
                "nFiles": self.nFiles + other.nFiles,
            })

    def as_map(self) -> map:
        return {
            "blank": self.blank,
            "comment": self.comment,
            "code": self.code,
            "nFiles": self.nFiles,
        }
