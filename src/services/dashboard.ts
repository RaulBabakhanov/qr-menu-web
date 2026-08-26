const viewsKey = 'qr-menu-menu-views'
const updatedKey = 'qr-menu-last-updated'
const historyKey = 'qr-menu-view-history'

export function getMenuViews() { return Number(localStorage.getItem(viewsKey) || 0) }
export function registerMenuView() {
	const today = new Date().toISOString().slice(0, 10)
	const history = getViewHistory()
	history[today] = (history[today] || 0) + 1
	localStorage.setItem(historyKey, JSON.stringify(history))
	localStorage.setItem(viewsKey, String(getMenuViews() + 1))
}
export function getViewHistory(): Record<string, number> { return JSON.parse(localStorage.getItem(historyKey) || '{}') as Record<string, number> }
export function setLastUpdated() { localStorage.setItem(updatedKey, new Date().toISOString()) }
export function getLastUpdated() { return localStorage.getItem(updatedKey) }
