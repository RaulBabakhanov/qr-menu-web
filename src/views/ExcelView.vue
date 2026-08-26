<script setup lang="ts">
import { computed, ref } from 'vue'
import * as XLSX from 'xlsx'
import { AlertCircle, CheckCircle2, Download, FileCheck2, FileSpreadsheet, RotateCcw, UploadCloud } from 'lucide-vue-next'
import { createStockRemote } from '../services/stocks'

type ImportRow={name:string;price:number;valid:boolean}
const rows=ref<ImportRow[]>([]),imported=ref(false),importing=ref(false),error=ref(''),fileName=ref(''),dragging=ref(false)
const validRows=computed(()=>rows.value.filter(r=>r.valid)),invalidRows=computed(()=>rows.value.filter(r=>!r.valid))
function normalizeHeader(v:unknown){return String(v??'').toLocaleLowerCase('tr-TR').replace(/ı/g,'i').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]/g,'')}
function parsePrice(v:unknown){if(typeof v==='number')return v;const t=String(v??'').replace(/₺|TL/gi,'').replace(/\s/g,'');if(!t)return 0;return Number(t.includes(',')?t.replace(/\./g,'').replace(',','.'):t)}
function isNameHeader(value:unknown){const h=normalizeHeader(value);return['stokadi','urunadi','urunismi','stokismi','menuadi','urun','product','name'].includes(h)||((h.includes('urun')||h.includes('stok')||h.includes('menu'))&&(h.includes('ad')||h.includes('isim')))}
function isPriceHeader(value:unknown){const h=normalizeHeader(value);return['fiyat','satisfiyati','birimfiyat','tutar','price','ucret'].includes(h)||h.includes('fiyat')||h.includes('ucret')||h.includes('tutar')||h.includes('price')}
function parse(file?:File){
  if(!file)return
  if(file.size>10*1024*1024){error.value='Dosya boyutu 10 MB sınırını aşamaz.';return}
  fileName.value=file.name;error.value='';imported.value=false
  const reader=new FileReader()
  reader.onload=e=>{try{
    const book=XLSX.read(e.target?.result,{type:'array'}),sheet=book.Sheets[book.SheetNames[0]]
    const matrix=XLSX.utils.sheet_to_json<unknown[]>(sheet,{header:1,defval:'',blankrows:false})
    let headerIndex=matrix.slice(0,20).findIndex(row=>row.some(isNameHeader)&&row.some(isPriceHeader))
    let nameIndex=-1,priceIndex=-1,startIndex=0
    if(headerIndex>=0){nameIndex=matrix[headerIndex].findIndex(isNameHeader);priceIndex=matrix[headerIndex].findIndex(isPriceHeader);startIndex=headerIndex+1}
    else{
      const sample=matrix.slice(0,30),width=Math.max(0,...sample.map(r=>r.length))
      let bestText=-1,bestNumber=-1,textScore=-1,numberScore=-1
      for(let col=0;col<width;col++){
        const values=sample.map(r=>r[col]).filter(v=>String(v??'').trim())
        const texts=values.filter(v=>typeof v==='string'&&!/^\s*[\d.,]+\s*$/.test(v)).length
        const numbers=values.filter(v=>parsePrice(v)>0).length
        if(texts>textScore){textScore=texts;bestText=col}
        if(numbers>numberScore){numberScore=numbers;bestNumber=col}
      }
      nameIndex=bestText;priceIndex=bestNumber
    }
    rows.value=matrix.slice(startIndex).map(row=>{const name=String(row[nameIndex]??'').trim(),price=parsePrice(row[priceIndex]);return{name,price,valid:Boolean(name)&&Number.isFinite(price)&&price>0}}).filter(r=>r.name||r.price)
    if(!rows.value.length)error.value='Dosyada aktarılabilir ürün satırı bulunamadı.'
  }catch{error.value='Dosya okunamadı. Geçerli bir Excel dosyası seçin.'}}
  reader.readAsArrayBuffer(file)
}
function drop(e:DragEvent){dragging.value=false;parse(e.dataTransfer?.files?.[0])}
async function importRows(){
  if(importing.value)return
  importing.value=true;error.value=''
  try { await Promise.all(validRows.value.map(r=>createStockRemote(r.name,r.price,'Ana Yemekler'))); imported.value=true }
  catch(e){error.value=e instanceof Error?e.message:'Ürünler veritabanına aktarılamadı.'}
  finally{importing.value=false}
}
function reset(){rows.value=[];fileName.value='';error.value='';imported.value=false}
function downloadTemplate(){const b=XLSX.utils.book_new(),s=XLSX.utils.json_to_sheet([{'Stok Adı':'Adana Kebap',Fiyat:250},{'Stok Adı':'Ayran',Fiyat:40}]);XLSX.utils.book_append_sheet(b,s,'Ürünler');XLSX.writeFile(b,'qr-menu-urun-sablonu.xlsx')}
</script>

<template>
<div class="excel-page">
  <header class="excel-head"><div><span>TOPLU ÜRÜN İŞLEMİ</span><h2>Excel ile hızlı aktarım</h2><p>Ürün listenizi saniyeler içinde içe aktarın, menünüzü hızla hazırlayın.</p></div><button class="template-button" @click="downloadTemplate"><Download :size="17"/><span>Örnek şablonu indir</span></button></header>
  <div class="steps"><div class="active"><i>1</i><span><b>Dosya seç</b><small>Excel dosyanızı yükleyin</small></span></div><em></em><div :class="{active:rows.length}"><i>2</i><span><b>Kontrol et</b><small>Ürünlerinizi inceleyin</small></span></div><em></em><div :class="{active:imported}"><i>3</i><span><b>İçe aktar</b><small>Menünüze ekleyin</small></span></div></div>
  <div class="excel-grid">
    <section class="excel-card upload-card"><div class="card-title"><span class="title-icon"><FileSpreadsheet :size="20"/></span><div><h3>Excel dosyanızı yükleyin</h3><p>.xlsx veya .xls formatı desteklenir</p></div></div>
      <label :class="['dropzone',{dragging,'has-file':fileName}]" @dragover.prevent="dragging=true" @dragleave.prevent="dragging=false" @drop.prevent="drop"><input type="file" accept=".xlsx,.xls" @change="parse(($event.target as HTMLInputElement).files?.[0])"/><span class="drop-icon"><FileCheck2 v-if="fileName" :size="31"/><UploadCloud v-else :size="31"/></span><strong>{{fileName||'Dosyanızı buraya sürükleyin'}}</strong><p>{{fileName?'Dosya hazır · değiştirmek için tıklayın':'veya bilgisayarınızdan seçmek için tıklayın'}}</p><small>Maksimum dosya boyutu: 10 MB</small></label>
      <div class="column-note"><CheckCircle2 :size="17"/><div><b>Gerekli sütunlar</b><span>Dosyanızda “Stok Adı” ve “Fiyat” başlıkları bulunmalıdır.</span></div></div><button v-if="fileName" class="reset-file" @click="reset"><RotateCcw :size="14"/> Dosyayı kaldır</button><p v-if="error" class="error-message"><AlertCircle :size="15"/>{{error}}</p>
    </section>
    <section class="excel-card preview-card"><div class="preview-head"><div><h3>Aktarım önizlemesi</h3><p>{{rows.length?`${rows.length} ürün satırı bulundu`:'Dosyanızdaki ürünler burada görünecek'}}</p></div><span v-if="rows.length" class="ready"><i></i>HAZIR</span></div>
      <div v-if="!rows.length" class="preview-empty"><span><FileSpreadsheet :size="31"/></span><h4>Henüz dosya seçilmedi</h4><p>Sol taraftan Excel dosyanızı yükleyerek başlayın.</p><button @click="downloadTemplate"><Download :size="14"/> Şablonu indir</button></div>
      <div v-else class="preview-content"><div class="summary"><div><span>Geçerli ürün</span><strong>{{validRows.length}}</strong></div><div :class="{warning:invalidRows.length}"><span>Hatalı satır</span><strong>{{invalidRows.length}}</strong></div></div><div class="table-wrap"><table><thead><tr><th>Ürün adı</th><th>Fiyat</th><th>Durum</th></tr></thead><tbody><tr v-for="(row,i) in rows" :key="i"><td><b>{{row.name||'İsimsiz ürün'}}</b></td><td>{{row.price?`${row.price.toLocaleString('tr-TR')} ₺`:'—'}}</td><td><span :class="row.valid?'valid':'invalid'"><CheckCircle2 v-if="row.valid" :size="14"/><AlertCircle v-else :size="14"/>{{row.valid?'Uygun':'Kontrol et'}}</span></td></tr></tbody></table></div><button class="import-button" :disabled="!validRows.length||imported||importing" @click="importRows"><CheckCircle2 :size="17"/>{{importing?'Veritabanına aktarılıyor...':imported?'Ürünler başarıyla aktarıldı':`${validRows.length} ürünü menüye aktar`}}</button></div>
    </section>
  </div>
</div>
</template>

<style scoped>
.excel-page{max-width:1300px;margin:auto}.excel-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:24px}.excel-head>div>span{color:var(--orange);font-size:9px;font-weight:800;letter-spacing:1.5px}.excel-head h2{font-size:32px;letter-spacing:-1.2px;margin:7px 0}.excel-head p{font-size:12px;color:var(--muted);margin:0}.template-button{height:43px;border:1px solid #f0a47e;border-radius:11px;background:#fff9f5;color:#d85d28;padding:0 15px;display:flex;align-items:center;gap:8px;font-size:11px;font-weight:700;cursor:pointer}.steps{height:74px;background:#fff;border:1px solid var(--line);border-radius:14px;margin-bottom:17px;padding:0 28px;display:flex;align-items:center;box-shadow:0 4px 16px #20252208}.steps>div{display:flex;align-items:center;gap:10px;color:#a0a7a2}.steps i{width:29px;height:29px;border-radius:50%;display:grid;place-items:center;background:#eff1ee;font-style:normal;font-size:10px;font-weight:800}.steps b,.steps small{display:block}.steps b{font-size:10px}.steps small{font-size:8px;margin-top:3px}.steps em{height:1px;flex:1;background:#e6e9e5;margin:0 20px}.steps .active{color:#27302b}.steps .active i{background:#fff0e9;color:var(--orange)}.excel-grid{display:grid;grid-template-columns:.85fr 1.15fr;gap:17px}.excel-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:25px;box-shadow:0 6px 24px #2025220b}.card-title{display:flex;gap:12px;align-items:center;margin-bottom:21px}.title-icon{width:42px;height:42px;border-radius:11px;background:#fff0e9;color:var(--orange);display:grid;place-items:center}.excel-card h3{font-size:15px;margin:0 0 4px}.excel-card p{font-size:9px;color:var(--muted);margin:0}.dropzone{height:238px;border:2px dashed #dce1dc;border-radius:14px;background:#fafbf9;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;transition:.2s;text-align:center;padding:20px}.dropzone:hover,.dropzone.dragging{border-color:var(--orange);background:#fff9f5}.dropzone.has-file{border-color:#64aa7e;background:#f4fbf6}.dropzone input{display:none}.drop-icon{width:57px;height:57px;border-radius:16px;background:#fff;color:var(--orange);display:grid;place-items:center;margin-bottom:14px;box-shadow:0 8px 22px #2025220d}.has-file .drop-icon{color:#26925a}.dropzone strong{font-size:12px}.dropzone p{margin:7px 0}.dropzone small{font-size:8px;color:#a2a9a4}.column-note{display:flex;gap:10px;margin-top:17px;padding:12px;border-radius:11px;background:#f2f8f4;color:#32845a}.column-note div{flex:1}.column-note b,.column-note span{display:block}.column-note b{font-size:9px}.column-note span{font-size:8px;color:#6f7d74;margin-top:3px}.reset-file{border:0;background:none;color:#d85d28;font-size:9px;font-weight:700;display:flex;align-items:center;gap:5px;margin:13px auto 0;cursor:pointer}.error-message{display:flex;align-items:center;gap:6px;color:#d54d43!important;margin-top:12px!important}.preview-head{display:flex;justify-content:space-between;padding-bottom:20px;border-bottom:1px solid var(--line)}.ready{height:25px;display:flex;align-items:center;gap:5px;background:#ebf8f1;color:#21895a;border-radius:7px;padding:0 8px;font-size:8px;font-weight:800}.ready i{width:6px;height:6px;border-radius:50%;background:currentColor}.preview-empty{height:340px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}.preview-empty>span{width:59px;height:59px;border-radius:17px;background:#f2f4f1;color:#a2aaa4;display:grid;place-items:center}.preview-empty h4{font-size:12px;margin:14px 0 5px}.preview-empty button{border:0;background:none;color:var(--orange);font-size:9px;font-weight:700;margin-top:15px;display:flex;align-items:center;gap:5px;cursor:pointer}.summary{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:17px 0}.summary div{background:#f2faf5;border-radius:10px;padding:12px}.summary span,.summary strong{display:block}.summary span{font-size:8px;color:#758078}.summary strong{font-size:20px;color:#248b59;margin-top:3px}.summary .warning{background:#fff5ef}.summary .warning strong{color:#d86a35}.table-wrap{max-height:225px;border:1px solid var(--line);border-radius:11px;overflow:auto}.table-wrap th,.table-wrap td{padding:10px 12px}.table-wrap th{font-size:8px}.table-wrap td{font-size:10px}.valid,.invalid{display:inline-flex;align-items:center;gap:5px;font-size:8px;font-weight:700;color:#248b59}.invalid{color:#d75b4e}.import-button{width:100%;height:44px;border:0;border-radius:11px;background:#202522;color:#fff;margin-top:16px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:10px;font-weight:800;cursor:pointer}.import-button:hover{background:var(--orange)}.import-button:disabled{background:#d9ddda;color:#959d97;cursor:not-allowed}@media(max-width:900px){.excel-grid{grid-template-columns:1fr}.steps small{display:none}}@media(max-width:600px){.excel-head{align-items:stretch;flex-direction:column}.template-button{justify-content:center}.steps{padding:0 13px}.steps em{margin:0 8px}.steps span{display:none}.excel-card{padding:18px}}
</style>
