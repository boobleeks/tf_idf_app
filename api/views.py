from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import logout
from .serializers import UserRegisterSerializer, ChangePasswordSerializer, DocumentSerializer, DocumentDetailSerializer, CollectionSerializer, StatisticsSerializer
from .models import Document, Collection, Statistics
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from .decorators import track_processing_time
from .metrics import get_metrics
import re
from collections import Counter
from .version import __version__

############## Статистика рантайм и тд ##############################

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def getData(request):
    '''Получение статуса приложения'''
    data = {
        'status': 'OK'
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def getVersion(request):
    '''Получение версии приложения'''
    data = {
        'version': __version__
    }
    return Response(data)

class MetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        documents = Document.objects.filter(owner=request.user)
        collections = Collection.objects.filter(owner=request.user)

        documents_total = documents.count()
        total_length = sum(len(doc.content or '') for doc in documents)
        average_document_length = total_length / documents_total if documents_total > 0 else 0

        all_words = []
        for doc in documents:
            content = doc.content or ''
            words = re.findall(r'\b\w+\b', content.lower())
            all_words.extend(words)

        word_counts = Counter(all_words)
        most_common_words = [word for word, _ in word_counts.most_common(10)]
        rarest_words = [word for word, count in word_counts.items() if count == 1][:10]

        documents_per_collection = {
        collection.name: collection.documents.count() for collection in collections
    }
        extra_metrics = get_metrics()
        return Response({
        "documents_total": documents_total,
        "average_document_length": round(average_document_length, 2),
        "most_common_words": most_common_words,
        "rarest_words": rarest_words,
        "documents_per_collection": documents_per_collection,
        "processing_metrics": extra_metrics
    })

############### Рега Логаут и все такое ######################

class RegisterView(generics.CreateAPIView):
    '''Регистрация нового пользователя'''
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(ObtainAuthToken):
    @swagger_auto_schema(operation_description="Аутентификация пользователя по логину и паролю")
    def post(self, request, *args, **kwargs):
        '''Аутентификация пользователя по логину и паролю для получения токена'''
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'created': created,
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            # 'password': user.password,
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(operation_description="Выход пользователя и удаление токена")
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response(
            {
                "success": True,
                "message": "Вы успешно вышли из системы",
                "status": "success",
                "status_code": status.HTTP_200_OK
            })

class ChangePasswordView(generics.UpdateAPIView):
    '''Смена пароля текущего пользователя'''
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.data.get('old_password')):
            return Response({"old_password": ["Wrong password."]}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(serializer.data.get('new_password'))
        request.user.save()
        return Response(status=status.HTTP_200_OK)

class DeleteUserView(generics.DestroyAPIView):
    '''Удаление учетной записи пользователя'''
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def perform_destroy(self, instance):
        instance.delete()


############### Для работы с документами ##########################
from .utils import calculate_statistics, huffman


class HuffmanAPIView(APIView):
    def get(self, request, doc_id):
        document = get_object_or_404(Document, id=doc_id)
        result = huffman(document.content)
        return Response(result, status=status.HTTP_200_OK)


class DocumentListCreateView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Получить список загруженных пользователем документов")
    def get_queryset(self):
        '''Получение списка загруженных документов'''
        return Document.objects.filter(owner=self.request.user)
    

    @swagger_auto_schema(operation_description="Загрузить новый документ")
    @track_processing_time
    def perform_create(self, serializer):
        '''Добавление документа в список'''
        serializer.save(owner=self.request.user)
        calculate_statistics(serializer.instance)
    

class DocumentDetailView(generics.RetrieveDestroyAPIView):
    '''Просмотр и удаление одного документа'''
    serializer_class = DocumentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'doc_id'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    @swagger_auto_schema(operation_description="Получить содержимое выбранного документа")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Удалить выбранный документ")
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class DocumentStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(operation_description="Получить статистику по документу")
    def get(self, request, doc_id):
        '''Получение статистики документа'''
        document = get_object_or_404(Document, id=doc_id, owner=request.user)
        statistics = Statistics.objects.filter(document=document).first()
        return Response(statistics.data if statistics else {})

########################## Для работы с коллекциями ###############################

from .utils import calculate_collection_statistics

class CollectionListView(generics.ListCreateAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CollectionDetailView(generics.RetrieveAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Collection.objects.none()
        
        return Collection.objects.filter(owner=self.request.user)

class CollectionStatisticsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StatisticsSerializer
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Collection.objects.none()
        return Collection.objects.filter(owner=self.request.user)

    @track_processing_time
    def get_object(self):
        collection = super().get_object()
        statistics = Statistics.objects.filter(collection=collection).first()
        if not statistics:
            statistics = calculate_collection_statistics(collection)
        return statistics

class AddDocumentToCollectionView(APIView):
    def post(self, request, pk, doc_id, *args, **kwargs):
        try:
            collection = get_object_or_404(Collection, id=pk)
            
            if collection.owner != request.user:
                raise PermissionDenied("Вы не владеете данной коллекцией!")
            
            document = get_object_or_404(Document, id=doc_id)
            
            if document.owner != request.user:
                raise PermissionDenied("Это не ваш документ имейте совесть")
            
            if collection.documents.filter(id=document.id).exists():
                return Response(
                    {"detail": "Документ уже находится в коллекции"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            collection.documents.add(document)
            calculate_collection_statistics(collection)

            return Response(
                {"detail": "Документ успешно добавлен, поздравляю!"},
                status=status.HTTP_200_OK
            )
        
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {"detail": "ОшибОчка: " + str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class RemoveDocumentFromCollectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk, doc_id):
        collection = get_object_or_404(Collection, id=pk, owner=request.user)
        document = get_object_or_404(Document, id=doc_id, owner=request.user)

        collection.documents.remove(document)
        calculate_collection_statistics(collection)

        return Response(status=status.HTTP_204_NO_CONTENT)

