from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator  # Es para comentarios
from django.contrib.auth.models import User  # Es para al final en comentarios

from user_app.models import Account


# Create your models here.


class Empresa(models.Model):
    nombre = models.CharField(max_length=250)
    website = models.URLField(max_length=250)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.nombre


class Edificacion(models.Model):
    direccion = models.CharField(max_length=250)
    pais = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=500)
    imagen = models.CharField(max_length=900)
    active = models.BooleanField(default=True)
    avg_calificacion = models.FloatField(default=0)
    number_calificacion = models.IntegerField(default=0)
    empresa = models.ForeignKey(Empresa,
                                on_delete=models.CASCADE,
                                related_name="edificacionlist") # El nombre relacionado hace la
    # asociación entre ambas tablas. El término list indica que es un conjunto de valores (one many)
    created = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.direccion


class Comentario(models.Model):
    # Se agregó posteriormente
    comentario_user = models.ForeignKey(Account, on_delete=models.CASCADE)
    calificacion = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    edificacion = models.ForeignKey(
        Edificacion,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    texto = models.CharField(max_length=200, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    update = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.calificacion) + " " + self.edificacion.direccion
