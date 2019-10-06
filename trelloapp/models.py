import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Activity(models.Model):
    DRAGGED = 'dragged'
    FROM = 'from'
    TO = 'to'
    MOVED = 'M'
    RENAME = 'R'
    ACTIVITY_TYPES = (
                        (MOVED, 'MOVED'),
                        (RENAME, 'RENAME'),
                        (DRAGGED, 'dragged'),
                        (FROM, 'from'),
                        (TO, 'to')
                     )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length = 20, choices = ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "{} {}".format(self.activity_type, self.content_object)



class Board(models.Model):
    title = models.CharField(max_length=50)
    date_created = models.DateTimeField(default = timezone.now())   
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete =models.CASCADE)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class BoardMembers(models.Model):
    board = models.ForeignKey('Board', on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    owner = models.BooleanField(default=False)
    
    def __str__(self):
        return "{} {}".format(self.board.title, self.member)

class TrelloList(models.Model):
    title = models.CharField(max_length=50)
    date_created =models.DateTimeField(default = timezone.now())
    board = models.ForeignKey('Board', on_delete = models.CASCADE)
    archive = models.BooleanField(default=False)
    activity_from = GenericRelation(Activity)
    activity_to = GenericRelation(Activity)

    def __str__(self):
        return self.title

class Card(models.Model):
    title = models.CharField(max_length=50)
    date_created = models.DateTimeField(default = timezone.now())
    labels = models.CharField(max_length=50)
    trello_list = models.ForeignKey('TrelloList', on_delete=models.CASCADE)
    archive = models.BooleanField(default=False)
    drag = GenericRelation(Activity)


    def __str__(self):
        return self.title
    

class BoardInvite(models.Model):
    member = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    board = models.ForeignKey('Board', on_delete=models.CASCADE)
    email = models.EmailField(max_length= 50)

    def __str__(self):
        return self.email



@receiver(post_save, sender=Board)
def create_member(sender, instance, created, **kwargs):
    if created:
        BoardMembers.objects.create(board=instance, member=instance.owner, owner=True)
    if created:
        BoardInvite.objects.create(board=instance, email=instance.owner.email)




@receiver(post_save, sender=TrelloList)
def create_from_list(sender, instance, created, **kwargs):
    if created:
        import pdb; pdb.set_trace()
        Activity.objects.create(content_object=instance, activity_type=Activity.TO, user=request.user)
