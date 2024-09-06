from xata.client import XataClient
import config
import cogenai
import base64

def add_official_course():
    xata = XataClient(api_key=config.xata_key, db_url=config.xata_endpoint)

    # Generate the course files
    en_file, ru_file = cogenai.generate_course('python.yaml')
    en_file = str(en_file)
    ru_file = str(ru_file)
    # Encode the file contents to base64
    en_file_base64 = base64.b64encode(en_file.encode(encoding="utf-8")).decode('utf-8')
    ru_file_base64 = base64.b64encode(ru_file.encode(encoding="utf-8")).decode('utf-8')

    # Prepare the record to be inserted
    record = xata.records().insert("courses_official", {
        "en": {
            "base64Content": en_file_base64,
        },
        "ru": {
            "base64Content": ru_file_base64,
        }
    })
    return record

print(add_official_course())
