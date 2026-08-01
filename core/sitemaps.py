"""
Sitemaps for SEO.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'plans', 'about', 'locations', 'classes', 'blog_list', 'contact']

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    """Sitemap for blog posts."""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at