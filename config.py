import json

with open('./env.json') as f:
    loaded_json = json.load(f)

    DBINFO = loaded_json['db_info']
    CONTRACT_INFO = loaded_json['contract_info']
    MAILER_INFO = loaded_json['mailer']

# TODO: Modify here!
MAIL_TEMPLATE = """
<TEXT> {tx_hash} {address}
"""
