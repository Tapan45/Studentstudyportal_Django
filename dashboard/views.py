# Inside your Django app views.py file

from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from .forms import DashboardForm
from youtubesearchpython import VideosSearch
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import wikipedia

from django.http import HttpResponse 


def home(request):
    return render(request,'dashboard/home.html')
@login_required
def notes(request):
    print (request.user)
    if request.method == "POST":
      form = NotesForm(request.POST)
      if form.is_valid():
          notes=Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
          notes.save()
          messages.success(request,f"Notes added from  {request.user.username} successfully!!") 
          return redirect('notes')  
    else:  
      form = NotesForm()
      notes =Notes.objects.filter(user=request.user)
      context ={'notes':notes,'form':form}
      return render(request,'dashboard/notes.html',context)
    
@login_required   
def delete_note(request,pk=None):
  Notes.objects.get(id=pk).delete()
  return redirect("notes")   

class NotesDetailView(generic.DetailView):
  model = Notes 
  
  
@login_required 
def homework(request):
  if  request.method == "POST":
          form = HomeworkForm(request.POST) 
          if form.is_valid():
            try:
                 finished=request.POST['is_finished']
                 if finished =='on':
                       finished == True
                 else:
                       finished = False
            except:
                 finished = False       
            homeworks = Homework(
                  user = request.user,
                  subject = request.POST['subject'],
                  title = request.POST['title'],
                  description = request.POST['description'],
                  due = request.POST['due'],
                  is_finished = finished
               )
            homeworks.save()
            messages.success(request,f'Homework added from  {request.user.username}!!')
            return redirect ('homework')
            
  else:
                
      form=HomeworkForm()
  homework=Homework.objects.filter(user=request.user)
  if len(homework)==0:
        homework_done=True
  else:
        homework_done=False
  context = {'homeworks':homework,'homeworks_done':homework_done,'form':form}
  return render (request,'dashboard/homework.html',context)

@login_required
def update_homework(request,pk=None):
  homework = Homework.objects.get(id=pk)
  if homework.is_finished == True:
    homework.is_finished =False
  else:
    homework.is_finished = True
    homework.save()
    return redirect ('homework')
      
@login_required      
def delete_homework(request,pk=None):
  Homework.objects.get(id=pk).delete()
  return redirect("homework") 


@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            
            todos = Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished
            )
            todos.save()
            messages.success(request, f"Todo Added from {request.user.username}!!!")
            return HttpResponseRedirect('/todo') 
            
    else:
        form = TodoForm()
        todo = Todo.objects.filter(user=request.user)
        if len(todo) == 0:
            todos_done = True
        else:
            todos_done = False
            
        context = {
            'form': form,
            'todos': todo,
            'todos_done': todos_done
        }
        
        return render(request, "dashboard/todo.html", context)

def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")




 



def youtube (request):
   if  request.method == "POST" :
     form = DashboardForm(request.POST)
     text=request.POST['text'] 
     video = VideosSearch(text,limit=10) 
     result_list=[]
     for i in video.result()['result']:
           result_dict ={
               'input':text,
               'duration':i['title'],
               'thumbnail':i['thumbnails'][0]['url'],
               'channel':i['channel']['name'],
               'link':i['link'],
               'views':i['viewCount']['short'],
               'title':i['title'],
               'published':i['publishedTime']
             
             
             
             
             
           }
           desc=''
           if i['descriptionSnippet']:
                 for j in i['descriptionSnippet']:
                      desc += j['text']
                 
           result_dict['description']=desc
           result_list.append(result_dict)
           context ={
               'form':form,
               'results':result_list
             
             
           }
     return render (request,"dashboard/youtube.html",context)
   else:
        
      
      
     form = DashboardForm()
     context = {'form':form}
     return render(request,"dashboard/youtube.html",context)
   
   
def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        
        if r.status_code == 200:  
            answer = r.json()
            result_list = []

            if 'items' in answer:  
                for item in answer['items']:
                    volume_info = item.get('volumeInfo', {})
                    result_dict = {
                        'title': volume_info.get('title', ''),
                        'subtitle': volume_info.get('subtitle', ''),
                        'description': volume_info.get('description', ''),
                        'count': volume_info.get('pageCount', ''),
                        'categories': volume_info.get('categories', []),
                        'rating': volume_info.get('averageRating', ''),
                        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                        'preview': volume_info.get('previewLink', '')  
                    }
                    result_list.append(result_dict)

                context = {
                    'form': form,
                    'results': result_list
                }
                return render(request, "dashboard/books.html", context)
            else:
                messages.error(request, "No book results found.")
        else:
            messages.error(request, f"Failed to fetch books. Error: {r.status_code}")

    form = DashboardForm()
    context = {'form': form}
    return render(request, "dashboard/books.html", context)



def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        try:
            r = requests.get(url)
            r.raise_for_status() 
            answer = r.json()

            if isinstance(answer, list) and answer: 
                word_data = answer[0]
                phonetics = word_data.get('phonetics', [{'text': 'N/A'}])[0].get('text', 'N/A')
                audio = word_data.get('phonetics', [{'audio': 'N/A'}])[0].get('audio', 'N/A')
                meanings = word_data.get('meanings', [])
                if meanings:
                    definition = meanings[0].get('definitions', [{'definition': 'N/A'}])[0].get('definition', 'N/A')
                    example = meanings[0].get('definitions', [{'example': 'N/A'}])[0].get('example', 'N/A')
                    synonyms = meanings[0].get('definitions', [{'synonyms': []}])[0].get('synonyms', [])
                else:
                    definition = example = 'N/A'
                    synonyms = []
                
                context = {
                    'form': form,
                    'input': text,
                    'phonetics': phonetics,
                    'audio': audio,
                    'definition': definition,
                    'example': example,
                    'synonyms': synonyms
                }
            else:
                context = {
                    'form': form,
                    'input': text,
                    'error_message': 'No data found for the word.'
                }
        except requests.RequestException as e:
            context = {
                'form': form,
                'input': text,
                'error_message': f"Failed to fetch data. Error: {e}"
            }
        
        return render(request, "dashboard/dictionary.html", context)
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, "dashboard/dictionary.html", context)
    


def wiki(request):
    if request.method =='POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search= wikipedia.page(text)
        context={
          'form':form,
          'title':search.title,
          'link':search.url,
          'details':search.summary
        
        }
        return render (request,"dashboard/wiki.html",context)
    else:
       form = DashboardForm()
       context = {
         'form':form
        }
    
    return render (request,"dashboard/wiki.html",context)
    

def conversion(request):
    if request.method =="POST":
        form = ConversionForm(request.POST)
        if request.POST['measurment'] == 'length':
            measurement_form =ConversionLengthForm()
            context ={
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer =''
                if input and int(input)>=0:
                    if first == 'yard' and second =='foot':
                        answer = f'{input}yard ={int(input)*3}foot'
                    if  first == 'foot' and second =='yard':
                        answer = f'{input}foot = {int(input)/3}yard'
                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                 }
        if request.POST['measurment'] == 'mass':
            measurement_form = ConversionMassForm()
            context ={
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer =''
                if input and int(input) >=0:
                    if first == 'pound' and second =='kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if  first == 'kilogram' and second =='pound':
                        answer = f'{input}kilogram = {int(input)*2.20462} pound'
                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                 }    
        return render(request, "dashboard/conversion.html", context)       
                
    else:
    
     form = ConversionForm()
     context ={
         'form':form,
         'input': False
     }
     return render (request,"dashboard/conversion.html",context)
     
     
def register(request):
    
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"Account created for {username}!!!")
            return redirect ("login")
    else :
     form =UserCreationForm()
    context ={
        'form':form
    }
         
    
    return render (request,"dashboard/register.html",context)


@login_required
def profile (request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False,user=request.user)
    if len (homeworks) == 0:
        homework_done =True
    else:   
        homework_done =False
    if len (todos) == 0:
        todos_done =True
    else:   
        todos_done =False 
    context ={
        'homeworks':homeworks,
        'homework_done':homework_done,
        'todos':todos,
        'todos_done':todos_done
    } 
    return render (request,"dashboard/profile.html")