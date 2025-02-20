from ftml.document import FTMLDocument
from ftml.ftml_data import FTMLData, simplify_data
from ftml.schema import FTMLSchema


def load(data: str, schema: str = None) -> FTMLData:
    if schema:
        schema_obj = FTMLSchema.load(schema)
        document = FTMLDocument.load(data, schema=schema_obj.schema_def)
        simple_data = simplify_data(document.data)
        return FTMLData(simple_data, document, schema_obj)
    else:
        document = FTMLDocument.load(data)
        simple_data = simplify_data(document.data)
        return FTMLData(simple_data, document)


def dump(data: dict, file=None) -> str:
    """
    Convert a Python dictionary to FTML format.
    If a file is provided, write the output to the file.
    """
    document = FTMLDocument.from_dict(data)
    ftml_output = document.to_ftml()
    if file:
        file.write(ftml_output)
    return ftml_output


def validate(data: dict, schema: str) -> bool:
    """
    Validate a Python dictionary against an FTML schema.
    Raises ValidationError if the data is invalid.
    """
    schema_obj = FTMLSchema.load(schema)
    return schema_obj.validate(data)


def load_file(path: str, schema: str = None) -> dict:
    """
    Load FTML data from a file and parse it into a Python dictionary.
    If a schema is provided, validate the data against it.
    """
    with open(path, "r") as file:
        data = file.read()
    return load(data, schema)


def dump_file(data: dict, path: str):
    """
    Convert a Python dictionary to FTML format and write it to a file.
    """
    with open(path, "w") as file:
        dump(data, file)
