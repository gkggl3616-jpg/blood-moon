"""XFS Gezgini: a bounded, paginated, read-only desktop archive browser."""
from __future__ import annotations
import math
import os
import queue
import sys
import threading
import time
import tkinter as tk
from collections import Counter
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import xfs_core as core

PAGE_SIZE = 200

class Browser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('XFS Gezgini — Salt Okunur')
        self.geometry('1320x800'); self.minsize(1000, 620)
        self.archive = None; self.matches = []; self.page = 0
        self.messages = queue.Queue(); self.jobs = {}; self.serial = 0
        self.search_timer = None; self.closing = False
        self.query = tk.StringVar(); self.ext = tk.StringVar(value='Tümü')
        self.status = tk.StringVar(value='Başlamak için bir XFS arşivi açın.')
        self.summary = tk.StringVar(value='Arşiv açık değil')
        self.page_text = tk.StringVar(value='0 kayıt')
        style = ttk.Style(self); style.theme_use('clam')
        family = 'Segoe UI' if os.name == 'nt' else 'DejaVu Sans'
        style.configure('.', font=(family, 10))
        style.map('TCombobox', fieldbackground=[('readonly', '#101820')], foreground=[('readonly', '#e8edf2')], selectbackground=[('readonly', '#101820')], selectforeground=[('readonly', '#e8edf2')])
        style.configure('.', background='#17212c', foreground='#e8edf2', fieldbackground='#101820')
        style.configure('Treeview', background='#101820', foreground='#edf1f4', fieldbackground='#101820', rowheight=29)
        style.map('Treeview', background=[('selected', '#536c83')])
        style.configure('TButton', padding=7)
        style.configure('Title.TLabel', font=(family, 18, 'bold'))
        self.configure(bg='#17212c')
        top = ttk.Frame(self, padding=14); top.pack(fill='x')
        ttk.Label(top, text='XFS GEZGİNİ', style='Title.TLabel').pack(side='left')
        ttk.Label(top, text='  •  Salt okunur arşiv tarayıcısı').pack(side='left')
        self.open_button = ttk.Button(top, text='XFS Aç', command=self.open_file); self.open_button.pack(side='right')
        ttk.Label(self, textvariable=self.summary, padding=(14, 3), wraplength=1250).pack(fill='x')
        filters = ttk.Frame(self, padding=14); filters.pack(fill='x')
        ttk.Label(filters, text='Ad / klasör ara:').pack(side='left')
        self.search = ttk.Entry(filters, textvariable=self.query); self.search.pack(side='left', fill='x', expand=True, padx=8)
        ttk.Label(filters, text='Dosya türü:').pack(side='left')
        self.types = ttk.Combobox(filters, textvariable=self.ext, state='readonly', width=18, values=['Tümü', '.ltb', '.dtx', '.txt', '.lta', '.ltc', '.wav'])
        self.types.pack(side='left', padx=8)
        self.query.trace_add('write', self.schedule_search)
        self.types.bind('<<ComboboxSelected>>', self.schedule_search)
        panes = ttk.Panedwindow(self, orient='horizontal'); panes.pack(fill='both', expand=True, padx=14)
        left = ttk.Frame(panes); right = ttk.Frame(panes, padding=(12,0,0,0))
        panes.add(left, weight=3); panes.add(right, weight=2)
        tree_area = ttk.Frame(left); tree_area.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(tree_area, columns=('ext', 'size', 'packed'), selectmode='extended')
        self.tree.heading('#0', text='Arşiv içindeki tam yol'); self.tree.column('#0', width=480, minwidth=280, stretch=True)
        for key, title, width in [('ext','Tür',65),('size','Açılmış',90),('packed','Paketli',90)]:
            self.tree.heading(key, text=title); self.tree.column(key, width=width, stretch=False, anchor='e')
        scrollbar = ttk.Scrollbar(tree_area, orient='vertical', command=self.tree.yview)
        horizontal = ttk.Scrollbar(tree_area, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=horizontal.set)
        self.tree.grid(row=0,column=0,sticky='nsew'); scrollbar.grid(row=0,column=1,sticky='ns'); horizontal.grid(row=1,column=0,sticky='ew')
        tree_area.rowconfigure(0,weight=1); tree_area.columnconfigure(0,weight=1)
        self.tree.bind('<<TreeviewSelect>>', self.show_selected)
        nav = ttk.Frame(left); nav.pack(fill='x', pady=8)
        ttk.Button(nav, text='◀ Önceki', command=lambda:self.turn_page(-1)).pack(side='left')
        ttk.Label(nav, textvariable=self.page_text).pack(side='left',padx=10)
        ttk.Button(nav, text='Sonraki ▶', command=lambda:self.turn_page(1)).pack(side='left')
        ttk.Button(nav, text='Sayfayı Seç', command=lambda:self.tree.selection_set(self.tree.get_children())).pack(side='right')
        ttk.Label(right,text='DOSYA BİLGİSİ / ÖNİZLEME',font=(family,12,'bold')).pack(anchor='w',pady=(0,8))
        self.details = tk.Text(right,wrap='word',bg='#101820',fg='#dbe6f0',insertbackground='white',font=('Consolas' if os.name == 'nt' else 'DejaVu Sans Mono',10),borderwidth=0,padx=12,pady=12,state='disabled')
        self.details.pack(fill='both',expand=True)
        self.set_details('Bir kayıt seçin.\n\nMetin ve hex önizleme: en fazla 256 KiB.\n\n3B model görüntüleyicisi bu sürümde yoktur.')
        actions = ttk.Frame(self,padding=14); actions.pack(fill='x')
        self.export_button=ttk.Button(actions,text='Seçilenleri Dışa Aktar',command=lambda:self.export(False));self.export_button.pack(side='left')
        self.all_button=ttk.Button(actions,text='Filtredeki Tümünü Dışa Aktar',command=lambda:self.export(True));self.all_button.pack(side='left',padx=8)
        self.csv_button=ttk.Button(actions,text='Filtre Listesini CSV Kaydet',command=self.export_csv);self.csv_button.pack(side='left')
        self.cancel_button=ttk.Button(actions,text='İşlemi İptal Et',command=self.cancel_main,state='disabled');self.cancel_button.pack(side='right')
        self.progress=ttk.Progressbar(self,mode='determinate');self.progress.pack(fill='x',padx=14)
        ttk.Label(self,textvariable=self.status,padding=14,wraplength=1250).pack(fill='x')
        self.protocol('WM_DELETE_WINDOW',self.close)
        self.after(50,self.drain)
    def set_details(self,text):
        self.details.configure(state='normal');self.details.delete('1.0','end');self.details.insert('1.0',text);self.details.configure(state='disabled')
    def job(self,channel,work,done):
        if channel in self.jobs:self.jobs[channel][1].set()
        self.serial+=1;serial=self.serial;cancel=threading.Event()
        self.jobs[channel]=(serial,cancel,done)
        def run():
            last=[0.0]
            def progress(current,total,label=''):
                now=time.monotonic()
                if now-last[0]>.10:
                    last[0]=now;self.messages.put((channel,serial,'progress',(current,total,label)))
            try:result=work(cancel,progress);self.messages.put((channel,serial,'done',result))
            except core.Cancelled:self.messages.put((channel,serial,'cancelled',None))
            except Exception as exc:self.messages.put((channel,serial,'error',str(exc)))
        threading.Thread(target=run,daemon=True,name='xfs-'+channel).start()
    def drain(self):
        # Bounded drain prevents an event flood from starving paint/input events.
        for _ in range(40):
            try:channel,serial,kind,value=self.messages.get_nowait()
            except queue.Empty:break
            job=self.jobs.get(channel)
            if not job or job[0]!=serial:continue
            if kind=='progress':
                if channel=='main':
                    current,total,label=value;self.progress['value']=100*current/max(1,total)
                    if label:self.status.set(label)
                continue
            del self.jobs[channel]
            if channel=='main':self.busy(False)
            if kind=='done':job[2](value)
            elif kind=='error':
                if channel=='preview':self.set_details(self.current_info+'\n\nÖnizleme açılamadı: '+value)
                else:self.status.set('Hata: '+value);messagebox.showerror('İşlem tamamlanamadı',value,parent=self)
            elif channel=='main':self.status.set('İşlem iptal edildi. Tamamlanan dosyalar korundu; yarım dosya kaldırıldı.')
        if self.winfo_exists():self.after(50,self.drain)
    def busy(self,value):
        state='disabled' if value else 'normal'
        for button in (self.open_button,self.export_button,self.all_button,self.csv_button):button.configure(state=state)
        self.cancel_button.configure(state='normal' if value else 'disabled')
        if not value:self.progress['value']=0
    def cancel_main(self):
        if 'main' in self.jobs:self.jobs['main'][1].set();self.status.set('İptal ediliyor…')
    def open_file(self):
        path=filedialog.askopenfilename(title='XFS arşivini seçin',filetypes=[('Xenesis arşivi','*.xfs'),('Tüm dosyalar','*.*')])
        if not path:return
        self.busy(True);self.status.set('Dosya tablosu okunuyor…')
        def done(archive):
            self.archive=archive
            counts=Counter(e.extension or '(uzantısız)' for e in archive.entries)
            self.types['values']=['Tümü']+sorted(counts)
            self.summary.set(f'{archive.path}  |  XFS {archive.version}  |  {len(archive.entries):,} dosya  |  {format_size(archive.size)}')
            self.ext.set('Tümü');self.start_search();self.status.set('Arşiv açıldı. Arşiv içeriği değiştirilmez.')
        self.job('main',lambda c,p:core.open_archive(path,c,p),done)
    def schedule_search(self,*_):
        if self.search_timer:self.after_cancel(self.search_timer)
        self.search_timer=self.after(250,self.start_search)
    def start_search(self):
        self.search_timer=None
        if not self.archive:return
        archive=self.archive;query=self.query.get();extension=self.ext.get()
        extension='' if extension=='Tümü' else extension
        def done(indices):self.matches=indices;self.page=0;self.render_page()
        self.job('filter',lambda c,p:core.filter_entries(archive.entries,query,extension,c),done)
    def render_page(self):
        if 'preview' in self.jobs:self.jobs['preview'][1].set();del self.jobs['preview']
        self.tree.delete(*self.tree.get_children())
        start=self.page*PAGE_SIZE
        for index in self.matches[start:start+PAGE_SIZE]:
            e=self.archive.entries[index]
            self.tree.insert('', 'end',iid=str(index),text=e.path,values=(e.extension,format_size(e.size),format_size(e.packed)))
        pages=max(1,math.ceil(len(self.matches)/PAGE_SIZE))
        self.page_text.set(f'{len(self.matches):,} sonuç • {self.page+1}/{pages}')
        self.set_details('Bir kayıt seçin. Çoklu seçim: Ctrl / Shift.\n\nSeçimler bu sayfa içindir; bütün sonuçlar için “Filtredeki Tümünü” düğmesini kullanın.')
    def turn_page(self,step):
        page=self.page+step
        if 0<=page<math.ceil(len(self.matches)/PAGE_SIZE):self.page=page;self.render_page()
    def show_selected(self,*_):
        selection=self.tree.selection()
        if not selection or not self.archive:return
        archive=self.archive;e=archive.entries[int(selection[-1])]
        self.current_info=f'{e.path}\n\nTür: {e.extension}\nAçılmış boyut: {e.size:,} bayt\nPaketli boyut: {e.packed:,} bayt\nArşiv konumu: {e.offset:,}\nSeçili kayıt: {len(selection)}'
        info=self.current_info;self.set_details(info+'\n\nÖnizleme hazırlanıyor…')
        def done(data):
            if data is None:body='Bu dosya 256 KiB önizleme sınırını aşıyor. Dışa aktararak açabilirsiniz.'
            elif e.extension in ('.txt','.ini','.json','.xml','.csv','.cfg','.lta','.bms'):
                try:body=data.decode('utf-8-sig')
                except UnicodeDecodeError:body=data.decode('cp1254',errors='replace')
            else:
                body='İlk 1.024 bayt (hex):\n'+'\n'.join(f'{n:08X}  '+data[n:n+16].hex(' ') for n in range(0,min(len(data),1024),16))
                if e.extension=='.ltb' and len(data)>=40:
                    body=f'LTB başlığı: tür {int.from_bytes(data[:2],"little")}, dosya sürümü {int.from_bytes(data[2:4],"little")}, model sürümü {int.from_bytes(data[20:24],"little")}\n\n'+body
            self.set_details(info+'\n\n'+body)
        self.job('preview',lambda c,p:core.preview(archive,e,cancel=c),done)
    def export(self,all_matches):
        if not self.archive:return
        indices=list(self.matches) if all_matches else [int(i) for i in self.tree.selection()]
        if not indices:messagebox.showinfo('Dosya seçin','Önce dışa aktarılacak kayıtları seçin.',parent=self);return
        folder=filedialog.askdirectory(title='Ayrı bir çıktı klasörü seçin')
        if not folder:return
        archive=self.archive;self.busy(True);self.status.set(f'{len(indices)} dosya çıkarılıyor…')
        def work(cancel,progress):
            results=Counter();errors=[]
            for number,index in enumerate(indices):
                core.check_cancel(cancel);e=archive.entries[index]
                try:
                    def item_progress(current,total):progress(number+current/max(1,total),len(indices),f'{number+1}/{len(indices)} • {e.path}')
                    results[core.extract_entry(archive,e,folder,cancel,item_progress)]+=1
                except core.Cancelled:raise
                except (core.XFSError,OSError) as exc:
                    results['failed']+=1
                    if len(errors)<100:errors.append(f'{e.path}: {exc}')
                progress(number+1,len(indices),f'{number+1}/{len(indices)} dosya işlendi')
            return results,errors
        def done(result):
            counts,errors=result
            self.progress['value']=100;self.status.set(f'Tamamlandı: {counts["written"]} çıkarıldı, {counts["skipped"]} mevcut dosya korundu, {counts["failed"]} hata.')
            if errors:self.set_details('Çıkarma hataları (ilk 100):\n\n'+'\n'.join(errors))
        self.job('main',work,done)
    def export_csv(self):
        if not self.archive:return
        path=filedialog.asksaveasfilename(title='Filtre listesini kaydet',defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if not path:return
        archive=self.archive;indices=tuple(self.matches);self.busy(True)
        self.job('main',lambda c,p:core.save_list(archive,indices,path),lambda _:self.status.set('Filtre listesi kaydedildi.'))
    def close(self):
        self.closing=True
        for _,cancel,_ in self.jobs.values():cancel.set()
        if self.jobs:
            self.busy(True);self.search.configure(state='disabled');self.types.configure(state='disabled')
            self.status.set('Kapatılıyor… Yarım dosyalar temizleniyor.')
            self.after(50,self.finish_close)
        else:self.destroy()
    def finish_close(self):
        if self.jobs:self.after(50,self.finish_close)
        else:self.destroy()

def format_size(value):
    for suffix in ('B','KiB','MiB','GiB'):
        if value<1024 or suffix=='GiB':return f'{value:.1f} {suffix}' if suffix!='B' else f'{value} B'
        value/=1024

if __name__=='__main__':
    app = Browser()
    if '--smoke-test' in sys.argv:
        app.after(1000, app.close)
    app.mainloop()
