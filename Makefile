HOME :=

define exclude
	grep -vP "^($(shell echo $(1) | sed "s/\s/\|/g"))"
endef

FINDFILES := find src/home -type f -name

IGNORE := $(patsubst %,src/home/%,$(shell cat ignore))
RAW := $(patsubst %,src/home/%,$(shell cat raw))
UNSEEN := $(IGNORE) $(RAW)

SRCDIRS := $(shell find src/home -mindepth 1 -type d | sed "s/$$/\//" | $(call exclude,$(IGNORE)))
DISTDIRS := $(patsubst src/home/%,dist/%,$(SRCDIRS))

SRCHTML := $(shell $(FINDFILES) \*.html | $(call exclude,$(UNSEEN)))
DISTHTML := $(patsubst src/home/%,dist/%,$(SRCHTML))

SRCCSS := $(shell $(FINDFILES) \*.css | $(call exclude,$(UNSEEN)))
DISTCSS := $(patsubst src/home/%,dist/%,$(SRCCSS))

SRCJS := $(shell $(FINDFILES) \*.js | $(call exclude,$(UNSEEN)))
DISTJS := $(patsubst src/home/%,dist/%,$(SRCJS))

PROCESSED := $(SRCHTML) $(SRCCSS) $(SRCJS)

NOTCOPY := $(IGNORE) $(PROCESSED)
SRCCOPY := $(shell $(FINDFILES) \* | $(call exclude,$(NOTCOPY)))
DISTCOPY := $(patsubst src/home/%,dist/%,$(SRCCOPY))

TEXTMODE := $(patsubst dist/%.html,dist/%.txt,$(DISTHTML))

all: $(DISTHTML) $(DISTCSS) $(DISTJS) $(DISTCOPY) $(TEXTMODE)

$(DISTHTML): $(SRCHTML) | $(DISTDIRS)
	cat $(patsubst dist/%,src/home/%,$@) \
		| python htmlsubst.py \
		| sed "s/\$$HOME/$(HOME)/g" \
		| minify --type html \
		> $@
	echo "<!-- Using a plain text browser? Visit thomaskaldahl.com/$(patsubst dist/%.html,%.txt,$@) for a plain text transcript of this page. -->" > $@.tmp
	cat $@ >> $@.tmp
	cat $@.tmp > $@
	rm $@.tmp

$(DISTCSS): $(SRCCSS) | $(DISTDIRS)
	cat $(patsubst dist/%,src/home/%,$@) | minify --type css > $@

$(DISTJS): $(SRCJS) | $(DISTDIRS)
	cat $(patsubst dist/%,src/home/%,$@) | sed "s/\$$HOME/$(HOME)/g" | minify --type js > $@

$(DISTCOPY): $(SRCCOPY) | $(DISTDIRS)
	cp $(patsubst dist/%,src/home/%,$@) $@

$(TEXTMODE): $(DISTHTML) | $(DISTDIRS)
	pandoc -f html -t plain $(patsubst dist/%.txt,dist/%.html,$@) > $@

$(DISTDIRS): | dist $(SRCDIRS)
	for d in $(DISTDIRS); do if [ ! -d $$d ]; then mkdir $$d; fi; done

dist: | src/home
	mkdir dist

run:
	php -t dist -S localhost:3000

clean:
	rm -rf dist
