// frontend/src/stores/app.js
import { writable } from 'svelte/store';

export const appState = writable({
    user: null,
    isAuthenticated: false,
    currentImage: null,
    currentImages: [],
    invoiceData: {},
    isProcessing: false,
    isVerifying: false,
    error: null,
    success: null,
    saved: false
});

export const authStore = writable({
    token: null,
    user: null,
    isAuthenticated: false
});

export const invoiceStore = writable({
    currentInvoice: {},
    invoices: [],
    loading: false
});