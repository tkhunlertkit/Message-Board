run: app.db
	python run.py

app.db:
	python db_create.py

clean:
	rm -rf ./tmp/associations/ ./tmp/nonces/ ./tmp/temp/ app.db	
