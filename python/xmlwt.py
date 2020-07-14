import xml.sax as sax

wikt = \
"J:/downloads/enwiktionary-20190301-pages-articles.xml/enwiktionary-20190301-pages-articles.xml"

class Handler(sax.handler.ContentHandler):

    def startDocument(self, ):
        self.cntr = 0
        self.printable = 0

    def spacer(self):
        return '  '*self.cntr

    def characters(self, content):

        if self.printable:
            if len(content.strip())>0:
                if self.printable == 'title' or \
                (self.printable =='text' and content.startswith("# ") and not content.startswith("#*")):
                    print(self.spacer()+"> "+content)

    def startElement(self, name, attrs):

        if name == 'title' or name == 'text':
            self.printable = name

            attnames = attrs.getNames()
            if len(attnames)==0:
                a = ''
            else:
                a = ' - ' + ','.join([k+"="+attrs.getValue(k) for k in attnames])


            print('{}{}{}'.format(self.spacer(), name, a))
        else:
            self.printable = 0

        self.cntr+=1

    def endElement(self, name):
        self.cntr-=1

h = Handler()

with open(wikt, 'rb') as f:
    sax.parse(f,h)
