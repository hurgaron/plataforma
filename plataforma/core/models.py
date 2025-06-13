# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    chave = models.CharField(max_length=32, unique=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class UsuarioManager(BaseUserManager):
    def create_user(self, email, empresa, senha=None, **extra_fields):
        if not email:
            raise ValueError("Email obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, empresa=empresa, **extra_fields)
        user.set_password(senha)
        user.save()
        return user

    def create_superuser(self, email, senha=None, **extra_fields):
        empresa = Empresa.objects.first() or Empresa.objects.create(nome='Sistema', cnpj='00.000.000/0001-00', chave='sistema')
        return self.create_user(email, empresa, senha, is_staff=True, is_superuser=True, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'ADMIN'
    COLABORADOR = 'COLAB'
    TIPO_USUARIO = [
        (ADMIN, 'Administrador'),
        (COLABORADOR, 'Colaborador'),
    ]

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO, default=COLABORADOR)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'empresa']

    objects = UsuarioManager()

    def __str__(self):
        return f'{self.nome} ({self.empresa.nome})'
