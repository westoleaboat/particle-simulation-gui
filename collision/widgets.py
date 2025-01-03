""" 
collision/widgets.py: file containing the widgets of our app
"""

import tkinter as tk
from tkinter import ttk

from datetime import datetime
from decimal import Decimal, InvalidOperation
from .constants import FieldTypes as FT

import string

##################
# Widget Classes #
##################

class ValidatedMixin:
  """Adds a validation functionality to an input widget"""

  def __init__(self, *args, error_var=None, **kwargs):
    self.error = error_var or tk.StringVar()
    super().__init__(*args, **kwargs)

    vcmd = self.register(self._validate)
    invcmd = self.register(self._invalid)

    self.configure(
      validate='all',
      validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
      invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
    )

  def _toggle_error(self, on=False):
    self.configure(foreground=('red' if on else 'black'))

  def _validate(self, proposed, current, char, event, index, action):
    """The validation method.

    Don't override this, override _key_validate, and _focus_validate
    """
    self.error.set('')
    self._toggle_error()

    valid = True
    # if the widget is disabled, don't validate
    state = str(self.configure('state')[-1])
    if state == tk.DISABLED:
      return valid

    if event == 'focusout':
      valid = self._focusout_validate(event=event)
    elif event == 'key':
      valid = self._key_validate(
      proposed=proposed,
      current=current,
      char=char,
      event=event,
      index=index,
      action=action
    )
    return valid

  def _focusout_validate(self, **kwargs):
    return True

  def _key_validate(self, **kwargs):
    return True

  def _invalid(self, proposed, current, char, event, index, action):
    if event == 'focusout':
      self._focusout_invalid(event=event)
    elif event == 'key':
      self._key_invalid(
        proposed=proposed,
        current=current,
        char=char,
        event=event,
        index=index,
        action=action
      )

  def _focusout_invalid(self, **kwargs):
    """Handle invalid data on a focus event"""
    self._toggle_error(True)

  def _key_invalid(self, **kwargs):
    """Handle invalid data on a key event.  By default we want to do nothing"""
    pass

  def trigger_focusout_validation(self):
    valid = self._validate('', '', '', 'focusout', '', '')
    if not valid:
      self._focusout_invalid(event='focusout')
    return valid


class DateEntry(ValidatedMixin, ttk.Entry):

  def _key_validate(self, action, index, char, **kwargs):
    valid = True

    if action == '0':  # This is a delete action
      valid = True
    elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
      valid = char.isdigit()
    elif index in ('4', '7'):
      valid = char == '-'
    else:
      valid = False
    return valid

  def _focusout_validate(self, event):
    valid = True
    if not self.get():
      self.error.set('A value is required')
      valid = False
    try:
      datetime.strptime(self.get(), '%Y-%m-%d')
    except ValueError:
      self.error.set('Invalid date')
      valid = False
    return valid


class RequiredEntry(ValidatedMixin, ttk.Entry):

  def _focusout_validate(self, event):
    valid = True
    if not self.get():
      valid = False
      self.error.set('A value is required')
    return valid


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):

  def _key_validate(self, proposed, action, **kwargs):
    valid = True
    # if the user tries to delete,
    # just clear the field
    if action == '0':
      self.set('')
      return True

    # get our values list
    values = self.cget('values')
    # Do a case-insensitve match against the entered text
    matching = [
      x for x in values
      if x.lower().startswith(proposed.lower())
    ]
    if len(matching) == 0:
      valid = False
    elif len(matching) == 1:
      self.set(matching[0])
      self.icursor(tk.END)
      valid = False
    return valid

  def _focusout_validate(self, **kwargs):
    valid = True
    if not self.get():
      valid = False
      self.error.set('A value is required')
    return valid


class ValidatedSpinbox(ValidatedMixin, ttk.Spinbox):
  """A Spinbox that only accepts Numbers"""

  def __init__(self, *args, min_var=None, max_var=None,
    focus_update_var=None, from_='-Infinity', to='Infinity', **kwargs
   ):
    super().__init__(*args, from_=from_, to=to, **kwargs)
    increment = Decimal(str(kwargs.get('increment', '1.0')))
    self.precision = increment.normalize().as_tuple().exponent
    # there should always be a variable,
    # or some of our code will fail
    self.variable = kwargs.get('textvariable')
    if not self.variable:
      self.variable = tk.DoubleVar()
      self.configure(textvariable=self.variable)

    if min_var:
      self.min_var = min_var
      self.min_var.trace_add('write', self._set_minimum)
    if max_var:
      self.max_var = max_var
      self.max_var.trace_add('write', self._set_maximum)
    self.focus_update_var = focus_update_var
    self.bind('<FocusOut>', self._set_focus_update_var)

  def _set_focus_update_var(self, event):
    value = self.get()
    if self.focus_update_var and not self.error.get():
      self.focus_update_var.set(value)

  def _set_minimum(self, *_):
    current = self.get()
    try:
      new_min = self.min_var.get()
      self.config(from_=new_min)
    except (tk.TclError, ValueError):
      pass
    if not current:
      self.delete(0, tk.END)
    else:
      self.variable.set(current)
    self.trigger_focusout_validation()

  def _set_maximum(self, *_):
    current = self.get()
    try:
      new_max = self.max_var.get()
      self.config(to=new_max)
    except (tk.TclError, ValueError):
      pass
    if not current:
      self.delete(0, tk.END)
    else:
      self.variable.set(current)
    self.trigger_focusout_validation()

  def _key_validate(
    self, char, index, current, proposed, action, **kwargs
  ):
    if action == '0':
      return True
    valid = True
    min_val = self.cget('from')
    max_val = self.cget('to')
    no_negative = min_val >= 0
    no_decimal = self.precision >= 0

    # First, filter out obviously invalid keystrokes
    if any([
        (char not in '-1234567890.'),
        (char == '-' and (no_negative or index != '0')),
        (char == '.' and (no_decimal or '.' in current))
    ]):
      return False

    # At this point, proposed is either '-', '.', '-.',
    # or a valid Decimal string
    if proposed in '-.':
      return True

    # Proposed is a valid Decimal string
    # convert to Decimal and check more:
    proposed = Decimal(proposed)
    proposed_precision = proposed.as_tuple().exponent

    if any([
      (proposed > max_val),
      (proposed_precision < self.precision)
    ]):
      return False

    return valid

  def _focusout_validate(self, **kwargs):
    valid = True
    value = self.get()
    min_val = self.cget('from')
    max_val = self.cget('to')

    try:
      d_value = Decimal(value)
    except InvalidOperation:
      self.error.set(f'Invalid number string: {value}')
      return False

    if d_value < min_val:
      self.error.set(f'Value is too low (min {min_val})')
      valid = False
    if d_value > max_val:
      self.error.set(f'Value is too high (max {max_val})')
      valid = False

    return valid

class ValidatedRadioGroup(ttk.Frame):
  """A validated radio button group"""

  def __init__(
    self, *args, variable=None, error_var=None,
    values=None, button_args=None, **kwargs
  ):
    
    super().__init__(*args, **kwargs)
    self.variable = variable or tk.StringVar()
    self.error = error_var or tk.StringVar()
    self.values = values or list()
    self.button_args = button_args or dict()

    for v in self.values:
      button = ttk.Radiobutton(
        self, value=v, text=v,
        variable=self.variable, **self.button_args
      )
      button.pack(
        side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x'
      )
    self.bind('<FocusOut>', self.trigger_focusout_validation)

  def trigger_focusout_validation(self, *_):
    self.error.set('')
    if not self.variable.get():
      self.error.set('A value is required')


class BoundText(tk.Text):
  """A Text widget with a bound variable.

    Add the following to Text widget:      
          -pass in a StringVar, which it will be bound to
          -update widget contents whenever the variable is updated;
             for example if loaded in from file or changed by other widget
          -update variable contents whenever widget is updated;
             for example when user types or pastes content into widget

    Override initializer to allow a control variable to be passed in,
    use textvariable argument to pass in a StringVar object
  """

  def __init__(self, *args, textvariable=None, **kwargs):
    super().__init__(*args, **kwargs)
    self._variable = textvariable
    if self._variable:
      # insert any default value
      self.insert('1.0', self._variable.get())
      self._variable.trace_add('write', self._set_content)
      self.bind('<<Modified>>', self._set_var)

    # Configure tags for different character types and colors
    self.tag_configure("integer", foreground="blue")
    self.tag_configure("special", foreground="red")
    self.tag_configure("letter", foreground="green")

  def _set_var(self, *_):
    """Set the variable to the text contents"""
    if self.edit_modified():
      content = self.get('1.0', 'end-1chars')
      self._variable.set(content)
      self.edit_modified(False)

  def _set_content(self, *_):
    """Set the text contents to the variable"""
    self.delete('1.0', tk.END)
    # self.insert('1.0', self._variable.get())
    
    content = self._variable.get()        # for adding color to text widget
    self.insert_with_tags(content)        # depending on tags

  def insert_with_tags(self, content):
        """Insert text with different tags for integer, special, and letter characters."""
        for char in content:
            if char in string.ascii_letters:
                self.insert(tk.END, char, "letter")
            elif char in string.digits:
                self.insert(tk.END, char, "integer")
            elif char in string.punctuation:
                self.insert(tk.END, char, "special")
            else:
                self.insert(tk.END, char)  # Default tag (no style)

###########################
# Compound Widget Classes #
###########################


class LabelInput(ttk.Frame):
  """A widget containing a label and input together.
    Minimal set of arguments may be:
    
        -parent widget
        -text for the label
        -type of input widget to use
        -dictionary of arguments to pass to input widget

    Call superclass initializer so Frame widget can be constructed.
    Pass parent argument, since that will be the parent widget of
    the Frame itsel, the parent widget for the Label and input
    widget is self, that is, the LabelInput object itself.
    It requires a variable to be bound to each widget (since each
    widget can be bound to one) and an extra dict arg to pass to 
    label widget, in case needed.
    Defaults input_class to ttk.Entry for being the most common case.
    demo:
          LabelInput(
              frame, 'Notes',
              input_class=BoundText, var=self._vars['Notes'],
              input_args={"width": 75, "height": 10}
          ).grid(sticky=tk.W + tk.E)

    **Default arguments are evaluated when the function definition is first run. 
    This means that a dictionary object created in the function signature will 
    be the same object every time the function is run, rather than a fresh, 
    empty dictionary each time. 
    Since we want a fresh, empty dictionary each time, we create the dictionaries 
    inside the function body rather than the argument list.
    To use RadioButton widgets with LabelInput, we need to pass in a
    list of values to the input arguments, just as for Combobox.
  """

  # this dictonary act as a key to translate our model's
  # field types into an appropiate widget type
  field_types = {
    FT.string: RequiredEntry,
    FT.string_list: ValidatedCombobox,
    FT.short_string_list: ValidatedRadioGroup,
    FT.iso_date_string: DateEntry,
    FT.long_string: BoundText,
    FT.decimal: ValidatedSpinbox,
    FT.integer: ValidatedSpinbox,
    FT.boolean: ttk.Checkbutton
  }

  def __init__(
    self, parent, label, var, input_class=None,
    input_args=None, label_args=None, field_spec=None,
    disable_var=None, **kwargs
  ):
    super().__init__(parent, **kwargs)
    input_args = input_args or {}
    label_args = label_args or {}
    # save input_var to an instance variable
    self.variable = var
    # save label as property of the variable object
    # to avoid references to LabelInput objects;
    # can access them through variable object if needed.
    self.variable.label_widget = self

    # Process the field spec to determine input_class and validation
    if field_spec:
      field_type = field_spec.get('type', FT.string)
      input_class = input_class or self.field_types.get(field_type)
      # min, max, increment
      if 'min' in field_spec and 'from_' not in input_args:
        input_args['from_'] = field_spec.get('min')
      if 'max' in field_spec and 'to' not in input_args:
        input_args['to'] = field_spec.get('max')
      if 'inc' in field_spec and 'increment' not in input_args:
        input_args['increment'] = field_spec.get('inc')
        # values
      if 'values' in field_spec and 'values' not in input_args:
        input_args['values'] = field_spec.get('values')

    # setup the label
    if input_class in (ttk.Checkbutton, ttk.Button):
      # Buttons don't need labels, they're built-in
      input_args["text"] = label
    else:
      self.label = ttk.Label(self, text=label, **label_args)
      self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

    # setup the variable
    if input_class in (
        ttk.Checkbutton, ttk.Button, ttk.Radiobutton, ValidatedRadioGroup
    ):
      input_args["variable"] = self.variable
    else:
      input_args["textvariable"] = self.variable

    # Setup the input
    if input_class == ttk.Radiobutton:
      # for Radiobutton, create one input per value
      self.input = tk.Frame(self)
      for v in input_args.pop('values', []):
        button = input_class(
          self.input, value=v, text=v, **input_args
        )
        button.pack(side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x')
    else:
      self.input = input_class(self, **input_args)
    # with self.input created, add to layout
    self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
    self.columnconfigure(0, weight=1)

    # Set up error handling & display
    self.error = getattr(self.input, 'error', tk.StringVar())
    ttk.Label(self, textvariable=self.error).grid(
      row=2, column=0, sticky=(tk.W + tk.E)
    )

    # Set up disable variable
    if disable_var:   # p.154
      self.disable_var = disable_var
      self.disable_var.trace_add('write', self._check_disable)

  def _check_disable(self, *_):
    if not hasattr(self, 'disable_var'):
      return

    if self.disable_var.get():
      self.input.configure(state=tk.DISABLED)
      self.variable.set('')
      self.error.set('')
    else:
      self.input.configure(state=tk.NORMAL)

  def grid(self, sticky=(tk.E + tk.W), **kwargs):
    """Override grid to add default sticky values"""
    # widget to stick to the left and right sides of container w/ max width possible.
    # rather than passing sticky=(tk.E + tk.W) every time
    super().grid(sticky=sticky, **kwargs)

