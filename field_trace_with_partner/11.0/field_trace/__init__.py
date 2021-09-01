from . import models


def fire_query(cr, registry):
	cr.execute('''update ir_model_fields set "trace" = 't' where "track_visibility" is NOT NULL''')
	print('--------------------- done')
