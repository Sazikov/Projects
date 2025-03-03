from django import forms


class EditUserForm(forms.Form):

    user_surname = forms.CharField(max_length=63, min_length=2, label='Фамилия', required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Фамилия'}))

    user_name = forms.CharField(max_length=63, min_length=2, label='Имя', required=True,
                                widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Имя'}))

    user_name2 = forms.CharField(max_length=63, min_length=2, label='Отчество', required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Отчество'}))

    date_birth = forms.DateField(label="Дата рождения", required=True, widget=forms.DateInput(attrs={'type': 'date',
                                                                                                     'class': 'form-input'}))

    comment = forms.CharField(max_length=511, min_length=4, label='Укажите дополнительную информацию о себе:', required=True,
                              widget=forms.Textarea(
                                 attrs={'class': 'form-input', 'placeholder': 'Дополнительная информация', 'rows': 1}))


class LoginUserForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
