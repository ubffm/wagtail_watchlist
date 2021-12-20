
'''Metadata-schema:

{
    "author",
    "contributor",
    "title",
    "subtitle",
    "placePublished",
    "datePublished",
    "editor",
    "language",
    "publisher",
    "subject",
    "doi",
    "uri", == id
    "isbn"
    "issn",
}
'''

def bibtex_export(metadata):

    json_mapping = {
        "author":["author","contributor"],  # csv
        "subtitle":["subtitle"],
        "address":["placePublished"],
        "year":["datePublished"],
        "editor":["editor"],
        "language":["language"],
        "publisher":["publisher"],
        "keywords":["subject"],  # csv
        "doi":["doi"],
        "title":["title"],
        "url":["uri"],  # whitespace seperated
        "isbn":["isbn"],  # csv
        "issn":["issn"],  # csv
    }

    response = f'@misc{{{metadata["uri"]},\n\t'

    for key,value in json_mapping.items():
        result = list()
        for tag in value:

            data = metadata.get(tag,None)
            if data is not None:
                if isinstance(data,list):
                    result += data
                else:
                    result.append(data)

        if key != 'url' and result != []:
            response = response + f'{key} = {{{", ".join(result)}}},\n\t'
        elif key == 'url' and result != []:
            response = response + f'{key} = {{{" ".join(result)}}},\n\t'

    response = response[:-1] + '}'

    return response

def endnote_export(metadata):

    json_mapping = {
        "%A":["author","contributor"],
        "%B":["subtitle"],
        "%C":["placePublished"],
        "%D":["datePublished"],
        "%E":["editor"],
        "%G":["language"],
        "%I":["publisher"],
        "%K":["subject"],
        "%R":["doi"],
        "%T":["title"],
        "%U":["uri"],
        "%@":["isbn","issn"],
    }

    response = '%0 Generic\n'

    for key,value in json_mapping.items():
        for tag in value:
            data = metadata.get(tag,None)

            if data is not None:
                if isinstance(data,list):
                    for item in data:
                        response = response + key + '  - ' + item + '\n'
                else:
                    response = response + key + '  - ' + data + '\n'

    return response

def ris_export(metadata):

    json_mapping = {
        "AU":["author","contributor"],
        "T2":["subtitle"],
        "CY":["placePublished"],
        "PY":["datePublished"],
        "ED":["editor"],
        "LA":["language"],
        "PB":["publisher"],
        "KW":["subject"],
        "DO":["doi"],
        "T1":["title"],
        "UR":["uri"],
        "SN":["isbn","issn"],
    }

    response = 'TY  - GEN\n'

    for key,value in json_mapping.items():
        for tag in value:
            data = metadata.get(tag,None)
            if data is not None:
                if isinstance(data,list):
                    for item in data:
                        response = response + key + '  - ' + item + '\n'
                else:
                    response = response + key + '  - ' + data + '\n'

    response = response + "ER  - "
    return response
