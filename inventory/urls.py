from django.urls import path

from .views import (
    DashboardView,
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    StockUpdateView,
    LowStockReportView,
)

app_name = "inventory"

urlpatterns = [

    path(
        "",
        DashboardView.as_view(),
        name="dashboard",
    ),

    path(
        "products/",
        ProductListView.as_view(),
        name="products",
    ),

    path(
        "products/add/",
        ProductCreateView.as_view(),
        name="product-add",
    ),

    path(
        "products/<int:pk>/edit/",
        ProductUpdateView.as_view(),
        name="product-edit",
    ),

    path(
        "products/<int:pk>/delete/",
        ProductDeleteView.as_view(),
        name="product-delete",
    ),

    path(
        "products/<int:pk>/stock/",
        StockUpdateView.as_view(),
        name="stock-update",
    ),

    path(
        "reports/low-stock/",
        LowStockReportView.as_view(),
        name="low-stock",
    ),

]