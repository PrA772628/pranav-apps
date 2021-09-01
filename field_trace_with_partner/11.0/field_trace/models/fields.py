from odoo import api, fields, models, tools

class IrModelField(models.Model):
    _inherit = 'ir.model.fields'

    trace = fields.Boolean('Enable Ordered Tracking',default=False)

    def _reflect_field_params(self, field,):
        vals = super(IrModelField, self)._reflect_field_params(field)
        model = self.env['ir.model']._get(field.model_name)
        trace_f = self.env['ir.model.fields'].search([('model_id', '=', model.id),('name','=',field.name),('trace','=',True)])
        trace = False
        if trace_f and trace_f.trace == True:
            vals['trace'] = True
        else:
            vals['trace'] = False
        return vals

    def _instanciate_attrs(self, field_data):
        attrs = super(IrModelField, self)._instanciate_attrs(field_data)
        if attrs and field_data.get('trace'):
            attrs['trace'] = field_data['trace']
        return attrs


    @api.onchange('trace')
    def trace_field(self):
        self.state = 'manual'
        print('------------- onchange self : ',self)
        self.env.cr.execute('''update ir_model_fields set "state" = 'manual' where id = %(id)s''',{'id' : self._origin.id})

    def write(self,vals):
        result = super(IrModelField, self).write(vals)
        print('------------- write self : ',self)
        if vals['trace'] == True:
            self.env.cr.execute('''update ir_model_fields set "state"='base', "trace"='t' where id = %(id)s''',{'id' : self.id})
        else:
            self.env.cr.execute('''update ir_model_fields set "state"='base', "trace"='f' where id = %(id)s''',{'id' : self.id})
        return result

    

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # @tools.ormcache('self.env.uid', 'self.env.su')
    def _get_tracked_fields(self,updated_fields):
        res = super(MailThread, self)._get_tracked_fields(updated_fields)

        c_tracked_fields = []
        for name, field in self._fields.items():
            if getattr(field, 'trace', True):
                c_tracked_fields.append(name)

        if c_tracked_fields:
            return self.fields_get(c_tracked_fields)
        return res


    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        record = super(MailThread , self).message_post(body=body, subject=subject, message_type=message_type,
                     subtype=subtype, parent_id=parent_id, attachments=attachments,
                     content_subtype=content_subtype, **kwargs)
        print('\n\n\n\n------------------------- this is message created id : ',record)
        if record.partner_ids and record.model == 'sale.order':
            record.write({'author_id':record.partner_ids.ids[0]})
        return record



    def _message_track(self, tracked_fields, initial):
        changes, tracking_ids = super(MailThread, self)._message_track(tracked_fields=tracked_fields, initial=initial)
        data = []
        f_data = []
        for i,j in zip(changes,tracking_ids):
            if j[2].get('field_type') != 'datetime' and j[2].get('trace') == True:
                if j[2].get('new_value_integer') != j[2].get('old_value_integer') or j[2].get('old_value_datetime') !=  j[2].get('new_value_datetime'):
                    data.append(j)
                    f_data.append(i)
            else:
                print('----------------- problem : ',j)
        tracking_ids = data
        changes = set(f_data)
        return changes, tracking_ids


class MailTracking(models.Model):
    _inherit = 'mail.tracking.value'

    trace = fields.Boolean(default=False)

    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info):
        attrs = super(MailTracking, self).create_tracking_values(initial_value=initial_value,new_value=new_value,col_name=col_name,col_info=col_info)
        field = self.env['ir.model.fields']._get(self.env.context.get('params').get('model') if self.env.context and self.env.context.get('params') and self.env.context.get('params').get('model') else None, col_name)
        if attrs:
            attrs['trace'] = True if field.trace == True else False
        return attrs

