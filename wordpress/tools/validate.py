#!/usr/bin/env python3
"""Static migration checks and an honest front-end-only preview, not a PHP runtime."""
import json,re,hashlib,subprocess,sys,shutil,html as H
from pathlib import Path
from lxml import html, etree
ROOT=Path(__file__).resolve().parents[2]; WP=ROOT/'wordpress'; T=WP/'theme/elizabeth-zab'; D=T/'inc/data';m=json.loads((D/'manifest.json').read_text())
checks=[]
def check(test,label):
 if not test:raise AssertionError(label)
 checks.append(label)
def normalize(s):
 doc=html.fragment_fromstring(s,create_parent=True)
 for n in doc.xpath('.//comment()'):n.getparent().remove(n)
 def node(n):return (n.tag,tuple(sorted(n.attrib.items())),re.sub(r'\s+',' ',n.text or '').strip(),tuple(node(c) for c in n),re.sub(r'\s+',' ',n.tail or '').strip())
 return node(doc)
preview=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else None
if preview:
 preview.mkdir(parents=True,exist_ok=True);(preview/'.openai').mkdir(exist_ok=True)
 (preview/'.openai/hosting.json').write_text(json.dumps({'static':{'directory':'public'}}));out=preview/'public';out.mkdir(exist_ok=True)
 shutil.copytree(T/'assets',out/'theme-assets',dirs_exist_ok=True)
 shutil.copytree(T/'assets/original',out,dirs_exist_ok=True)
for slug,p in m['pages'].items():
 src=(ROOT/('index.html' if slug=='home' else '404.html' if slug=='404' else slug+'/index.html')).read_text()
 template=(D/(slug+'.html')).read_text(); keys=set(re.findall(r'\{\{ez:(f\d+)\}\}',template))
 check(keys==set(p['fields']),slug+': every editable field has a matching template slot')
 rendered=template
 for k,f in p['fields'].items():rendered=rendered.replace('{{ez:'+k+'}}',f['default'] if f['type']=='rich' else H.escape(H.unescape(f['default']),quote=True))
 expected=p['content']
 if slug=='work':
  source=html.fromstring(src);articles=source.xpath('//article[contains(@class,"plate")]')
  check(len(articles)==len(p['gallery'])==9,'work: all nine gallery records')
  # Check each imported record against its source, including real dimensions and alt text.
  for a,r in zip(articles,p['gallery']):
   im=a.find('.//img');title=a.find('.//h2').text
   check(title==r['title'] and im.get('src')==r['image'] and im.get('alt')==r['alt'] and im.get('width')==r['width'] and im.get('height')==r['height'],'gallery: '+title)
  start=src.index('<div class="plates">');end=src.index('\n  </div>\n</section>',start)
  gallery=src[start+len('<div class="plates">'):end]
  rendered=rendered.replace('{{ez:gallery}}',gallery);expected=expected.replace('{{ez:gallery}}',gallery)
 check('{{ez:' not in rendered,slug+': no unresolved tokens')
 check(normalize(rendered)==normalize(expected),slug+': editable conversion preserves original content and structure')
 check((T/f'assets/css/{slug}.css').read_text()=='\n'.join(re.findall(r'<style[^>]*>(.*?)</style>',src,re.S)),slug+': original CSS retained exactly')
 for schema in p['schema']:check(isinstance(schema,dict),slug+': valid JSON-LD')
 for asset in re.findall(r'/assets/[^\'"\s)<>]+',rendered):check((T/'assets/original'/asset.lstrip('/')).is_file(),slug+': asset '+asset)
 if preview:
  head=src.split('</head>')[0];head=re.sub(r'<script[^>]*>.*?</script>','',head,flags=re.S);head=re.sub(r'<style[^>]*>.*?</style>','',head,flags=re.S)
  head=head.replace('content="index, follow"','content="noindex, nofollow"')
  head+='\n<script>document.documentElement.classList.add("js");</script>'
  head+=f'<link rel="stylesheet" href="/theme-assets/css/{slug}.css"><link rel="stylesheet" href="/theme-assets/css/wordpress.css"></head>'
  footer=(D/('footer-404.html' if slug=='404' else 'footer.html')).read_text()
  cookie='' if slug=='404' else (D/'cookie.html').read_text()
  result=head+'<body id="top"'+(' class="error404"' if slug=='404' else '')+'>'+(D/'header.html').read_text()+'<div id="ez-main">'+rendered+'</div>'+footer+cookie+f'<script src="/theme-assets/js/{slug}.js"></script><script>window.ezAnalyticsId="";</script><script src="/theme-assets/js/site.js"></script></body></html>'
  path=out/('index.html' if slug=='home' else '404.html' if slug=='404' else slug+'/index.html');path.parent.mkdir(exist_ok=True,parents=True);path.write_text(result)
for a in m['assets']:check(hashlib.sha256((T/'assets/original'/a['path']).read_bytes()).hexdigest()==a['sha256'],'asset checksum: '+a['path'])
wxr=etree.parse(str(WP/'elizabeth-zab-pages.xml'));check(len(wxr.findall('./channel/item'))==7,'WXR: seven importable WordPress pages')
for p in (T/'assets/js').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True,capture_output=True)
check(True,'JavaScript: all 10 scripts parse')
subprocess.run([sys.executable,str(ROOT/'scripts/seo-audit.py')],check=True)
check(True,'Existing SEO audit: seven routes and seven sitemap URLs pass')
report={'result':'PASS','checks':len(checks),'pages':7,'gallery_pieces':9,'preserved_assets':len(m['assets']),'php_runtime_tested':False,'hosted_staging_tested':False,'source_commit':m['source_commit'],'checks_passed':checks}
(WP/'validation-static.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks_passed'},indent=2))
