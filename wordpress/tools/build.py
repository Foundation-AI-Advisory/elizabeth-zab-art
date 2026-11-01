#!/usr/bin/env python3
"""Deterministic conversion of the pinned static source into an editable theme."""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import re,json,shutil,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
WP=ROOT/'wordpress'; T=WP/'theme/elizabeth-zab'; DATA=T/'inc/data'; DATA.mkdir(parents=True,exist_ok=True)
PAGES={'home':'index.html','work':'work/index.html','story':'story/index.html','studio':'studio/index.html','designers':'designers/index.html','qa':'qa/index.html','classes':'classes/index.html','404':'404.html'}
TITLES={'home':'Home','work':'Work','story':'Story','studio':'Studio','designers':'Designers','qa':'Q&A','classes':'Classes','404':'Page not found'}
class Nodes(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=False);self.s=s;self.lines=[0];self.stack=[];self.nodes=[]
  for m in re.finditer('\n',s):self.lines.append(m.end())
  self.feed(s)
 def pos(self):l,c=self.getpos();return self.lines[l-1]+c
 def handle_starttag(self,tag,attrs):
  st=self.pos();n={'tag':tag,'attrs':dict(attrs),'start':st,'open_end':st+len(self.get_starttag_text())};self.nodes.append(n)
  if tag not in ['img','br','hr','meta','link','input','source','wbr','area','base','embed','param','track']:self.stack.append(n)
  else:n.update(end=n['open_end'],close_start=n['open_end'])
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i]['tag']==tag:
    n=self.stack[i];n.update(close_start=self.pos(),end=self.s.find('>',self.pos())+1);self.stack=self.stack[:i];break
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def plain(s):return unescape(re.sub('<[^>]+>','',s)).strip()
def exact(s,tag,cls):
 for n in Nodes(s).nodes:
  if n['tag']==tag and cls in n['attrs'].get('class','').split():return s[n['start']:n['end']]
 raise ValueError((tag,cls))
def extract(s,slug):
 fields={}; rep=[]; covered=[]
 def add(st,en,typ,label,value=None):
  if any(st>=a and en<=b for a,b in covered):return
  k='f%03d'%(len(fields)+1);fields[k]={'type':typ,'label':label,'default':s[st:en] if value is None else value};rep.append((st,en,'{{ez:'+k+'}}'));covered.append((st,en))
 for n in Nodes(s).nodes:
  if 'end' not in n:continue
  tag=n['tag'];a=n['attrs'];inner=s[n['open_end']:n['close_start']];cl=a.get('class','').split()
  chosen=tag in ['p','h1','h2','h3','h4','li','dt','dd','summary','figcaption'] or any(c in cl for c in ['eyebrow','pull-quote','cap'])
  if chosen and not any(t in inner for t in ['Wed 3–7', '3987 Medina Rd, Studio 3', 'Akron, OH 44333', 'Inside Salon Lofts, Studio 3']) and plain(inner) and '<svg' not in inner and '<img' not in inner and '{{ez:gallery}}' not in inner:
   # Preserve home headline line breaks as independent editable clauses.
   if tag=='h1' and 'hero-tagline' in cl:continue
   typ='rich' if '<' in inner or tag in ['p','dd','li'] else 'text'
   add(n['open_end'],n['close_start'],typ, ('Heading' if tag.startswith('h') else 'Text')+' — '+plain(inner)[:65])
  elif tag=='span' and a.get('class')=='ht-last' or (tag=='span' and inner in ['Walk In,','See the Work,']):
   add(n['open_end'],n['close_start'],'text','Home headline — '+plain(inner))
  elif tag=='a' and plain(inner) and '<svg' not in inner:
   add(n['open_end'],n['close_start'],'rich' if '<' in inner else 'text','Link text — '+plain(inner)[:55])
  start=s[n['start']:n['open_end']]
  for attr in ['src','alt','aria-label','href']:
   if attr not in a:continue
   if attr=='src' and tag!='img':continue
   if attr=='aria-label' and a.get('role')!='img':continue
   if attr=='href' and (a[attr].startswith('tel:') or 'instagram.com' in a[attr]):continue
   m=re.search(r'\b'+attr+r'\s*=\s*([\'"])(.*?)\1',start,re.S)
   if m:
    typ='image' if attr=='src' else 'url' if attr=='href' else 'attribute'
    add(n['start']+m.start(2),n['start']+m.end(2),typ,('Image' if attr=='src' else 'Image description' if attr in ['alt','aria-label'] else 'Link destination')+' — '+(plain(inner) or a.get('alt') or a.get('aria-label') or a[attr])[:55],unescape(m.group(2)))
  for m in re.finditer(r'url\(([\'"]?)(/assets/[^)\'"\s]+)\1\)',start):
   add(n['start']+m.start(2),n['start']+m.end(2),'image','Background image — '+(a.get('aria-label') or a.get('class','Artwork'))[:65])
 for st,en,v in sorted(rep,reverse=True):s=s[:st]+v+s[en:]
 return s,fields
manifest={'source_commit':'6e85ac6c2b80cd6b7972dec2fd121f09def39a82','source_url':'https://github.com/Foundation-AI-Advisory/elizabeth-zab-art','pages':{},'assets':[]}
for slug,path in PAGES.items():
 src=(ROOT/path).read_text(); head=src.split('</head>')[0]; body=re.search(r'<body[^>]*>(.*?)</body>',src,re.S).group(1)
 css='\n'.join(re.findall(r'<style[^>]*>(.*?)</style>',src,re.S)); (T/f'assets/css/{slug}.css').write_text(css)
 scripts=[x for x in re.findall(r'<script>(.*?)</script>',src,re.S) if 'gtag' not in x and 'ezart_cookie' not in x and 'document.documentElement.classList' not in x]
 (T/f'assets/js/{slug}.js').write_text('\n'.join(scripts))
 schema=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',src,re.S)]
 header=exact(body,'header','site-header');footer=exact(body,'footer','site-footer')
 if slug=='home':
  (DATA/'header.html').write_text(header);(DATA/'footer.html').write_text(footer);(DATA/'cookie.html').write_text(exact(body,'div','cookie-banner'))
 if slug=='404':(DATA/'footer-404.html').write_text(footer)
 body=body.replace(header,'').replace(footer,'')
 if 'cookie-banner' in body:body=body.replace(exact(body,'div','cookie-banner'),'')
 body=re.sub(r'<script[^>]*>.*?</script>','',body,flags=re.S)
 gallery=[]
 if slug=='work':
  for n in Nodes(body).nodes:
   if n['tag']=='article' and 'plate' in n['attrs'].get('class','').split():
    block=body[n['start']:n['end']]
    def cl(c):return plain(exact(block,'p' if c in ['plate-meta','plate-note'] else 'h2',c))
    im=next(n for n in Nodes(block).nodes if n['tag']=='img')['attrs']
    gallery.append({'title':cl('plate-title'),'medium':cl('plate-meta'),'description':cl('plate-note'),'image':im['src'],'alt':im['alt'],'width':im['width'],'height':im['height']})
  plates=exact(body,'div','plates');body=body.replace(plates,'<div class="plates">{{ez:gallery}}</div>')
 template,fields=extract(body,slug)
 (DATA/f'{slug}.html').write_text(template)
 meta={m.group(2):unescape(m.group(4)) for m in re.finditer(r'<meta\s+(name|property)="([^"]+)"\s+content=("|\')(.*?)\3',head,re.S)}
 manifest['pages'][slug]={'title':TITLES[slug],'path':'/' if slug=='home' else '/'+slug+'/','seo_title':plain(re.search(r'<title>(.*?)</title>',head,re.S).group(1)),'meta':meta,'schema':schema,'fields':fields,'gallery':gallery,'content':body}
# Original artwork and root icon copies remain byte-identical.
ORIG=T/'assets/original';ORIG.mkdir(exist_ok=True)
for p in sorted(list((ROOT/'assets').glob('*'))+list(ROOT.glob('*.png'))+list(ROOT.glob('*.ico'))+list(ROOT.glob('*.svg'))+[ROOT/'llms.txt']):
 rel=p.relative_to(ROOT).as_posix();d=ORIG/rel;d.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,d)
 manifest['assets'].append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size})
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Page and meta export for the built-in WordPress XML importer. Local importer is preferred.
from xml.sax.saxutils import escape
items=[]
def cd(s):return '<![CDATA['+s.replace(']]>',']]]]><![CDATA[>')+']]>'
for i,(slug,p) in enumerate(manifest['pages'].items(),1):
 if slug=='404':continue
 metas={'_wp_page_template':'page-templates/migrated.php','_ez_layout':slug,'_ez_fields_json':json.dumps({k:v['default'] for k,v in p['fields'].items()},ensure_ascii=False),'_ez_gallery_json':json.dumps(p['gallery'],ensure_ascii=False),'_ez_seo_title':p['seo_title'],'_ez_description':p['meta'].get('description',''),'_ez_import_commit':manifest['source_commit']}
 body=p['content']
 if slug=='work':
  orig=(ROOT/PAGES[slug]).read_text();body=body.replace('<div class="plates">{{ez:gallery}}</div>',exact(orig,'div','plates'))
 meta_xml=''.join('<wp:postmeta><wp:meta_key>'+cd(k)+'</wp:meta_key><wp:meta_value>'+cd(v)+'</wp:meta_value></wp:postmeta>' for k,v in metas.items())
 items.append(f'<item><title>{escape(p["title"])}</title><link>https://elizabethzab.art{p["path"]}</link><dc:creator>migration</dc:creator><guid isPermaLink="false">https://elizabethzab.art/?page_id={i}</guid><content:encoded>{cd(body)}</content:encoded><wp:post_id>{i}</wp:post_id><wp:post_date>2026-10-21 00:00:00</wp:post_date><wp:post_date_gmt>2026-10-21 00:00:00</wp:post_date_gmt><wp:post_name>{slug}</wp:post_name><wp:status>publish</wp:status><wp:post_type>page</wp:post_type><wp:post_parent>0</wp:post_parent><wp:menu_order>{i}</wp:menu_order><wp:comment_status>closed</wp:comment_status><wp:ping_status>closed</wp:ping_status>{meta_xml}</item>')
(WP/'elizabeth-zab-pages.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:wfw="http://wellformedweb.org/CommentAPI/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:wp="http://wordpress.org/export/1.2/"><channel><title>Elizabeth Zab Art</title><link>https://elizabethzab.art</link><description>Migration content</description><language>en-US</language><wp:wxr_version>1.2</wp:wxr_version><wp:base_site_url>https://elizabethzab.art</wp:base_site_url><wp:base_blog_url>https://elizabethzab.art</wp:base_blog_url>'+''.join(items)+'</channel></rss>\n')
print('Built',len(manifest['pages'])-1,'pages,',len(manifest['assets']),'assets,',sum(len(p['fields']) for p in manifest['pages'].values()),'editable fields')
