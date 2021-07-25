import json


class FileData(object):
    """
        Class that contains the data for the single language calculated by `cloc`
    """

    def __init__(self, data: map, lang=None):
        if lang is None:
            if 'lang' not in data:
                print("Missing `lang` field in data:", json.dumps(data))
                exit(-1)
            else:
                self.lang = data['lang']
        else:
            self.lang = lang
        self.numFiles = data['nFiles']
        self.blank = data['blank']
        self.comment = data['comment']
        self.code = data['code']

    def get_field(self, field: str) -> int:
        if field == 'code':
            return self.code
        elif field == "nFiles":
            return self.numFiles
        elif field == 'blank':
            return self.blank
        elif field == 'comment':
            return self.comment

    def to_string(self):
        return f"Language {self.lang} has {self.code} lines of code"

    def add_other_data(self, other_data, inPlace=True):
        """
            Adds another `FileData` object to `self`

            `self.lang` and `other_data.lang` must have the same value

            if `inPlace` is `True`, this call will modify the internal state of `FileData`,
            otherwise it will generate a new `FileData` object
        """
        if not isinstance(other_data, FileData):
            raise Exception("You can sum only two FileData objects")
        if other_data.lang != self.lang:
            raise Exception(
                "It doesn't make sense to sum two FileData that are on different languages")
        if inPlace:
            self.numFiles += other_data.numFiles
            self.blank += other_data.blank
            self.comment += other_data.comment
            self.code += other_data.code
        else:
            return FileData({
                'lang': self.lang,
                'nFiles': self.numFiles + other_data.numFiles,
                'blank': self.blank + other_data.blank,
                'comment': self.comment + other_data.comment,
                'code': self.code + other_data.code,
            })

    def as_map(self) -> map:
        return {
            'lang': self.lang,
            'nFiles': self.numFiles,
            'blank': self.blank,
            'comment': self.comment,
            'code': self.code
        }
