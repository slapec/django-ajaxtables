from vanilla import ListView
from django.http import HttpResponse
from django.template.context import RequestContext

class AjaxListView(ListView):
    template_names = ['ajaxtables/object_list.html', 'ajaxtables/object_list_data.html']
    filter_form_class = None
    page_size = 10
    page_kwarg = 'page'

    def get_page_from_request(self):
        page_size = int(self.request.GET.get('pageSize', self.page_size))
        act_page = int(self.request.GET.get('toPage', 1))
        return page_size, act_page

    def get_template_names(self):
        try:
            assert len(self.template_names) == 2
        except AssertionError:
            msg = "'%s' must have two template names. One for view the" \
                  "table, and one for the jax loaded data."
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        if self.request.is_ajax():
            return [self.template_names[1]]
        return [self.template_names[0]]

    def form_to_filters(self, form_data):
        return {}

    def paginate_queryset(self, queryset):
        page_size, act_page = self.get_page_from_request()
        return super(AjaxListView, self).paginate_queryset(queryset, page_size)

    def get(self, request, *args, **kwargs):
        if request.is_ajax(): ## no filter form provided, and request for data
            queryset = self.get_queryset()
            page_size, act_page = self.get_page_from_request()
            page = self.paginate_queryset(queryset)
            self.object_list = page.object_list
            context = self.get_context_data(
                page_obj=page,
                is_paginated=page.has_other_pages(),
                paginator=page.paginator,
            )
            return self.render_to_response(context)
        form = self.filter_form_class(request.POST or None) if self.filter_form_class else None
        return self.render_to_response({'form': form, 'page_size': self.page_size})

    def post(self, request, *args, **kwargs):
        form = self.filter_form_class(request.POST or None)
        if form.is_valid():
            filters = self.form_to_filters(form.cleaned_data)
            queryset = self.get_queryset().filter(**filters)
            page = self.paginate_queryset(queryset)
            self.object_list = page.object_list
            context = self.get_context_data(
                page_obj=page,
                is_paginated=page.has_other_pages(),
                paginator=page.paginator,
            )
            return self.render_to_response(context)