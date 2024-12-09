from django import forms
from .models import Perfil, Cliente, TipoDispositivo, PerfilCuenta

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['notas', 'id_cliente', 'id_tipo_dispositivo', 'id_perfil_cuenta']
        widgets = {
            'notas': forms.TextInput(attrs={'class': 'form-control'}),
            'id_cliente': forms.Select(attrs={'class': 'form-control'}),
            'id_tipo_dispositivo': forms.Select(attrs={'class': 'form-control'}),
            'id_perfil_cuenta': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_cliente'].queryset = Cliente.objects.all()
        self.fields['id_tipo_dispositivo'].queryset = TipoDispositivo.objects.all()
        self.fields['id_perfil_cuenta'].queryset = PerfilCuenta.objects.filter(asignado=False)
