#!/usr/bin/env python3
from pathlib import Path
import argparse, io, json, os, re, sys, time
from urllib.parse import urlparse
import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'assets' / 'image-sources.json'
OUTDIR = ROOT / 'assets' / 'products'
REPORT = ROOT / 'assets' / 'image-sync-report.json'
UA = 'Mozilla/5.0 (compatible; GlobalTechCatalogImageSync/1.0)'


def normalize_image(raw: bytes, dest: Path):
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.mode in ('RGBA','LA'):
            bg = Image.new('RGBA', im.size, 'white')
            bg.alpha_composite(im.convert('RGBA'))
            im = bg.convert('RGB')
        else:
            im = im.convert('RGB')
        im = ImageOps.exif_transpose(im)
        # White canvas + contain preserves product aspect ratio and creates a consistent catalog look.
        max_side = 900
        im.thumbnail((max_side,max_side), Image.Resampling.LANCZOS)
        canvas = Image.new('RGB',(900,900),'white')
        x=(900-im.width)//2; y=(900-im.height)//2
        canvas.paste(im,(x,y))
        dest.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(dest,'WEBP',quality=84,method=6)


def fetch(session, url):
    r=session.get(url,timeout=28,allow_redirects=True,headers={'User-Agent':UA,'Accept':'image/avif,image/webp,image/apng,image/*,*/*;q=0.8','Referer':urlparse(url).scheme+'://'+urlparse(url).netloc+'/'})
    r.raise_for_status()
    ctype=(r.headers.get('content-type') or '').lower()
    if 'image/' not in ctype and not r.content.startswith((b'\xff\xd8',b'\x89PNG',b'RIFF')):
        raise ValueError(f'not an image: {ctype}')
    if len(r.content) < 500:
        raise ValueError('image payload too small')
    return r.content


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--force',action='store_true',help='redownload even if local file exists')
    args=ap.parse_args()
    data=json.loads(MANIFEST.read_text(encoding='utf-8'))
    products=data['products']
    if args.dry_run:
        print(f'{len(products)} product image definitions OK')
        missing=[p['model'] for p in products if not p.get('candidates') and not (ROOT/p['local']).exists()]
        print(f'{len(missing)} products have neither remote candidate nor preseeded local image')
        if missing: print('\n'.join(missing))
        return 0
    session=requests.Session()
    results=[]
    ok=0
    for idx,p in enumerate(products,1):
        dest=ROOT/p['local']
        candidates=p.get('candidates') or []
        status='kept-local' if dest.exists() else 'missing'
        error=''
        # Always try exact-model remote source so old/wrong placeholders get replaced.
        if candidates:
            for url in candidates:
                try:
                    raw=fetch(session,url)
                    normalize_image(raw,dest)
                    status='downloaded'
                    error=''
                    break
                except Exception as e:
                    error=f'{type(e).__name__}: {e}'
            if status!='downloaded' and dest.exists(): status='kept-local-after-fetch-failure'
        if dest.exists(): ok+=1
        results.append({'model':p['model'],'local':p['local'],'status':status,'error':error})
        print(f'[{idx:03}/{len(products):03}] {p["model"]}: {status}')
        time.sleep(0.08)
    REPORT.write_text(json.dumps({'total':len(products),'local_present':ok,'results':results},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Local images present: {ok}/{len(products)}')
    # Do not fail the workflow just because one vendor blocks hotlinking; existing local files remain intact.
    return 0

if __name__=='__main__':
    raise SystemExit(main())
