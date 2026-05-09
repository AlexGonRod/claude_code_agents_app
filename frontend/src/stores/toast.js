import { writable } from 'svelte/store';

export const toast = writable({ message: '', type: 'success', visible: false });

export function showToast(message, type = 'success', duration = 3000) {
  toast.set({ message, type, visible: true });
  setTimeout(() => {
    toast.set({ message: '', type: 'success', visible: false });
  }, duration);
}