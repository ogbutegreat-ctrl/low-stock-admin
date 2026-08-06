from django import forms

from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [

            "name",

            "sku",

            "description",

            "image",

            "category",

            "supplier",

            "quantity",

            "minimum_stock",

            "reorder_threshold",

            "maximum_stock",

            "purchase_price",

            "selling_price",

        ]

        widgets = {

            "name": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Product name",

                }

            ),

            "sku": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "SKU",

                }

            ),

            "description": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 4,

                    "placeholder": "Product description",

                }

            ),

            "image": forms.ClearableFileInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "category": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "supplier": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "quantity": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "min": 0,

                }

            ),

            "minimum_stock": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "min": 0,

                }

            ),

            "reorder_threshold": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "min": 0,

                }

            ),

            "maximum_stock": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "min": 0,

                }

            ),

            "purchase_price": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                }

            ),

            "selling_price": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                }

            ),

        }


class StockUpdateForm(forms.Form):

    TRANSACTION_CHOICES = (

        ("IN", "Stock In"),

        ("OUT", "Stock Out"),

    )

    transaction_type = forms.ChoiceField(

        choices=TRANSACTION_CHOICES,

        widget=forms.Select(

            attrs={

                "class": "form-select",

            }

        ),

    )

    quantity = forms.IntegerField(

        min_value=1,

        widget=forms.NumberInput(

            attrs={

                "class": "form-control",

                "placeholder": "Enter quantity",

            }

        ),

    )

    reason = forms.CharField(

        required=False,

        widget=forms.Textarea(

            attrs={

                "class": "form-control",

                "rows": 3,

                "placeholder": "Reason for this stock update",

            }

        ),

    )