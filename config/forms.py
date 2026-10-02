from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout

ALERT = HTML("""
    <div class="alert alert-info" role="alert">
        Fo hatene katak kampu ho simbolu Asterik <strong>(*)</strong> obrigatóriu tenki prienxe.!
    </div>
""")

BUTTONS = HTML("""
    <div class="mt-4">
        <button class="btn btn-sm btn-success" type="submit">
            <i class="fa fa-save"></i> Save
        </button>
        <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
            <i class="fa fa-times"></i> Cancel
        </button>
    </div>
""")


def bootstrap_widgets(form):
	"""Tau class Bootstrap ba kampu hotu-hotu iha form."""
	for field in form.fields.values():
		widget = field.widget
		css = 'form-check-input' if getattr(widget, 'input_type', '') == 'checkbox' else 'form-control'
		widget.attrs.update({'class': css})


def make_helper(*rows):
	"""FormHelper ho alerta, kampu (Row/Column) no botaun Save/Cancel."""
	helper = FormHelper()
	helper.form_method = 'post'
	helper.layout = Layout(ALERT, *rows, BUTTONS)
	return helper
