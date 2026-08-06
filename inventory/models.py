from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Category(models.Model):

    name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Supplier(models.Model):

    name = models.CharField(max_length=150)

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=20, blank=True)

    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):

    STATUS_CHOICES = (
        ("NORMAL", "Normal"),
        ("LOW", "Low Stock"),
        ("CRITICAL", "Critical"),
        ("OUT", "Out of Stock"),
    )

    name = models.CharField(max_length=150)

    sku = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="products"
    )

    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    minimum_stock = models.PositiveIntegerField(default=5)

    reorder_threshold = models.PositiveIntegerField(default=10)

    maximum_stock = models.PositiveIntegerField(default=50)

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NORMAL"
    )

    last_restocked = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def suggested_reorder(self):
        return max(0, self.maximum_stock - self.quantity)

    def update_status(self):

        if self.quantity == 0:
            self.status = "OUT"

        elif self.quantity <= self.minimum_stock:
            self.status = "CRITICAL"

        elif self.quantity <= self.reorder_threshold:
            self.status = "LOW"

        else:
            self.status = "NORMAL"

    def clean(self):

        if self.minimum_stock >= self.reorder_threshold:
            raise ValidationError(
                "Minimum stock must be less than the reorder threshold."
            )

        if self.reorder_threshold >= self.maximum_stock:
            raise ValidationError(
                "Reorder threshold must be less than the maximum stock."
            )

        if self.selling_price < self.purchase_price:
            raise ValidationError(
                "Selling price cannot be less than purchase price."
            )

    def save(self, *args, **kwargs):

        self.full_clean()

        self.update_status()

        if self.quantity > 0:
            self.last_restocked = timezone.now()

        super().save(*args, **kwargs)


class InventoryTransaction(models.Model):

    TRANSACTION_TYPES = (
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    quantity = models.PositiveIntegerField()

    note = models.TextField(blank=True)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.product.name} - {self.transaction_type}"


class StockAdjustment(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="adjustments"
    )

    previous_quantity = models.PositiveIntegerField()

    new_quantity = models.PositiveIntegerField()

    reason = models.TextField()

    adjusted_by = models.CharField(max_length=100)

    adjusted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-adjusted_at"]

    def __str__(self):
        return (
            f"{self.product.name}: "
            f"{self.previous_quantity} → {self.new_quantity}"
        )