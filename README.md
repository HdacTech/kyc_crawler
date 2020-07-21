# KYC crawler

## Initial DB schema creation

Use `create.sql`

## Install dependencies

`pip3 install -r requirements.txt`

## Prerequisite

### Credential setting

Create `env.json` using `env.example.json` and revise as below:

```json
{
    "db_info": {
        "host": "<address>",
        "db": "atolo",
        "user": "<db_user>",
        "password": "<password>"
    },
    "contract_info": {
        "rest_server": "",
        "admin_mnemonic": "",
        "swap_proxy": "",
        "swap_hash": ""
    },
    "mailer" : {
        "host": "",
        "sender": "",
        "password": ""
    }
}
```

* `db_info.host`: Host address of AWS RDB
* `db_info.db`: Database name of AWS RDB
* `db_info.user`: Database user
* `db_info.password`: Password of the user

<br />

* `contract_info.rest_server`: Address of rest server of ATOLO blockchain
* `contract_info.admin_mnemonic`: Mnemonic words of admin account
* `contract_info.swap_proxy`: Contract address of `swap_proxy`
* `contract_info.swap_hash`: Contact address of `swap_hash`

<br />

* `mailer.host`: SMTP server address of a mailer
* `mailer.sender`: Sender account of the SMTP server
* `mailer.password`: Password of the sender account

### Main scheduler

* `python3 kyc_crawler_from_argos.py`: Gather KYC complete information and input to DB
* `python3 kyc_info_save_to_chain.py`: Execute KYC save contract to chain
* `python3 send_mail.py`: Send mail alert to the KYC registerers
