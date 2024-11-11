from xata.client import XataClient
import config
import cogenai
import base64
import table_init
import asyncio

def community_course(file, user_id):
    xata = XataClient(api_key=config.xata_key, db_url=config.xata_endpoint)
    print('Initialising table')
    asyncio.run(table_init.init_db())
    # Generate the course files
    cogenai.generate_course(file)
    # Encode the file contents to base64
    input("Check files and press 'Enter' if done")
    with open(f'{file}.by.gen.txt') as f: by = f.read()
    with open(f'{file}.eng.gen.txt') as f: en = f.read()
    with open(f'{file}.ru.gen.txt') as f: ru = f.read()
    en_file_base64 = base64.b64encode(en.encode(encoding="utf-8")).decode('utf-8')
    ru_file_base64 = base64.b64encode(ru.encode(encoding="utf-8")).decode('utf-8')
    by_file_base64 = base64.b64encode(by.encode(encoding='utf-8')).decode('utf-8')
    # Prepare the record to be inserted
    record = xata.records().insert("courses_community", {
        "en": {
            "base64Content": en_file_base64,
        },
        "ru": {
            "base64Content": ru_file_base64,
        },
        "by": {
           'base64Content': by_file_base64,
        },
        "user_id": int(user_id)
    })
    return record

print(community_course('s.yaml', '1437220885'))
