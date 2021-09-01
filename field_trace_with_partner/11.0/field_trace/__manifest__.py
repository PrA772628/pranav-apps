# -*- coding: utf-8 -*-
{
    "name": "Fields_traceability",
    "summary": """
       Fields Traceability""",
    "description": """   
    """,
    "author": "Vpcs",
    "version": "11.0.1.0",
    "depends": ['mail','base','sale'],
    "data": [
        'view/fields.xml',
    ],
    "demo": [],
    "post_init_hook": 'fire_query',
}
