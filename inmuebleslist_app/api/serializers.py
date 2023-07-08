from rest_framework import serializers
from inmuebleslist_app.models import Edificacion, Empresa, Comentario
# core arguments: son las restricciones que se imponen a los campos (por ejemplo, id solo lectura)


class ComentariosSerializer(serializers.ModelSerializer):
    # Será un valor registrado
    comentario_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        exclude = ['edificacion']
        # fields = "__all__"


class EdificacionSerializer(serializers.ModelSerializer):
    # para campos calculados
    # longitud_direccion = serializers.SerializerMethodField()
    comentarios = ComentariosSerializer(many=True, read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre')

    class Meta:
        model = Edificacion
        fields = "__all__"  # O se definen, o que realice todos de manera automática
        # fields = ['id', 'pais', 'active', 'imagen']
        # exclude = ['id']  # Todos a excepción de


# Para hacer que la URL de la empresa sea mejor su id
# class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
class EmpresaSerializer(serializers.ModelSerializer):
    edificacionlist = EdificacionSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = "__all__"

# class EmpresaSerializer(serializers.ModelSerializer):
    # edificacionlist = EdificacionSerializer(many=True, read_only=True)
    # edificacionlist = serializers.StringRelatedField(many=True)
    # edificacionlist = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    # Para que marque como URL la información de los inmuebles
    # edificacionlist = serializers.HyperlinkedRelatedField(
    #    many=True,
    #    read_only=True,
    #    view_name='edificacion-detalle'
    # )

    # class Meta:
    #    model = Empresa
    #    fields = "__all__"


#    @staticmethod
#    def get_longitud_direccion(object):
#        cantidad_caracteres = len(object.direccion)
#        return cantidad_caracteres
#
#    def validate(self, data):
#        if data['direccion'] == data['pais']:
#            raise serializers.ValidationError("La dirección y el pais deben ser diferentes")
#        else:
#            return data
#
#    def validate_imagen(self, data):
#        if len(data) < 2:
#            raise serializers.ValidationError("La url de la imagen es muy corta")
#        else:
#            return data
#

# def longitud_columna(value):
#    if len(value) < 2:
#        raise serializers.ValidationError("El valor es demasiado corto")


# class InmuebleSerializer(serializers.Serializer):
#    id = serializers.IntegerField(read_only=True)
#    direccion = serializers.CharField(validators=[longitud_columna])
#    pais = serializers.CharField(validators=[longitud_columna])
#    descripcion = serializers.CharField()
#    imagen = serializers.CharField()
#    active = serializers.BooleanField()

#    def create(self, validated_data):
#        return Inmueble.objects.create(**validated_data)

#    def update(self, instance, validated_data):
#        instance.direccion = validated_data.get('direccion', instance.direccion)
#        instance.pais = validated_data.get('pais', instance.pais)
#        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
#        instance.imagen = validated_data.get('imagen', instance.imagen)
#        instance.active = validated_data.get('active', instance.active)
#        instance.save()
#        return instance

#    def validate(self, data):
#        if data['direccion'] == data['descripcion']:
#            raise serializers.ValidationError("La dirección y descripción no pueden ser idénticos")
#        else:
#            return data
