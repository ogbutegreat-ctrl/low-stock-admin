from django.db.models import (
    Count,
    Sum,
    F,
    DecimalField,
    ExpressionWrapper,
)

from .models import (
    Product,
    Category,
    Supplier,
)


class InventoryService:

    @staticmethod
    def dashboard_statistics():
        return {
            "total_products": Product.objects.count(),
            "total_categories": Category.objects.count(),
            "total_suppliers": Supplier.objects.count(),
            "total_stock": Product.objects.aggregate(
                total=Sum("quantity")
            )["total"] or 0,
            "low_stock": Product.objects.filter(
                status="LOW"
            ).count(),
            "critical_stock": Product.objects.filter(
                status="CRITICAL"
            ).count(),
            "out_of_stock": Product.objects.filter(
                status="OUT"
            ).count(),
        }

    @staticmethod
    def low_stock_products():
        return (
            Product.objects.filter(
                quantity__lte=F("reorder_threshold")
            )
            .select_related(
                "category",
                "supplier",
            )
            .order_by("quantity")
        )

    @staticmethod
    def reorder_suggestions():
        return (
            Product.objects.filter(
                quantity__lte=F("reorder_threshold")
            )
            .annotate(
                reorder_quantity=F("maximum_stock") - F("quantity")
            )
            .select_related(
                "category",
                "supplier",
            )
            .order_by("quantity")
        )

    @staticmethod
    def category_chart():
        return (
            Category.objects.annotate(
                total_products=Count("products")
            )
            .values(
                "name",
                "total_products",
            )
            .order_by("name")
        )

    @staticmethod
    def inventory_status_chart():
        return (
            Product.objects.values("status")
            .annotate(
                total=Count("id")
            )
            .order_by("status")
        )

    @staticmethod
    def total_inventory_value():

        total = Product.objects.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("purchase_price"),
                    output_field=DecimalField(
                        max_digits=15,
                        decimal_places=2,
                    ),
                )
            )
        )

        return total["total"] or 0

    @staticmethod
    def recent_low_stock(limit=10):
        return (
            Product.objects.filter(
                quantity__lte=F("reorder_threshold")
            )
            .select_related(
                "category",
                "supplier",
            )
            .order_by("quantity")[:limit]
        )