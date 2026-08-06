from django.contrib import admin

from .models import (
    Category,
    Supplier,
    Product,
    InventoryTransaction,
    StockAdjustment,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "created_at",
    )

    search_fields = (
        "name",
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "phone",
    )

    search_fields = (
        "name",
        "email",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "sku",
        "category",
        "supplier",
        "quantity",
        "status",
    )

    list_filter = (
        "category",
        "supplier",
        "status",
    )

    search_fields = (
        "name",
        "sku",
    )


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "transaction_type",
        "quantity",
        "date",
    )

    list_filter = (
        "transaction_type",
    )


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "previous_quantity",
        "new_quantity",
        "adjusted_by",
        "adjusted_at",
    )