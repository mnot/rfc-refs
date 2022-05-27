PYTHON = python3

update: rfcs
	$(PYTHON) extract-refs.py refs.json > tmp.json
	mv tmp.json refs.json

.PHONY: rfcs
rfcs:
	rsync -az --delete --include 'rfc*.txt' --include 'rfc*.xml' --exclude '*' ftp.rfc-editor.org::rfcs rfcs

.PHONY: refs.json
refs.json:
	$(PYTHON) extract-refs.py > $@

.PHONY: lint
lint: *.py
	black $^

.PHONY: clean
clean:
	rm -f refs.json
