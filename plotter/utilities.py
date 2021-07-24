import json
import subprocess
import typing

from .model.src.aggregated import AggregatedData
from .model.src.filedata import FileData


def get_cloc_data(folder: str) -> typing.Tuple[typing.List[FileData], AggregatedData]:
    """
        Get the data of `folder` using the `cloc` utility

        Returns the list of languages contained in the repository
    """
    p = subprocess.Popen(['cloc', folder, '--json'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_lines = p.stdout.readlines()
    output = ""
    for line in output_lines:
        output += line.decode('utf-8')

    output = json.loads(output)
    languages = [lang for lang in output if lang != 'header']
    data = []
    aggregated = None
    for lang in languages:
        if lang == 'SUM':
            aggregated = AggregatedData(output[lang])
        else:
            data.append(FileData(output[lang], lang=lang))
    return (data, aggregated)
