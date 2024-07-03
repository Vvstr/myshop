from django.contrib import admin
from .models import Category, Product
from django.shortcuts import render
from .recommender import Recommender


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price',
                    'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}

    # def get_recommendations_graph(self, request):
    #     r = Recommender(Product.objects.all())
    #     r.fit()
    #     r.visualize_graph()
    #     return render(request, 'admin/recommendations_graph.html', {})
