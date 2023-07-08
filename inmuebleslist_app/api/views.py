from rest_framework.permissions import IsAuthenticated  # Cuando el acceso es para un área
from rest_framework.response import Response
from inmuebleslist_app.api.pagination import EdificacionPagination, EdificacionLOPagination
from inmuebleslist_app.models import Edificacion, Empresa, Comentario
from inmuebleslist_app.api.serializers import EdificacionSerializer, \
    EmpresaSerializer, ComentariosSerializer
# from rest_framework.decorators import api_view # No se utiliza en conjunto con la clase
from rest_framework import status, generics, viewsets  # mixins
from rest_framework.views import APIView  # apiview es para juntar las definiciones
# from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from inmuebleslist_app.api.permissions import IsComentarioUserOrReadOnly, IsAdminOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from inmuebleslist_app.api.throttling import ComentarioListThrottle, ComentarioCreateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


# https://jsonviewer.stack.hu/


class UsuarioComentario(generics.ListAPIView):
    serializer_class = ComentariosSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        return Comentario.objects.filter(comentario_user__username=username)
    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Comentario.objects.filter(comentario_user__username = username)


class ComentarioCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ComentariosSerializer
    throttle_classes = [ComentarioCreateThrottle]

    def get_queryset(self):
        return Comentario.objects.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        inmueble = Edificacion.objects.get(pk=pk)
        user = self.request.user
        # Si no se quiere que el usuario deje más de 2 comentarios para la misma edificacion
        comentario_queryset = Comentario.objects.filter(
            edificacion=inmueble,
            comentario_user=user
        )
        if comentario_queryset.exists():
            raise ValidationError("El usuario ya dejó un comentario para el inmueble")
        if inmueble.number_calificacion == 0:
            inmueble.avg_calificacion = serializer.validated_data['calificacion']
        else:
            inmueble.avg_calificacion = (serializer.validated_data['calificacion'] + inmueble.avg_calificacion) / 2
        inmueble.number_calificacion = inmueble.number_calificacion + 1
        inmueble.save()
        serializer.save(edificacion=inmueble, comentario_user=user)


class ComentarioList(generics.ListCreateAPIView):  # Clase concreta
    # queryset = Comentario.objects.all()
    serializer_class = ComentariosSerializer  # Automáticamente crea el response
    # Hasta que haya iniciado sesión
    # https://www.base64encode.org/
    # permission_classes = [IsAuthenticated]
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]
    throttle_classes = [ComentarioListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comentario_user__username', 'active']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comentario.objects.filter(edificacion=pk)  # Los comentarios de ese inmueble


class ComentarioDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentariosSerializer  # Hace una herencia de clase
    # el problema es que envía toda la información, y no por el id, por lo que es necesario
    # modificar la forma como realiza la forma
    permission_classes = [IsComentarioUserOrReadOnly]
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'comentario-detail'

# class ComentarioList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#    queryset = Comentario.objects.all()
#    serializer_class = ComentariosSerializer
#
#    def get(self, request, *args, **kwargs):
#        return self.list(request, *args, **kwargs)
#
#    def post(self, request, *args, **kwargs):
#        return self.create(request, *args, **kwargs)
#
#


# class ComentarioDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#    queryset = Comentario.objects.all()
#    serializer_class = ComentariosSerializer
#
#    def get(self, request, *args, **kwargs):
#        return self.retrieve(request, *args, **kwargs)
#


# class EmpresaVS(viewsets.ViewSet):  # VS ViewSet Clase que ya tiene definidos los métodos, pero
#    # se están sobreescribiendo
#    def list(self, request):
#        queryset = Empresa.objects.all()
#        serializer = EmpresaSerializer(queryset, many=True)
#        return Response(serializer.data)
#
#    def retrieve(self, request, pk=None):
#        queryset = Empresa.objects.all()
#        edificacionlist = get_object_or_404(queryset, pk=pk)
#        serializer = EmpresaSerializer(edificacionlist)
#        return Response(serializer.data)
#
#    def create(self, request):
#        serializer = EmpresaSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        else:
#            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#    def update(self, request, pk):
#        try:
#            empresa = Empresa.objects.get(pk=pk)
#        except Empresa.DoesNotExist:
#            return Response({'error' : 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
#        serializer = EmpresaSerializer(empresa, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        else:
#            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#    def destroy(self, request, pk):
#        try:
#            empresa = Empresa.objects.get(pk=pk)
#        except Empresa.DoesNotExist:
#            return Response({'error' : 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
#        empresa.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
#

class EmpresaVS(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    

class EmpresaAV(APIView):
    @staticmethod
    def get(request):
        inmuebles = Empresa.objects.all()
        # serializer = EmpresaSerializer(inmuebles, many=True)
        serializer = EmpresaSerializer(inmuebles, many=True, context={'request': request})
        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Esta clase sería al final
class EmpresaDetalleAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @staticmethod
    def get(request, pk):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'Error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpresaSerializer(empresa, context={'request': request})
        return Response(serializer.data)

    @staticmethod
    def put(request, pk):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'Error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpresaSerializer(empresa, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(pk):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'Error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        empresa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EdificacionList(generics.ListAPIView):
    queryset = Edificacion.objects.all()
    serializer_class = EdificacionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = EdificacionPagination   # EdificacionLOPagination
    # filter_backends = [DjangoFilterBackend]
    search_fields = ['direccion', 'empresa__nombre']


class EdificacionAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @staticmethod
    def get(request):
        inmuebles = Edificacion.objects.all()
        serializer = EdificacionSerializer(inmuebles, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = EdificacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EdificacionDetalleAV(APIView):
    @staticmethod
    def get(request, pk):
        try:
            inmueble = Edificacion.objects.get(pk=pk)
        except Edificacion.DoesNotExist:
            return Response(('Error', 'Edificacion no encontrado'), status=status.HTTP_404_NOT_FOUND)
        serializer = EdificacionSerializer(inmueble)
        return Response(serializer.data)

    @staticmethod
    def put(request, pk):
        try:
            inmueble = Edificacion.objects.get(pk=pk)
        except Edificacion.DoesNotExist:
            return Response(('Error', 'Edificacion no encontrado'), status=status.HTTP_404_NOT_FOUND)
        serializer = EdificacionSerializer(inmueble, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk):
        try:
            inmueble = Edificacion.objects.get(pk=pk)
        except Edificacion.DoesNotExist:
            return Response(('Error', 'Edificacion no encontrado'), status=status.HTTP_404_NOT_FOUND)
        inmueble.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET', 'POST'])
# def inmuebles_list(request):
#     if request.method == 'GET':
#         inmuebles = Inmueble.objects.all()
#         serializer = InmuebleSerializer(inmuebles, many=True)
#         return Response(serializer.data)
#     if request.method == 'POST':
#         de_serializer = InmuebleSerializer(data=request.data)
#         if de_serializer.is_valid():
#             de_serializer.save()
#             return Response(de_serializer.data)
#         else:
#             return Response(de_serializer.errors)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def inmuebles_detalle(request, pk):
#     if request.method == 'GET':
#         try:
#             inmueble = Inmueble.objects.get(pk=pk)
#             serializer = InmuebleSerializer(inmueble)
#             return Response(serializer.data)
#         except Inmueble.DoesNotExist:
#             return Response(('Error', 'El inmueble no existe'), status=status.HTTP_404_NOT_FOUND)
#     if request.method == 'PUT':
#         inmueble = Inmueble.objects.get(pk=pk)
#         de_serializer = InmuebleSerializer(inmueble, data=request.data)
#         if de_serializer.is_valid():
#             de_serializer.save()
#             return Response(de_serializer.data)
#         else:
#             return Response(de_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     if request.method == 'DELETE':
#         try:
#             inmueble = Inmueble.objects.get(pk=pk)
#             inmueble.delete()
#         except Inmueble.DoesNotExist:
#             return Response(('Error', 'El inmueble no existe'), status=status.HTTP_404_NOT_FOUND)
#         return Response(status=status.HTTP_204_NO_CONTENT)
