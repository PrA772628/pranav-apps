{
    "name": "Alter Imported Sheet",
    "version": "13.0.1.0.0",
    "application": True,
    "website": "https://vperfectcs.com",
    "author": "Vperfectcs",
    "category": "Extra Tools",
    "description": """
        import data from csv and xlsx file then you can edit and save data.
    """,
    "depends": ["web"],
    "external_dependencies": {
        "python": [
            "beautifulsoup4",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/import_data.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "post_init_hook": "create_dir",
}
