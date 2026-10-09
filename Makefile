.PHONY: dev prod

dev:
	cp .env.dev .env && docker compose up -d

prod:
	cp .env.prod .env && docker compose up -d