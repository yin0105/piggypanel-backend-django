import unicodedata
from user.models import User
from django.utils.text import slugify

def generate_username(full_name):
    
    """
    >>> from utils import generate_username
    >>> from django.contrib.auth.models import User
    >>>
    >>> name = 'Sebastião Henrique de Almeida Gonçalves'
    >>> username = generate_username(name)
    >>> print username
    sgoncalves
    >>> u = User(username=username, password="123456", email="teste1@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiaog
    >>> u = User(username=username, password="123456", email="teste2@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiao1
    >>> u = User(username=username, password="123456", email="teste3@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiao2
    >>> u = User(username=username, password="123456", email="teste4@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiao3
    >>> u = User(username=username, password="123456", email="teste5@fundacaoaprender.org.br")
    >>> u.save()
    """
        
    name = unicodedata.normalize('NFKD', str(full_name.lower()))
    name = name.split(' ')
    lastname = name[-1]
    firstname = name[0]
    
    # tente iniciais dos primeiros nomes mais ultimo nome inteiro
    username = '%s%s' % (firstname[0], lastname)
    if User.objects.filter(username=username).count() > 0:
        # se não servir isso, tente primeiro nome inteiro mais iniciais dos ultimos nomes
        username = '%s%s' % (firstname, lastname[0])
        if User.objects.filter(username=username).count() > 0:
            # se não servir, coloque o primeiro nome, mais um número
            users = User.objects.filter(username__regex=r'^%s[1-9]{1,}$' % firstname).order_by('username').values('username')                
            if len(users) > 0:
                last_number_used = map(lambda x: int(x['username'].replace(firstname,'')), users)
                print(last_number_used)
                last_number_used.sort()
                last_number_used = last_number_used[-1]
                number = last_number_used + 1
                username = '%s%s' % (firstname, number)
            else:
                username = '%s%s' % (firstname, 1)
    
    return username