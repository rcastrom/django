from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from inmuebleslist_app.api.views import inmuebles_list, inmuebles_detalle
from inmuebleslist_app.api.views import EdificacionAV, \
    EdificacionDetalleAV, EmpresaAV, EmpresaDetalleAV, \
    ComentarioList, ComentarioDetail, ComentarioCreate, EmpresaVS, UsuarioComentario, \
    EdificacionList

router = DefaultRouter()
router.register('empresa', EmpresaVS, basename='empresa')  # No conviene con más rutas


urlpatterns = [
    path('edificacion/', EdificacionAV.as_view(), name='edificacion'),
    path('edificacion/list/', EdificacionList.as_view(), name='edificacion-list'),
    path('edificacion/<int:pk>/', EdificacionDetalleAV.as_view(), name='edificacion-detail'),
    path('', include(router.urls)),
    # path('empresa/', EmpresaAV.as_view(), name='empresa'),
    # path('empresa/<int:pk>/', EmpresaDetalleAV.as_view(), name='empresa-detail'),
    path('edificacion/<int:pk>/comentario-create/', ComentarioCreate.as_view(), name='comentario-create'),
    path('edificacion/comentario/<int:pk>/', ComentarioDetail.as_view(), name='comentario-detail'),
    path('edificacion/<int:pk>/comentario/', ComentarioList.as_view(), name='comentario-list'),
    path('edificacion/comentarios/', UsuarioComentario.as_view(), name='usuario-comentarios-detal'),
    # path('edificacion/comentarios/<str:username>/', UsuarioComentario.as_view(), name='usuario-comentarios-detal'),
    # path('edificacion/comentario/<int:pk>/', ComentarioDetail.as_view(), name='comentario-detail'),
    # path('list/', inmuebles_list, name='inmueble-list'),
    # path('<int:pk>/', inmuebles_detalle, name='inmueble-detalles'),
]
