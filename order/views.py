from django.views.generic import ListView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Sum
from django_tables2 import RequestConfig
from .models import Order, OrderItem, CURRENCY
from .forms import OrderCreateForm, OrderEditForm
from product.models import Product, Category
from .tables import ProductTable, OrderItemTable, OrderTable


@method_decorator(staff_member_required, name='dispatch')
class HomepageView(ListView):
    template_name = 'index.html'
    paginate_by = 50
    model = Order

    def get_queryset(self):
        qs = Order.objects.all()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.all()
        total_sales = orders.aggregate(Sum('final_value'))['final_value__sum'] if orders.exists() else 0
        paid_value = orders.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum']\
            if orders.filter(is_paid=True).exists() else 0
        remaining = total_sales - paid_value
        paid_percent, remain_percent = round((paid_value/total_sales)*100, 1), round((remaining/total_sales)*100, 1)
        total_sales = f'{total_sales} {CURRENCY}'
        paid_value = f'{paid_value} {CURRENCY}'
        remaining = f'{remaining} {CURRENCY}'
        orders = OrderTable(orders)
        RequestConfig(self.request).configure(orders)
        context.update(locals())
        return context


@staff_member_required
def auto_create_order_view(request):
    new_order = Order.objects.create()
    return redirect(new_order.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class OrderListView(ListView):
    template_name = 'list.html'
    model = Order

    def get_queryset(self):
        qs = Order.objects.all()
        if self.request.GET:
            qs = Order.filter_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = OrderTable(self.object_list)
        RequestConfig(self.request).configure(orders)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateOrderView(CreateView):
    template_name = 'form.html'
    form_class = OrderCreateForm
    model = Order

    def get_success_url(self):
        self.new_object.refresh_from_db()
        return reverse('update_order', kwargs={'pk': self.new_object.id})

    def form_valid(self, form):
        object = form.save()
        object.refresh_from_db()
        self.new_object = object
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class OrderUpdateView(UpdateView):
    model = Order
    template_name = 'order_update.html'
    form_class = OrderEditForm
    success_url = reverse_lazy('homepage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Order, pk=self.kwargs['pk'])
        qs_p = Product.objects.filter(active=True)[:12]
        products = ProductTable(qs_p)
        order_items = OrderItemTable(instance.order_items.all())
        RequestConfig(self.request).configure(products)
        RequestConfig(self.request).configure(order_items)
        context.update(locals())
        return context


@staff_member_required
def delete_order(request, pk):
    instance = get_object_or_404(Order, id=pk)
    instance.delete()
    messages.warning(request, 'The order is deleted!')
    return redirect(reverse('homepage'))


@staff_member_required
def ajax_add_product(request, pk, dk):
    instance = get_object_or_404(Order, id=pk)
    product = get_object_or_404(Product, id=dk)
    order_item, created = OrderItem.objects.get_or_create(order=instance, product=product)
    if created:
        order_item.qty = 1
        order_item.price = product.value
        order_item.discount_price = product.discount_value
    else:
        order_item.qty += 1
    order_item.save()
    instance.refresh_from_db()
    order_items = OrderItemTable(instance.order_items.all())
    RequestConfig(request).configure(order_items)
    data = dict()
    data['result'] = render_to_string(template_name='include/order_container.html',
                                      request=request,
                                      context={'instance': instance,
                                               'order_items': order_items
                                               }
                                    )
    return JsonResponse(data)


@staff_member_required
def ajax_modify_order_item(request, pk, action):
    order_item = get_object_or_404(OrderItem, id=pk)
    instance = order_item.order
    if action == 'remove':
        order_item.qty -= 1
        if order_item.qty < 1: order_item.qty = 1
    if action == 'add':
        order_item.qty += 1
    order_item.save()
    if action == 'delete':
        order_item.delete()
    data = dict()
    instance.refresh_from_db()
    order_items = OrderItemTable(instance.order_items.all())
    RequestConfig(request).configure(order_items)
    data['result'] = render_to_string(template_name='include/order_container.html',
                                      request=request,
                                      context={
                                          'instance': instance,
                                          'order_items': order_items
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_search_products(request):
    q = request.GET.get('q', None)
    products = Product.objects.all().filter(title__startswith=q) if q else Product.objects.none()
    products = products[:12]
    data = dict()
    data['products'] = render_to_string(template_name='',
                                        request=request,
                                        context={
                                            'products': products
                                        })
    return JsonResponse(data)


@staff_member_required
def order_action_view(request, pk, action):
    instance = get_object_or_404(Order, id=pk)
    if action == 'is_paid':
        instance.is_paid = True
        instance.save()
    if action == 'delete':
        instance.delete()
    return redirect(reverse('homepage'))