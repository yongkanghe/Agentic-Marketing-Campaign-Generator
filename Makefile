.PHONY: ux-test

ux-test:
	GEMINI_KEY=$(GEMINI_KEY) npm test -- --run
