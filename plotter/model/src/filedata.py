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

    def to_string(self):
        return f"Language {self.lang} has {self.code} lines of code"

    def as_map(self) -> map:
        return {
            'lang': self.lang,
            'nFiles': self.numFiles,
            'blank': self.blank,
            'comment': self.comment,
            'code': self.code
        }
