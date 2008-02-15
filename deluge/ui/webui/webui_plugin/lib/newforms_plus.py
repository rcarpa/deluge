# -*- coding: utf-8 -*-
#
# Copyright (C) Martijn Voncken 2008 <mvoncken@gmail.com>
# Django Lisence, see ./newforms/LICENCE
#

from newforms import *
import newforms
from newforms.forms import BoundField

import sys, os

import webpy022 as web #todo:remove this dependency.







#Form
class FilteredForm(newforms.Form):
    """
    used to enable more complex layouts.
    the filter argument contains the names of the fields to render.
    """
    def _html_output_filtered(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row, filter):
        """
        Helper function for outputting HTML. Used by as_table(), as_ul(), as_p().
        newforms_plus: 99% c&p from newforms, added filter.
        """
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        for name, field in self.fields.items():
            #FilteredForm
            if (filter != None) and (not name in filter):
                continue
            #/FilteredForm
            bf = BoundField(self, field, name)
            bf_errors = ErrorList([escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend(['(Hidden field %s) %s' % (name, e) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                if errors_on_separate_row and bf_errors:
                    output.append(error_row % bf_errors)
                label = bf.label and bf.label_tag(escape(bf.label + ':')) or ''
                if field.help_text:
                    help_text = help_text_html % field.help_text
                else:
                    help_text = u''
                output.append(normal_row % {'errors': bf_errors, 'label': label, 'field': unicode(bf), 'help_text': help_text})
        if top_errors:
            output.insert(0, error_row % top_errors)
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and insert the hidden fields.
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else: # If there aren't any rows in the output, just append the hidden fields.
                output.append(str_hidden)
        return u'\n'.join(output)

    def as_table(self , filter = None): #add class="newforms"
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output_filtered(u'<tr><th class="newforms">%(label)s</th><td class="newforms">%(errors)s%(field)s%(help_text)s</td></tr>', u'<tr><td colspan="2">%s</td></tr>', '</td></tr>', u'<br />%s', False, filter)

    def as_ul(self, filter = None):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output_filtered(u'<li>%(errors)s%(label)s %(field)s%(help_text)s</li>', u'<li>%s</li>', '</li>', u' %s', False , filter)

    def as_p(self , filter = None):
        "Returns this form rendered as HTML <p>s."
        return self._html_output_filtered(u'<p>%(label)s %(field)s%(help_text)s</p>', u'<p>%s</p>', '</p>', u' %s', True, filter)

class Form(FilteredForm):
    info = ""
    title = "No Title"
    def __init__(self,data = None):
        if data == None:
            data = self.initial_data()
        newforms.Form.__init__(self,data)

    def initial_data(self):
        "override in subclass"
        return None

    def start_save(self):
        "called by config_page"
        data = web.Storage(self.clean_data)
        self.validate(data)
        self.save(data)
        self.post_save()

    def save(self, vars):
        "override in subclass"
        raise NotImplementedError()

    def post_save(self):
        pass

    def validate(self, data):
        pass

#convenience Input Fields.
class CheckBox(newforms.BooleanField):
    "Non Required BooleanField,why the f is it required by default?"
    def __init__(self,label, **kwargs):
        newforms.BooleanField.__init__(self,label=label,required=False,**kwargs)

class IntChoiceField(newforms.ChoiceField):
    """same as ChoiceField, but returns an int
    hint : Use IntChoiceField(choices=enumerate("list","of","strings"]))
             for index-based values on a list of strings.
    """
    def __init__(self, label, choices, **kwargs):
        newforms.ChoiceField.__init__(self, label=label, choices=choices,**kwargs)

    def clean(self, value):
        return int(newforms.ChoiceField.clean(self, value))

class MultipleChoice(newforms.MultipleChoiceField):
    #temp/test/debug!!
    "Non Required MultipleChoiceField,why the f is it required by default?"
    def __init__(self, label, choices, **kwargs):
        newforms.MultipleChoiceField.__init__(self, label=label, choices=choices,
            widget=newforms.CheckboxSelectMultiple, required=False)

class ServerFolder(newforms.CharField):
    def __init__(self, label, **kwargs):
        newforms.CharField.__init__(self, label=label,**kwargs)

    def clean(self, value):
        if value == None:
            value = ""
        value = value.rstrip('/').rstrip('\\')
        self.validate(value)
        return newforms.CharField.clean(self, value)

    def validate(self, value):
        if (value and not os.path.isdir(value)):
            raise newforms.ValidationError(_("This folder does not exist."))

class Password(newforms.CharField):
    def __init__(self, label, **kwargs):
        newforms.CharField.__init__(self, label=label, widget=newforms.PasswordInput,
            **kwargs)

#Deluge specific:
class _DelugeIntInput(newforms.TextInput):
    """
    because deluge-floats are edited as ints.
    """
    def render(self, name, value, attrs=None):
        try:
            value = int(float(value))
            if value == -1:
                value = _("Unlimited")
        except:
            pass
        return newforms.TextInput.render(self, name, value, attrs)

class DelugeInt(newforms.IntegerField):
    def __init__(self, label , **kwargs):
        newforms.IntegerField.__init__(self, label=label, min_value=-1,
            max_value=sys.maxint, widget=_DelugeIntInput, **kwargs)

    def clean(self, value):
        if str(value).lower() == _('Unlimited').lower():
            value = -1
        return int(newforms.IntegerField.clean(self, value))

class DelugeFloat(DelugeInt):
    def clean(self, value):
        return int(DelugeInt.clean(self, value))

#/fields





