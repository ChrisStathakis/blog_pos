from django.contrib import admin
from django.urls import path

from order.views import (HomepageView, OrderUpdateView, CreateOrderView, delete_order,
                         OrderListView,
                         ajax_add_product, ajax_modify_order_item, ajax_search_products,
                         order_action_view
                         )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomepageView.as_view(), name='homepage'),
    path('order-list/', OrderListView.as_view(), name='order_list'),
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('update/<int:pk>/', OrderUpdateView.as_view(), name='update_order'),
    path('delete/<int:pk>/', delete_order, name='delete_order'),
    path('action/<int:pk>/<slug:action>/', order_action_view, name='order_action' ),


    #  ajax_calls
    path('ajax/search-products/', ajax_search_products, name='ajax-search'),
    path('ajax/add-product/<int:pk>/<int:dk>/', ajax_add_product, name='ajax_add'),
    path('ajax/modify-product/<int:pk>/<slug:action>', ajax_modify_order_item, name='ajax_modify'),
]
