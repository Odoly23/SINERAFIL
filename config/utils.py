import datetime
from decimal import Decimal

from django.utils import timezone


def f_monthname(month):
	m = ['Janeiru', 'Fevereiru', 'Marsu', 'Abril', 'Maiu', 'Junhu', 'Julhu', 'Agostu', 'Setembru',
		'Outubru', 'Novembru', 'Dezembru']
	return m[month - 1]


def first_day_of_month(day=None):
	day = day or timezone.localdate()
	return day.replace(day=1)


def month_start(day, back=0):
	"""Loron dahuluk fulan ne'ebé `back` fulan molok `day` (back negativu = fulan tuir mai)."""
	index = day.year * 12 + (day.month - 1) - back
	return datetime.date(index // 12, index % 12 + 1, 1)


def to_decimal(value):
	return Decimal(str(value or 0))
