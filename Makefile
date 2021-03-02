# main Makefile calling other Makefiles

all:
	make -C ./docs/ -f Makefile

files:
	make -C ./docs/ -f Makefile files

clean:
	make -C ./docs/ -f Makefile clean

docx:
	make -C ./docs/ -f Makefile docx

html:
	make -C ./docs/ -f Makefile html