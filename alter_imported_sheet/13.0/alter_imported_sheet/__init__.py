import os
from . import models
from odoo.exceptions import UserError

def create_dir(cr, registry):
    try:
        current_path_ = os.getcwd()
        current_path = current_path_ + '/'
        path = os.path.join(current_path, "import_data_files")
        os.mkdir(path)
    except:
        raise UserError("Path is not created. please contact to your system administrator")