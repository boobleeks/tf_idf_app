from django.urls import path
from .views import (getData, RegisterView, LoginView, LogoutView, ChangePasswordView, DeleteUserView,
    DocumentListCreateView, DocumentDetailView, DocumentStatisticsView,
    CollectionListView, CollectionDetailView, CollectionStatisticsView,
    AddDocumentToCollectionView, RemoveDocumentFromCollectionView, HuffmanAPIView, MetricsView, getVersion)

urlpatterns = [
    ##### Пути для статистики и прочего #####
    
    path('status/', getData),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    path('version/', getVersion),
    ##### Пути для работы с документами #####
    
    path('documents/', DocumentListCreateView.as_view() ), # выдает список документов загруженных пользователем
    path('documents/<uuid:doc_id>', DocumentDetailView.as_view() ), #выдаает содержимое документа и удаляет документ по медотду DELETE, текст внутри content
    path('documents/<uuid:doc_id>/statistics', DocumentStatisticsView.as_view() ),

    ##### Пути для работы с коллекциями #####
    
    path('collections/', CollectionListView.as_view()),
    path('collections/<int:pk>/', CollectionDetailView.as_view()),
    path('collections/<int:pk>/statistics/', CollectionStatisticsView.as_view()),
    path('collections/<int:pk>/<uuid:doc_id>/', AddDocumentToCollectionView.as_view()),
    path('collections/<int:pk>/<uuid:doc_id>/delete/', RemoveDocumentFromCollectionView.as_view()),
    
    ##### Пути для рега, лога и тд. пользователей #####

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/<int:user_id>/', ChangePasswordView.as_view(), name='change-password'),
    path('user/<int:user_id>/delete/', DeleteUserView.as_view(), name='delete-user'),
    
    ##### КОД ХАФМАНА
    path('documents/<uuid:doc_id>/huffman/', HuffmanAPIView.as_view(), name='document-huffman')

]

