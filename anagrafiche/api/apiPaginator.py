#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'custom_page_size'
    max_page_size = 1000

