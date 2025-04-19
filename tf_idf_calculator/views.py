from django.shortcuts import render, redirect

# Create your views here.
from .forms import UploadFileForm
from .functions import TfidfComputer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def upload_file(request):
    context = {"form": UploadFileForm()}
    
    if request.method == "POST":
        request.session.flush()
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():  
            files = request.FILES.getlist("file")
            tfidf = TfidfComputer(files)
            tfidf_list = tfidf.results
            request.session['txt_data'] = sorted(
                tfidf_list, 
                key=lambda x: x["idf"], 
                reverse=True
            )
            request.session["docs_num"] = len(list(files))
            request.session.modified = True
            return redirect('upload_file')

    session_data = request.session.get('txt_data', [])
    docs_number = request.session.get('docs_num')
    words_total = len(session_data)
    paginator = Paginator(session_data, 50)
    page_number = request.GET.get('page')
    
    try:
        words = paginator.page(page_number)
    except PageNotAnInteger:
        words = paginator.page(1)
    except EmptyPage:
        words = paginator.page(paginator.num_pages)
    
    context["words"] = words
    context["docs"] = docs_number
    context["total_words"] = words_total
    return render(request, "tf_idf_calculator/upload.html", context)