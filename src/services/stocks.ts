import type { Stock } from '../types'
import { setLastUpdated } from './dashboard'

const seed: Stock[] = [
  { id: 1, name: 'Adana Kebap', price: 250, category: 'Ana Yemekler', createdAt: '2025-02-08', status: 'active' },
  { id: 2, name: 'Tavuk Şiş', price: 190, category: 'Ana Yemekler', createdAt: '2025-02-07', status: 'active' },
  { id: 3, name: 'Künefe', price: 120, category: 'Tatlılar', createdAt: '2025-02-06', status: 'active' },
  { id: 4, name: 'Ayran', price: 40, category: 'İçecekler', createdAt: '2025-02-04', status: 'active' },
]
const key = 'lokanta-stocks'
function defaultCategory(name: string) {
  const normalized = name.toLocaleLowerCase('tr')
  const words = normalized.split(/\s+/)
  if (['ayran', 'bira', 'lager', 'pilsner', 'ipa', 'weizen', 'stout', 'kola', 'çay', 'kahve', 'su'].some(item => words.includes(item))) return 'İçecekler'
  if (['künefe', 'baklava', 'tatlı', 'pasta', 'sütlaç', 'kazandibi', 'dondurma'].some(item => normalized.includes(item))) return 'Tatlılar'
  if (['gözleme', 'pide', 'lahmacun', 'börek', 'mantı'].some(item => normalized.includes(item))) return 'Hamur İşleri'
  if (normalized.includes('tost')) return 'Tostlar'
  if (['patates kızartması', 'yoğurtlu patates', 'kızarmış hellim'].some(item => normalized.includes(item))) return 'Atıştırmalıklar'
  if (['çorba', 'mercimek', 'ezogelin'].some(item => normalized.includes(item))) return 'Çorbalar'
  if (['kebap', 'şiş', 'köfte', 'döner'].some(item => normalized.includes(item))) return 'Kebaplar'
  if (['gün tabağı', 'gün menüsü', 'sosyete tabağı'].some(item => normalized.includes(item))) return 'Gün Menüleri'
  if (['kahvaltı', 'menemen', 'omlet'].some(item => normalized.includes(item))) return 'Kahvaltı'
  return 'Ana Yemekler'
}
const defaultImages: Record<string, string> = {
  'bira': 'https://images.unsplash.com/photo-1535958636474-b021ee887b13?auto=format&fit=crop&w=240&q=80',
  'adana kebap': 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=240&q=80',
  'tavuk şiş': 'https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=240&q=80',
  'künefe': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=240&q=80',
  'ayran': 'https://images.unsplash.com/photo-1576186726115-4d51596775d1?auto=format&fit=crop&w=240&q=80',
  'mito gurme gün tabağı': 'https://d2fdt3nym3n14p.cloudfront.net/venue/4189/gallery/27024/conversions/Social-19-big.jpg',
  'sosyete tabağı': 'https://images.deliveryhero.io/image/fd-tr/Products/7361441.jpg?width=900',
  'geleneksel gün tabağı': 'https://vogue.com.tr/static/img/content/23-12/28/mceu_79959681011703763506239.jpg',
  'gözleme': 'https://i.lezzet.com.tr/images-800x600/4305f2fe-016a-4c61-af8c-eacd00d2ca75-a41dd40d-ab4b-47c2-88ee-e909412ec809',
  'kuymak': 'https://www.doyouknowturkey.com/wp-content/uploads/2019/07/maxresdefault.jpg',
  'mıhlama': 'https://dobbernationloves.com/wp-content/uploads/2021/02/Kuymak-Mihlama-7.jpeg',
  'kavurma': 'https://cdn.yemek.com/mnresize/1250/833/uploads/2023/06/kavurma-kac-kalori-shutter-12.jpg',
  'omlet peynirli': 'https://images.deliveryhero.io/image/fd-tr/products/31949054.jpg?width=900',
  'peynirli omlet': 'https://static.where-e.com/Australia/Envy-Espresso_7095dda48234d733fb1aa107a8985131.jpg',
  'omlet sade': 'https://www.sethachon.com/wp-content/uploads/2023/05/Plain-Omelette-copy.jpg',
  'sade omlet': 'https://images.deliveryhero.io/image/hungerstation/menus/menuitem/hsimg-8093653?quality=75&webp=true&width=900',
  'menemen': 'https://images.unsplash.com/photo-1590412200988-a436970781fa?auto=format&fit=crop&w=900&q=82',
  'serpme kahvaltı': 'https://images.deliveryhero.io/image/fd-tr/Products/7361441.jpg?width=900',
  'tost kaşarlı': 'https://static.ticimax.cloud/cdn-cgi/image/width%3D-%2Cquality%3D85/9247/uploads/urunresimleri/buyuk/kasarli-tost-dcb9.jpg',
  'kaşarlı tost': 'https://images.deliveryhero.io/image/fd-tr/LH/k4jj-listing.jpg',
  'tost sucuklu': 'https://www.tasocakfirin.com/image/cache/catalog/products_2021/Sucuklu-Tost-1000x1000.jpg',
  'sucuklu tost': 'https://vasalisa.store/images/product_68790affee8575.51113590.jpg',
  'kızarmış hellim': 'https://imgrosetta.yemek.com/file/160150/160150-1250x833.jpg',
  'hızlı kahvaltı tabağı': 'https://images.deliveryhero.io/image/fd-tr/Products/74618972.jpg?width=900',
  'mito serpme kahvaltı': 'https://www.grandma.com.tr/wp-content/uploads/2024/05/GRANDMA-EDIT-PS-mart24-23.jpg',
  'yoğurtlu patates': 'https://i.lezzet.com.tr/images-800x600/d061bdf7-9441-4b6d-abed-122756ad20c4-293b42c4-7f78-40ee-a7c5-4a0d0cd04f03',
  'patates kızartması': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=900&q=82',
}

function imageForStock(stock: Stock) {
  const name = stock.name.toLocaleLowerCase('tr')
  if (stock.image?.startsWith('data:')) return stock.image
  if (defaultImages[name]) return defaultImages[name]
  if (stock.image && !stock.image.includes('photo-1547592180-85f173990554')) return stock.image
  if (name.includes('gözleme')) return defaultImages['gözleme']
  if (name.includes('kuymak')) return defaultImages['kuymak']
  if (name.includes('mıhlama') || name.includes('muhlama')) return defaultImages['mıhlama']
  if (name.includes('kavurma')) return defaultImages['kavurma']
  if (name.includes('omlet') && name.includes('peynir')) return defaultImages['omlet peynirli']
  if (name.includes('omlet')) return defaultImages['omlet sade']
  if (name.includes('tatlı') || stock.category === 'Tatlılar') return 'https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=900&q=82'
  if (name.includes('içecek') || stock.category === 'İçecekler') return 'https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=82'
  return 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=82'
}

export function getStocks(): Stock[] {
  const stored = localStorage.getItem(key)
  if (!stored) { const initialized = seed.map(stock => ({ ...stock, category: defaultCategory(stock.name), image: defaultImages[stock.name.toLocaleLowerCase('tr')] })); localStorage.setItem(key, JSON.stringify(initialized)); return initialized }
  const categoryMigrationKey = 'lokanta-stock-categories-v3'
  const shouldCategorize = !localStorage.getItem(categoryMigrationKey)
  const normalizedStocks = (JSON.parse(stored) as Stock[]).map(stock => { const normalized = { ...stock, category: shouldCategorize ? defaultCategory(stock.name) : (stock.category ?? defaultCategory(stock.name)), status: stock.status ?? 'active' } as Stock; return { ...normalized, image: imageForStock(normalized) } })
  if (shouldCategorize) { localStorage.setItem(key, JSON.stringify(normalizedStocks)); localStorage.setItem(categoryMigrationKey, '1') }
  return normalizedStocks
}
export function saveStocks(stocks: Stock[]) { localStorage.setItem(key, JSON.stringify(stocks)); setLastUpdated() }
export function addStock(name: string, price: number, category = defaultCategory(name)) {
  const stocks = getStocks(); const stock: Stock = { id: Date.now(), name, price, category, createdAt: new Date().toISOString(), status: 'active' }
  saveStocks([stock, ...stocks]); return stock
}
export function removeStock(id: number) { saveStocks(getStocks().filter(stock => stock.id !== id)) }
export function clearStocks() { saveStocks([]) }
export function updateStock(updated: Stock) { saveStocks(getStocks().map(stock => stock.id === updated.id ? updated : stock)) }
