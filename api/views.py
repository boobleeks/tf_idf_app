from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import logout
from .serializers import UserRegisterSerializer, ChangePasswordSerializer, DocumentSerializer, DocumentDetailSerializer, CollectionSerializer
from .models import Document, Collection, Statistics
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


############## Статистика рантайм и тд ##############################

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def getData(request):
    data = {
        'status': 'OK'
    }
    return Response(data)

############### Рега Логаут и все такое ######################

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
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
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def perform_destroy(self, instance):
        instance.delete()


############### Для работы с документами ##########################
from .utils import calculate_statistics

class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        calculate_statistics(serializer.instance)

class DocumentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DocumentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'doc_id' 
    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

class DocumentStatisticsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "doc_id"
    def get(self, request, *args, **kwargs):
        document = self.get_object()
        statistics = Statistics.objects.filter(document=document).first()
        return Response(statistics.data if statistics else {})

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

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
        return Collection.objects.filter(owner=self.request.user)

class CollectionStatisticsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    

    def get(self, request, *args, **kwargs):
        collection = self.get_object()
        statistics = Statistics.objects.filter(collection=collection).first()
        if not statistics:
            statistics = calculate_collection_statistics(collection)
        if statistics:
            return Response(statistics.data)
        return Response({"response":"no documents in collection"})
        

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)

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
        

class RemoveDocumentFromCollectionView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'collection_id'
    def delete(self, request, *args, **kwargs):
        collection = Collection.objects.get(id=kwargs['pk'], owner=request.user)
        document = Document.objects.get(id=kwargs['doc_id'], owner=request.user)
        
        collection.documents.remove(document)
        calculate_collection_statistics(collection)
        return Response(status=status.HTTP_204_NO_CONTENT)

