from xata.client import XataClient
import asyncio
import config

async def init_db():
    xata = XataClient(api_key=config.xata_key, db_url=config.xata_endpoint)
    schema_users = {"columns": [{"name": "language","type": "string"},{'name':'courses','type': 'text'},{'name': 'status','type': 'string'}]}
    schema_courses_community ={'columns': [{'name': 'en', 'type': 'file'},{'name': 'ru','type': 'file'},{'name': "user_id",'type': 'int'}]}
    schema_courses_verified = {'columns': [{'name': 'en','type': 'file'},{'name': 'ru','type': 'file'},{'name': "user_id",'type': 'int'}]}
    schema_courses_official={'columns': [{'name': 'en','type': 'file'},{'name': 'ru','type': 'file'}]}
    xata.table().create('users')
    xata.table().create('courses_community')
    xata.table().create('courses_verified')
    xata.table().create('courses_official')

    xata.table().set_schema('users', schema_users)
    xata.table().set_schema('courses_community', schema_courses_community)
    xata.table().set_schema('courses_verified', schema_courses_verified)
    xata.table().set_schema('courses_official', schema_courses_official)

    return 'ok'
