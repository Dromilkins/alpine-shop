from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        coerce=int,
        label='Количество'
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        # Получаем максимальное количество из параметров
        max_quantity = kwargs.pop('max_quantity', 20)
        super().__init__(*args, **kwargs)
        self.fields['quantity'].choices = [(i, str(i)) for i in range(1, max_quantity + 1)]