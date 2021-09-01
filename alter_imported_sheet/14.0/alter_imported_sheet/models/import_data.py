import io
import os
import xlrd
import shutil
import binascii
import tempfile
from bs4 import BeautifulSoup
from datetime import date, datetime
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import Warning, UserError


import logging

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug("Cannot `import csv`.")
try:
    import base64
except ImportError:
    _logger.debug("Cannot `import base64`.")


class ImportData(models.Model):
    _name = "import.data"

    name = fields.Char("Name", readonly=True)
    file = fields.Binary(string="Import file", attachment=True)
    import_data = fields.Html(string="Import_data")
    save_data = fields.Boolean(
        string="Save Edited Data ?",
        help="If this option is ticked saved data inside Data view will be added in Attachment Sheet also.",
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "file_attachment_rel",
        "file_id",
        "attachment_id",
        string="Attachments",
        help="Attachments are linked to a document through model / res_id and to the message "
        "through this field.",
    )
    is_csv = fields.Boolean(string="File type?")

    @api.onchange('file')
    def set_save_data(self):
        if self.save_data:
            self.save_data = False

    def write(self, vals):
        res = super(ImportData, self).write(vals)
        if self.save_data or vals.get("save_data", False) == True:
            # soup = BeautifulSoup(self.import_data) if not BeautifulSoup(vals['import_data']) else BeautifulSoup(vals['import_data'])
            soup = (
                BeautifulSoup(vals["import_data"])
                if not BeautifulSoup(self.import_data)
                else BeautifulSoup(self.import_data)
            )
            table = soup.find("table", attrs={"class": "detail_data"})
            headings = [th.get_text().strip() for th in table.find("tr").find_all("th")]
            datasets = []
            for row in table.find_all("tr")[1:]:
                dataset = [td.get_text() for td in row.find_all("td")]
                datasets.append(dataset)
            # write back to file
            try:
                current_path_ = os.getcwd()
                current_path = current_path_ + "/"
                path = os.path.join(current_path, "import_data_files")
                local_file = path + "/" + self.attachment_ids.name
                final_data = []
                final_data += headings
                for i in datasets:
                    final_data += i

                with open(local_file, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(headings)
                    for i in datasets:
                        writer.writerow(i)
                    f.close()
                with open(local_file, "rb") as fb:
                    out_file = fb.read()
                    fb.close()
                    self.attachment_ids.write(
                        {
                            "datas": base64.b64encode(out_file),
                            "mimetype": "text/csv"
                            if self.is_csv == True
                            else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        }
                    )
            except:
                raise UserError('Not found any path. Check Your current directory "import_data_files" is exist or not.')

        return res

    def load_data(self):
        attachment_data = {
            "name": self.name,
            "type": "binary",
            "datas": self.file,
            "res_model": self._name,
            "res_id": self.id,
        }
        try:
            if not self.attachment_ids:
                self.write({"attachment_ids": [(0, 0, attachment_data)]})
            if self.attachment_ids:
                if self.attachment_ids.name != self.name:
                    self.attachment_ids = [(2, r.id) for r in self.attachment_ids]
                    self.write({"attachment_ids": [(0, 0, attachment_data)]})
            keys = []
            csv_data = base64.b64decode(self.attachment_ids.datas)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            csv_reader = csv.reader(data_file, delimiter=",")
            fields = []
            rows = []
            fields = next(csv_reader)
            for row in csv_reader:
                rows.append(row)
            field_for_data = ""
            data_for_data = ""
            row_for_data = ""
            for i in fields:
                field_for_data += """<th style="font-size:15px">""" + i + """</th>"""

            for j in rows:
                for k in j:
                    data_for_data += (
                        """<td style="font-size:13px;font-weight: normal;">"""
                        + k
                        + """</td>"""
                    )
                row_for_data += """<tr>""" + data_for_data + """</tr>"""
                data_for_data = ""

            data = (
                """
                <table class="table table-bordered detail_data" style="table-layout: auto;width: 150px;">
                <tr>"""
                + field_for_data
                + """</tr>

               """
                + row_for_data
                + """
                </table>
            """
            )
            self.write({"import_data": data, "is_csv": True})

        except:
            try:
                if not self.attachment_ids:
                    self.write({"attachment_ids": [(0, 0, attachment_data)]})
                if self.attachment_ids:
                    if self.attachment_ids.name != self.name:
                        self.attachment_ids = [(2, r.id) for r in self.attachment_ids]
                        self.write({"attachment_ids": [(0, 0, attachment_data)]})
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.attachment_ids.datas))
                fp.seek(0)
                fields = []
                rows = []
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
                for row_no in range(sheet.nrows):
                    if row_no <= 0:
                        fields = list(
                            map(
                                lambda row: isinstance(row.value, bytes)
                                and row.value.encode("utf-8")
                                or str(row.value),
                                sheet.row(row_no),
                            )
                        )
                    else:
                        line = list(
                            map(
                                lambda row: isinstance(row.value, bytes)
                                and row.value.encode("utf-8")
                                or str(row.value),
                                sheet.row(row_no),
                            )
                        )
                        rows.append(line)
                field_for_data = ""
                data_for_data = ""
                row_for_data = ""
                for i in fields:
                    field_for_data += (
                        """<th style="font-size:15px">""" + i + """</th>"""
                    )

                for j in rows:
                    for k in j:
                        data_for_data += (
                            """<td style="font-size:13px;font-weight: normal;">"""
                            + k
                            + """</td>"""
                        )
                    row_for_data += """<tr>""" + data_for_data + """</tr>"""
                    data_for_data = ""
                data = (
                    """
                    <table class="table table-bordered detail_data" style="table-layout: auto;width: 150px;">
                    <tr>"""
                    + field_for_data
                    + """</tr>

                   """
                    + row_for_data
                    + """
                    </table>
                """
                )
                self.write({"import_data": data, "is_csv": False})

            except:
                raise UserError("Selected file is not csv or xlsx.")


class BaseModuleUninstall(models.TransientModel):
    _inherit = "base.module.uninstall"

    def action_uninstall(self):
        if self.module_ids.filtered(lambda r : r.name == 'alter_imported_sheet') and self.module_ids:
            try:
                current_path_ = os.getcwd()
                current_path = current_path_ + "/"
                path = os.path.join(current_path, "import_data_files")
                shutil.rmtree(path)
                return super(BaseModuleUninstall, self).action_uninstall()
            except:
                return super(BaseModuleUninstall, self).action_uninstall()
        else:
            return super(BaseModuleUninstall, self).action_uninstall()
