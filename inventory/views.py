from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import (
    ProductForm,
    StockUpdateForm,
)

from .models import (
    Product,
    Category,
    Supplier,
    InventoryTransaction,
    StockAdjustment,
)

from .services import InventoryService


class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = "inventory/dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["stats"] = (
            InventoryService.dashboard_statistics()
        )

        context["category_chart"] = (
            InventoryService.category_chart()
        )

        context["status_chart"] = (
            InventoryService.inventory_status_chart()
        )

        context["recent_low_stock"] = (
            InventoryService.recent_low_stock()
        )

        context["inventory_value"] = (
            InventoryService.total_inventory_value()
        )

        context["reorder_suggestions"] = (
            InventoryService.reorder_suggestions()
        )

        return context


class ProductListView(LoginRequiredMixin, ListView):

    model = Product

    template_name = "inventory/product_list.html"

    context_object_name = "products"

    paginate_by = 10

    def get_queryset(self):

        queryset = Product.objects.select_related(
            "category",
            "supplier"
        )

        search = self.request.GET.get("search")

        category = self.request.GET.get("category")

        supplier = self.request.GET.get("supplier")

        status = self.request.GET.get("status")

        if search:

            queryset = queryset.filter(

                Q(name__icontains=search)

                |

                Q(sku__icontains=search)

            )

        if category:

            queryset = queryset.filter(
                category_id=category
            )

        if supplier:

            queryset = queryset.filter(
                supplier_id=supplier
            )

        if status:

            queryset = queryset.filter(
                status=status
            )

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["categories"] = (
            Category.objects.all()
        )

        context["suppliers"] = (
            Supplier.objects.all()
        )

        return context


class LowStockReportView(
    LoginRequiredMixin,
    ListView,
):

    model = Product

    paginate_by = 10

    template_name = (
        "inventory/low_stock_report.html"
    )

    context_object_name = "products"

    def get_queryset(self):

        queryset = Product.objects.filter(

            quantity__lte=F(
                "reorder_threshold"
            )

        ).select_related(

            "category",

            "supplier"

        )

        search = self.request.GET.get("search")

        category = self.request.GET.get("category")

        supplier = self.request.GET.get("supplier")

        status = self.request.GET.get("status")

        sort = self.request.GET.get("sort")

        if search:

            queryset = queryset.filter(

                Q(name__icontains=search)

                |

                Q(sku__icontains=search)

            )

        if category:

            queryset = queryset.filter(
                category_id=category
            )

        if supplier:

            queryset = queryset.filter(
                supplier_id=supplier
            )

        if status:

            queryset = queryset.filter(
                status=status
            )

        if sort == "lowest":

            queryset = queryset.order_by(
                "quantity"
            )

        elif sort == "highest":

            queryset = queryset.order_by(
                "-quantity"
            )

        elif sort == "name":

            queryset = queryset.order_by(
                "name"
            )

        else:

            queryset = queryset.order_by(
                "quantity"
            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["categories"] = (
            Category.objects.all()
        )

        context["suppliers"] = (
            Supplier.objects.all()
        )

        return context


class ProductCreateView(
    LoginRequiredMixin,
    CreateView,
):

    model = Product

    form_class = ProductForm

    template_name = (
        "inventory/product_form.html"
    )

    success_url = reverse_lazy(
        "inventory:products"
    )

    def form_valid(self, form):

        messages.success(

            self.request,

            "Product added successfully."

        )

        return super().form_valid(form)

class ProductUpdateView(
    LoginRequiredMixin,
    UpdateView,
):

    model = Product

    form_class = ProductForm

    template_name = (
        "inventory/product_form.html"
    )

    success_url = reverse_lazy(
        "inventory:products"
    )

    def form_valid(self, form):

        messages.success(

            self.request,

            "Product updated successfully."

        )

        return super().form_valid(form)


class ProductDeleteView(
    LoginRequiredMixin,
    DeleteView,
):

    model = Product

    template_name = (
        "inventory/product_delete.html"
    )

    success_url = reverse_lazy(
        "inventory:products"
    )

    def delete(self, request, *args, **kwargs):

        messages.success(

            request,

            "Product deleted successfully."

        )

        return super().delete(
            request,
            *args,
            **kwargs
        )


class StockUpdateView(
    LoginRequiredMixin,
    View,
):

    template_name = (
        "inventory/stock_update.html"
    )

    def get(self, request, pk):

        product = get_object_or_404(
            Product,
            pk=pk
        )

        form = StockUpdateForm()

        return render(

            request,

            self.template_name,

            {

                "product": product,

                "form": form,

            }

        )

    def post(self, request, pk):

        product = get_object_or_404(
            Product,
            pk=pk
        )

        form = StockUpdateForm(
            request.POST
        )

        if form.is_valid():

            previous_quantity = (
                product.quantity
            )

            quantity = form.cleaned_data[
                "quantity"
            ]

            transaction_type = (
                form.cleaned_data[
                    "transaction_type"
                ]
            )

            reason = form.cleaned_data[
                "reason"
            ]

            if transaction_type == "IN":

                product.quantity += quantity

            else:

                if quantity > product.quantity:

                    messages.error(

                        request,

                        "Insufficient stock available."

                    )

                    return render(

                        request,

                        self.template_name,

                        {

                            "product": product,

                            "form": form,

                        }

                    )

                product.quantity -= quantity

            product.save()

            InventoryTransaction.objects.create(

                product=product,

                transaction_type=transaction_type,

                quantity=quantity,

                note=reason,

            )

            StockAdjustment.objects.create(

                product=product,

                previous_quantity=previous_quantity,

                new_quantity=product.quantity,

                reason=reason,

                adjusted_by=request.user.username,

            )

            messages.success(

                request,

                "Stock updated successfully."

            )

            return redirect(
                "inventory:products"
            )

        return render(

            request,

            self.template_name,

            {

                "product": product,

                "form": form,

            }

        )