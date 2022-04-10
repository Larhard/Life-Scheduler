import wtforms.widgets


class CheckboxInput(wtforms.widgets.CheckboxInput):
    def __call__(self, field, **kwargs):
        if field.disabled:
            kwargs["disabled"] = True

        return super().__call__(field, **kwargs)


class BooleanField(wtforms.BooleanField):
    widget = CheckboxInput()
    disabled = False
