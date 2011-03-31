
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User

from forms_builder.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH
from forms_builder.forms.managers import FormManager
from perms.utils import is_admin
from perms.models import TendenciBaseModel
from user_groups.models import Group

#STATUS_DRAFT = 1
#STATUS_PUBLISHED = 2
STATUS_CHOICES = (
    ('draft', "Draft"), 
    ('published', "Published"),
)

FIELD_CHOICES = (
    ("CharField", _("Text")),
    ("CharField/django.forms.Textarea", _("Paragraph Text")),
    ("BooleanField", _("Checkbox")),
    ("ChoiceField", _("Choose from a list")),
    ("MultipleChoiceField", _("Multi select")),
    ("EmailField", _("Email")),
    ("FileField", _("File upload")),
    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
    ("DateTimeField", _("Date/time")),
    #("ModelMultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi checkbox")),
)

FIELD_FUNCTIONS = (
    ("GroupSubscription", _("Subscribe to Group")),
)

class Form(TendenciBaseModel):
    """
    A user-built form.
    """

    title = models.CharField(_("Title"), max_length=50)
    slug = models.SlugField(editable=False, max_length=100, unique=True)
    intro = models.TextField(_("Intro"), max_length=2000)
    response = models.TextField(_("Confirmation Text"), max_length=2000)
#    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, 
#        default=STATUS_PUBLISHED)
    send_email = models.BooleanField(_("Send email"), default=False, help_text=
        _("If checked, the person entering the form will be sent an email"))
    email_from = models.EmailField(_("From address"), blank=True, 
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send copies to"), blank=True, 
        help_text=_("One or more email addresses, separated by commas"), 
        max_length=200)
    
    objects = FormManager()

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")
        permissions = (("view_form","Can view form"),)
    
    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Create a unique slug from title - append an index and increment if it 
        already exists.
        """
        if not self.slug:
            self.slug = slugify(self.title)
            i = 0
            while True:
                if i > 0:
                    if i > 1:
                        self.slug = self.slug.rsplit("-", 1)[0]
                    self.slug = "%s-%s" % (self.slug, i)
                if not Form.objects.filter(slug=self.slug):
                    break
                i += 1
        super(Form, self).save(*args, **kwargs)
        
    @models.permalink
    def get_absolute_url(self):
        return ("form_detail", (), {"slug": self.slug})

    def admin_link_view(self):
        url = self.get_absolute_url()
        return "<a href='%s'>%s</a>" % (url, ugettext("View on site"))
    admin_link_view.allow_tags = True
    admin_link_view.short_description = ""

    def admin_link_export(self):
        url = reverse("admin:form_export", args=(self.id,))
        return "<a href='%s'>%s</a>" % (url, ugettext("Export entries"))
    admin_link_export.allow_tags = True
    admin_link_export.short_description = ""

class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)

class Field(models.Model):
    """
    A field for a user-built form.
    """
    
    form = models.ForeignKey("Form", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES,
        max_length=64)
    field_function = models.CharField(_("Special Functionality"),
        choices=FIELD_FUNCTIONS, max_length=64, null=True, blank=True)
    function_params = models.CharField(_("Group Name or Names"),
        max_length=100, null=True, blank=True, help_text="Comma separated if more than one")
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
        help_text="Comma separated options where applicable")
        
    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        order_with_respect_to = "form"
    
    def __unicode__(self):
        return self.label
        
    #def queryset(self):
    #    group_names = []
    #    if self.field_type == "ModelMultipleChoiceField/django.forms.CheckboxSelectMultiple":
    #        for val in self.choices.split(','):
    #            group_name = val.strip()
    #            group_names.append(group_name)
    #    groups = Group.objects.filter(name__in=group_names)
    #    return groups
        
    def execute_function(self, entry, value):
        if self.field_function == "GroupSubscription":
            if value:
                for val in self.function_params.split(','):
                    group = Group.objects.get(name=val)
                    entry.subscribe(group)

class FormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    form = models.ForeignKey("Form", related_name="entries")
    entry_time = models.DateTimeField(_("Date/time"))
    
    class Meta:
        verbose_name = _("Form entry")
        verbose_name_plural = _("Form entries")
        
    def __unicode__(self):
        u = ''
        for f in self.fields.all()[0:5]:
            u = u + str(f) + ' '
        return u[0:len(u)-1]

    @models.permalink
    def get_absolute_url(self):
        return ("form_entry_detail", (), {"id": self.pk})
    
    def subscribe(self, group):
        """
        Subscribe FormEntry to group specified.
        """
        # avoiding circular imports
        from subscribers.models import GroupSubscription as GS
        GS.objects.create(group=group, subscriber=self)

    def unsubscribe(self, group):
        """
        Unsubscribe FormEntry from group specified
        """
        # avoiding circular imports
        from subscribers.models import GroupSubscription as GS
        try:
            sub = GS.objects.get(group=group, subscriber=self)
            sub.delete()
        except GS.DoesNotExist:
            pass
    
class FieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """
    
    entry = models.ForeignKey("FormEntry", related_name="fields")
    field = models.ForeignKey("Field", related_name="field")
    value = models.CharField(max_length=FIELD_MAX_LENGTH)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")
    
    def __unicode__(self):
        return ('%s: %s' % (self.field.label, self.value))
    
    def save(self, *args, **kwargs):
        super(FieldEntry, self).save(*args, **kwargs)
        self.field.execute_function(self.entry, self.value)
    
