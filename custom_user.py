


class User(AbstractUser, index.Indexed):
    first_name_alternative = models.CharField(_('first name alternative'), max_length=30, blank=True)
    last_name_alternative = models.CharField(_('last name alternative'), max_length=30, blank=True)
    patronymic_name_alternative = models.CharField(_('patronymic name alternative'), max_length=60, blank=True)
    description_alternative = models.TextField(_('description alternative'), blank=True, help_text=_('Person description.'))
    position_alternative = models.CharField(_('position alternative'), blank=True, max_length=255, help_text=_('Current position alternativ'))
    awards = ArrayField(models.CharField(max_length=300, blank=True), default=list, verbose_name=_('awards'), blank=True)
    vacation_from = models.DateField(_('vacation from'), blank=True, null=True)
    vacation_due = models.DateField(_('vacation due'), blank=True, null=True)

    search_fields = AbstractUser.search_fields + [
        index.SearchField('first_name_alternative', partial_match=True, boost=5),
        index.SearchField('last_name_alternative', partial_match=True, boost=5),

        index.SearchField('patronymic_name_alternative', partial_match=True),
        index.SearchField('description_alternative', partial_match=True),
        index.SearchField('position_alternative', partial_match=True),
    ]

    api_search_fields = ('last_name', 'first_name', 'first_name_alternative', 'last_name_alternative')

    class Meta(AbstractUser.Meta):
        ordering = ('last_name', 'first_name')
