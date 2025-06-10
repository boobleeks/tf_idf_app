from django.urls import path
from .views import (getData, RegisterView, LoginView, LogoutView, ChangePasswordView, DeleteUserView,
    DocumentListCreateView, DocumentDetailView, DocumentStatisticsView,
    CollectionListView, CollectionDetailView, CollectionStatisticsView,
    AddDocumentToCollectionView, RemoveDocumentFromCollectionView)

urlpatterns = [
    ##### Пути для статистики и прочего #####
    
    path('status/', getData),

    ##### Пути для работы с документами #####
    
    path('documents/', DocumentListCreateView.as_view() ), # выдает список документов загруженных пользователем
    path('documents/<uuid:doc_id>', DocumentDetailView.as_view() ), #выдаает содержимое документа, текст внутри
    path('documents/<uuid:doc_id>/statistics', DocumentStatisticsView.as_view() ), #выдает статистику по данному документу (с учётом коллекции)
    path('documents/<uuid:doc_id>/delete', DocumentDetailView.as_view()), #удаляет документ

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
    
]