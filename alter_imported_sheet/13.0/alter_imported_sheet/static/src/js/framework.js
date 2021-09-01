odoo.define('alter_imported_sheet.framework', function(require) {
    "use strict";
    var fc = require("web.FormController");
    var rf = require("web.relational_fields")

    var relational_fields_inc = rf.FieldMany2ManyBinaryMultiFiles.include({
        _render: function() {
            this._super();
            if (this.model == 'import.data') {
                this.$('div.o_attachment_delete').remove();
                this.$('div.oe_add').remove();
            }
        },
    })
    var FormController1 = fc.include({
        remove_class: function() {
            $(document).ready(function() {
                if (this.location.href.split("&").length > 2 && this.location.href.split("&")[2].substring(6) == "import.data") {
                    if (document.querySelectorAll('.note-toolbar')) {
                        document.querySelectorAll('.note-toolbar').forEach(function(a) {
                            a.remove();
                        })
                    }
                }
            });
        },
        _onEdit: function() {
            this.remove_class();
            this._super();
        },
    })
});