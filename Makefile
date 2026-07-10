PYTHON ?= python
MANAGE := $(PYTHON) manage.py
HOST ?= 127.0.0.1
PORT ?= 8000
ADMIN_USER ?= cclx
ADMIN_PASS ?= cclx

.PHONY: help check test run migrate makemigrations shell createsuperuser admin clean-pyc

help:
	@echo "Available commands:"
	@echo "  make check            Run Django system checks"
	@echo "  make test             Run Django tests"
	@echo "  make run              Start dev server on HOST:PORT"
	@echo "  make migrate          Apply database migrations"
	@echo "  make makemigrations   Create database migrations"
	@echo "  make shell            Open Django shell"
	@echo "  make admin            Create/update default admin user"
	@echo "  make clean-pyc        Remove Python cache files"

check:
	$(MANAGE) check

test:
	$(MANAGE) test

run:
	$(MANAGE) runserver $(HOST):$(PORT)

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

shell:
	$(MANAGE) shell

createsuperuser:
	$(MANAGE) createsuperuser

admin:
	$(MANAGE) shell -c "from django.contrib.auth.models import User; u, _ = User.objects.get_or_create(username='$(ADMIN_USER)'); u.is_staff=True; u.is_superuser=True; u.is_active=True; u.set_password('$(ADMIN_PASS)'); u.save(); print('admin ready:', u.username)"

clean-pyc:
	$(PYTHON) -c "import pathlib, shutil; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
